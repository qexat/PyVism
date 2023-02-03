from builtins import divmod as _divmod
from typing import Any

from pyvism.constants import MEMORY_MAX_ADDR, NULL
from pyvism.runtime.builtins import (
    MemoryValue,
    Target,
    TargetKind,
    VMState,
    mnemonic,
    stream_endpoints,
)

# NOTE: Do not from ... import ... this module
# Use instruction.<something> to access an object


def _mov_memory(ms: VMState, address: int, value: MemoryValue) -> VMState:
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


def _mov_register(ms: VMState, address: int, value: int) -> VMState:
    if not (0 <= value < MEMORY_MAX_ADDR):
        raise ValueError(f"{hex(value)} is not a valid memory address")

    ms.registers[address] = value

    return ms


@mnemonic
def mov(ms: VMState, target: Target, value: Any) -> VMState:
    if target.address == NULL:
        raise RuntimeError("attempted to write to an invalid address")

    match target.kind:
        case TargetKind.Memory:
            return _mov_memory(ms, target.address, value)
        case TargetKind.Register:
            return _mov_register(ms, target.address, value)
        case _:
            raise ValueError(f"{target}: bad instruction 'mov'")


def _add(l: Any, r: Any) -> Any:
    supports_add = (int, float, bool, str, bytes, list, tuple)  # type: ignore
    if isinstance(l, supports_add) and isinstance(r, supports_add):
        return l + r  # type: ignore
    elif isinstance(l, set) and isinstance(r, set):
        return l | r  # type: ignore


@mnemonic
def add(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = _add(l, r)

    return ms


def _sub(l: Any, r: Any) -> Any:
    if isinstance(l, (int, set)) and isinstance(r, (int, set)):
        return l - r  # type: ignore
    elif isinstance(l, str) and isinstance(r, str):
        return l.replace(r, "")
    elif isinstance(l, (list, tuple)) and isinstance(r, (list, tuple)):
        return type(l)(v for v in l if v not in r)  # type: ignore


@mnemonic
def sub(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = _sub(l, r)

    return ms


@mnemonic
def mul(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l * r

    return ms


@mnemonic
def intdiv(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l // r

    return ms


@mnemonic
def modulo(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l % r

    return ms


@mnemonic
def divmod(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.address, rsource.address
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr], ms.memory[raddr] = _divmod(l, r)

    return ms


@mnemonic
def write(ms: VMState, fd: int, value: str) -> VMState:
    stream = ms.streams.get(fd)

    if stream is None:
        raise ValueError(f"file is either closed or does not exist")

    stream.write(value)

    return ms


@mnemonic
def flush(ms: VMState, target: Target) -> VMState:
    stream = ms.streams.get((fd := target.address))

    if stream is None:
        raise ValueError(f"stream {stream!r} does not exist")

    endpoint = stream_endpoints[fd]

    endpoint.write(stream.getvalue())
    endpoint.flush()

    ms.streams.reset_buffer(fd)

    return ms


@mnemonic
def print(ms: VMState, source: Target) -> VMState:
    addr = source.address
    v = ms.memory[addr]

    if v is not None:
        ms = (
            write(ms.stdout, str(v)) >> flush(Target(TargetKind.Stream, ms.stdout))
        ).run(ms)

    return ms


char_map: dict[str, mnemonic[*tuple[Any, ...]]] = {
    "+": add,
    "-": sub,
    "×": mul,
    "/": intdiv,
    "%": modulo,
    "÷": divmod,
    "p": print,
    "f": flush,
}

op_type_combinations: dict[mnemonic[*tuple[Any, ...]], set[tuple[type, ...]]] = {
    add: {
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
    sub: {
        (int, int),
        (str, str),
        (list, list),
        (set, set),
        (tuple, tuple),
    },
    mul: {
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
    intdiv: {(int, int), (int, bool)},
    modulo: {(int, int), (int, bool)},
    divmod: {(int, int), (int, bool)},
}