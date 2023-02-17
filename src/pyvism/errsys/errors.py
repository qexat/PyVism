"""
Here are defined all the compilation errors that could be thrown, and few helpers for some.
"""
from pyvism.compiler.tools import CompilerState
from pyvism.compiler.tools import PosTypeDef
from pyvism.compiler.tools import TypeDef
from pyvism.constants import confusable_symbols
from pyvism.errsys.tools import Error
from pyvism.errsys.tools import ErrorLine
from pyvism.errsys.tools import InfoLine
from pyvism.errsys.tricks import get_args_types_no_E009
from pyvism.errsys.tricks import get_buffer_eval_no_E002
from pyvism.errsys.tricks import get_pseudo_mnemonic_no_E008
from pyvism.parser.tools import CARET_MODES
from pyvism.parser.tools import FileHandler
from pyvism.parser.tools import macro_mode_request
from pyvism.parser.tools import MacroKind
from pyvism.parser.tools import Mode
from pyvism.parser.tools import program_mode_request


# E001: invalid selector type
def E001(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E001: invalid selector type

	## Examples

	- `&0`: `0` is not a valid identifier for Memory (`&`)
	- `$x`: `x` is not a valid address for Register (`$`)
	- `:D`: `D` is not a valid integer for Stream (`:`)
	"""

	selector_type = state.get_target_kind_type()
	received_value = state.read_buffer()

	message = f"invalid {selector_type.name}"
	summary = f"{message} {received_value!r}"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos + 1), message)

	return Error("E001", summary, file.name, error_line)


# E002: invalid literal
def E002(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E002: invalid literal

	## Example

	>>> &x ^l "hello ^n

	`"hello` is an unterminated string, therefore an invalid literal.
	"""
	received_value = state.read_buffer()

	message = "invalid literal"
	summary = f"{message} {received_value!r}"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos), message)

	return Error("E002", summary, file.name, error_line)


# E003: mismatched types
def E003(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E003: mismatched types

	## Example

	>>> &x ^l 69 ^n

	`x` is of type `int`.

	>>> &x ^l "Hello" ^n

	`str` cannot be assigned to `x` because this latter is an integer.
	"""

	received_value = get_buffer_eval_no_E002(state)
	target_typedef = state.get_target_typedef()

	found_type = type(received_value)
	expected_type = target_typedef.type

	message = f"expected `{expected_type.__name__}`, found {found_type.__name__}"
	summary = "mismatched types"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos), message)
	info_lines = _E003_info_gen(file, target_typedef)

	return Error("E003", summary, file.name, error_line, info_lines)


def _E003_info_gen(file: FileHandler, typedef: TypeDef) -> list[InfoLine]:
	if not isinstance(typedef, PosTypeDef):
		return []

	return [
		InfoLine(
			file.get_line(typedef.line_number - 1),
			*typedef.data,
			f"was defined here as {typedef.type.__name__}",
		),
	]


# E004: unexpected end of line
def E004(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E004: unexpected end of line

	## Example

	>>> &x ^

	`^` was expecting a mode at the next character, but it encountered
	an end of line instead.
	"""

	guess_expected = _E004_guess_expected(file, state)

	message = f"expected {guess_expected} here" if guess_expected else "here"
	summary = "unexpected end of line"
	lc, ln, sp, ep = file.freeze_position(file.pos)
	error_line = ErrorLine(lc, ln, sp, ep + 1, message)

	return Error("E004", summary, file.name, error_line)


def _E004_guess_expected(file: FileHandler, state: CompilerState) -> str | None:
	guess: str | None = None
	file.pos -= 1  # avoids IndexError due to EOL

	if program_mode_request(file, state):
		guess = "mode character"
	elif macro_mode_request(file, state):
		guess = "macro character"
	elif state.mode is Mode.Select:
		guess = state.get_target_kind_type().name
	elif state.mode is Mode.Assign:
		assign_kind = state.mode_type

		if assign_kind:
			guess = assign_kind.name.lower()

	file.pos += 1
	return guess


# E005: invalid mode
def E005(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E005: invalid mode

	## Example

	>>> &x ^r

	`r` is not a valid mode.
	"""

	symbol = file.current_char

	message = "invalid mode"
	summary = f"{message} {symbol!r}"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos), message)
	hint = "try using one of the following candidates:"
	candidates = _E005_get_candidates()

	return Error(
		"E005",
		summary,
		file.name,
		error_line,
		hint_message=hint,
		candidate_messages=candidates,
	)


def _E005_get_candidates() -> list[str]:
	return [f"`^{c}" for c in CARET_MODES.keys()]


# E006: undefined macro
def E006(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E006: undefined macro

	## Example

	>>> ?z

	`z` is not a defined macro.
	"""

	symbol = file.current_char

	message = "this macro is undefined"
	summary = f"macro `?{symbol}` is undefined"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos), message)
	hint = "try using one of the following candidates:"
	candidates = _E006_get_candidates()

	return Error(
		"E006",
		summary,
		file.name,
		error_line,
		hint_message=hint,
		candidate_messages=candidates,
	)


def _E006_get_candidates() -> list[str]:
	return [f"`?{c}`" for c in MacroKind.values()]


# E007: invalid escape sequence
def E007(file: FileHandler, _: CompilerState) -> Error:
	"""
	# E007: invalid escape sequence

	## Example

	>>> &x ^sHello\\p^n

	`\\p` is not a valid escape sequence.
	"""

	message = "invalid escape sequence"
	summary = f"{message} '\\{file.current_char}'"
	lc, ln, sp, ep = file.freeze_position(file.pos - 1)
	error_line = ErrorLine(lc, ln, sp, ep + 1, message)

	return Error("E007", summary, file.name, error_line)


# E008: unknown symbol
def E008(file: FileHandler, _: CompilerState) -> Error:
	"""
	# E008: unknown symbol

	## Example

	>>> z

	`z` is not a valid symbol.
	"""

	symbol = file.current_char
	similar_symbol = _E008_get_similar_sym(symbol)

	message = "unknown symbol"
	summary = f"{message} {symbol!r}"
	lc, ln, sp, ep = file.freeze_position(file.pos)
	error_line = ErrorLine(lc, ln, sp, ep + 1, message)
	hint = None if similar_symbol is None else f"did you mean `{similar_symbol}`?"

	return Error("E008", summary, file.name, error_line, hint_message=hint)


def _E008_get_similar_sym(char: str) -> str | None:
	return confusable_symbols.get(char, None)


# E009: unmatching number of parameters
def E009(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E009: unmatching number of parameters

	## Example

	>>> +

	`+` expects three args, but none are set.
	"""

	symbol = file.current_char

	expected = get_pseudo_mnemonic_no_E008(symbol).get_identifier_number()
	received = _E009_get_received_args_number(state, expected)

	message = "unmatching number of parameters"
	summary = f"{message} for {symbol!r}: expected {expected} but got {received}"
	lc, ln, sp, ep = file.freeze_position(file.pos)
	error_line = ErrorLine(lc, ln, sp, ep + 1, message)

	return Error("E009", summary, file.name, error_line)


def _E009_get_received_args_number(
	state: CompilerState,
	expected_args_number: int,
) -> int:
	return len([arg for arg in state.registers[:expected_args_number] if arg is not None])


# E010: no overload for operator
def E010(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E010: no overload for operator

	## Example

	>>> &a ^l 0 ^n
	>>> &b ^l 6 ^n
	>>> &c ^l "9" ^n
	>>> $0 ^l "a" ^n $1 ^l "b" ^n $2 ^l "c" ^n
	>>> +

	`+` does not support `int` (`&b`) and `str` (`&c`).
	"""

	symbol = file.current_char

	args_types = get_args_types_no_E009(state, symbol)
	args_types_str = _E010_pretty_args_types(args_types)

	message = f"no overload for {args_types_str}"
	summary = f"no overload for `{symbol}` with {args_types_str}"
	lc, ln, sp, ep = file.freeze_position(file.pos)
	error_line = ErrorLine(lc, ln, sp, ep + 1, message)

	return Error("E010", summary, file.name, error_line)


def _E010_pretty_args_types(args_types: tuple[type, *tuple[type, ...]]) -> str:
	*except_last, last = args_types

	if not except_last:
		return f"`{last.__name__}`"

	return (
		", ".join(map(lambda t: f"`{t.__name__}`", except_last)) + f" and `{last.__name__}`"
	)


# E011: undefined identifier
def E011(file: FileHandler, state: CompilerState) -> Error:
	"""
	# E011: undefined identifier

	## Example

	>>> $0 ^l "x" ^n

	`x` is not a defined identifier.
	"""

	undefined_identifier = get_buffer_eval_no_E002(state)

	message = "undefined identifier"
	summary = f"undefined identifier `{undefined_identifier}`"
	error_line = ErrorLine(*file.freeze_position(state.mode_spos), message)

	return Error("E011", summary, file.name, error_line)
