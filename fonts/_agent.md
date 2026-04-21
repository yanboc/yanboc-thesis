# fonts

本目录存放模板依赖字体文件，主要由 `settings/design.tex` 通过相对路径加载。

## 文件总览

- `FandolSong-Regular.otf`、`FandolSong-Bold.otf`
- `FandolHei-Regular.otf`、`FandolHei-Bold.otf`
- `FandolKai-Regular.otf`
- `FandolFang-Regular.otf`

### 字体映射关系

主要内容：
- 宋体、黑体、楷体、仿宋在配置文件中已绑定到上述字体文件。
- 模板通过 `fontspec` 与 `ctex` 相关命令调用这些字体。

可改项建议：
- 可按学校规范替换字体，但需同步修改 `settings/design.tex` 的字体名与族定义。

注意事项：
- 不建议仅替换文件名不改配置；这会导致 XeLaTeX/LuaLaTeX 找不到字体。
