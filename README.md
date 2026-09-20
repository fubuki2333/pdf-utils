# pdf-utils

PDF 转换工具集 —— 一个窗口，左侧选功能，右侧操作。

## 功能

| 功能 | 说明 |
| --- | --- |
| **PDF 转 Word** | 转成可编辑的 `.docx`，尽量还原原文档排版 |
| **PDF 转 Markdown** | 转成 `.md`，保留标题层级、加粗/斜体、列表和表格 |

两个功能都支持扫描版 PDF：勾选「使用 PaddleOCR 识别」，按页渲染后逐页识别，
支持中文（`ch`）和英文（`en`）。OCR 模型已内置，下载后无需联网即可使用。

## 安装

### 方式一：直接使用打包好的程序

下载 `PDF工具箱.exe` 双击运行，无需安装 Python 或任何依赖。

### 方式二：从源码运行

1. 确保已安装 Python 3.12+
2. 克隆或下载项目代码
3. 安装依赖并安装本项目：

```bash
pip install -r requirements.txt
pip install -e .
```

4. 运行：

```bash
python -m pdf_utils
```

不装包也可以，用 `run.py` 直接把 `src/` 加进 `sys.path`：

```bash
python run.py
```

## 使用说明

1. **选功能**：在左侧列表点击「PDF 转 Word」或「PDF 转 Markdown」
2. **选文件**：点击「浏览」选择需要转换的 PDF，输出路径会自动按功能补上扩展名
3. **选择模式**：
   - 常规 PDF（文字可选中的）直接点「开始转换」
   - 扫描版 PDF 勾选「使用 PaddleOCR 识别」，并选择语言
4. **开始转换**：点击「开始转换」按钮
5. **查看结果**：转换完成后会自动打开输出文件所在目录

## 依赖项

- pdf2docx
- PyMuPDF (fitz)
- python-docx
- PaddleOCR / PaddlePaddle
- Pillow (PIL)
- OpenCV (cv2)

## 代码结构

```
src/pdf_utils/
    __main__.py          入口：启动界面 / 分发自检命令
    gui.py               界面：左侧功能列表 + 右侧操作区
    tools.py             功能注册表：界面只读这里，不认识任何转换模块
    converters/          各个转换功能，一个功能一个模块
        to_word.py       PDF -> Word
        to_markdown.py   PDF -> Markdown（标题/行内格式/表格还原）
    ocr.py               PaddleOCR 加载与逐页识别
    selfcheck.py         自检
scripts/make_test_pdfs.py   生成测试用 PDF
run.py                   开发时直接跑源码
pdf_utils.spec           PyInstaller 打包配置
```

加一个功能 = 在 `converters/` 加一个转换模块 + 在 `tools.py` 里加一条记录
（名称、说明、输出扩展名、转换函数），界面和自检都会自动带上它。

## 测试

生成一组覆盖各种场景的测试 PDF：

```bash
python scripts/make_test_pdfs.py     # 输出到 ./test_pdfs
```

| 文件 | 用途 |
| --- | --- |
| `01_normal.pdf` | 文字版英文，含标题层级、行内加粗/斜体、列表、表格 |
| `02_chinese.pdf` | 文字版中文，含标题、加粗、表格 |
| `03_scanned.pdf` | 图片版，没有文字层，必须勾选 OCR 才能转出内容 |
| `04_multipage.pdf` | 8 页，验证页序和进度条 |
| `05_broken.pdf` | 不是 PDF 的文件，验证错误提示 |

## 打包

打包前先在开发机上跑一次 OCR，让 PaddleOCR 把模型缓存到 `~/.paddleocr`，
构建脚本会把模型一并打进包里，用户下载后无需联网即可识别。

```bash
python -m pdf_utils --self-check     # 检查 Markdown 解析 + 两个功能的端到端转换
python -m pdf_utils --self-test      # 检查 OCR 可用（含模型加载和一次真实识别）
pyinstaller pdf_utils.spec
```

打包后建议再对 exe 跑一次，确认依赖没有漏收：

```bash
dist/PDF工具箱.exe --self-check
dist/PDF工具箱.exe --self-test
```

## 常见问题

### 1. 转换失败怎么办？
- 检查PDF文件是否损坏
- 确保有足够的系统内存
- 对于大文件，转换可能需要较长时间

### 2. OCR识别不准确怎么办？
- 确保选择了正确的语言
- 对于清晰度较低的扫描件，识别效果可能会受到影响
- 尝试调整PDF文件的DPI设置

### 3. 程序启动缓慢怎么办？
- 首次启动需要加载模型，会比较慢
- 后续启动会快很多

### 4. PDF 转 Markdown 出来的标题层级不对？
标题层级是按字号相对正文的比例猜的（>1.8 倍为一级，>1.45 为二级，>1.25 为三级），
版式特殊的 PDF 可能需要手动调整。

### 5. 选了英文 OCR 却提示要联网？
随程序打包的只有中文模型。首次用英文识别时 PaddleOCR 会自动下载英文模型，
之后就能离线使用。要彻底离线，参考上面「打包」一节把英文模型也缓存进 `~/.paddleocr`。

## 版本历史

- **v1.0**：PDF 转 Word（PaddleOCR 版）
- **v1.1**：重构为多功能工具箱界面，新增 PDF 转 Markdown

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，欢迎联系开发者。
