from pyvism.frontend import vmbc
from pyvism.py_utils import MapLikeEnum


class CompilationTarget(MapLikeEnum):
	Bytecode = vmbc.frontend
