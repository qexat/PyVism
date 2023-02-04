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


@mnemonic
def add(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l + r

    return ms


@mnemonic
def union(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l | r

    return ms


@mnemonic
def sub(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l - r

    return ms


@mnemonic
def subst(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = l.replace(r, "")

    return ms


@mnemonic
def seqdiff(ms: VMState, lsource: Target, rsource: Target) -> VMState:
    laddr, raddr = lsource.id, rsource.id
    l, r = ms.memory[laddr], ms.memory[raddr]

    ms.memory[laddr] = type(l)(v for v in l if v not in r)

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


# Base OP => supported type combinations
# For each: type combination => specialized mnemonic or None (None = take the base OP)
op_type_specialization: dict[
    mnemonic[*tuple[Any, ...]],
    dict[tuple[type, ...], mnemonic[*tuple[Any, ...]] | None],
] = {
    add: {
        (int, int): None,
        (int, bool): None,
        (float, float): None,
        (float, int): None,
        (float, bool): None,
        (str, str): None,
        (bytes, bytes): None,
        (list, list): None,
        (tuple, tuple): None,
        (set, set): union,
    },
    sub: {
        (int, int): None,
        (str, str): subst,
        (list, list): seqdiff,
        (set, set): None,
        (tuple, tuple): seqdiff,
    },
    mul: {
        (int, int): None,
        (int, bool): None,
        (int, str): None,
        (float, float): None,
        (float, int): None,
        (float, bool): None,
        (str, int): None,
        (str, bool): None,
        (bytes, int): None,
        (bytes, bool): None,
        (list, int): None,
        (list, bool): None,
        (tuple, int): None,
        (tuple, bool): None,
    },
    intdiv: {
        (int, int): None,
        (int, bool): None,
    },
    modulo: {
        (int, int): None,
        (int, bool): None,
    },
    divmod: {
        (int, int): None,
        (int, bool): None,
    },
}
