from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
import inspect
from io import StringIO
from re import compile as re_compile
import sys
from typing import Any, Callable, Generic, TypeVar, TypeVarTuple, Self

from pyvism.constants import MEMORY_MAX_ADDR, NULL

__all__ = (
	"ADDRESS_REGEXP",
	"PRGM_MODE_CHAR",
	"DEBUG_MODE_CHAR",
	"ESCAPABLE_CHARS",
	"DISCARDED_CHARS",
	"MemoryValue",
	"UnsetType",
	"TargetKind",
	"Target",
	"MacroKind",
	"AssignKind",
	"Mode",
	"NS_MODES",
	"STREAM_IDS",
	"stream_endpoints",
	"BufferMap",
	"StreamMap",
	"ModeBufferMap",
	"TypeDef",
	"ConstTypeDef",
	"VarTypeDef",
	"instruction",
	"mnemonic",
)


KT = TypeVar("KT")
Ts = TypeVarTuple("Ts")


class SupportsContains(Enum):
	@classmethod
	def values(cls):
		for member in cls:
			yield member.value

	@classmethod
	def contains(cls, value: Any) -> bool:
		return value in {member.value for member in cls}


ADDRESS_REGEXP = re_compile(r"[0-9A-F]+")

PRGM_MODE_CHAR = "^"
DEBUG_MODE_CHAR = "?"
ESCAPABLE_CHARS = {
	"\\": "\\",
	"n": "\n",
	"t": "\t",
	"b": "\b",
	"f": "\f",
	"r": "\r",
	"e": "\x1b",
	PRGM_MODE_CHAR: PRGM_MODE_CHAR,
	DEBUG_MODE_CHAR: DEBUG_MODE_CHAR,
}

DISCARDED_CHARS = {" "}


MemoryValue = (
	int
	| float
	| bool
	| str
	| bytes
	| list[Any]
	| tuple[Any, ...]
	| set[Any]
	| dict[Any, Any]
	| None
)


UnsetType = type(None)


class TargetKind(SupportsContains):
	Memory = "&"
	Register = "$"
	Stream = ":"


@dataclass
class Target:
	kind: TargetKind
	id: int

	def __repr__(self):
		return f"\x1b[37m{self.kind.name}\x1b[39m[\x1b[36m{self.id}\x1b[39m]"

	def clone(self) -> Self:
		return type(self)(self.kind, self.id)

	# Implementation detail
	@classmethod
	def default(cls):
		return cls(TargetKind.Memory, NULL)


class MacroKind(SupportsContains):
	Debug = "d"


class AssignKind(SupportsContains):
	String = "s"
	Literal = "l"


class Mode(Enum):
	Normal = auto()  # do stuff (operations, ...)
	Select = auto()  # select target of future assignment
	Assign = auto()  # write the value of the assignment


# Non-sugar modes (i.e. `^mode` syntax)
NS_MODES = {
	"n": Mode.Normal,
	**{atchar: Mode.Assign for atchar in AssignKind.values()},
}


STREAM_IDS = {"null": -1, "stdout": 0, "stderr": 1}

stream_endpoints = defaultdict(
	lambda: sys.stdout,
	{
		0: sys.stdout,
		1: sys.stderr,
	},
)


class BufferMap(dict[KT, StringIO], ABC):
	def add(self, id: KT) -> KT:
		"""
		Create a new StringIO stream and return the key ID.
		"""

		if id in self.keys():
			raise ValueError(f"stream {id} already exists")

		self[id] = StringIO()
		return id

	def reset_buffer(self, id: KT) -> None:
		"""
		Reset the stream of key `id`.
		"""

		stream = self.get(id)

		if stream is None:
			raise ValueError(f"{id}: no stream")

		self[id] = StringIO()


class StreamMap(BufferMap[int]):
	@classmethod
	def new(cls) -> Self:
		stream_map = cls()

		for name in STREAM_IDS.values():
			BufferMap[int].add(stream_map, name)

		return stream_map

	def add(self) -> int:
		fd = len(self)
		return super().add(fd)


class ModeBufferMap(BufferMap[Mode]):
	@classmethod
	def new(cls) -> Self:
		buffer_map = cls()

		for mode in Mode:
			BufferMap[Mode].add(buffer_map, mode)

		return buffer_map


@dataclass
class TypeDef(ABC):
	type: type[MemoryValue]


class ConstTypeDef(TypeDef):
	pass


@dataclass
class VarTypeDef(TypeDef):
	line_number: int
	spos: int
	epos: int


@dataclass
class VMState:
	memory: list[Any] = field(default_factory=lambda: [None] * MEMORY_MAX_ADDR)
	typing: list[type[MemoryValue]] = field(
		default_factory=lambda: [type(None)] * MEMORY_MAX_ADDR
	)

	streams: StreamMap = field(default_factory=StreamMap.new)
	stdout: int = field(init=False)

	def __post_init__(self) -> None:
		self.stdout = STREAM_IDS["stdout"]


@dataclass
class instruction(Generic[*Ts]):
	mnemonic: Callable[[VMState, *Ts], VMState]
	operands: tuple[*Ts]

	def run(self, ms: VMState) -> VMState:
		return self.mnemonic(ms, *self.operands)

	@staticmethod
	def prettify(value: Any) -> str:
		c = 6 if isinstance(value, (int, str)) else 7
		return f" \x1b[3{c}m{value!r}\x1b[39m"

	def __repr__(self) -> str:
		mnemonic = f"\x1b[31m{self.mnemonic.__name__.lower()}\x1b[39m"

		operands = [self.prettify(operand) for operand in self.operands]
		# Using ", ".join(...) makes operands of type unknown??
		operands_str = str.join(format(",", "^"), operands)

		return f"{mnemonic:<12} {operands_str}"

	def __rshift__(self, other: "instruction[*tuple[Any, ...]]") -> "instruction[*Ts]":
		def _(ms: VMState, *operands: *Ts) -> VMState:
			return other.mnemonic(self.mnemonic(ms, *operands), *other.operands)

		return mnemonic(_)(*self.operands)


class mnemonic(Generic[*Ts]):
	def __init__(self, mnemonic_func: Callable[[VMState, *Ts], VMState]) -> None:
		self.func = mnemonic_func
		self.args = len(inspect.signature(mnemonic_func).parameters) - 1

	def __call__(self, *operands: *Ts) -> instruction[*Ts]:
		return instruction(self.func, operands)
