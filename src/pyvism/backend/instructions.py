from typing import Any

from pyvism.backend.tools import IdentifierLike
from pyvism.backend.tools import mnemonic
from pyvism.backend.tools import StreamIDLike


@mnemonic("_UNARY_WT_MNEMONIC")
def _UNARY_WT_MNEMONIC(_: IdentifierLike) -> IdentifierLike:
	...


@mnemonic("_BINARY_WT_MNEMONIC")
def _BINARY_WT_MNEMONIC(_: IdentifierLike, __: IdentifierLike) -> IdentifierLike:
	...


@mnemonic("_UNARY_NT_MNEMONIC")
def _UNARY_NT_MNEMONIC(_: IdentifierLike) -> None:
	...


@mnemonic("_BINARY_NT_MNEMONIC")
def _BINARY_NT_MNEMONIC(_: IdentifierLike, __: IdentifierLike) -> None:
	...


@mnemonic("_TERNARY_NT_MNEMONIC")
def _TERNARY_NT_MNEMONIC(
	_: IdentifierLike,
	__: IdentifierLike,
	___: IdentifierLike,
) -> None:
	...


# UNARY WITH TARGET
_UNARY_WT = _UNARY_WT_MNEMONIC.similar
# BINARY WITH TARGET
_BINARY_WT = _BINARY_WT_MNEMONIC.similar
# UNARY NO TARGET
_UNARY_NT = _UNARY_NT_MNEMONIC.similar
# BINARY NO TARGET
_BINARY_NT = _BINARY_NT_MNEMONIC.similar
# TERNARY NO TARGET
_TERNARY_NT = _TERNARY_NT_MNEMONIC.similar


# *- ASSIGNATION -* #


@mnemonic("MEMCH")
def MEMCH(_: Any) -> IdentifierLike:
	...


# *- STREAM STUFF -* #


@mnemonic("SWRITE")
def SWRITE(_: str) -> StreamIDLike:
	...


@mnemonic("SFLUSH")
def SFLUSH() -> StreamIDLike:
	...


@mnemonic("PRINTV")
def PRINTV(_: IdentifierLike) -> None:
	...


# *- MATH -* #
ADD = _BINARY_WT("ADD")
SUB = _BINARY_WT("SUB")
MUL = _BINARY_WT("MUL")
INTDIV = _BINARY_WT("INTDIV")
MODULO = _BINARY_WT("MODULO")
DIVMOD = _BINARY_WT("DIVMOD")
NEG = _UNARY_WT("NEG")
POW = _BINARY_WT("POW")
POW2 = _UNARY_WT("POW2")

# *- LOGIC -* #
AND = _BINARY_WT("AND")
OR = _BINARY_WT("OR")
XOR = _BINARY_WT("XOR")
NOT = _UNARY_WT("NOT")
SLL = _BINARY_WT("SLL")
SRL = _BINARY_WT("SRL")
SRA = _BINARY_WT("SRA")

# *- BRANCHING -* #
BEQ = _TERNARY_NT("BEQ")
BEQ0 = _BINARY_NT("BEQ0")
BEQ1 = _BINARY_NT("BEQ1")
BNE = _TERNARY_NT("BNE")
BGE = _TERNARY_NT("BGE")
BGT = _TERNARY_NT("BGT")
BLE = _TERNARY_NT("BLE")
BLT = _TERNARY_NT("BLT")
JUMP = _UNARY_NT("JUMP")

# *- HIGH-LEVEL -*#
UNION = _BINARY_WT("UNION")
INTER = _BINARY_WT("INTER")
DIFF = _BINARY_WT("DIFF")
SYMDIFF = _BINARY_WT("SYMDIFF")
CRTPROD = _BINARY_WT("CRTPROD")
REPLIC = _BINARY_WT("REPLIC")

PATHJOIN = _BINARY_WT("PATHJOIN")
