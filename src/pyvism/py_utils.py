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


def bold(s: str) -> str:
	return f"\x1b[1m{s}\x1b[22m"


def color(s: str, c: int) -> str:
	return f"\x1b[3{c}m{s}\x1b[39m"
