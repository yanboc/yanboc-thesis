"""
示例1：基于重构的异常检测（Reconstruction-Based Anomaly Detection）

主要内容：
- 信号-噪声数据生成（正交特征 + 正常/异常 patch）
- 浅层卷积自编码器 ConvAE 训练与权重追踪
- 结果可视化

参考文献：
[1] Two-Layer Convolutional Autoencoders Trained on Normal Data Provably Detect Unseen Anomalies, Yanbo Chen & Weiwei Liu, https://openreview.net/forum?id=FnbGlnKbIU

使用方法:
    在项目根目录: python examples/example_1.py
"""

from pathlib import Path
import math
import os
import json
import itertools

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

PLOT_PATH = Path("/root/autodl-tmp/ezflt/thesis/rbad/figures")
MODEL_PATH = Path("/root/autodl-tmp/ezflt/thesis/rbad/models")
os.makedirs(PLOT_PATH, exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)
os.makedirs((PLOT_PATH / f"error_boxplot"), exist_ok=True)
os.makedirs((PLOT_PATH / f"kernel_heatmaps"), exist_ok=True)
os.makedirs((PLOT_PATH / f"norm_growth"), exist_ok=True)

# 自包含配置，不依赖项目根 config.py
def _get_rbad_config():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "experiment_id": "example_experiment_RBAD",
        "seed": 42,
        "repeats": 1,
        "device": device,
        "data": {
            "data_type": "tensor",
            "train_size": 4000,
            "test_size": 1000,
            "batch_size": 64,
            "shuffle": True,
            "parameters": {
                "P": [16, 28, 32, 64, 128], 
                "d_P_ratio": [1.2], 
                "C_d_ratio": [0.8, 1.2], 
                "NNF_ratio": [0.5],
                "NRP_ratio": [0, 0.1, 0.2],
            },
        }
    }

def process_parameters(P, d_P_ratio, C_d_ratio, NNF_ratio, NRP_ratio):
    d = math.floor(P * d_P_ratio)
    C = math.floor(d * C_d_ratio)
    NNF = math.floor(P * NNF_ratio)
    NRP = math.ceil(P * NRP_ratio) + 2
    return (P, d, C, NNF, NRP)

def generate_feature(d, device="cuda"):
    M = torch.randn(d, d, device=device)
    Q, _ = torch.linalg.qr(M)
    return Q

def generate_beta(d, NNF, device="cuda"):
    beta = torch.zeros(d, device=device)
    beta[NNF:] = torch.rand(d - NNF, device=device)
    return beta

def generate_normal(feature, beta, P, N, NNF, sigma=0.01, device="cuda"):
    feature_index = torch.multinomial(beta, N * (P - NNF), replacement=True)
    feature_index = feature_index.view(N, P - NNF)
    nor_features = feature[:NNF, :]
    x_nor = nor_features.unsqueeze(0).repeat(N, 1, 1)
    x_aux = feature[feature_index]
    x = torch.cat([x_nor, x_aux], dim=1) + torch.randn(
        N, P, feature.shape[1], device=device
    ) * sigma
    return x

def generate_semantic_anomaly(feature, beta, P, N_sa, NRP, NNF, sigma=0.01, device="cuda"):
    x = generate_normal(feature=feature, beta=beta, P=P, N=N_sa, NNF=NNF, sigma=sigma, device=device)
    feature_index = torch.multinomial(beta, N_sa * NRP, replacement=True)
    feature_index = feature_index.view(N_sa, NRP)
    x[:, :NRP, :] = feature[feature_index] + torch.randn(
        N_sa, NRP, feature.shape[1], device=device
    ) * 0.15
    return x

def generate_non_semantic_anomaly(feature, beta, P, N_nsa, NRP, NNF, device="cuda"):
    x = generate_normal(feature=feature, beta=beta, P=P, N=N_nsa, NNF=NNF, device=device)
    x[:, :NRP, :] = torch.randn(
        N_nsa, NRP, feature.shape[1], device=device
    ) * 0.5
    return x

class ConvAE(nn.Module):
    """
    浅层卷积自编码器：用 nn.Linear(d, C) 作为可追踪的 encoder，便于 ezflt FeatureTracker 记录核演化。
    """

    def __init__(self, d: int, C: int, device="cuda"):
        super().__init__()
        self.d = d
        self.C = C
        self.device = device
        self.encoder = nn.Linear(d, C)
        nn.init.normal_(self.encoder.weight, std=0.001)
        self.relu = nn.ReLU()

    def forward(self, x):
        bsz, P, d = x.shape
        # Encoder: (bsz, P, d) @ (d, C) -> (bsz, P, C)
        x = F.linear(x, self.encoder.weight)
        x = self.relu(x)
        indices = torch.argmax(x.transpose(1, 2), dim=-1, keepdim=True)
        expanded = self.encoder.weight.unsqueeze(0).expand(bsz, -1, -1)
        output = torch.zeros(bsz, P, d, device=self.device)
        output.scatter_add_(
            dim=1,
            index=indices.expand(-1, -1, d),
            src=expanded,
        )
        return output

def run_one_experiment(params, all_kernels_norm, all_kernels_inner_product, device="cuda", use_checkpoint=True):
    P, d, C, NNF, NRP = process_parameters(*params)
    model_id = f"P={P}_d={d}_C={C}_NNF={NNF}"
    plot_id = f"P={P}_d={d}_C={C}_NNF={NNF}_NRP={NRP}"
    epochs = 100
    N = 4000
    sigma = 0.01

    

    all_kernels_inner_product[model_id] = torch.zeros(epochs//10, C, device=device)
    all_kernels_norm[model_id] = torch.zeros(epochs//10, C, device=device)

    feature = generate_feature(d, device=device)
    beta = generate_beta(d=d, NNF=NNF, device=device)
    X = generate_normal(feature=feature, beta=beta, P=P, N=N, NNF=NNF, sigma=sigma, device=device)

    device = torch.device(_get_rbad_config()["device"])
    model = ConvAE(d=d, C=C, device=device)
    model.to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    # 重构任务：目标与输入相同
    dataset = TensorDataset(X, X)
    train_loader = DataLoader(
        dataset,
        batch_size=4000,
        shuffle=True,
    )

    if os.path.exists(os.path.join(MODEL_PATH, f"{model_id}.pth")) and use_checkpoint:
        model.encoder.weight.data = torch.load(
            os.path.join(MODEL_PATH, f"{model_id}.pth"), map_location=device
        )
        all_kernels_norm[model_id] = torch.load(
            os.path.join(MODEL_PATH, f"{model_id}_norm.pth"), map_location=device, weights_only=True
        )
        all_kernels_inner_product[model_id] = torch.load(
            os.path.join(MODEL_PATH, f"{model_id}_inner_product.pth"), map_location=device, weights_only=True
        )
        print(f"Loaded model from {os.path.join(MODEL_PATH, f"{model_id}.pth")}")
    else:
        for epoch in range(epochs):
            model.train()
            for batch_idx, (batch_x, batch_y) in enumerate(train_loader):
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                recon = model(batch_x)
                loss = criterion(recon, batch_y)
                loss.backward()
                optimizer.step()

            # eval
            if (epoch + 1) % 10 == 0:
                model.eval()
                with torch.no_grad():
                    for batch_idx, (batch_x, batch_y) in enumerate(train_loader):
                        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                        recon = model(batch_x)
                        loss = criterion(recon, batch_y)
                        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")
                    all_kernels_norm[model_id][epoch//10, :] = torch.norm(model.encoder.weight.detach().cpu(), dim=-1)
                    all_kernels_inner_product[model_id][epoch//10, :] = torch.max(torch.tensordot(model.encoder.weight, feature, dims=([-1], [-1])), dim=-1).values.detach().cpu()

        torch.save(model.encoder.weight.detach().cpu(), os.path.join(MODEL_PATH, f"{model_id}.pth"))
        torch.save(all_kernels_norm[model_id], os.path.join(MODEL_PATH, f"{model_id}_norm.pth"))
        torch.save(all_kernels_inner_product[model_id], os.path.join(MODEL_PATH, f"{model_id}_inner_product.pth"))

    plot_reconstruction_error(model, feature, beta, P, NNF, NRP, sigma, plot_id, C, d)
    plot_kernel_heatmaps(all_kernels_norm, all_kernels_inner_product)

def plot_reconstruction_error(model, feature, beta, P, NNF, NRP, sigma, plot_id, C, d):
    dev = model.device if hasattr(model, "device") else next(model.parameters()).device
    N = 1000
    X_sem = generate_semantic_anomaly(feature=feature, beta=beta, P=P, N_sa=N, NRP=NRP, NNF=NNF, sigma=sigma, device=dev)
    X_nsa = generate_non_semantic_anomaly(feature=feature, beta=beta, P=P, N_nsa=N, NRP=NRP, NNF=NNF, device=dev)
    X_nor = generate_normal(feature=feature, beta=beta, P=P, N=N, NNF=NNF, sigma=sigma, device=dev)

    with open(os.path.join(MODEL_PATH, "mean_loss.json"), "r", encoding="utf-8") as f:
        mean_loss = json.load(f)

    if (P in mean_loss["P"]) and (d in mean_loss["d"]) and (C in mean_loss["C"]) and (NNF in mean_loss["NNF"]) and (NRP in mean_loss["NRP"]):
        pass
    else:
        mean_loss["P"].append(P)
        mean_loss["d"].append(feature.shape[0])
        mean_loss["C"].append(C)
        mean_loss["NNF"].append(NNF)
        mean_loss["NRP"].append(NRP)
        mean_loss["nor"].append(F.mse_loss(model(X_nor), X_nor).detach().cpu().item())
        mean_loss["sem"].append(F.mse_loss(model(X_sem), X_sem).detach().cpu().item())
        mean_loss["non-sem"].append(F.mse_loss(model(X_nsa), X_nsa).detach().cpu().item())

        with open(os.path.join(MODEL_PATH, "mean_loss.json"), "w", encoding="utf-8") as f:
            json.dump(mean_loss, f, ensure_ascii=False, indent=4)

    nor_err = F.mse_loss(model(X_nor), X_nor, reduction='none').mean(dim=(1, 2)).detach().cpu().numpy()
    sem_err = F.mse_loss(model(X_sem), X_sem, reduction='none').mean(dim=(1, 2)).detach().cpu().numpy()
    nsa_err = F.mse_loss(model(X_nsa), X_nsa, reduction='none').mean(dim=(1, 2)).detach().cpu().numpy()
    labels = ['nor', 'sem', 'non-sem']
    data_list = [nor_err, sem_err, nsa_err]
    # box_colors = ['#4575b4', '#ffffbf', '#d73027']
    box_colors = ['#dde8fc', '#f8cecc', '#b85450']

    # 4. 纵坐标轴范围（rescale，手动指定/自动适配二选一）
    # y_min = -5   # 纵轴最小值
    # y_max = 10   # 纵轴最大值
    y_min = min([min(d) for d in data_list]) * 0.9  # 自动取最小值-1
    y_max = max([max(d) for d in data_list]) * 1.01  # 自动取最大值+1

    # ===================== 绘制箱型图 =====================
    # 创建画布（可调尺寸、分辨率）
    fig, ax = plt.subplots(figsize=(5, 5), dpi=72)

    # 绘制基础箱型图
    box_plot = ax.boxplot(
        data_list,
        labels=labels,                # 每组标签
        patch_artist=True,            # 开启箱体填充色（必须开才能改颜色）
        showmeans=True,               # 显示均值点
        showfliers=True,              # 显示异常值（True/False）
        notch=False,                  # 是否绘制凹口箱型图（False=普通箱型图）
        widths=0.8,                   # 箱体宽度（0-1，默认0.5）
        sym='x',                      # 异常值标记样式（x/+/o/*等）
        vert=True,                    # 垂直/水平箱型图（True=垂直，False=水平）
        positions=None,               # 箱体位置（默认[1,2,3]，可自定义如[1,2.5,4]）
        
        # 样式参数（精细化调整）
        meanprops={
            'marker': 'o',            # 均值点样式
            'markerfacecolor': 'yellow', # 均值点填充色
            'markeredgecolor': 'black',  # 均值点边框色
            'markersize': 6,          # 均值点大小
            'markeredgewidth': 1      # 均值点边框宽度
        },
        medianprops={
            'color': 'black',         # 中位数线颜色
            'linewidth': 1,           # 中位数线宽度
            'linestyle': '-'          # 中位数线样式（-/_/--/-.等）
        },
        whiskerprops={
            'color': 'gray',          # 须线颜色
            'linewidth': 1,         # 须线宽度
            'linestyle': '--'         # 须线样式
        },
        capprops={
            'color': 'black',         # 端线（须线顶端）颜色
            'linewidth': 1          # 端线宽度
        },
        flierprops={
            'marker': 'x',            # 异常值样式
            'markerfacecolor': 'white', # 异常值填充色
            'markeredgecolor': 'black', # 异常值边框色
            'markersize': 6,          # 异常值大小
            'alpha': 0.7              # 异常值透明度（0-1）
        }
    )

    for box, color in zip(box_plot['boxes'], box_colors):
        box.set(facecolor=color,    # 箱体填充色
                edgecolor='black',  # 箱体边框色
                linewidth=1,        # 箱体边框宽度
                alpha=0.8)          # 箱体透明度（0-1）

    ax.set_ylim(y_min, y_max)  # 手动设置纵轴范围
    # ax.set_yticks(np.arange(y_min, y_max+1, 1))  # 纵轴刻度间隔（示例：每1个单位显示一个刻度）
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))  # 纵轴刻度格式（保留3位小数）

    ax.set_xlabel('Data Types', fontsize=14, labelpad=10)
    ax.set_ylabel('Reconstruction Error', fontsize=14, labelpad=10)

    ax.tick_params(axis='x', labelsize=12, rotation=0)
    ax.tick_params(axis='y', labelsize=12)

    # 3. 网格线
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='gray')  # 仅显示水平网格线
    ax.set_axisbelow(True)  # 网格线置于图表底层（不遮挡箱型图）

    # 4. 边框样式
    for spine in ax.spines.values():  # 隐藏顶部/右侧边框
        spine.set_visible(True)
        spine.set_linewidth(1.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 5. 图例（可选，标注均值/中位数）
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w',markerfacecolor='yellow', markeredgecolor='black', markersize=8, label='Mean'),
        Line2D([0], [0], color='black', linewidth=1, label='Median'),
        Line2D([0], [0], marker='x', color='w',markerfacecolor='white', markeredgecolor='black', markersize=6, label='Outliers'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12)

    # 5. 显示图表
    plt.tight_layout()  # 自动调整布局
    plt.savefig(PLOT_PATH / f"error_boxplot" / f"re_{plot_id}.pdf")
    plt.close()

def plot_kernel_heatmaps(all_kernels_norm, all_kernels_inner_product, num_epochs_per_plot=10):
    for model_id in all_kernels_inner_product:
        C = all_kernels_inner_product[model_id].shape[1]
        epochs_total = all_kernels_norm[model_id].shape[0]
        step = max(1, epochs_total // num_epochs_per_plot)
        n_rows = (epochs_total + step - 1) // step
        plot_values_ip = np.zeros((n_rows, C))
        plot_values_norm = np.zeros((n_rows, C))
        for i in range(n_rows):
            e = min(i * step, epochs_total - 1)
            plot_values_norm[i, :] = all_kernels_norm[model_id][e].detach().cpu().numpy()
            n = plot_values_norm[i, :]
            n[n == 0] = 1e-8
            plot_values_ip[i, :] = all_kernels_inner_product[model_id][e].detach().cpu().numpy() / n

        fig, axes = plt.subplots(2, 1, figsize=(max(C, 4), 2 * n_rows), dpi=72)

        ax_ip = sns.heatmap(
            plot_values_ip,
            annot=True,
            cbar=False,
            fmt=".3f",
            cmap=custom_cmap,
            square=False,
            ax=axes[0],
        )
        ax_ip.set_xlabel("Kernel ID")
        ax_ip.set_ylabel("Epoch")

        ax_norm = sns.heatmap(
            plot_values_norm * 10,
            annot=True,
            cbar=False,
            fmt=".4f",
            cmap=custom_cmap,
            square=False,
            ax=axes[1],
        )
        # ax_norm.set_title(f"Kernels Norm (x10)")
        ax_norm.set_xlabel("Kernel ID")
        ax_norm.set_ylabel("Epoch")
        plt.tight_layout()
        plt.savefig(PLOT_PATH / f"kernel_heatmaps" / f"{model_id}.pdf")
        plt.close()
        print(f"  Saved {model_id}.pdf")

def plot_mean_loss(mean_loss):
    for j in range(len(mean_loss["P"])//6):
        for k in range(6):
            i = j * 6 + k
            plot_id = f"P={mean_loss['P'][i]}_d={mean_loss['d'][i]}_C={mean_loss['C'][i]}_NNF={mean_loss['NNF'][i]}_NRP={mean_loss['NRP'][i]}"
            # ===================== 1. 准备数据（整理为DataFrame格式） =====================
            X = mean_loss["P"][i]
            Y1 = mean_loss["nor"][i]
            Y2 = mean_loss["sem"][i]
            Y3 = mean_loss["non-sem"][i]

            cdr = 0.8
            if mean_loss["C"][i] == math.floor(mean_loss["d"][i] * 1.2):
                cdr = 1.2
            nrp = 0
            if mean_loss["NRP"][i] == math.ceil(mean_loss["P"][i] * 0.1) + 2:
                nrp = 0.1
            if mean_loss["NRP"][i] == math.ceil(mean_loss["P"][i] * 0.2) + 2:
                nrp = 0.2

            # 整理为Seaborn兼容的长格式DataFrame
            df = pd.DataFrame({
                'X': np.concatenate([X, X, X]),
                'Y': np.concatenate([Y1, Y2, Y3]),
                'Group': ['Normal']*len(X) + ['Semantic']*len(X) + ['Non-Semantic']*len(X)
            })

            # ===================== 2. 配置样式与字体 =====================
            sns.set_style("whitegrid")  # 内置样式（可选：darkgrid/white/ticks）
            plt.rcParams['font.sans-serif'] = ['FandolHei', 'WenQuanYi Micro Hei']
            plt.rcParams['axes.unicode_minus'] = False

            # ===================== 3. 绘制多折线图 =====================
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

            # 用Seaborn绘制（自动区分组别）
            sns.lineplot(
                data=df,
                x='X',
                y='Y',
                hue='Group',          # 按Group列区分折线
                style='Group',        # 按Group列区分线型
                markers=True,         # 显示标记点
                dashes=False,         # 禁用默认虚线（如需自定义线型，设为True）
                linewidth=2,
                markersize=8,
                palette=['#2166ac', '#b2182b', '#1a9850'],  # 自定义3组颜色
                ax=ax
            )

            # ===================== 4. 美化标注 =====================
            ax.set_title('Seaborn版：单X轴 + 3组Y轴数据折线图', fontsize=16, pad=20)
            ax.set_xlabel('X轴（自变量）', fontsize=12)
            ax.set_ylabel('Y轴（因变量）', fontsize=12)
            ax.legend(title='数据组别', fontsize=10, title_fontsize=12)

            # 隐藏顶部/右侧边框
            sns.despine(top=True, right=True)

        plt.tight_layout()
        plt.savefig(PLOT_PATH / f"line_plots" / f"mean_loss_cdr={cdr}_nrp={nrp}.pdf")
        plt.close()

if __name__ == "__main__":

    CONFIG = _get_rbad_config()
    torch.manual_seed(42)

    colors_list = [
    (0, '#f8cecc'),
    (1, '#b85450')]
    custom_cmap = LinearSegmentedColormap.from_list('my_coolwarm', colors_list, N=256)

    mean_loss = {"P": [], "d": [], "C": [], "NNF": [], "NRP": [], "nor": [], "sem": [], "non-sem": []}
    with open(os.path.join(MODEL_PATH, "mean_loss.json"), "w", encoding="utf-8") as f:
        json.dump(mean_loss, f, ensure_ascii=False, indent=4)

    for params in list(itertools.product(*CONFIG["data"]["parameters"].values())):
        print("RBAD 示例：多组参数训练 + 核范数/内积可视化")
        print("=" * 60)
        all_kernels_norm = {}
        all_kernels_inner_product = {}
        print(f"  参数组合: {params}")
        run_one_experiment(
            params, all_kernels_norm, all_kernels_inner_product
        )
