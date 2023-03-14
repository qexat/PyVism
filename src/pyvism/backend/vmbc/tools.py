"""
Tools to build VM ByteCode instructions.
"""
import inspect
import sys
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from io import StringIO
from typing import Any
from typing import Generic
from typing import Self
from typing import TextIO
from typing import TypeVarTuple

from pyvism.constants import STREAM_IDS

Ts = TypeVarTuple("Ts")


class StreamMap(dict[int, TextIO]):
    @classmethod
    def new(cls, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> Self:
        stream_map = cls()

        stream_map[0] = stdout
        stream_map[1] = stderr

        return stream_map


@dataclass
class VMState:
    stdout_endpoint: TextIO
    stderr_endpoint: TextIO
    devnull_endpoint: TextIO = field(default_factory=StringIO)
    memory: dict[str, Any] = field(default_factory=dict)
    streams: StreamMap = field(init=False)
    stdout_fd: int = field(init=False)

    def __post_init__(self) -> None:
        self.streams = StreamMap.new(self.stdout_endpoint, self.stderr_endpoint)
        self.stdout_fd = STREAM_IDS["stdout"]


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
