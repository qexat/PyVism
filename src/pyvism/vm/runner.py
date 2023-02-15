from typing import TextIO

from result import Err, Ok

from pyvism.compiler.compiler import compile
from pyvism.errsys.tools import report_abortion
from pyvism.frontend.map import CompilationTarget
from pyvism.vm.vm import VM


def run(file: TextIO) -> int:
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
