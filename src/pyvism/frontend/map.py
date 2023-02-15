from pyvism.frontend import vmbc
from pyvism.py_utils import SupportsContains


class CompilationTarget(SupportsContains):
	Bytecode = vmbc.frontend
