from typing import Any
from typing import LiteralString

from pyvism.backend.instructions import ADD
from pyvism.backend.instructions import DIFF
from pyvism.backend.instructions import DIVMOD
from pyvism.backend.instructions import INTDIV
from pyvism.backend.instructions import MODULO
from pyvism.backend.instructions import MUL
from pyvism.backend.instructions import PATHJOIN
from pyvism.backend.instructions import PRINTV
from pyvism.backend.instructions import REPLIC
from pyvism.backend.instructions import SFLUSH
from pyvism.backend.instructions import SUB
from pyvism.backend.instructions import SWRITE
from pyvism.backend.instructions import UNION
from pyvism.backend.tools import AnyIRMnemonic
from pyvism.backend.tools import PseudoMnemonic
from pyvism.compiler.types import MemoryValue
from pyvism.compiler.types import UnsetType


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


def dispatch(
	symbol: str,
	*types: * tuple[type[MemoryValue], *tuple[type[MemoryValue], ...]],
) -> AnyIRMnemonic | None:
	"""
	Given a symbol and the operand types, return the corresponding IR mnemonic.

	**IMPORTANT ⚠️**

	→ `types` order matters!
	For example, with symbol `+`, it should be as following:
	`destination type`, `source 1 type`, `source 2 type`

	Don't use `symbol_table` directly, but this helper function instead.
	"""

	pseudo = symbol_table.get(symbol, None)

	# When symbol is unknown -- this should not happen (E008)
	if pseudo is None:
		return None

	return pseudo.get_overload(types)
