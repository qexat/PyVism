"""
Constants used across PyVism blocks.
"""

__all__ = (
	'__version__',
	'REGISTER_MAX_ADDR',
	'NULL',
	'REPL_PROMPT',
	'confusable_symbols',
)


__version__ = '2.1.1'

import os
from random import choice

from pyvism.py_utils import bold
from pyvism.py_utils import color_rgb
from pyvism.py_utils import light
from pyvism import qtheme


REGISTER_MAX_ADDR = 0x10

PRGM_MODE_CHAR = '^'
MACRO_MODE_CHAR = '?'

DISCARDED_CHARS = {' '}
ESCAPABLE_CHARS = {
	'\\': '\\',
	'n': '\n',
	't': '\t',
	'b': '\b',
	'f': '\f',
	'r': '\r',
	'e': '\x1b',
	PRGM_MODE_CHAR: PRGM_MODE_CHAR,
	MACRO_MODE_CHAR: MACRO_MODE_CHAR,
}

NULL = -1

STREAM_IDS = {'null': NULL, 'stdout': 0, 'stderr': 1}


REPL_SYNOPSIS = (
	bold(color_rgb('PyVism', choice(qtheme.COLORS)))
	+ color_rgb(' :: ', qtheme.FAINT)
	+ color_rgb(f'v{__version__}', qtheme.NORMAL)
)
REPL_PROMPT = light('>>> ')
CMD_MODE_CHAR = '!'
REPL_HISTORY_FILE = os.path.abspath('src/pyvism/repl/.history.rvism')


confusable_symbols: dict[str, str] = {'*': '×'}
