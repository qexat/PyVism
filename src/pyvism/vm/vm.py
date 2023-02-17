"""
PyVism Virtual Machine.
"""
import contextlib
import sys
from os import linesep
from typing import TextIO

from pyvism.frontend.vmbc.tools import AnyInstruction
from pyvism.frontend.vmbc.tools import VMState


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
					print(
						f"\x1b[1;31mRuntime exception:",
						f"  {type(e).__name__}: {e}",
						f"{linesep}[Illegal operation]\x1b[22;39m",
						sep=linesep,
						file=sys.stderr,
					)
					if self.strict_mode:
						return None
