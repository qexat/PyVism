"""
Some utils to extend Python.
"""

from enum import Enum
from typing import Any, TypeVar


T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")


class SupportsContains(Enum):
	@classmethod
	def values(cls):
		for member in cls:
			yield member.value

	@classmethod
	def contains(cls, value: Any) -> bool:
		return value in {member.value for member in cls}
