"""
Universal version of the REPL.
"""
from io import StringIO

from pyvism.constants import CMD_MODE_CHAR
from pyvism.py_utils import write_out
from pyvism.repl.tools import BaseREPL


class REPL(BaseREPL):
	def __post_init__(self, **_: bool) -> None:
		pass

	@property
	def is_command_mode(self) -> bool:
		return self.buffer.getvalue().startswith(CMD_MODE_CHAR)

	def _strip_bang(self) -> None:
		cmd_buffer = self.buffer.getvalue()[1:]
		self.buffer = StringIO()
		self.buffer.write(cmd_buffer)

	def write(self, string: str) -> None:
		"""
		Handy function to write the input to the buffer + stdout.
		"""

		write_out(string)
		self.buffer.write(string)

	def start(self) -> None:
		"""
		Main function -- Start the REPL.
		"""

		while True:
			self.buffer.write((input_value := input()))

			if input_value:
				if self.is_command_mode:
					self._strip_bang()
					self.run_command()
				else:
					self.eval_input()
			self.reset()
