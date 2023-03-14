"""
Tools to build backend objects.
"""
from collections.abc import Callable
from typing import Generic
from typing import LiteralString
from typing import TypeVar

from pyvism.frontend.tools import IRI


T = TypeVar("T")


class TargetBackEnd(Generic[T]):
    def __init__(self, backend: Callable[[list[IRI[LiteralString]]], list[T]]) -> None:
        self.backend = backend

    def __call__(self, ir: list[IRI[LiteralString]]) -> list[T]:
        return self.backend(ir)
