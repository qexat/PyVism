"""
Contains a simple enum that lists the front-ends.
"""
from pyvism.frontend import vmbc
from pyvism.py_utils import MapLikeEnum


class CompilationTarget(MapLikeEnum):
    Bytecode = vmbc.frontend
