"""PDF 转 Word。

常规 PDF 交给 pdf2docx 还原排版；扫描版没有文字层，只能走 OCR，
识别结果按页写成段落（OCR 拿不到排版信息，做不到 pdf2docx 那种还原度）。
"""

from ..ocr import ocr_pages


def pdf_to_docx(pdf_path, out_path, use_ocr, lang, progress=None, status=None):
    if use_ocr:
        import docx

        word_doc = docx.Document()
        for page_num, text in enumerate(ocr_pages(pdf_path, lang, progress, status)):
            if page_num > 0:
                word_doc.add_page_break()
            if text.strip():
                word_doc.add_paragraph(text)
        word_doc.save(out_path)
    else:
        from pdf2docx import Converter

        cv = Converter(pdf_path)
        try:
            cv.convert(out_path, start=0, end=None)
        finally:
            cv.close()
