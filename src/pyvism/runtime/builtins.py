from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from io import StringIO
from re import compile as re_compile
from typing import Any, TypeVar

from pyvism.constants import NULL

__all__ = (
    "ADDRESS_REGEXP",
    "PRGM_MODE_CHAR",
    "DEBUG_MODE_CHAR",
    "ESCAPABLE_CHARS",
    "MemoryValue",
    "TargetKind",
    "target_kind_map",
    "Target",
    "MacroKind",
    "macro_kind_map",
    "AssignType",
    "assign_type_map",
    "Mode",
    "NS_MODES",
    "STREAM_IDS",
    "BufferMap",
    "StreamMap",
    "ModeBufferMap",
    "TypeDef",
    "ConstTypeDef",
    "VarTypeDef",
)


KT = TypeVar("KT")


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


class TargetKind(Enum):
    Memory = auto()
    Register = auto()
    Stream = auto()


target_kind_map = {
    "&": TargetKind.Memory,
    "$": TargetKind.Register,
    ":": TargetKind.Stream,
}


@dataclass
class Target:
    kind: TargetKind
    address: int

    def __repr__(self):
        return f"\x1b[37m{self.kind.name}\x1b[39m[\x1b[36m{self.address}\x1b[39m]"

    def clone(self) -> "Target":
        return type(self)(self.kind, self.address)

    # Implementation detail
    @classmethod
    def default(cls):
        return cls(TargetKind.Memory, NULL)


class MacroKind(Enum):
    Debug = auto()


macro_kind_map = {
    "d": MacroKind.Debug,
}


class AssignType(Enum):
    String = auto()
    Literal = auto()


assign_type_map = {
    "s": AssignType.String,
    "l": AssignType.Literal,
}


class Mode(Enum):
    Normal = auto()  # do stuff (operations, ...)
    Select = auto()  # select target of future assignment
    Assign = auto()  # write the value of the assignment
    Macro = auto()  # ?<char> macro mode


# Non-sugar modes (i.e. `^mode` syntax)
NS_MODES = {
    "n": Mode.Normal,
    **{atchar: Mode.Assign for atchar in assign_type_map.keys()},
}


STREAM_IDS = {"null": -1, "stdout": 0, "stderr": 1}


class BufferMap(dict[KT, StringIO], ABC):
    @abstractmethod
    def get(self, id: KT) -> StringIO | None:
        """
        Get the stream of key `id`.
        """
        pass

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
    def new(cls) -> "StreamMap":
        stream_map = cls()

        for name in STREAM_IDS.values():
            BufferMap[int].add(stream_map, name)

        return stream_map

    def get(self, fd: int) -> StringIO | None:
        if not (0 <= fd < len(self)):
            return None
        return self[fd]

    def add(self) -> int:
        fd = len(self)
        return super().add(fd)


class ModeBufferMap(BufferMap[Mode]):
    @classmethod
    def new(cls) -> "ModeBufferMap":
        buffer_map = cls()

        for mode in Mode:
            BufferMap[Mode].add(buffer_map, mode)

        return buffer_map

    def get(self, mode: Mode):
        if not mode in Mode:
            return None
        return self[mode]


@dataclass
class TypeDef_:
    type: type[MemoryValue]
    line: int = 1
    spos: int = 0
    epos: int = 0


@dataclass
class TypeDef(ABC):
    type: type[MemoryValue]


class ConstTypeDef(TypeDef):
    pass


@dataclass
class VarTypeDef(TypeDef):
    line: int
    spos: int
    epos: int
