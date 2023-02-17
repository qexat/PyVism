"""
Vism built-in types.
"""
from typing import Any
from typing import Literal


class UnsetTypeMeta(type):
	def __instancecheck__(self, _: Any) -> Literal[True]:
		return True


class UnsetType(metaclass=UnsetTypeMeta):
	def __repr__(self) -> str:
		return "<Unset>"


MemoryValue = (
	int
	| float
	| complex
	| bool
	| str
	| bytes
	| list[Any]
	| tuple[Any, ...]
	| set[Any]
	| dict[Any, Any]
	| None
	| UnsetType
)
