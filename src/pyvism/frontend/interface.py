"""
Interface for front-ends to easily deal with IR.
"""
from typing import Any
from typing import LiteralString

from pyvism.compiler.types import MemoryValue
from pyvism.compiler.types import UnsetType
from pyvism.frontend.instructions import ADD
from pyvism.frontend.instructions import DIFF
from pyvism.frontend.instructions import DIVMOD
from pyvism.frontend.instructions import INTDIV
from pyvism.frontend.instructions import MODULO
from pyvism.frontend.instructions import MUL
from pyvism.frontend.instructions import PATHJOIN
from pyvism.frontend.instructions import PRINTV
from pyvism.frontend.instructions import REPLIC
from pyvism.frontend.instructions import SFLUSH
from pyvism.frontend.instructions import SUB
from pyvism.frontend.instructions import SWRITE
from pyvism.frontend.instructions import UNION
from pyvism.frontend.tools import PseudoMnemonic


pseudo_mnemonics: list[PseudoMnemonic[LiteralString, Any, *tuple[Any, ...]]] = [
    PseudoMnemonic(
        "+",
        {
            ADD: [
                (int, int, int),
                (int, int, bool),
                (int, bool, int),
                (int, bool, bool),
                (float, int, float),
                (float, float, int),
                (float, float, float),
                (float, float, bool),
                (float, bool, float),
                (complex, int, complex),
                (complex, float, complex),
                (complex, complex, int),
                (complex, complex, float),
                (complex, complex, complex),
                (complex, complex, bool),
                (complex, bool, complex),
            ],
            UNION: [
                (str, str, str),
                (bytes, bytes, bytes),
                (list, list, list),
                (tuple, tuple, tuple),
                (set, set, set),
                (dict, dict, dict),
            ],
        },
    ),
    PseudoMnemonic(
        "-",
        {
            SUB: [
                (int, int, int),
                (int, int, bool),
                (int, bool, int),
                (int, bool, bool),
                (float, int, float),
                (float, float, int),
                (float, float, float),
                (float, float, bool),
                (float, bool, float),
                (complex, int, complex),
                (complex, float, complex),
                (complex, complex, int),
                (complex, complex, float),
                (complex, complex, complex),
                (complex, complex, bool),
                (complex, bool, complex),
            ],
            DIFF: [
                (str, str, str),
                (bytes, bytes, bytes),
                (list, list, list),
                (tuple, tuple, tuple),
                (set, set, set),
                (dict, dict, dict),
            ],
        },
    ),
    PseudoMnemonic(
        "×",
        {
            MUL: [
                (int, int, int),
                (int, int, bool),
                (int, bool, int),
                (int, bool, bool),
                (float, int, float),
                (float, float, int),
                (float, float, float),
                (float, float, bool),
                (complex, int, complex),
                (complex, float, complex),
                (complex, complex, int),
                (complex, complex, float),
                (complex, complex, complex),
                (complex, complex, bool),
                (complex, bool, complex),
            ],
            REPLIC: [
                (str, int, str),
                (str, bool, str),
                (str, str, int),
                (str, str, bool),
                (bytes, int, bytes),
                (bytes, bool, bytes),
                (bytes, bytes, int),
                (bytes, bytes, bool),
                (list, int, list),
                (list, bool, list),
                (list, list, int),
                (list, list, bool),
                (tuple, int, tuple),
                (tuple, bool, tuple),
                (tuple, tuple, int),
                (tuple, tuple, bool),
            ],
        },
    ),
    PseudoMnemonic(
        "/",
        {
            INTDIV: [
                (int, int, int),
                (int, int, bool),
                (int, bool, int),
                (int, bool, bool),
            ],
            PATHJOIN: [
                (str, str, str),
            ],
        },
    ),
    PseudoMnemonic(
        "%",
        {
            MODULO: [
                (int, int, int),
                (int, int, bool),
                (int, bool, int),
                (int, bool, bool),
            ],
        },
    ),
    PseudoMnemonic(
        "÷",
        {
            DIVMOD: [
                (tuple[int, int], int, int),
                (tuple[int, int], int, bool),
                (tuple[int, int], bool, int),
                (tuple[int, int], bool, bool),
            ],
        },
    ),
    PseudoMnemonic(
        "p",
        {
            PRINTV: [
                (
                    UnsetType,
                    MemoryValue,
                ),
            ],
        },
    ),
    PseudoMnemonic(
        "w",
        {
            SWRITE: [
                (int, str),
            ],
        },
    ),
    PseudoMnemonic(
        "f",
        {
            SFLUSH: [
                (int,),
            ],
        },
    ),
]

symbol_table = {pseudo.symbol: pseudo for pseudo in pseudo_mnemonics}


def get_pseudo_mnemonic(
    symbol: str,
) -> PseudoMnemonic[LiteralString, Any, *tuple[Any, ...]] | None:
    return symbol_table.get(symbol, None)
