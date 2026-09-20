"""功能注册表 —— 界面只读这里，不直接认识任何转换模块。

加一个功能 = 加一个模块 + 在下面加一条记录，界面代码不用动。
每条记录描述的是「这个功能和别的功能有什么不同」：输出扩展名、保存对话框的
过滤条件、以及真正干活的转换函数。
"""

from .converters.to_markdown import pdf_to_markdown
from .converters.to_word import pdf_to_docx

# 转换函数统一签名：(pdf_path, out_path, use_ocr, lang, progress=None, status=None)
TOOLS = [
    {
        "name": "PDF 转 Word",
        "desc": "转成可编辑的 .docx。扫描版 PDF 请勾选下方 OCR 识别。",
        "ext": ".docx",
        "filetypes": [("Word 文件", "*.docx"), ("所有文件", "*.*")],
        "run": pdf_to_docx,
    },
    {
        "name": "PDF 转 Markdown",
        "desc": "转成 .md，保留标题、加粗、列表和表格结构。",
        "ext": ".md",
        "filetypes": [("Markdown 文件", "*.md"), ("所有文件", "*.*")],
        "run": pdf_to_markdown,
    },
]
