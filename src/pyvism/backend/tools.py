"""
Tools to build front-end objects.
"""
from collections.abc import Callable
from typing import Generic
from typing import LiteralString
from typing import TypeVar

from pyvism.frontend.tools import IRI


T = TypeVar("T")


class TargetFrontEnd(Generic[T]):
    def __init__(self, frontend: Callable[[list[IRI[LiteralString]]], list[T]]) -> None:
        self.frontend = frontend

    def __call__(self, ir: list[IRI[LiteralString]]) -> list[T]:
        return self.frontend(ir)
