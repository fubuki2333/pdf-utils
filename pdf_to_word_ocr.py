import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pdf2docx import Converter
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import docx
from docx.shared import Inches

class PDFtoWordConverterOCR:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转Word工具 (带OCR功能)")
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
        self.title_label = tk.Label(self.main_frame, text="PDF转Word工具 (带OCR功能)", font=("微软雅黑", 16, "bold"))
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
            text="使用OCR识别（适用于扫描版PDF）", 
            variable=self.ocr_var, 
            font=("微软雅黑", 10)
        )
        self.ocr_checkbutton.pack(side=tk.LEFT, padx=5)
        
        # OCR语言选择
        self.lang_label = tk.Label(self.ocr_frame, text="OCR语言:", font=("微软雅黑", 10))
        self.lang_label.pack(side=tk.LEFT, padx=5)
        
        self.lang_var = tk.StringVar(value="chi_sim")
        self.lang_combobox = ttk.Combobox(
            self.ocr_frame, 
            textvariable=self.lang_var, 
            values=[("chi_sim", "简体中文"), ("chi_tra", "繁体中文"), ("eng", "英文"), ("chi_sim+eng", "中英文")],
            font=("微软雅黑", 10),
            width=10
        )
        self.lang_combobox.pack(side=tk.LEFT, padx=5)
        self.lang_combobox['values'] = ["chi_sim", "chi_tra", "eng", "chi_sim+eng"]
        
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
        
        try:
            self.status_var.set("转换中...")
            self.progress_var.set(0)
            self.root.update()
            
            if use_ocr:
                # 使用OCR转换
                self.convert_with_ocr(pdf_path, docx_path, ocr_lang)
            else:
                # 使用常规转换
                self.convert_without_ocr(pdf_path, docx_path)
            
            self.status_var.set("转换完成")
            self.progress_var.set(100)
            messagebox.showinfo("成功", f"PDF转换为Word成功！\n输出文件: {docx_path}")
            
            # 打开输出文件所在目录
            output_dir = os.path.dirname(docx_path)
            os.startfile(output_dir)
            
        except Exception as e:
            self.status_var.set("转换失败")
            self.progress_var.set(0)
            messagebox.showerror("错误", f"转换失败: {str(e)}")
    
    def convert_without_ocr(self, pdf_path, docx_path):
        """不使用OCR的常规转换"""
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
    
    def convert_with_ocr(self, pdf_path, docx_path, ocr_lang):
        """使用OCR的转换（适用于扫描版PDF）"""
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        
        # 创建Word文档
        word_doc = docx.Document()
        
        for page_num in range(num_pages):
            # 更新进度
            progress = (page_num + 1) / num_pages * 100
            self.progress_var.set(progress)
            self.status_var.set(f"转换中... (第{page_num + 1}/{num_pages}页)")
            self.root.update()
            
            # 获取页面
            page = doc.load_page(page_num)
            
            # 将页面转换为图像
            pix = page.get_pixmap(dpi=300)  # 高DPI以提高OCR精度
            img_path = f"temp_page_{page_num}.png"
            pix.save(img_path)
            
            # 打开图像并进行OCR
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img, lang=ocr_lang)
            
            # 将文本添加到Word文档
            if page_num > 0:
                word_doc.add_page_break()
            
            # 添加页面文本
            if text.strip():
                word_doc.add_paragraph(text)
            
            # 尝试添加表格（如果有）
            # 注意：这部分可能需要更复杂的实现
            
            # 删除临时图像
            os.remove(img_path)
        
        # 保存Word文档
        word_doc.save(docx_path)
        
        # 关闭PDF文档
        doc.close()

def main():
    # 检查是否安装了必要的库
    required_libs = [
        ('pdf2docx', 'pdf2docx'),
        ('PyMuPDF', 'fitz'),
        ('Pillow', 'PIL'),
        ('pytesseract', 'pytesseract'),
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
        import sys
        
        # 尝试安装缺失的依赖
        print(f"正在安装必要的依赖: {', '.join(missing_libs)}")
        try:
            for lib in missing_libs:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print("依赖安装成功！")
        except Exception as e:
            print(f"依赖安装失败: {str(e)}")
            print(f"请手动运行: pip install {' '.join(missing_libs)}")
            input("按回车键退出...")
            return
    
    # 检查tesseract-ocr是否可用
    try:
        import pytesseract
        # 尝试获取tesseract版本
        pytesseract.get_tesseract_version()
    except Exception as e:
        print(f"tesseract-ocr不可用: {e}")
        print("正在尝试自动查找tesseract-ocr...")
        
        # 尝试自动查找tesseract路径
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"D:\Program Files\Tesseract-OCR\tesseract.exe",
            r"D:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            print(f"找到tesseract-ocr: {found_path}")
            pytesseract.pytesseract.tesseract_cmd = found_path
            try:
                pytesseract.get_tesseract_version()
                print("tesseract-ocr配置成功！")
            except Exception as e2:
                print(f"配置失败: {e2}")
                print("请确保已安装tesseract-ocr并添加到系统PATH")
                input("按回车键退出...")
                return
        else:
            print("未找到tesseract-ocr，请手动安装并添加到系统PATH")
            input("按回车键退出...")
            return
    
    # 创建主窗口
    root = tk.Tk()
    app = PDFtoWordConverterOCR(root)
    root.mainloop()

if __name__ == "__main__":
    main()