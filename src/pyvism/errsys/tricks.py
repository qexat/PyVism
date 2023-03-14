"""
Tricks to get values and skipping usual checks.
"""
from typing import Any
from typing import LiteralString

from pyvism.compiler.tools import CompilerState
from pyvism.frontend.interface import symbol_table
from pyvism.frontend.tools import IdentifierLike
from pyvism.frontend.tools import PseudoMnemonic
from pyvism.frontend.tools import StreamIDLike


def get_buffer_eval_no_E002(state: CompilerState) -> Any:
    return state.evaluate_buffer().unwrap()


def get_pseudo_mnemonic_no_E008(
    symbol: str,
) -> PseudoMnemonic[LiteralString, Any, *tuple[Any, ...]]:
    return symbol_table[symbol]


def get_operands_no_E009(
    state: CompilerState,
    kinds: tuple[type, *tuple[type, ...]],
) -> list[IdentifierLike | StreamIDLike]:
    return list(state.get_operands(kinds))  # type: ignore


def get_args_types_no_E009(
    state: CompilerState,
    symbol: str,
) -> tuple[type, *tuple[type, ...]]:
    pm = get_pseudo_mnemonic_no_E008(symbol)
    operands = get_operands_no_E009(state, pm.kinds)
    return tuple(state.get_operands_types(operands))
