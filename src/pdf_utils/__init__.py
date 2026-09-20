"""PDF 工具箱：多功能的 PDF 转换工具。

包结构：
    __main__.py     入口（python -m pdf_utils）
    gui.py          界面
    tools.py        功能注册表，界面只读这里
    converters/     各个转换功能，一个功能一个模块
    ocr.py          PaddleOCR 加载与识别
    selfcheck.py    自检
"""

__version__ = "1.1.0"
