"""PDF 工具箱入口。

    python -m pdf_utils              启动界面
    python -m pdf_utils --self-check 跑自检，见 selfcheck.py

各模块分工见包内各文件的模块文档。
"""

import sys

# 本模块既是 `python -m pdf_utils` 的入口，也是 PyInstaller 的入口脚本。
# PyInstaller 把入口脚本当顶层模块编译，相对导入会报「no known parent package」，
# 所以这里用绝对导入；包内其余模块照常用相对导入。
from pdf_utils.gui import PdfToolbox
from pdf_utils.ocr import prepare_runtime_path


def main():
    import tkinter as tk
    from tkinter import messagebox

    prepare_runtime_path()

    required_libs = [('pdf2docx', 'pdf2docx'), ('PyMuPDF', 'fitz'), ('python-docx', 'docx')]
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

    root = tk.Tk()
    PdfToolbox(root)
    root.mainloop()


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        from pdf_utils.selfcheck import check_convert, check_markdown

        check_markdown()
        check_convert()
        sys.exit(0)
    if "--check-models" in sys.argv:
        from pdf_utils.selfcheck import check_models

        check_models()
        sys.exit(0)
    if "--self-test" in sys.argv:
        from pdf_utils.selfcheck import check_models

        check_models(with_ocr=True)
        sys.exit(0)

    main()
