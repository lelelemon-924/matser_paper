# 基于指令微调与安全对齐的数字电网大语言模型应用研究

本仓库为硕士学位论文初稿的 LaTeX 工程，包含论文源文件、插图资源以及编译所需的哈尔滨工业大学学位论文模板（hithesis v3）文件。

## 目录结构

| 文件/目录 | 说明 |
| --- | --- |
| `论文初稿.tex` | 论文主文件（摘要、正文、参考文献均在其中） |
| `figures/` | 论文插图（PDF/PNG） |
| `hithesisbook.cls` | hithesis 文档类 |
| `hithesis.sty` | hithesis 宏包 |
| `hithesisbook.cfg` | hithesis 配置文件 |
| `hithesis.bst`、`hitszthesis.bst` | 参考文献样式 |
| `论文初稿.pdf` | 编译生成的论文 PDF |

## 编译方法

需要安装 TeX Live 或 MiKTeX，并使用 XeLaTeX 编译。为更新交叉引用和目录，请连续运行两次：

```bash
xelatex -interaction=nonstopmode 论文初稿.tex
xelatex -interaction=nonstopmode 论文初稿.tex
```

## 说明

- 参考文献直接内嵌在 `论文初稿.tex` 中，无需额外的 `.bib` 文件。
- `.gitignore` 已排除编译中间产物和本地敏感文件（如 `api_key.txt`），请勿将其提交到仓库。
