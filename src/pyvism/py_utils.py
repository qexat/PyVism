"""
Some utils to extend Python.
"""
from enum import Enum
from typing import Any


class SupportsContains(Enum):
	@classmethod
	def values(cls):
		for member in cls:
			yield member.value

	@classmethod
	def contains(cls, value: Any) -> bool:
		return value in {member.value for member in cls}
