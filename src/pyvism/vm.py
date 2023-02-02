import inspect
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVarTuple

from pyvism.constants import MEMORY_MAX_ADDR, NULL, REGISTER_MAX_ADDR
from pyvism.runtime.builtins import (
    STREAM_IDS,
    MemoryValue,
    StreamMap,
    Target,
    TargetKind,
)


Ts = TypeVarTuple("Ts")


class VM:
    @dataclass
    class State:
        memory: list[Any] = field(default_factory=lambda: [None] * MEMORY_MAX_ADDR)
        typing: list[type[MemoryValue]] = field(
            default_factory=lambda: [type(None)] * MEMORY_MAX_ADDR
        )
        registers: list[int] = field(
            default_factory=lambda: list(range(REGISTER_MAX_ADDR))
        )

        streams: StreamMap = field(default_factory=StreamMap.new)
        stdout: int = field(init=False)

        def __post_init__(self) -> None:
            self.stdout = STREAM_IDS["stdout"]

    def __init__(self) -> None:
        if MEMORY_MAX_ADDR < REGISTER_MAX_ADDR:
            raise RuntimeError("illegal register max address")

        self.state = VM.State()

    def run(self, bytecode: list["instruction[*tuple[Any, ...]]"]) -> None:
        for instr in bytecode:
            self.state = instr.run(self.state)


@dataclass
class instruction(Generic[*Ts]):
    mnemonic: Callable[[VM.State, *Ts], VM.State]
    operands: tuple[*Ts]

    def run(self, ms: VM.State) -> VM.State:
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
        def _(ms: VM.State, *operands: *Ts) -> VM.State:
            return other.mnemonic(self.mnemonic(ms, *operands), *other.operands)

        return mnemonic(_)(*self.operands)


class mnemonic(Generic[*Ts]):
    def __init__(self, mnemonic_func: Callable[[VM.State, *Ts], VM.State]) -> None:
        self.func = mnemonic_func
        self.args = len(inspect.signature(mnemonic_func).parameters) - 1

    def __call__(self, *operands: *Ts) -> instruction[*Ts]:
        return instruction(self.func, operands)


class InstructionSet:
    @staticmethod
    def _mov_memory(ms: VM.State, address: int, value: MemoryValue) -> VM.State:
        slot_type = ms.typing[address]
        value_type = type(value)

        if slot_type is not type(None) and not isinstance(value, slot_type):
            raise TypeError(
                f"address {address}: "
                f"expected type {slot_type.__name__}, got {value_type.__name__}"
            )

        ms.memory[address] = value
        ms.typing[address] = value_type

        return ms

    @staticmethod
    def _mov_register(ms: VM.State, address: int, value: int) -> VM.State:
        if not (0 <= value < MEMORY_MAX_ADDR):
            raise ValueError(f"{hex(value)} is not a valid memory address")

        ms.registers[address] = value

        return ms

    @mnemonic
    @staticmethod
    def mov(ms: VM.State, target: Target, value: Any) -> VM.State:
        if target.address == NULL:
            raise RuntimeError("attempted to write to an invalid address")

        match target.kind:
            case TargetKind.Memory:
                return InstructionSet._mov_memory(ms, target.address, value)
            case TargetKind.Register:
                return InstructionSet._mov_register(ms, target.address, value)
            case _:
                raise ValueError(f"{target}: bad instruction 'mov'")

    @staticmethod
    def _add(l: Any, r: Any) -> Any:
        supports_add = (int, float, bool, str, bytes, list, tuple)  # type: ignore
        if isinstance(l, supports_add) and isinstance(r, supports_add):
            return l + r  # type: ignore
        elif isinstance(l, set) and isinstance(r, set):
            return l | r  # type: ignore

    @mnemonic
    @staticmethod
    def add(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr] = l + r

        return ms

    @staticmethod
    def _sub(l: Any, r: Any) -> Any:
        if isinstance(l, (int, set)) and isinstance(r, (int, set)):
            return l - r  # type: ignore
        elif isinstance(l, str) and isinstance(r, str):
            return l.replace(r, "")
        elif isinstance(l, (list, tuple)) and isinstance(r, (list, tuple)):
            return type(l)(v for v in l if v not in r)  # type: ignore

    @mnemonic
    @staticmethod
    def sub(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr] = InstructionSet._sub(l, r)

        return ms

    @mnemonic
    @staticmethod
    def mul(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr] = l * r

        return ms

    @mnemonic
    @staticmethod
    def intdiv(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr] = l // r

        return ms

    @mnemonic
    @staticmethod
    def modulo(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr] = l % r

        return ms

    @mnemonic
    @staticmethod
    def divmod(ms: VM.State, lsource: Target, rsource: Target) -> VM.State:
        laddr, raddr = lsource.address, rsource.address
        l, r = ms.memory[laddr], ms.memory[raddr]

        ms.memory[laddr], ms.memory[raddr] = divmod(l, r)

        return ms

    @mnemonic
    @staticmethod
    def write(ms: VM.State, fd: int, value: str) -> VM.State:
        stream = ms.streams.get(fd)

        if stream is None:
            raise ValueError(f"file is either closed or does not exist")

        stream.write(value)

        return ms

    @mnemonic
    @staticmethod
    def flush(ms: VM.State) -> VM.State:
        stdout = ms.streams.get(ms.stdout)

        if stdout is None:
            raise ValueError("stdout is uninitialized")

        sys.stdout.write(stdout.getvalue())
        sys.stdout.flush()

        ms.streams.reset_buffer(ms.stdout)

        return ms

    @mnemonic
    @staticmethod
    def print(ms: VM.State, source: Target) -> VM.State:
        addr = source.address
        v = ms.memory[addr]

        if v is not None:
            ms = (
                InstructionSet.write(ms.stdout, str(v)) >> InstructionSet.flush()
            ).run(ms)

        return ms


def type_compat_error(op: str, type1: type, type2: type):
    raise TypeError(f"{op}: incompatible types {type1.__name__} and {type2.__name__}")


instruction_map: dict[str, mnemonic[*tuple[Any, ...]]] = {
    "+": InstructionSet.add,
    "-": InstructionSet.sub,
    "×": InstructionSet.mul,
    "/": InstructionSet.intdiv,
    "%": InstructionSet.modulo,
    "÷": InstructionSet.divmod,
    "p": InstructionSet.print,
    "f": InstructionSet.flush,
}

op_type_combinations: dict[mnemonic[*tuple[Any, ...]], set[tuple[type, ...]]] = {
    InstructionSet.add: {
        (int, int),
        (int, bool),
        (float, float),
        (float, int),
        (float, bool),
        (str, str),
        (bytes, bytes),
        (list, list),
        (tuple, tuple),
        (set, set),
    },
    InstructionSet.sub: {
        (int, int),
        (str, str),
        (list, list),
        (set, set),
        (tuple, tuple),
    },
    InstructionSet.mul: {
        (int, int),
        (int, bool),
        (int, str),
        (float, float),
        (float, int),
        (float, bool),
        (str, int),
        (str, bool),
        (bytes, int),
        (bytes, bool),
        (list, int),
        (list, bool),
        (tuple, int),
        (tuple, bool),
    },
    InstructionSet.intdiv: {(int, int), (int, bool)},
    InstructionSet.modulo: {(int, int), (int, bool)},
    InstructionSet.divmod: {(int, int), (int, bool)},
}
