"""
Compiler macros. They are a special piece of Vism that are executed
during compilation rather than runtime.
"""
from pyvism.compiler.tools import CompilerState
from pyvism.parser.tools import FileHandler
from pyvism.parser.tools import MacroKind


def debug(_: FileHandler, state: CompilerState) -> None:
	"""
	Prints the IR instructions of the code that was compiled since then.
	"""

	print("\x1b[2m" + " DEBUG ".center(80, "=") + "\x1b[22m")
	for instr in state.ir:
		print(instr)
	print("\x1b[2m" + "=" * 80 + "\x1b[22m")


macro_map = {
	MacroKind.Debug: debug,
}
