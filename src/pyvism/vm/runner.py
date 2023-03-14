from typing import TextIO

from pyvism.compiler.compiler import compile
from pyvism.errsys.tools import report_abortion
from pyvism.frontend.map import CompilationTarget
from pyvism.vm.vm import VM
from result import Err
from result import Ok


def run(file: TextIO) -> int:
    """
    Convenient function to run a Vism file.
    """

    vm = VM()

    match compile(file, CompilationTarget.Bytecode):
        case Ok(bytecode):
            vm.run(bytecode)
            return 0
        case Err(errors):
            for error in errors:
                error.throw()
            report_abortion()
            return 1
