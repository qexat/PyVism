"""
Tools to define Intermediate Representation Instructions.
"""
from collections.abc import Callable
from io import StringIO
from types import UnionType
from typing import Any
from typing import Generic
from typing import Literal
from typing import LiteralString
from typing import overload
from typing import TypeVar
from typing import TypeVarTuple

from pyvism.compiler.types import MemoryValue
from pyvism.compiler.types import UnsetType

OP_SYMBOL = TypeVar("OP_SYMBOL", bound=LiteralString)
OP_NAME = TypeVar("OP_NAME", bound=LiteralString)
SIM_OP_NAME = TypeVar("SIM_OP_NAME", bound=LiteralString)

# The utensils for a certain amount of type tomfoolery
Ts = TypeVarTuple("Ts")
T_Dest = TypeVar("T_Dest")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")


class IRI(Generic[OP_NAME]):
    def __init__(
        self,
        mnemonic: "IRMnemonic[OP_NAME, Any, *tuple[Any, ...]]",
        dest: Any,
        dest_type: type,
        args: tuple[Any, ...],
        args_types: tuple[type, ...],
    ) -> None:
        self.mnemonic = mnemonic
        self.dest = dest
        self.dest_type = dest_type
        self.args = args
        self.args_types = args_types

    def __repr__(self) -> str:
        operands = StringIO()
        if self.dest is not None:
            operands.write(f"{self.dest}, ")
        operands.write(", ".join(map(str, self.args)))

        return " ".join((self.mnemonic.name, operands.getvalue()))


class IRMnemonic(Generic[OP_NAME, T_Dest, *Ts]):
    _op_id = 0

    def __init__(self, name: OP_NAME, psi: Callable[[*Ts], T_Dest]) -> None:
        self.name = name
        self.__psi = psi
        _dest_kind: type[T_Dest] = psi.__annotations__["return"]
        _args_kinds: tuple[*Ts] = tuple(kind for k, kind in psi.__annotations__.items() if k != "return")  # type: ignore
        self.dest_kind = _dest_kind
        self.args_kinds = _args_kinds
        self.nb_ident_args = len(
            [v for v in psi.__annotations__.values() if v is IdentifierLike],
        )
        self.id = IRMnemonic._op_id
        IRMnemonic._op_id += 1

    @overload
    def __call__(
        self: "IRMnemonic[OP_NAME, T_Dest, T1]",
        dest: T_Dest,
        dest_type: type,
        args: tuple[T1],
        args_types: tuple[type],
    ) -> IRI[OP_NAME]:
        ...

    @overload
    def __call__(
        self: "IRMnemonic[OP_NAME, T_Dest, T1, T2]",
        dest: T_Dest,
        dest_type: type,
        args: tuple[T1, T2],
        args_types: tuple[type, type],
    ) -> IRI[OP_NAME]:
        ...

    @overload
    def __call__(
        self: "IRMnemonic[OP_NAME, T_Dest, T1, T2, T3]",
        dest: T_Dest,
        dest_type: type,
        args: tuple[T1, T2, T3],
        args_types: tuple[type, type, type],
    ) -> IRI[OP_NAME]:
        ...

    def __call__(
        self,
        dest: T_Dest,
        dest_type: type,
        args: tuple[*Ts],
        args_types: tuple[type, ...],
    ) -> IRI[OP_NAME]:
        return IRI(self.untyped_copy(), dest, dest_type, args, args_types)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: "AnyIRMnemonic") -> bool:
        return self.name == other.name

    def untyped_copy(self) -> "IRMnemonic[OP_NAME, Any, *tuple[Any, ...]]":
        return IRMnemonic(self.name, self.__psi)  # type: ignore

    def similar(self, copy_name: SIM_OP_NAME) -> "IRMnemonic[SIM_OP_NAME, T_Dest, *Ts]":
        return IRMnemonic(copy_name, self.__psi)


AnyIRMnemonic = IRMnemonic[LiteralString, Any, *tuple[Any, ...]]


def mnemonic(
    name: OP_NAME,
) -> Callable[[Callable[[*Ts], T_Dest]], IRMnemonic[OP_NAME, T_Dest, *Ts]]:
    def decorator(psi: Callable[[*Ts], T_Dest]) -> IRMnemonic[OP_NAME, T_Dest, *Ts]:
        return IRMnemonic(name, psi)

    return decorator


class PseudoMnemonic(Generic[OP_SYMBOL, T_Dest, *Ts]):
    @property
    def symbol(self):
        return self.__symbol

    @property
    def overloads(self):
        return self.__overloads

    def get_identifier_number(self) -> int:
        return len([kind for kind in self.kinds if kind is IdentifierLike])

    def __init__(
        self,
        symbol: OP_SYMBOL,
        overloads: dict[
            IRMnemonic[LiteralString, T_Dest, *Ts],
            list[tuple[type | UnionType, ...]],
        ],
    ) -> None:
        self.__symbol = symbol
        self.__overloads = {
            signature: overload
            for overload, signatures in overloads.items()
            for signature in signatures
        }
        _first_overload = list(overloads.keys())[0]
        self.dest_kind = _first_overload.dest_kind
        self.args_kinds = _first_overload.args_kinds
        self.kinds = (self.dest_kind, *self.args_kinds)

    def get_overload(
        self,
        received_signature: tuple[type, ...],
    ) -> IRMnemonic[LiteralString, T_Dest, *Ts] | None:
        for signature, overload in self.overloads.items():
            if len(received_signature) != len(signature):
                # Every overload has the same number of args, so if one
                # does not have the same as `types`, none will
                return None

            for i, arg_t in enumerate(signature):
                # MemoryValue <=> Any, UnsetType <=> None
                if arg_t in {MemoryValue, UnsetType}:
                    continue

                if received_signature[i] is not arg_t:
                    break
            else:  # no loop break => we found the overload
                return overload

        return None


class IdentifierLike(str):
    code: Literal[0] = 0


class StreamIDLike(int):
    code: Literal[1] = 1
