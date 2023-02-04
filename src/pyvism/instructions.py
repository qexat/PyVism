from builtins import divmod as _divmod
from typing import Any

from pyvism.constants import NULL
from pyvism.runtime.builtins import (
    Target,
    TargetKind,
    VMState,
    mnemonic,
    stream_endpoints,
)

# NOTE: Do not from ... import ... this module
# Use instruction.<something> to access an object


@mnemonic
def mov(ms: VMState, target: Target, value: Any) -> VMState:
    if target.id == NULL:
        raise RuntimeError("attempted to write to an invalid address")

    if target.kind is not TargetKind.Memory:
        raise ValueError(f"{target}: bad instruction 'mov'")

    ms.memory[target.id] = value

    return ms


def _add(l: Any, r: Any) -> Any:
    supports_add = (int, float, bool, str, bytes, list, tuple)  # type: ignore
    if isinstance(l, supports_add) and isinstance(r, supports_add):
        return l + r  # type: ignore
    elif isinstance(l, set) and isinstance(r, set):
        return l | r  # type: ignore


@mnemonic
def add(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
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
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = _sub(l, r)

    return ms


@mnemonic
def mul(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l * r

    return ms


@mnemonic
def intdiv(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l // r

    return ms


@mnemonic
def modulo(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l % r

    return ms


@mnemonic
def divmod(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
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
    stream = ms.streams.get((fd := target.id))

    if stream is None:
        raise ValueError(f"stream {stream!r} does not exist")

    endpoint = stream_endpoints[fd]

    endpoint.write(stream.getvalue())
    endpoint.flush()

    ms.streams.reset_buffer(fd)

    return ms


@mnemonic
def print(ms: VMState, source: Target) -> VMState:
    addr = source.id
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
