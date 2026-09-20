"""自检。都是纯 CLI 逻辑，不碰界面。

    python pdf_utils.py --self-check     Markdown 解析 + 两个功能的端到端转换
    python pdf_utils.py --check-models   检查 OCR 模型目录解析
    python pdf_utils.py --self-test      上面全部 + 跑一次真实识别
"""

import os
import sys


def check_markdown():
    """给 PDF->Markdown 的解析逻辑留一个可跑的检查。"""
    import fitz

    from .converters.to_markdown import page_markdown

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 80), "Big Title", fontsize=24)
    page.insert_text((72, 120), "Body text here.", fontsize=11)
    md = page_markdown(page)

    assert md.startswith("# Big Title"), md
    assert "Body text here." in md, md
    assert not any(line.startswith("#") for line in md.splitlines()[1:]), md
    doc.close()
    print("Markdown 解析自检通过：")
    print(md)


def check_convert():
    """端到端跑一遍两个功能，确认整条转换链路可用。

    打包后同样能跑，是验证 exe 里 pdf2docx / PyMuPDF 有没有被漏收的手段。
    """
    import tempfile
    import zipfile

    import fitz

    from .tools import TOOLS

    tmp = tempfile.mkdtemp(prefix="pdf_utils_check_")
    src = os.path.join(tmp, "sample.pdf")
    doc = fitz.open()
    for page_num in range(2):
        page = doc.new_page()
        page.insert_text((72, 80), "Report Title", fontsize=22, fontname="hebo")
        page.insert_text((72, 120), f"Page {page_num + 1} body text.", fontsize=11)
    doc.save(src)
    doc.close()

    # 直接遍历注册表，新增功能会自动被这个自检覆盖
    for tool in TOOLS:
        out_path = os.path.join(tmp, "sample" + tool["ext"])
        tool["run"](src, out_path, False, "ch")
        assert os.path.getsize(out_path) > 0, f"{tool['name']} 没有产出文件"
        print(f"  {tool['name']} -> {os.path.basename(out_path)} "
              f"({os.path.getsize(out_path)} 字节)")

    # docx 必须是合法 Word 文件，光看文件非空会被一个空壳骗过去
    with zipfile.ZipFile(os.path.join(tmp, "sample.docx")) as z:
        assert "word/document.xml" in z.namelist(), "docx 不是有效的 Word 文件"

    with open(os.path.join(tmp, "sample.md"), encoding="utf-8") as f:
        md = f.read()
    assert md.count("# Report Title") == 2, md
    assert "Page 1 body text." in md, md

    print("端到端转换自检通过")


def check_models(with_ocr=False):
    """自检：验证模型目录解析，可选额外跑一次真实识别。

    开发模式下模型目录不存在，会退回 PaddleOCR 自己的 ~/.paddleocr 缓存，
    因此 --self-test 在开发模式下通过，并不代表打包后的 exe 能离线跑。
    要验证打包场景，先在开发机跑一次 OCR 生成缓存，把 ~/.paddleocr 拷成
    项目下的 paddleocr_models/，再执行本自检。
    """
    from .ocr import get_engine, model_root, resolve_model_dirs

    dirs = resolve_model_dirs("ch")
    print(f"模型根目录: {model_root()}")
    for key in ("det_model_dir", "rec_model_dir", "cls_model_dir"):
        print(f"  {key}: {dirs.get(key) or '<缺失，将回退到 PaddleOCR 自带缓存>'}")
    if dirs:
        for path in dirs.values():
            assert os.path.isfile(os.path.join(path, "inference.pdmodel")), path
        print("模型目录解析通过")

    if not with_ocr:
        return

    import numpy as np
    from PIL import Image, ImageDraw

    ocr = get_engine("ch")
    img = Image.new("RGB", (420, 120), "white")
    ImageDraw.Draw(img).text((20, 45), "Hello OCR 12345", fill="black")
    result = ocr.ocr(np.array(img))
    texts = [line[1][0] for line in result[0]] if result and result[0] else []
    print(f"识别结果: {texts}")
    assert texts, "OCR 未返回任何结果"
    print("端到端 OCR 通过")
