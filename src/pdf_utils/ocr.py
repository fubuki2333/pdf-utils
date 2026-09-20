"""PaddleOCR 的加载与逐页识别。

单独成模块是因为这里同时管着两件麻烦事：打包后的运行时路径、以及模型目录的
定位（内置模型 / PaddleOCR 自带缓存）。转换逻辑不该关心这些。
"""

import os
import sys


def prepare_runtime_path():
    """让 frozen 环境下 paddleocr 的绝对导入可以解析。"""
    if not getattr(sys, "frozen", False):
        return

    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return

    candidates = [meipass, os.path.join(meipass, "_internal")]
    for base_dir in candidates:
        if not os.path.isdir(base_dir):
            continue
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        paddleocr_root = os.path.join(base_dir, "paddleocr")
        if os.path.isdir(paddleocr_root):
            if paddleocr_root not in sys.path:
                sys.path.insert(0, paddleocr_root)
            extra_dirs = [
                os.path.join(paddleocr_root, "tools"),
                os.path.join(paddleocr_root, "ppocr"),
                os.path.join(paddleocr_root, "ppocr", "utils"),
                os.path.join(paddleocr_root, "ppstructure"),
                os.path.join(paddleocr_root, "ppstructure", "layout"),
                os.path.join(paddleocr_root, "ppstructure", "table"),
                os.path.join(paddleocr_root, "ppstructure", "recovery"),
            ]
            for extra_dir in extra_dirs:
                if os.path.isdir(extra_dir) and extra_dir not in sys.path:
                    sys.path.insert(0, extra_dir)


def _find_inference_dir(root, lang, stage):
    """在 root 下找到 <stage> 的模型目录（含 inference.pdmodel 的那层）。

    兼容三种布局：打包时的 whl/<stage>/<lang>/、官方缓存的
    whl/<stage>/<lang>/<模型名>/ 嵌套结构，以及 cls 那种没有语言层级的
    whl/<stage>/<模型名>/。
    """
    for stage_root in (os.path.join(root, "whl", stage, lang), os.path.join(root, "whl", stage)):
        if not os.path.isdir(stage_root):
            continue
        if os.path.isfile(os.path.join(stage_root, "inference.pdmodel")):
            return stage_root
        for entry in sorted(os.listdir(stage_root)):
            candidate = os.path.join(stage_root, entry)
            if os.path.isfile(os.path.join(candidate, "inference.pdmodel")):
                return candidate
    return None


def model_root():
    """模型根目录：打包后在 _MEIPASS 里，开发模式在项目根目录（src 的上一层）。"""
    if getattr(sys, "frozen", False):
        return os.path.join(getattr(sys, "_MEIPASS", ""), "paddleocr_models")
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, "paddleocr_models")


def resolve_model_dirs(lang):
    """返回随程序分发的模型目录，缺失时返回空字典（交给 PaddleOCR 自行下载）。"""
    base = model_root()
    if not os.path.isdir(base):
        return {}

    dirs = {}
    for stage, key in (("det", "det_model_dir"), ("rec", "rec_model_dir"), ("cls", "cls_model_dir")):
        found = _find_inference_dir(base, lang, stage)
        if found:
            dirs[key] = found
    return dirs


_engines = {}


def get_engine(lang, status=None):
    """按语言缓存 PaddleOCR 实例，避免每次转换都重新加载模型。"""
    if lang not in _engines:
        prepare_runtime_path()
        from paddleocr import PaddleOCR

        # 优先用随程序分发的模型，实现离线开箱即用；找不到再回退到自动下载
        model_dirs = resolve_model_dirs(lang)
        if not model_dirs and status:
            status("未找到内置OCR模型，首次识别需要联网下载...")
        _engines[lang] = PaddleOCR(use_angle_cls=False, lang=lang, **model_dirs)
    return _engines[lang]


def ocr_pages(pdf_path, lang, progress=None, status=None):
    """逐页渲染 + OCR，产出每页的纯文本（按行拼接）。"""
    import fitz  # PyMuPDF
    import numpy as np

    ocr = get_engine(lang, status)
    doc = fitz.open(pdf_path)
    try:
        num_pages = len(doc)
        for page_num in range(num_pages):
            if progress:
                progress((page_num + 1) / num_pages * 100)
            if status:
                status(f"识别中... (第{page_num + 1}/{num_pages}页)")

            pix = doc.load_page(page_num).get_pixmap(dpi=200)
            # PaddleOCR 2.x 只接受 ndarray / 路径 / bytes，不接受 PIL Image
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = img[:, :, :3]
            result = ocr.ocr(img)
            lines = [line[1][0] for line in result[0]] if result and result[0] else []
            yield "\n".join(lines)
    finally:
        doc.close()
