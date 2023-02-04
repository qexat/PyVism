from ast import literal_eval
from typing import Any

from result import Ok, Err, Result

from pyvism.runtime.builtins import *


def is_known_stream(fd: int) -> bool:
	return fd in STREAM_IDS.values()


def is_valid_address(s: str) -> bool:
	return ADDRESS_REGEXP.fullmatch(s) is not None


def is_valid_literal(s: str) -> bool:
	try:
		literal_eval(s)
	except (ValueError, SyntaxError):
		return False
	else:
		return True


def escape_literal(literal: str) -> str:
	escaped = literal
	for key, value in ESCAPABLE_CHARS.items():
		if key != value:
			escaped = escaped.replace(value, f"\\{key}")
	return escaped


def evaluate(unparsed_value: str, assign_type: AssignKind) -> Result[Any, None]:
	match assign_type:
		case AssignKind.String:
			return Ok(unparsed_value)
		case AssignKind.Literal:
			esc_value = escape_literal(unparsed_value)
			if not is_valid_literal(esc_value):
				return Err(None)
			return Ok(literal_eval(esc_value))
