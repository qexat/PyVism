"""
Constants used across PyVism blocks.
"""

__all__ = (
	"__version__",
	"REGISTER_MAX_ADDR",
	"NULL",
	"REPL_PROMPT",
	"confusable_symbols",
)


__version__ = "2.0.0"

from pyvism.py_utils import bold
from pyvism.py_utils import color


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

REPL_PROMPT = color(bold("VISM") + " ~> ", 7)


confusable_symbols: dict[str, str] = {"*": "×"}
