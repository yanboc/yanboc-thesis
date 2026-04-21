# includefile

本目录用于管理论文前置/中置/后置模块与可复用片段，是主文件装配流程的关键节点。

## 文件总览

- `frontmatter.tex`：英文封面、声明、授权协议、创新点页装配。
- `statement.tex`：论文原创性声明页。
- `protocol.tex`：学位论文使用授权协议书页。
- `innovation.tex`：论文创新点正文。
- `midmatter.tex`：中英文摘要与关键词。
- `backmatter.tex`：科研成果、学术服务、致谢等后置内容。
- `acknowledgement.tex`：致谢正文（当前为空）。
- `gls_cmd.tex`：术语与缩略语条目定义。

### 前置页装配（`frontmatter.tex`）

主要内容：
- 排版英文封面字段并插入模板图形。
- 依次引入声明、授权协议与创新点模块。

注意事项：
- 与 `figures/template/`、`WHUPhd.cls` 中字段定义耦合较强。

### 声明与授权（`statement.tex`、`protocol.tex`）

主要内容：
- 提供学校规范化声明文本与签字区域模板。

可改项建议：
- 可保留版式骨架，替换为目标院校要求文本。

### 摘要与关键词（`midmatter.tex`）

主要内容：
- 包含中文摘要、英文摘要及关键词块。
- 当前文件含具体 thesis 内容，后续应改为模板指引与占位文本。

### 后置页与术语（`backmatter.tex`、`acknowledgement.tex`、`gls_cmd.tex`）

主要内容：
- `backmatter.tex` 组织成果、致谢等模块并控制分页。
- `gls_cmd.tex` 定义 glossary 术语条目及首现样式规则。

注意事项：
- `gls_cmd.tex` 与 `settings/gls.tex` 联动；术语命名、排序字段需保持一致规范。
