"""
Contains a simple enum that lists the backends.
"""
from pyvism.backend import vmbc
from pyvism.py_utils import MapLikeEnum


class CompilationTarget(MapLikeEnum):
    Bytecode = vmbc.backend
