# settings

本目录集中管理论文模板的排版样式、引用格式、术语系统、绘图设置与编译策略。

## 文件总览

- `__settings__.tex`：总入口，按顺序加载本目录的各配置文件，并设置章节样式。
- `bib_style.tex`：参考文献样式与条目间距细节。
- `cleveref-chinese.tex`：中文交叉引用（章、节、图、表、定理等）命名与格式。
- `design.tex`：中文字体、颜色和 `tcolorbox` 环境。
- `gls.tex`：术语表/缩略语系统（`glossaries`）配置。
- `plotting.tex`：`tikz/pgfplots` 绘图环境和样式。
- `quick_compile.tex`：快速编译开关，替换图片与 TikZ 输入以提速。
- `shortcuts.tex`：常用宏命令、数学符号命令、算法相关包。

### 总配置入口（`__settings__.tex`）

主要内容：
- 加载 `booktabs`，并依次 `\input` 其他配置文件（文献、版式、术语、绘图、快捷命令、中文引用、快速编译）。
- 使用 `\ctexset` 统一章节格式：章标题居中加粗、中文编号“第X章”，并设置节/小节字体。
- 重定义 `\paragraph` 为“不编号的小标题段”样式。
- 定义 `myproof` 环境，自动在结尾输出方块证毕符号。

可改项建议：
- 可调整 `\ctexset` 中标题字号与显示风格以匹配学校规范。
- 可修改 `myproof` 默认标题文本（如“证明”/“Proof”）。

### 参考文献管理（`bib_style.tex`）

主要内容：
- 启用 `gbt7714`，并设置 `\bibliographystyle{gbt7714-numerical}`（国标数字制）。
- 使用 `etoolbox` 对 `natbib` 数值模式下的列表参数做补丁，统一参考文献条目间距（`itemsep`、`parsep`）。

### cleveref中文配置（`cleveref-chinese.tex`）

主要内容：
- 加载 `hyperref` 与 `cleveref`，实现可点击的中文交叉引用。
- 通过 `\crefname`/`\Crefname` 为 equation、figure、table、theorem、chapter、section 等对象设置中文名称。
- 通过 `\crefformat`、`\crefmultiformat`、`\crefrangeformat` 定义单个/多个/区间引用格式。

### 版式与字体设计（`design.tex`）

主要内容：
- 使用 `fontspec` + Fandol 字体配置中文字体族。
- 定义颜色常量与 `tcolorbox` 环境（`mybox`、`mynotice`、`mynote`）。

### 术语与缩略语系统（`gls.tex`）

主要内容：
- 启用 `glossaries` 并设置中文索引参数。
- 通过 `\input{includefile/gls_cmd.tex}` 载入术语条目定义。

### 绘图配置（`plotting.tex`）

主要内容：
- 启用 `tikz`、`pgfplots`、`tikz-3dplot`。
- 统一图元样式并声明多层绘图层级。

### 快速编译模式（`quick_compile.tex`）

主要内容：
- 通过 `\iffastcompile` 切换快速/完整编译。
- 快速模式下用 `figures/dummy.pdf` 替代真实图像与 TikZ 输入。

### 快捷命令与常用包（`shortcuts.tex`）

主要内容：
- 汇总常用包、数学符号宏与算子命令。
- 统一论文公式表达与算法环境接口。
