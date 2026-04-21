# WHU Thesis LaTeX Template

面向中文学位论文写作的 LaTeX 模板，提供可复用的论文结构、集中化配置和模块化维护方式。

![LaTeX](https://img.shields.io/badge/LaTeX-XeLaTeX-008080?logo=latex)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/License-See%20LICENSE-lightgrey)
![Status](https://img.shields.io/badge/Status-Template%20Ready-brightgreen)

## ✨ Features

- 统一入口：通过 `thesis.tex` 组装全文内容。
- 配置集中：`settings/` 统一管理字体、引用、术语、绘图与快捷命令。
- 内容模块化：封面/摘要/致谢、章节、附录、参考文献分目录维护。
- 中文友好：内置中文交叉引用与国标参考文献样式配置。
- 写作提速：支持快速编译模式（占位图替换）以减少迭代耗时。

## 🗂️ Project Structure

```text
.
├─ thesis.tex                # 主入口
├─ settings/                 # 全局排版与功能配置
├─ includefile/              # 封面、声明、摘要、后置内容
├─ chapters/                 # 正文章节（当前为 chap1-3）
├─ appendix/                 # 附录
├─ refs/                     # 参考文献与辅助脚本
├─ figures/                  # 图片与模板资源
└─ fonts/                    # 字体文件
```

各子目录下的 `_agent.md` 用于记录目录职责、编辑边界与维护建议。

## 🚀 Quick Start

1. 安装 LaTeX 发行版（推荐 TeX Live，或 MiKTeX）。
2. 使用 XeLaTeX 工作流编译 `thesis.tex`。
3. 按目录职责替换占位内容（章节、摘要、附录、作者信息等）。
4. 在 `refs/ref.bib` 维护文献条目并在正文中引用。
5. 定稿前执行完整编译，检查目录、引用与图表编号。

## 🔁 Recommended Workflow

- 日常改稿：使用快速链路（如 `xelatex + bibtex`）提升反馈速度。
- 术语更新：涉及 `glossaries` 时运行对应索引流程（如 `makeglossaries`）。
- 定稿构建：使用完整链路多轮编译，确保交叉引用与目录稳定。
- 文献整理：可结合 `refs/prepare_ref.py` 进行 Bib 条目去重与清理。

## 🛠️ Customization Guide

- 字体与配色：`settings/design.tex`
- 参考文献样式：`settings/bib_style.tex`
- 中文交叉引用：`settings/cleveref-chinese.tex`
- 术语系统：`settings/gls.tex` 与 `includefile/gls_cmd.tex`
- 绘图配置：`settings/plotting.tex`
- 快捷命令：`settings/shortcuts.tex`
- 快速编译：`settings/quick_compile.tex`

## 📚 References

- WHUTUG 模板：<https://github.com/whutug/whu-thesis>
- Overleaf 模板（黄正华老师）：<https://www.overleaf.com/latex/templates/wu-yi-da-xue-bo-shi-lun-wen-latex-mo-ban/rcdzgvqgkddk>
- GB/T 7714—2015 宏包：<https://github.com/zepinglee/gbt7714-bibtex-style>

## 📄 License

本项目采用仓库内 `LICENSE` 文件所声明的许可协议。
