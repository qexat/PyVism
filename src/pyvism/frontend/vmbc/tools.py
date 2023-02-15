import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVarTuple

from pyvism.constants import STREAM_IDS
from pyvism.compiler.tools import BufferMap

Ts = TypeVarTuple("Ts")


class StreamMap(BufferMap[int]):
	@classmethod
	def new(cls) -> "StreamMap":
		stream_map = cls()

		for id in STREAM_IDS.values():
			BufferMap[int].add(stream_map, id)

		return stream_map

	def add(self) -> int:
		fd = len(self)
		return super().add(fd)


@dataclass
class VMState:
	memory: dict[str, Any] = field(default_factory=dict)
	streams: StreamMap = field(default_factory=StreamMap.new)
	stdout: int = field(init=False)

	def __post_init__(self) -> None:
		self.stdout = STREAM_IDS["stdout"]


@dataclass
class instruction(Generic[*Ts]):
	mnemonic: Callable[[VMState, *Ts], VMState]
	operands: tuple[*Ts]

	def __rshift__(self, other: "instruction[*tuple[Any, ...]]") -> "instruction[*Ts]":
		@mnemonic
		def _(ms: VMState, *operands: *Ts) -> VMState:
			return other.mnemonic(self.mnemonic(ms, *operands), *other.operands)

		return _(*self.operands)

	def run(self, ms: VMState) -> VMState:
		return self.mnemonic(ms, *self.operands)


@dataclass
class mnemonic(Generic[*Ts]):
	func: Callable[[VMState, *Ts], VMState]
	nb_args: int = field(init=False)

	def __post_init__(self) -> None:
		self.nb_args = len(inspect.signature(self.func).parameters) - 1

	def __call__(self, *operands: *Ts) -> instruction[*Ts]:
		return instruction(self.func, operands)


AnyInstruction = instruction[*tuple[Any, ...]]
