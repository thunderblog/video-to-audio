#!/usr/bin/env python3
"""MP4 to MP3 Converter - エントリーポイント"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import main

if __name__ == "__main__":
    main()
