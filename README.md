# pdf-utils
PDF转换工具集

## 项目简介

这是一个PDF转换小工具集合，目前正常持续更新ing~
目前已提供的工具：

- **PDF转Word 基础版**：适用于常规PDF文件的转换
- **PDF转Word OCR增强版**：适用于扫描版PDF文件的转换，使用Tesseract OCR引擎
- **PDF转Word PaddleOCR版**：使用百度PaddleOCR引擎，提供更准确的文字识别

## 功能特点

### PaddleOCR版本特点
- ✅ 支持常规PDF文件转换
- ✅ 支持扫描版PDF文件的OCR识别
- ✅ 支持多语言识别（中文、英文、中英文混合）
- ✅ 图形用户界面，操作简单直观
- ✅ 实时转换进度显示
- ✅ 自动打开输出文件所在目录
- ✅ 内置依赖检查和自动安装功能

## 安装方法

1. 确保已安装Python 3.12+
2. 克隆或下载项目代码
3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 运行对应版本：

```bash
# 基础版
python pdf_to_word.py

# OCR增强版
python pdf_to_word_ocr.py

# PaddleOCR版
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

### 基础版依赖
- pdf2docx
- PyMuPDF (fitz)
- python-docx

### OCR增强版依赖
- 基础版所有依赖
- 额外的OCR库（Tesseract）
- 需自行安装Tesseract OCR引擎，[下载地址](https://github.com/UB-Mannheim/tesseract/wiki)

### PaddleOCR版依赖
- 基础版所有依赖
- PaddleOCR
- PaddlePaddle
- Pillow (PIL)
- OpenCV (cv2)

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
- PaddleOCR版本首次启动需要加载模型，会比较慢
- 后续启动会快很多

## 技术说明

### PaddleOCR版本技术特点
- 使用延迟导入技术加快启动速度
- 优化OCR配置以提高兼容性
- 支持多线程处理，提高转换效率
- 内置错误处理机制，提高程序稳定性

## 版本历史

- **v1.0**：初始版本

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，欢迎联系开发者。