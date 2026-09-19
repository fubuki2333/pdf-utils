import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import queue
import threading
import sys

def _prepare_paddleocr_runtime_path():
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

def _resolve_ocr_model_dirs(lang):
    """返回随程序分发的模型目录，缺失时返回空字典（交给 PaddleOCR 自行下载）。"""
    if getattr(sys, "frozen", False):
        base = os.path.join(getattr(sys, "_MEIPASS", ""), "paddleocr_models")
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paddleocr_models")
    if not os.path.isdir(base):
        return {}

    dirs = {}
    for stage, key in (("det", "det_model_dir"), ("rec", "rec_model_dir"), ("cls", "cls_model_dir")):
        found = _find_inference_dir(base, lang, stage)
        if found:
            dirs[key] = found
    return dirs

class PDFtoWordConverterPaddleOCR:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转Word工具 (PaddleOCR版)")
        self.root.geometry("700x400")
        self.root.resizable(False, False)
        
        # 设置窗口图标（可选）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 创建主框架
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        self.title_label = tk.Label(self.main_frame, text="PDF转Word工具 (PaddleOCR版)", font=("微软雅黑", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # 创建文件选择部分
        self.file_frame = tk.Frame(self.main_frame)
        self.file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = tk.Label(self.file_frame, text="PDF文件:", font=("微软雅黑", 10))
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path_var, width=40, font=("微软雅黑", 10))
        self.file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_button = tk.Button(self.file_frame, text="浏览", command=self.browse_file, font=("微软雅黑", 10))
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建输出路径部分
        self.output_frame = tk.Frame(self.main_frame)
        self.output_frame.pack(fill=tk.X, pady=10)
        
        self.output_label = tk.Label(self.output_frame, text="输出路径:", font=("微软雅黑", 10))
        self.output_label.pack(side=tk.LEFT, padx=5)
        
        self.output_path_var = tk.StringVar()
        self.output_entry = tk.Entry(self.output_frame, textvariable=self.output_path_var, width=40, font=("微软雅黑", 10))
        self.output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.output_button = tk.Button(self.output_frame, text="浏览", command=self.browse_output, font=("微软雅黑", 10))
        self.output_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建OCR选项部分
        self.ocr_frame = tk.Frame(self.main_frame)
        self.ocr_frame.pack(fill=tk.X, pady=10)
        
        self.ocr_var = tk.BooleanVar(value=False)
        self.ocr_checkbutton = tk.Checkbutton(
            self.ocr_frame, 
            text="使用PaddleOCR识别（适用于扫描版PDF）", 
            variable=self.ocr_var, 
            font=("微软雅黑", 10)
        )
        self.ocr_checkbutton.pack(side=tk.LEFT, padx=5)
        
        # OCR语言选择
        self.lang_label = tk.Label(self.ocr_frame, text="OCR语言:", font=("微软雅黑", 10))
        self.lang_label.pack(side=tk.LEFT, padx=5)
        
        self.lang_var = tk.StringVar(value="ch")
        self.lang_combobox = ttk.Combobox(
            self.ocr_frame, 
            textvariable=self.lang_var, 
            font=("微软雅黑", 10),
            width=10
        )
        self.lang_combobox.pack(side=tk.LEFT, padx=5)
        self.lang_combobox['values'] = ["ch", "en"]
        
        # 创建转换按钮
        self.convert_button = tk.Button(self.main_frame, text="开始转换", command=self.convert_pdf_to_word, font=("微软雅黑", 12, "bold"), bg="#4CAF50", fg="white", padx=20, pady=10)
        self.convert_button.pack(pady=20)
        
        # 创建状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, font=("微软雅黑", 10), fg="#666")
        self.status_label.pack(pady=10)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)

        self._ui_queue = queue.Queue()
        self._conversion_running = False
        self._ocr_engine = None
        self._ocr_engine_lang = None
        self.root.after(100, self._process_ui_queue)
    
    def browse_file(self):
        """浏览选择PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            # 自动设置输出路径
            base_name = os.path.splitext(file_path)[0]
            output_path = base_name + ".docx"
            self.output_path_var.set(output_path)
    
    def browse_output(self):
        """浏览选择输出路径"""
        output_path = filedialog.asksaveasfilename(
            title="保存Word文件",
            defaultextension=".docx",
            filetypes=[("Word文件", "*.docx"), ("所有文件", "*.*")]
        )
        if output_path:
            self.output_path_var.set(output_path)
    
    def convert_pdf_to_word(self):
        """转换PDF文件为Word文件"""
        pdf_path = self.file_path_var.get()
        docx_path = self.output_path_var.get()
        use_ocr = self.ocr_var.get()
        ocr_lang = self.lang_var.get()
        
        # 检查输入输出路径
        if not pdf_path:
            messagebox.showerror("错误", "请选择PDF文件")
            return
        
        if not docx_path:
            messagebox.showerror("错误", "请选择输出路径")
            return
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            messagebox.showerror("错误", "PDF文件不存在")
            return

        if self._conversion_running:
            messagebox.showwarning("提示", "当前已有转换任务在运行")
            return

        self._conversion_running = True
        self.convert_button.config(state=tk.DISABLED)
        self._ui_queue.put(("status", "转换中..."))
        self._ui_queue.put(("progress", 0))

        worker = threading.Thread(
            target=self._convert_worker,
            args=(pdf_path, docx_path, use_ocr, ocr_lang),
            daemon=True
        )
        worker.start()

    def _convert_worker(self, pdf_path, docx_path, use_ocr, ocr_lang):
        """后台执行转换任务。"""
        try:
            if use_ocr:
                self.convert_with_paddleocr(pdf_path, docx_path, ocr_lang)
            else:
                self.convert_without_ocr(pdf_path, docx_path)
            self._ui_queue.put(("done", docx_path))
        except Exception as e:
            self._ui_queue.put(("error", str(e)))

    def _process_ui_queue(self):
        """在主线程处理后台任务的UI更新。"""
        try:
            while True:
                kind, payload = self._ui_queue.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
                elif kind == "progress":
                    self.progress_var.set(payload)
                elif kind == "done":
                    self._conversion_running = False
                    self.convert_button.config(state=tk.NORMAL)
                    self.status_var.set("转换完成")
                    self.progress_var.set(100)
                    messagebox.showinfo("成功", f"PDF转换为Word成功！\n输出文件: {payload}")
                    output_dir = os.path.dirname(os.path.abspath(payload))
                    os.startfile(output_dir)
                elif kind == "error":
                    self._conversion_running = False
                    self.convert_button.config(state=tk.NORMAL)
                    self.status_var.set("转换失败")
                    self.progress_var.set(0)
                    messagebox.showerror("错误", f"转换失败: {payload}")
        except queue.Empty:
            pass

        try:
            self.root.after(100, self._process_ui_queue)
        except tk.TclError:
            return
    
    def convert_without_ocr(self, pdf_path, docx_path):
        """不使用OCR的常规转换"""
        from pdf2docx import Converter
        cv = Converter(pdf_path)
        try:
            cv.convert(docx_path, start=0, end=None)
        finally:
            cv.close()

    def _normalize_paddle_lang(self, ocr_lang):
        """将UI输入映射到PaddleOCR支持的语言。"""
        return ocr_lang if ocr_lang in {"ch", "en"} else "ch"

    def _get_ocr_engine(self, ocr_lang):
        """按语言缓存PaddleOCR实例，避免每次转换都重新加载模型。"""
        if self._ocr_engine is None or self._ocr_engine_lang != ocr_lang:
            _prepare_paddleocr_runtime_path()
            from paddleocr import PaddleOCR
            # 优先用随程序分发的模型，实现离线开箱即用；找不到再回退到自动下载
            model_dirs = _resolve_ocr_model_dirs(ocr_lang)
            if not model_dirs:
                self._ui_queue.put(("status", "未找到内置OCR模型，首次识别需要联网下载..."))
            # 简化配置，避免兼容性问题
            self._ocr_engine = PaddleOCR(use_angle_cls=False, lang=ocr_lang, **model_dirs)
            self._ocr_engine_lang = ocr_lang
        return self._ocr_engine

    def convert_with_paddleocr(self, pdf_path, docx_path, ocr_lang):
        """使用PaddleOCR的转换（适用于扫描版PDF）"""
        # 延迟导入PaddleOCR以加快启动速度
        import fitz  # PyMuPDF
        import numpy as np
        import docx

        ocr = self._get_ocr_engine(self._normalize_paddle_lang(ocr_lang))

        doc = fitz.open(pdf_path)
        try:
            num_pages = len(doc)
            word_doc = docx.Document()

            for page_num in range(num_pages):
                progress = (page_num + 1) / num_pages * 100
                self._ui_queue.put(("progress", progress))
                self._ui_queue.put(("status", f"转换中... (第{page_num + 1}/{num_pages}页)"))

                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)
                # PaddleOCR 2.x 只接受 ndarray / 路径 / bytes，不接受 PIL Image
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:
                    img = img[:, :, :3]
                result = ocr.ocr(img)

                text = ""
                if result and result[0]:
                    for line in result[0]:
                        text += line[1][0] + "\n"

                if page_num > 0:
                    word_doc.add_page_break()

                if text.strip():
                    word_doc.add_paragraph(text)

            word_doc.save(docx_path)
        finally:
            doc.close()

def main():
    # 检查是否安装了必要的库
    _prepare_paddleocr_runtime_path()

    required_libs = [
        ('pdf2docx', 'pdf2docx'),
        ('PyMuPDF', 'fitz'),
        ('python-docx', 'docx')
    ]
    
    missing_libs = []
    for lib_name, import_name in required_libs:
        try:
            __import__(import_name)
        except ImportError:
            missing_libs.append(lib_name)
    
    if missing_libs:
        import subprocess
        if getattr(sys, "frozen", False):
            messagebox.showerror("错误", f"缺少运行依赖: {', '.join(missing_libs)}，请重新安装完整版本。")
            return

        # 尝试安装缺失的依赖
        print(f"正在安装必要的依赖: {', '.join(missing_libs)}")
        try:
            for lib in missing_libs:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", lib])
            print("依赖安装成功！")
        except Exception as e:
            print(f"依赖安装失败: {str(e)}")
            print(f"请手动运行: pip install {' '.join(missing_libs)}")
            input("按回车键退出...")
            return
    
    # 创建主窗口
    root = tk.Tk()
    app = PDFtoWordConverterPaddleOCR(root)
    root.mainloop()

def _self_check(with_ocr=False):
    """自检：--check-models 验证模型目录解析，--self-test 额外跑一次真实识别。

    开发模式下模型目录不存在，会退回 PaddleOCR 自己的 ~/.paddleocr 缓存，
    因此 --self-test 在开发模式下通过，并不代表打包后的 exe 能离线跑。
    要验证打包场景，先在开发机跑一次 OCR 生成缓存，把 ~/.paddleocr 拷成
    项目下的 paddleocr_models/，再执行本自检。
    """
    base = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), "paddleocr_models")
    dirs = _resolve_ocr_model_dirs("ch")
    print(f"模型根目录: {base}")
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
    from paddleocr import PaddleOCR

    _prepare_paddleocr_runtime_path()
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", **dirs)
    img = Image.new("RGB", (420, 120), "white")
    ImageDraw.Draw(img).text((20, 45), "Hello OCR 12345", fill="black")
    result = ocr.ocr(np.array(img))
    texts = [line[1][0] for line in result[0]] if result and result[0] else []
    print(f"识别结果: {texts}")
    assert texts, "OCR 未返回任何结果"
    print("端到端 OCR 通过")

if __name__ == "__main__":
    if "--check-models" in sys.argv:
        _self_check()
        sys.exit(0)
    if "--self-test" in sys.argv:
        _self_check(with_ocr=True)
        sys.exit(0)

    main()
