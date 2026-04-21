# LaTeX 使用说明（基于 `settings/` 与 `WHUPhd.cls`）

## 1. 入口与总体组织。
主入口文件是 `thesis.tex`。
主文件通过 `\input{settings/__settings__}` 加载统一配置。
正文结构与章节安排可参考 `notes/structure.md`。
正文章节当前由 `chapters/chap1` 到 `chapters/chap3` 组成（可按需扩展）。
附录由 `appendix/notations` 与 `appendix/experiments` 组成。

## 2. 文档类与编译引擎。
文档类是 `WHUPhd`，当前选项为 `forlib`（见 `\documentclass[forlib]{WHUPhd}`）。
`settings/design.tex` 使用了 `fontspec` 与 `\setCJKmainfont`，因此需要 XeLaTeX 或 LuaLaTeX。
本项目字体路径依赖 `fonts/` 目录下 Fandol 字体族。
若字体文件缺失会导致中文字体相关错误。

## 3. 关键配置来源（`settings/__settings__.tex`）。
`settings/bib_style.tex`：参考文献样式与条目间距设置（`gbt7714-numerical`）。
`settings/design.tex`：中文字体、颜色方案与 `tcolorbox` 环境（如 `mynote`、`mynotice`）。
`settings/gls.tex`：`glossaries` 配置与术语命令入口（`includefile/gls_cmd.tex`）。
`settings/plotting.tex`：TikZ/PGFPlots 与图形样式。
`settings/shortcuts.tex`：数学符号与算子快捷命令（如 `\btheta`、`\attn`、`\softmax`）。
`settings/cleveref-chinese.tex`：中文交叉引用名称与格式（`\cref`/`\Cref`）。
`settings/quick_compile.tex`：快速编译占位图开关（`fastcompile`）。

## 4. `WHUPhd.cls` 中与写作强相关的约定。
页面版式、页眉页脚、目录深度、章节编号风格由类文件统一控制。
定理环境在类文件中已预定义（如 `theorem`、`lemma`、`proposition`、`assumption`、`proof`）。
摘要环境已定义为 `cnabstract` 与 `enabstract`。
图片默认搜索路径为 `figures/`（`\\graphicspath{{figures/}}`）。

## 5. 日常写作建议（面向本项目）。
新增术语优先走 `glossaries` 体系，避免正文硬编码缩写定义。
交叉引用优先使用 `\cref`，保持中文编号与名称自动一致。注意一些特殊情况：当\cref{}后面直接跟标点符号（如“，”、“。”、“；”、“：”、“！”、“？”）时，\cref会出问题。此时须使用 `\ref` 临时替换。
数学符号优先复用 `settings/shortcuts.tex` 中已有命令，避免同义新符号增殖。
图表优先使用 `booktabs` 风格，表题/图题保持“对象 + 数据集/设置 + 统计口径”的结构。
如需局部快速预览可开启 `fastcompiletrue`，提交前再切回 `fastcompilefalse`。

## 6. 与当前协作偏好的一致性提醒。
当前用户偏好是不需要助手执行 LaTeX 编译。
正文编辑建议保持“一句话一行”，便于索引、审阅与自动化检索。
