"""生成测试用 PDF，覆盖转换工具的各种场景。

用法：
    python scripts/make_test_pdfs.py [输出目录]     # 默认 ./test_pdfs

生成的文件：
    01_normal.pdf    文字版英文，含标题/加粗/斜体/列表/表格
    02_chinese.pdf   文字版中文，含标题/加粗/表格
    03_scanned.pdf   图片版（无文字层），必须走 OCR 才能转出内容
    04_multipage.pdf 8 页，用来验证翻页顺序和进度条
    05_broken.pdf    不是 PDF 的文件，用来验证错误提示
"""

import os
import sys

import fitz

# Base14 是 PyMuPDF 内置字体，不用外部字体文件就能给出 Bold/Oblique 的字体名，
# 正好用来验证转换器对加粗、斜体的识别。
HELV, HELV_B, HELV_I = "helv", "hebo", "heit"
CJK = "china-ss"  # 内置中文宋体


def _register_cjk_bold(doc):
    """注册微软雅黑粗体，拿不到就退回内置宋体（那种情况下中文没有粗体）。"""
    path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "msyhbd.ttc")
    if not os.path.isfile(path):
        return CJK
    try:
        doc[0].insert_font(fontname="msyhbd", fontfile=path)
        return "msyhbd"
    except Exception:
        return CJK


def _text_width(text, fontname, size):
    """量一段文字的宽度，用来把行内片段依次排下去。"""
    try:
        return fitz.get_text_length(text, fontname=fontname, fontsize=size)
    except ValueError:
        # 嵌入字体（中文）量不了宽，按全角=1em、半角=0.5em 估个够用的值
        return sum(size if ord(ch) > 0x2E80 else size * 0.5 for ch in text)


def _runs(page, x, y, runs, size=11):
    """在一行里混排多个 (文本, 字体) 片段，用来做行内加粗/斜体。"""
    for text, font in runs:
        page.insert_text((x, y), text, fontname=font, fontsize=size)
        x += _text_width(text, font, size)
    return x


def _table(page, x0, y0, rows, col_w=95.0, row_h=24.0, font=None):
    """画一个带框线的表格，find_tables() 靠这些线识别表格。"""
    font = font or HELV
    width, height = col_w * len(rows[0]), row_h * len(rows)
    for r in range(len(rows) + 1):
        page.draw_line(fitz.Point(x0, y0 + r * row_h), fitz.Point(x0 + width, y0 + r * row_h))
    for c in range(len(rows[0]) + 1):
        page.draw_line(fitz.Point(x0 + c * col_w, y0), fitz.Point(x0 + c * col_w, y0 + height))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            page.insert_text((x0 + c * col_w + 6, y0 + r * row_h + row_h * 0.68),
                             cell, fontname=font, fontsize=10)


def make_normal(path):
    """文字版英文：标题层级、行内加粗斜体、列表、表格。"""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((60, 70), "Quarterly Report", fontname=HELV_B, fontsize=24)
    page.insert_text((60, 95), "Prepared by the Analytics Team", fontname=HELV_I, fontsize=11)

    page.insert_text((60, 140), "1. Overview", fontname=HELV_B, fontsize=16)
    _runs(page, 60, 168, [
        ("Revenue grew ", HELV), ("18%", HELV_B),
        (" year over year, driven mainly by the ", HELV),
        ("enterprise", HELV_I), (" segment.", HELV),
    ])
    _runs(page, 60, 188, [
        ("Growth was ", HELV), ("strongest", HELV_B), (" in APAC.", HELV),
    ])

    page.insert_text((60, 226), "2. Key Metrics", fontname=HELV_B, fontsize=16)
    _table(page, 60, 244, [
        ["Region", "Revenue", "Growth"],
        ["APAC", "1,240", "24%"],
        ["EMEA", "980", "11%"],
        ["Americas", "1,510", "9%"],
    ])

    page.insert_text((60, 390), "3. Next Steps", fontname=HELV_B, fontsize=16)
    for i, item in enumerate([
        "Expand the partner program in Japan",
        "Hire two more solutions engineers",
        "Ship the self-serve onboarding flow",
    ]):
        _runs(page, 60, 418 + i * 20, [(f"{i + 1}. ", HELV), (item, HELV)])

    page.insert_text((60, 520), "Contact", fontname=HELV_B, fontsize=14)
    _runs(page, 60, 544, [("Email: ", HELV), ("analytics@example.com", HELV_I)])

    doc.save(path)
    doc.close()


def make_chinese(path):
    """文字版中文：标题层级、加粗、表格。"""
    doc = fitz.open()
    page = doc.new_page()
    bold = _register_cjk_bold(doc)

    page.insert_text((60, 70), "季度工作报告", fontname=CJK, fontsize=24)
    page.insert_text((60, 100), "2026 年第三季度 · 数据分析组", fontname=CJK, fontsize=11)

    page.insert_text((60, 145), "一、总体情况", fontname=CJK, fontsize=16)
    _runs(page, 60, 173, [
        ("本季度营收同比增长 ", CJK), ("18%", bold),
        ("，主要来自企业客户；其中华东区表现", CJK), ("最为突出", bold), ("。", CJK),
    ], size=11)
    page.insert_text((60, 195), "整体毛利率保持稳定，环比略有提升。", fontname=CJK, fontsize=11)

    page.insert_text((60, 235), "二、分区域数据", fontname=CJK, fontsize=16)
    _table(page, 60, 253, [
        ["区域", "营收（万元）", "同比"],
        ["华东", "1,240", "24%"],
        ["华南", "980", "11%"],
        ["华北", "1,510", "9%"],
    ], font=CJK)

    page.insert_text((60, 400), "三、下季度计划", fontname=CJK, fontsize=16)
    for i, item in enumerate([
        "拓展东南亚渠道合作",
        "补充两名解决方案工程师",
        "上线自助开通流程",
    ]):
        page.insert_text((60, 428 + i * 22), f"{i + 1}. {item}", fontname=CJK, fontsize=11)

    page.insert_text((60, 530), "联系方式", fontname=CJK, fontsize=14)
    page.insert_text((60, 554), "邮箱：analytics@example.com", fontname=CJK, fontsize=11)

    # 嵌入的字体不子集化会整份塞进 PDF（微软雅黑粗体 16 MB），子集化后只剩几十 KB
    doc.subset_fonts()
    doc.save(path)
    doc.close()


def make_scanned(path):
    """图片版：把内容渲染成位图再放进新 PDF，没有文字层，只能靠 OCR。"""
    src = fitz.open()
    page = src.new_page()
    page.insert_text((60, 70), "Scanned Document", fontname=HELV_B, fontsize=22)
    page.insert_text((60, 100), "This page has no text layer.", fontname=HELV_I, fontsize=11)
    page.insert_text((60, 145), "Invoice Summary", fontname=HELV_B, fontsize=16)
    _table(page, 60, 165, [
        ["Item", "Qty", "Price"],
        ["Widget", "2", "3.50"],
        ["Gadget", "10", "1.20"],
    ])
    page.insert_text((60, 300), "Thank you for your business.", fontname=HELV, fontsize=11)

    rect = page.rect
    png = page.get_pixmap(dpi=200).tobytes("png")
    src.close()

    doc = fitz.open()
    out = doc.new_page(width=rect.width, height=rect.height)
    out.insert_image(out.rect, stream=png)
    # PyMuPDF 存图时会把 PNG 解成裸 RGB，一份 11 MB；deflate=True 让保存时再压回去
    doc.save(path, deflate=True)
    doc.close()


def make_multipage(path, pages=8):
    """多页文档：每页内容不同，用来验证页序和进度。"""
    doc = fitz.open()
    for page_num in range(1, pages + 1):
        page = doc.new_page()
        page.insert_text((60, 70), f"Chapter {page_num}", fontname=HELV_B, fontsize=22)
        page.insert_text((60, 100), f"Section {page_num}.1  Introduction", fontname=HELV_B, fontsize=14)
        _runs(page, 60, 130, [
            ("This is ", HELV), (f"page {page_num}", HELV_B),
            (f" of {pages}. It exists so you can check that pages come out in order", HELV),
        ])
        page.insert_text((60, 150), "and that the progress bar advances.", fontname=HELV, fontsize=11)
        _table(page, 60, 180, [
            ["Page", "Words", "Status"],
            [str(page_num), str(120 * page_num), "draft"],
        ])
    doc.save(path)
    doc.close()


def make_broken(path):
    """写一个不是 PDF 的文件，用来验证选错文件时的错误提示。

    注意别用「截断正常 PDF」这招：MuPDF 有容错修复，截断后照样能打开，
    测不到失败路径。
    """
    with open(path, "wb") as f:
        f.write(b"This is not a PDF file.\n" + b"x" * 512 + b"\n%%EOF\n")


BUILDERS = [
    ("01_normal.pdf", make_normal),
    ("02_chinese.pdf", make_chinese),
    ("03_scanned.pdf", make_scanned),
    ("04_multipage.pdf", make_multipage),
    ("05_broken.pdf", make_broken),
]


def main():
    # 脚本在 scripts/ 下，项目根目录是它的上一层
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(project_root, "test_pdfs")
    os.makedirs(out_dir, exist_ok=True)

    for name, build in BUILDERS:
        build(os.path.join(out_dir, name))

    # 生成完顺手验一遍：文字版必须能直接抽到文字，图片版必须抽不到（否则测不到 OCR）
    print(f"输出目录: {out_dir}")
    for name, _ in BUILDERS:
        path = os.path.join(out_dir, name)
        size = os.path.getsize(path)
        try:
            doc = fitz.open(path)
            chars = sum(len(page.get_text().strip()) for page in doc)
            pages = len(doc)
            doc.close()
            note = f"{pages} 页, 文字层 {chars} 字"
        except Exception as e:
            note = f"无法打开（预期如此）: {type(e).__name__}"
        print(f"  {name:18} {size / 1024:8.1f} KB  {note}")

    normal = os.path.join(out_dir, "01_normal.pdf")
    doc = fitz.open(normal)
    assert "Quarterly Report" in doc[0].get_text(), "文字版没有文字层"
    doc.close()

    scanned = os.path.join(out_dir, "03_scanned.pdf")
    doc = fitz.open(scanned)
    assert not doc[0].get_text().strip(), "图片版混进了文字层，测不到 OCR"
    doc.close()

    print("自检通过：文字版有文字层，图片版没有")


if __name__ == "__main__":
    main()
