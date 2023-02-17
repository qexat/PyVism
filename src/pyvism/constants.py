"""
Constants used across PyVism blocks.
"""


__version__ = "1.0.0"

import os as _os
from random import choice as _choice

from pyvism.py_utils import bold as _bold
from pyvism.py_utils import color_rgb as _color_rgb
from pyvism.py_utils import light as _light
from pyvism import qtheme as _qtheme


REGISTER_MAX_ADDR = 0x10

PRGM_MODE_CHAR = "^"
MACRO_MODE_CHAR = "?"

DISCARDED_CHARS = {" "}
ESCAPABLE_CHARS = {
	"\\": "\\",
	"n": "\n",
	"t": "\t",
	"b": "\b",
	"f": "\f",
	"r": "\r",
	"e": "\x1b",
	PRGM_MODE_CHAR: PRGM_MODE_CHAR,
	MACRO_MODE_CHAR: MACRO_MODE_CHAR,
}

NULL = -1

STREAM_IDS = {"null": NULL, "stdout": 0, "stderr": 1}


REPL_SYNOPSIS = (
	_bold(_color_rgb("PyVism", _choice(_qtheme.COLORS)))
	+ _color_rgb(" :: ", _qtheme.FAINT)
	+ _color_rgb(f"v{__version__}", _qtheme.NORMAL)
)
REPL_PROMPT = _light(">>> ")
CMD_MODE_CHAR = "!"
REPL_HISTORY_FILE = _os.path.abspath("src/pyvism/repl/.history.rvism")


confusable_symbols: dict[str, str] = {"*": "×"}
