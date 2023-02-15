from typing import Any, LiteralString
from pyvism.compiler.tools import ParsingState
from pyvism.ir.interface import symbol_table
from pyvism.ir.tools import IdentifierLike, PseudoMnemonic, StreamIDLike


def get_buffer_eval_no_E002(state: ParsingState) -> Any:
	return state.evaluate_buffer().unwrap()


def get_pseudo_mnemonic_no_E008(
	symbol: str,
) -> PseudoMnemonic[LiteralString, Any, *tuple[Any, ...]]:
	return symbol_table[symbol]


def get_operands_no_E009(
	state: ParsingState,
	kinds: tuple[type, *tuple[type, ...]],
) -> list[IdentifierLike | StreamIDLike]:
	return list(state.get_operands(kinds))  # type: ignore


def get_args_types_no_E009(
	state: ParsingState,
	symbol: str,
) -> tuple[type, *tuple[type, ...]]:
	pm = get_pseudo_mnemonic_no_E008(symbol)
	operands = get_operands_no_E009(state, pm.kinds)
	return tuple(state.get_operands_types(operands))
