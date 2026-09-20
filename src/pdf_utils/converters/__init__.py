"""各个转换功能，一个功能一个模块。

每个模块对外暴露一个同签名的转换函数：

    convert(pdf_path, out_path, use_ocr, lang, progress=None, status=None)

在 tools.py 的 TOOLS 里注册后，界面和自检都会自动带上它。
"""
