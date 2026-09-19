# pdf-utils
PDF转换工具集

## 项目简介

这是一个PDF转换小工具，目前正常持续更新ing~

- **PDF转Word PaddleOCR版**：常规PDF直接转换；扫描版PDF用百度PaddleOCR引擎识别

## 功能特点

- ✅ 支持常规PDF文件转换
- ✅ 支持扫描版PDF文件的OCR识别
- ✅ 支持中文、英文识别
- ✅ 图形用户界面，操作简单直观
- ✅ 实时转换进度显示
- ✅ 自动打开输出文件所在目录
- ✅ OCR模型内置，下载后无需联网下载模型即可使用

## 安装方法

### 方式一：直接使用打包好的程序

下载 `PDF转Word工具(PaddleOCR版).exe` 双击运行，无需安装 Python 或任何依赖。

### 方式二：从源码运行

1. 确保已安装Python 3.12+
2. 克隆或下载项目代码
3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 运行：

```bash
python pdf_to_word_paddleocr.py
```

## 使用说明

1. **选择PDF文件**：点击「浏览」按钮选择需要转换的PDF文件
2. **设置输出路径**：工具会自动生成输出路径，也可以手动修改
3. **选择转换模式**：
   - 对于常规PDF，直接点击「开始转换」
   - 对于扫描版PDF，勾选「使用PaddleOCR识别」并选择合适的语言
4. **开始转换**：点击「开始转换」按钮
5. **查看结果**：转换完成后，工具会自动打开输出文件所在目录

## 依赖项

- pdf2docx
- PyMuPDF (fitz)
- python-docx
- PaddleOCR / PaddlePaddle
- Pillow (PIL)
- OpenCV (cv2)

## 打包

打包前先在开发机上跑一次 OCR，让 PaddleOCR 把模型缓存到 `~/.paddleocr`，
构建脚本会把模型一并打进包里，用户下载后无需联网即可识别。

```bash
python pdf_to_word_paddleocr.py --self-test   # 确认 OCR 可用
pyinstaller pdf_to_word_paddleocr.spec
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

## 版本历史

- **v1.0**：初始版本

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，欢迎联系开发者。