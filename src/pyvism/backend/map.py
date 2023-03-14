"""
Contains a simple enum that lists the front-ends.
"""
from pyvism.backend import vmbc
from pyvism.py_utils import MapLikeEnum


class CompilationTarget(MapLikeEnum):
    Bytecode = vmbc.frontend
