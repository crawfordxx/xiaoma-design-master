"""xiaoma-editor 测试包。

`python3 -m unittest discover -s skills/xiaoma-editor/tests -t .` 会把测试模块当成
`skills.xiaoma-editor.tests.test_xxx` 导入（目录名带连字符，不能用 import 语句），
所以在这里把 `scripts/` 和本目录塞进 sys.path，测试模块才能 `from _util import ...`、
`import cards`。放 __init__.py 而不是每个测试文件里，是为了只写一遍。
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE.parent / "scripts"), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
