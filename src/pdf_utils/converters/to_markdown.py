"""PDF 转 Markdown：按版面还原标题层级、行内格式和表格。

PyMuPDF 的 get_text("dict") 给出每个 span 的字体名、字号和 flags，标题层级
靠「字号相对正文的比例」猜，加粗/斜体靠 flags 加字体名兜底，表格靠
find_tables() 抽出来后按纵向位置插回页面原位。

OCR 模式下拿不到任何版面信息，退化成按行转段落。
"""

import re

from ..ocr import ocr_pages

# 只转义真的会破坏 Markdown 结构的字符。全量转义会把中文里的
# 句号、连字符也加上反斜杠，读起来全是噪音。
_MD_ESCAPE = re.compile(r"([\\`*_\[\]|])")


def _escape(text):
    return _MD_ESCAPE.sub(r"\\\1", text)


def _escape_cell(text):
    # 去掉 | 再交给 _escape，避免 `a|b` 变成 `a\\\|b`（多一层反斜杠）
    return _escape(text.replace("|", " "))


def _span_md(span, body_size, skip_emphasis=False):
    """把单个 span 转成行内 Markdown（加粗/斜体/等宽）。"""
    raw = span["text"]
    if not raw.strip():
        return raw

    flags = span.get("flags", 0)
    font = span.get("font", "")
    mono = bool(flags & 8) or "Mono" in font or "Courier" in font

    if mono:
        text = f"`{raw.strip()}`"
    else:
        text = _escape(raw.strip())
        if not skip_emphasis:
            # flags: bit1 = 斜体, bit4 = 加粗；字体名兜底（部分 PDF 不设 flag）
            italic = bool(flags & 2) or "Italic" in font or "Oblique" in font
            bold = bool(flags & 16) or "Bold" in font or font.endswith(("-B", ",Bold"))
            if bold:
                text = f"**{text}**"
            if italic:
                text = f"*{text}*"

    # 保留原有前后空格，否则 **bold**紧跟中文时会被解析器吞掉
    lead = raw[: len(raw) - len(raw.lstrip())]
    trail = raw[len(raw.rstrip()):]
    return f"{lead}{text}{trail}"


def _body_size(page):
    """页面正文的字号，取所有字符里出现最多的那个。"""
    sizes = {}
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"].strip():
                    size = round(span["size"], 1)
                    sizes[size] = sizes.get(size, 0) + len(span["text"])
    return max(sizes, key=sizes.get) if sizes else 12.0


def _heading_level(text, size, body_size):
    """按字号比例判断标题层级，0 表示不是标题。"""
    if size < body_size * 1.12 or len(text) > 80:
        return 0
    ratio = size / body_size
    for level, threshold in ((1, 1.8), (2, 1.45), (3, 1.25)):
        if ratio >= threshold:
            return level
    return 4


def _table_md(table):
    """把一个 PyMuPDF 表格转成 Markdown 表格。"""
    rows = [[("" if cell is None else " ".join(str(cell).split())) for cell in row]
            for row in table.extract()]
    rows = [row for row in rows if any(row)]
    if not rows:
        return ""

    cols = max(len(row) for row in rows)
    rows = [row + [""] * (cols - len(row)) for row in rows]
    out = ["| " + " | ".join(_escape_cell(c) for c in rows[0]) + " |",
           "|" + "---|" * cols]
    out += ["| " + " | ".join(_escape_cell(c) for c in row) + " |" for row in rows[1:]]
    return "\n".join(out)


def _block_md(block, body_size):
    """把一个文本块转成 Markdown 行。"""
    lines = []
    for line in block.get("lines", []):
        text = "".join(span["text"] for span in line["spans"])
        if not text.strip():
            continue
        # 标题：整行同字号且明显大于正文
        sizes = [span["size"] for span in line["spans"] if span["text"].strip()]
        size = max(sizes) if sizes else body_size
        level = _heading_level(text.strip(), size, body_size)
        if level:
            lines.append("#" * level + " " + _escape(text.strip()))
            continue
        # 普通行：按原始 span 还原行内格式
        lines.append("".join(_span_md(span, body_size) for span in line["spans"]))
    return "\n".join(lines)


def page_markdown(page):
    """把一页 PDF 转成 Markdown 文本。"""
    body_size = _body_size(page)

    # 表格区域内的文本块要跳过，否则会跟在表格后面重复一遍
    tables, table_boxes = [], []
    try:
        found = page.find_tables()
    except Exception:
        found = None
    if found:
        for table in found.tables:
            md = _table_md(table)
            if md:
                tables.append((table.bbox[1], md))
                table_boxes.append(table.bbox)

    def in_table(block):
        x0, y0, x1, y1 = block["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return any(bx0 <= cx <= bx1 and by0 <= cy <= by1
                   for bx0, by0, bx1, by1 in table_boxes)

    parts = [(block["bbox"][1], _block_md(block, body_size))
             for block in page.get_text("dict")["blocks"]
             if block.get("type") == 0 and not in_table(block)]
    parts += tables

    # 按纵向位置排序，让表格回到它在页面上的位置
    return "\n\n".join(text for _y, text in sorted(parts, key=lambda p: p[0]) if text.strip())


def _ocr_page_markdown(text):
    """OCR 结果没有版面信息，按行转成段落。"""
    return "\n".join(_escape(line) for line in text.splitlines() if line.strip())


def pdf_to_markdown(pdf_path, out_path, use_ocr, lang, progress=None, status=None):
    import fitz

    doc = fitz.open(pdf_path)
    try:
        num_pages = len(doc)
        ocr_texts = list(ocr_pages(pdf_path, lang, progress, status)) if use_ocr else None

        pages = []
        for page_num in range(num_pages):
            if ocr_texts is None:
                if progress:
                    progress((page_num + 1) / num_pages * 100)
                if status:
                    status(f"转换中... (第{page_num + 1}/{num_pages}页)")
                pages.append(page_markdown(doc.load_page(page_num)))
            else:
                pages.append(_ocr_page_markdown(ocr_texts[page_num]))
    finally:
        doc.close()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(p for p in pages if p.strip()) + "\n")
