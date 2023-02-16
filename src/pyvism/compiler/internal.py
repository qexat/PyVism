from collections.abc import Callable
from re import compile as compile_regex
from typing import Generic
from typing import TypeVar

from result import Err
from result import Ok
from result import Result

T = TypeVar("T")


def no_op(obj: T) -> T:
	return obj


class InternalType(Generic[T]):
	def __init__(self, name: str, regex: str, caster: Callable[[str], T]) -> None:
		self.name = name
		self.pattern = compile_regex(regex)
		self.caster = caster

	def evaluate(self, s: str) -> Result[T, None]:
		match = self.pattern.fullmatch(s)

		if match is None:
			return Err(None)

		return Ok(self.caster(s))


Address = InternalType("address", r"(?i)[0-9A-F]+", lambda s: int(s, base=16))
Integer = InternalType("integer", r"[+-]?[0-9]+", int)
Identifier = InternalType("identifier", r"(?i)[A-Z_]\w*", no_op)
