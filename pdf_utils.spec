# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

# 随程序分发的 OCR 模型，保证用户下载后无需联网下载模型即可识别。
# 首次构建前先在开发机上跑一次 OCR，让 PaddleOCR 把模型缓存到 ~/.paddleocr。
PADDLEOCR_HOME = os.environ.get("PADDLEOCR_HOME") or os.path.join(os.path.expanduser("~"), ".paddleocr")
if not os.path.isdir(PADDLEOCR_HOME):
    raise SystemExit(
        f"找不到 OCR 模型目录 {PADDLEOCR_HOME}。\n"
        f"请先运行一次 `python -m pdf_utils` 并完成一次 OCR 识别，"
        f"让 PaddleOCR 下载模型，或用 PADDLEOCR_HOME 环境变量指定模型目录。"
    )

paddleocr_models = []
for dirpath, _dirnames, filenames in os.walk(PADDLEOCR_HOME):
    for filename in filenames:
        src = os.path.join(dirpath, filename)
        dst = os.path.join("paddleocr_models", os.path.relpath(src, PADDLEOCR_HOME))
        paddleocr_models.append((src, os.path.dirname(dst)))

# PaddleOCR版本程序分析
paddleocr_datas, paddleocr_binaries, paddleocr_hiddenimports = collect_all('paddleocr')
paddle_datas, paddle_binaries, paddle_hiddenimports = collect_all('paddle')
pyclipper_datas, pyclipper_binaries, pyclipper_hiddenimports = collect_all('pyclipper')
paddleocr_py_datas = collect_data_files('paddleocr', include_py_files=True)

# paddleocr 的运行时依赖是裸导入，PyInstaller 的静态分析跟不进去
# （collect_all('paddleocr') 只收集 paddleocr 自己的文件，不跟进它的依赖），
# 漏掉它们 exe 会在识别时才报 ModuleNotFoundError。
# 下面这份清单是用 AST 扫 paddleocr 全部 .py 的顶层 import、再比对 venv 里
# 已安装的发行包得到的；新增/升级 paddleocr 后要重新扫一遍。
runtime_deps = [
    'skimage', 'imgaug', 'six', 'rapidfuzz', 'imageio', 'lmdb', 'tqdm',
    'requests', 'lxml', 'openpyxl', 'premailer', 'bs4', 'Cython',
]
runtime_datas, runtime_binaries, runtime_hiddenimports = [], [], []
for dep in runtime_deps:
    dep_datas, dep_binaries, dep_hiddenimports = collect_all(dep)
    runtime_datas += dep_datas
    runtime_binaries += dep_binaries
    runtime_hiddenimports += dep_hiddenimports

# 有些包（imageio 等）启动时会用 importlib.metadata 读自己的版本号，
# 只收集代码文件不带元数据会在运行时抛 PackageNotFoundError。
runtime_metadata = []
for dist in [
    'imageio', 'scikit-image', 'imgaug', 'rapidfuzz', 'six', 'scipy',
    'shapely', 'paddleocr', 'paddlepaddle', 'lmdb', 'tqdm', 'requests',
    'lxml', 'openpyxl', 'premailer', 'beautifulsoup4', 'Cython',
]:
    runtime_metadata += copy_metadata(dist)

# 打包 src 布局的包：pathex 指到 src，入口用包内的 __main__.py。
# 入口脚本是绝对导入（见 __main__.py 注释），所以 hiddenimports 里要显式列出
# 包内其余模块 —— PyInstaller 只会顺着入口的 import 走，漏了就运行时才炸。
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

a = Analysis([os.path.join(SRC_DIR, 'pdf_utils', '__main__.py')],
             pathex=[SRC_DIR],
             binaries=paddleocr_binaries + paddle_binaries + pyclipper_binaries + runtime_binaries,
             datas=paddleocr_datas + paddle_datas + paddleocr_py_datas + pyclipper_datas + paddleocr_models + runtime_datas + runtime_metadata,

              hiddenimports=[
                  'pdf_utils',
                  'pdf_utils.gui',
                  'pdf_utils.tools',
                  'pdf_utils.ocr',
                  'pdf_utils.selfcheck',
                  'pdf_utils.converters',
                  'pdf_utils.converters.to_word',
                  'pdf_utils.converters.to_markdown',
                  'pdf2docx',
                  'fitz',
                  'PIL',
                  'docx',
                  'imghdr',
                  'auto_log',
                  'tkinter',
                  'threading',
                  'os',
                  'subprocess',
                  'scipy',
                  'shapely',
              ] + paddleocr_hiddenimports + paddle_hiddenimports + pyclipper_hiddenimports + runtime_hiddenimports + ['pyclipper'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# 添加Cython的Utility目录
a.datas += [
    (r'Cython\Utility\CppSupport.cpp', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\CppSupport.cpp', 'DATA'),
    (r'Cython\Utility\CppConvert.pyx', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\CppConvert.pyx', 'DATA'),
    (r'Cython\Utility\MemoryView.pyx', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\MemoryView.pyx', 'DATA'),
    (r'Cython\Utility\MemoryView_C.c', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\MemoryView_C.c', 'DATA'),
    (r'Cython\Utility\ObjectHandling.c', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\ObjectHandling.c', 'DATA'),
    (r'Cython\Utility\StringTools.c', r'C:\Users\Cypher\AppData\Local\Programs\Python\Python312\Lib\site-packages\Cython\Utility\StringTools.c', 'DATA')
]

# 构建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 构建EXE文件
ex = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='PDF工具箱',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,  # 无控制台窗口
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon=None)  # 可以指定图标文件路径
