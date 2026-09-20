"""开发时直接跑源码，不用先装包：python run.py [--self-check ...]"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from pdf_utils.__main__ import main  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from pdf_utils import selfcheck

        if "--self-check" in sys.argv:
            selfcheck.check_markdown()
            selfcheck.check_convert()
        elif "--check-models" in sys.argv:
            selfcheck.check_models()
        elif "--self-test" in sys.argv:
            selfcheck.check_models(with_ocr=True)
        else:
            raise SystemExit(f"未知参数: {sys.argv[1:]}")
    else:
        main()
