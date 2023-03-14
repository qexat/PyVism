"""
PyVism Virtual Machine.
"""
import contextlib
import sys
from io import StringIO
from os import linesep
from typing import TextIO

from pyvism.backend.vmbc.tools import AnyInstruction
from pyvism.backend.vmbc.tools import VMState
from pyvism.py_utils import bold
from pyvism.py_utils import color
from pyvism.py_utils import eprint


class VM:
    def __init__(
        self,
        stdout: TextIO = sys.stdout,
        stderr: TextIO = sys.stderr,
        *,
        strict_mode: bool = True,
    ) -> None:
        self.state = VMState(stdout, stderr)

        self.strict_mode = strict_mode

    def run(self, bytecode: list[AnyInstruction]) -> None:
        with contextlib.redirect_stdout(self.state.stdout_endpoint):
            for instr in bytecode:
                try:
                    self.state = instr.run(self.state)
                except Exception as e:
                    eprint(create_exception_message(e), sep=linesep)
                    if self.strict_mode:
                        return None


def create_exception_message(e: Exception) -> str:
    message = StringIO()

    message.write(f"Runtime exception:{linesep}")
    message.write(f"  {type(e).__name__}: {e}{linesep}")
    message.write(f"[Illegal operation]")

    return bold(color(message.getvalue(), 1))
