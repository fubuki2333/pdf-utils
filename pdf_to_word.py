import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pdf2docx import Converter

class PDFtoWordConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转Word工具")
        self.root.geometry("600x300")
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
        self.title_label = tk.Label(self.main_frame, text="PDF转Word工具", font=("微软雅黑", 16, "bold"))
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
        
        # 创建转换按钮
        self.convert_button = tk.Button(self.main_frame, text="开始转换", command=self.convert_pdf_to_word, font=("微软雅黑", 12, "bold"), bg="#4CAF50", fg="white", padx=20, pady=10)
        self.convert_button.pack(pady=20)
        
        # 创建状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, font=("微软雅黑", 10), fg="#666")
        self.status_label.pack(pady=10)
    
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
            self.root.update()
            
            # 执行转换
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            
            self.status_var.set("转换完成")
            messagebox.showinfo("成功", f"PDF转换为Word成功！\n输出文件: {docx_path}")
            
            # 打开输出文件所在目录
            output_dir = os.path.dirname(docx_path)
            os.startfile(output_dir)
            
        except Exception as e:
            self.status_var.set("转换失败")
            messagebox.showerror("错误", f"转换失败: {str(e)}")

def main():
    # 检查是否安装了必要的库
    try:
        import pdf2docx
    except ImportError:
        import subprocess
        import sys
        
        # 尝试安装依赖
        print("正在安装必要的依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2docx"])
            print("依赖安装成功！")
        except Exception as e:
            print(f"依赖安装失败: {str(e)}")
            print("请手动运行: pip install pdf2docx")
            input("按回车键退出...")
            return
    
    # 创建主窗口
    root = tk.Tk()
    app = PDFtoWordConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()