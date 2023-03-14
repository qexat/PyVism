"""
Compiler macros. They are a special piece of Vism that are executed
during compilation rather than runtime.
"""
from shutil import get_terminal_size

from pyvism.compiler.tools import CompilerState
from pyvism.parser.tools import FileHandler
from pyvism.parser.tools import MacroKind
from pyvism.py_utils import light


def debug(file: FileHandler, state: CompilerState) -> None:
    """
    Prints the IR instructions of the code that was compiled since then.
    """

    cols, _ = get_terminal_size((80, 24))

    print(light(" DEBUG ".center(cols, "=")))
    for instr in state.ir:
        print(instr)
    print(light("+" * cols))


macro_map = {
    MacroKind.Debug: debug,
}
