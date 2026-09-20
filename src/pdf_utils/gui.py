"""tkinter 界面：左侧功能列表 + 右侧操作区。

所有功能共用同一套「选文件 → 选输出 → 转换 → 进度」流程，差异全部来自
tools.py 里的功能记录，所以这里没有一句 if 判断具体是哪个功能。
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import queue
import threading

from .tools import TOOLS


class PdfToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 工具箱")
        self.root.geometry("760x480")
        self.root.minsize(680, 440)

        self._ui_queue = queue.Queue()
        self._running = False

        self._build_header()
        self._build_body()

        self.root.after(100, self._process_ui_queue)
        # selection_set 不会同步触发 <<ListboxSelect>>，得自己调一次，
        # 否则启动时标题和说明是空的，要点一下才出来
        self.tool_listbox.selection_set(0)
        self._on_tool_select()

    # -- 布局 -------------------------------------------------------------

    def _build_header(self):
        header = tk.Frame(self.root, bg="#2F3542", padx=20, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="PDF 工具箱", font=("微软雅黑", 16, "bold"),
                 bg="#2F3542", fg="white").pack(anchor=tk.W)
        tk.Label(header, text="PDF 转 Word / Markdown，支持扫描版 OCR",
                 font=("微软雅黑", 9), bg="#2F3542", fg="#B0B7C3").pack(anchor=tk.W)

    def _build_body(self):
        body = tk.Frame(self.root)
        body.pack(fill=tk.BOTH, expand=True)

        # 左侧功能列表
        sidebar = tk.Frame(body, bg="#F0F1F4", width=170)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="功能", font=("微软雅黑", 10, "bold"),
                 bg="#F0F1F4", fg="#666", anchor=tk.W, padx=16, pady=10).pack(fill=tk.X)

        self.tool_listbox = tk.Listbox(
            sidebar, font=("微软雅黑", 10), activestyle="none",
            selectbackground="#4CAF50", selectforeground="white",
            bg="#F0F1F4", bd=0, highlightthickness=0, exportselection=False,
        )
        for tool in TOOLS:
            self.tool_listbox.insert(tk.END, "  " + tool["name"])
        self.tool_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.tool_listbox.bind("<<ListboxSelect>>", self._on_tool_select)

        # 右侧操作区
        content = tk.Frame(body, padx=24, pady=18)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tool_title = tk.Label(content, font=("微软雅黑", 13, "bold"), anchor=tk.W)
        self.tool_title.pack(fill=tk.X)
        self.tool_desc = tk.Label(content, font=("微软雅黑", 9), fg="#777",
                                  anchor=tk.W, justify=tk.LEFT, wraplength=500)
        self.tool_desc.pack(fill=tk.X, pady=(4, 14))

        self.file_path_var = self._file_row(content, "PDF 文件", self.browse_file)
        self.output_path_var = self._file_row(content, "输出路径", self.browse_output)

        options = tk.Frame(content)
        options.pack(fill=tk.X, pady=(12, 0))
        self.ocr_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text="使用 PaddleOCR 识别（适用于扫描版 PDF）",
                       variable=self.ocr_var, font=("微软雅黑", 10)).pack(side=tk.LEFT)
        tk.Label(options, text="语言:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(16, 4))
        self.lang_var = tk.StringVar(value="ch")
        lang_box = ttk.Combobox(options, textvariable=self.lang_var, width=6,
                                state="readonly", values=["ch", "en"])
        lang_box.pack(side=tk.LEFT)

        self.convert_button = tk.Button(content, text="开始转换", command=self.start_convert,
                                        font=("微软雅黑", 11, "bold"), bg="#4CAF50", fg="white",
                                        activebackground="#43A047", relief=tk.FLAT, pady=8)
        self.convert_button.pack(fill=tk.X, pady=(20, 12))

        self.status_var = tk.StringVar(value="就绪")
        tk.Label(content, textvariable=self.status_var, font=("微软雅黑", 9),
                 fg="#666", anchor=tk.W).pack(fill=tk.X)
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(content, variable=self.progress_var, maximum=100).pack(fill=tk.X, pady=(6, 0))

    def _file_row(self, parent, label, command):
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=5)
        tk.Label(row, text=label, font=("微软雅黑", 10), width=8, anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar()
        tk.Entry(row, textvariable=var, font=("微软雅黑", 10)).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 8))
        tk.Button(row, text="浏览", command=command, font=("微软雅黑", 9),
                  relief=tk.FLAT, bg="#E0E0E0", padx=12).pack(side=tk.RIGHT)
        return var

    # -- 功能切换 ---------------------------------------------------------

    @property
    def tool(self):
        index = self.tool_listbox.curselection()
        return TOOLS[index[0] if index else 0]

    def _on_tool_select(self, _event=None):
        tool = self.tool
        self.tool_title.config(text=tool["name"])
        self.tool_desc.config(text=tool["desc"])
        self.status_var.set("就绪")
        self.progress_var.set(0)
        # 扩展名变了，旧的输出路径必然失效，直接按新功能重算
        if self.file_path_var.get():
            self._set_default_output(self.file_path_var.get())

    def _set_default_output(self, pdf_path):
        self.output_path_var.set(os.path.splitext(pdf_path)[0] + self.tool["ext"])

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择PDF文件", filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)
            self._set_default_output(file_path)

    def browse_output(self):
        tool = self.tool
        output_path = filedialog.asksaveasfilename(
            title="保存文件", defaultextension=tool["ext"], filetypes=tool["filetypes"])
        if output_path:
            self.output_path_var.set(output_path)

    # -- 转换 -------------------------------------------------------------

    def start_convert(self):
        pdf_path = self.file_path_var.get()
        out_path = self.output_path_var.get()

        if not pdf_path:
            messagebox.showerror("错误", "请选择PDF文件")
            return
        if not out_path:
            messagebox.showerror("错误", "请选择输出路径")
            return
        if not os.path.exists(pdf_path):
            messagebox.showerror("错误", "PDF文件不存在")
            return
        if self._running:
            messagebox.showwarning("提示", "当前已有转换任务在运行")
            return

        self._running = True
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("转换中...")
        self.progress_var.set(0)

        tool = self.tool
        worker = threading.Thread(
            target=self._worker,
            args=(tool["run"], pdf_path, out_path, self.ocr_var.get(), self.lang_var.get()),
            daemon=True,
        )
        worker.start()

    def _worker(self, run, pdf_path, out_path, use_ocr, lang):
        try:
            run(pdf_path, out_path, use_ocr, lang,
                progress=lambda value: self._ui_queue.put(("progress", value)),
                status=lambda text: self._ui_queue.put(("status", text)))
            self._ui_queue.put(("done", out_path))
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
                    self._finish()
                    self.status_var.set("转换完成")
                    self.progress_var.set(100)
                    messagebox.showinfo("成功", f"转换成功！\n输出文件: {payload}")
                    os.startfile(os.path.dirname(os.path.abspath(payload)))
                elif kind == "error":
                    self._finish()
                    self.status_var.set("转换失败")
                    self.progress_var.set(0)
                    messagebox.showerror("错误", f"转换失败: {payload}")
        except queue.Empty:
            pass

        try:
            self.root.after(100, self._process_ui_queue)
        except tk.TclError:
            return

    def _finish(self):
        self._running = False
        self.convert_button.config(state=tk.NORMAL)
