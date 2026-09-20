## 功能

- **PDF 转 Word**：转成可编辑的 `.docx`，尽量还原原文档排版
- **PDF 转 Markdown**：转成 `.md`，保留标题层级、加粗/斜体、列表和表格

两个功能都支持扫描版 PDF：勾选「使用 PaddleOCR 识别」，按页渲染后逐页识别，支持中文（`ch`）和英文（`en`）。

## 下载

| 文件 | 说明 |
| --- | --- |
| `PDF工具箱.exe` | 免安装，双击运行。无需 Python 或任何依赖 |

单文件 exe，约 303 MB —— 体积主要来自内置的 PaddleOCR 模型，换来的是**中文识别开箱即用、无需联网下载模型**。

## 使用

1. 在左侧列表选择功能（PDF 转 Word / PDF 转 Markdown）
2. 点击「浏览」选择 PDF，输出路径会自动按功能补上扩展名
3. 常规 PDF 直接点「开始转换」；扫描版 PDF 勾选「使用 PaddleOCR 识别」并选择语言
4. 转换完成后自动打开输出目录

## 已知问题

- **英文 OCR 首次使用需要联网**：随程序打包的只有中文模型，首次选英文识别时 PaddleOCR 会自动下载英文模型（约 14 MB），之后即可离线使用。
- **Markdown 标题层级是推断的**：按字号相对正文的比例判断（>1.8 倍为一级，>1.45 为二级，>1.25 为三级），版式特殊的 PDF 可能需要手动调整。

## 从源码运行

```bash
pip install -r requirements.txt
pip install -e .
python -m pdf_utils
```

或免安装直接跑：

```bash
python run.py
```

## 自检

```bash
python -m pdf_utils --self-check     # Markdown 解析 + 两个功能的端到端转换
python -m pdf_utils --self-test      # OCR 可用性（含模型加载和一次真实识别）
```

---

本版本为首次发布，尚无 Windows 代码签名，SmartScreen 可能提示未知发布者。
