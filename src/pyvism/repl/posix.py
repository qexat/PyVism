# pyright: reportUninitializedInstanceVariable=false
"""
REPL for POSIX-based systems.
"""
from io import StringIO

from pyvism.constants import REPL_HISTORY_FILE
from pyvism.errsys.tools import report_panic
from pyvism.py_utils import color
from pyvism.py_utils import get_key
from pyvism.py_utils import light
from pyvism.py_utils import MagicKey
from pyvism.py_utils import read_file_lines
from pyvism.py_utils import ring_bell
from pyvism.py_utils import unwrite_out
from pyvism.py_utils import write_file_lines
from pyvism.py_utils import write_out
from pyvism.py_utils import write_out_new_line
from pyvism.repl.tools import BaseREPL


class REPL(BaseREPL):
	def __post_init__(
		self,
		**kwargs: bool,
	) -> None:
		self.history = read_file_lines(REPL_HISTORY_FILE)
		self.history.reverse()
		self.history_pos = 0
		self.STORE_INVALID_INPUT = kwargs.get("store_invalid_input", False)

		self.last_entered = ""
		self.is_command_mode: bool = False
		self.pos = 0

	def highlight(self, string: str) -> str:
		"""
		Basic inline syntax highlighting of the live input.
		"""

		final_string = string
		if string in {"&", "$", "^"}:
			final_string = color(string, 1)
		elif string.isdigit():
			final_string = color(string, 6)
		return final_string

	def write(self, string: str) -> None:
		"""
		Handy function to write the live input to the buffer + stdout.
		"""

		write_out(self.highlight(string))
		self.buffer.write(string)
		self.last_entered = string
		self.pos += len(string)

	def unwrite(self) -> None:
		"""
		Handy function that essentially handles backspaces.
		"""

		unwrite_out(len(self.last_entered))
		new_buffer_value = self.buffer.getvalue()[:-1]
		self.buffer = StringIO()
		self.buffer.write(new_buffer_value)
		self.pos -= 1

	def reset(self) -> None:
		"""
		Reset the REPL state to initials.
		"""

		self.history_pos = 0
		self.is_command_mode = False
		self.pos = 0

		super().reset()

	def clear_input(self) -> None:
		"""
		Clear the current input.
		"""

		for _ in range(self.pos):
			self.unwrite()
		self.buffer = StringIO()

	def type(self, string: str) -> None:
		"""
		Emulate the provided string being progressively typed in the REPL.
		"""

		for char in string:
			self.write(char)

	def history_up(self) -> None:
		"""
		If relevant, write the previous entry of history into the input.
		"""

		if self.history_pos < len(self.history):
			self.clear_input()
			self.type(self.history[self.history_pos])
			self.history_pos += 1
		else:
			ring_bell()

	def history_down(self) -> None:
		"""
		If relevant, write the next entry of history into the input.
		"""

		if self.history_pos > 0:
			self.history_pos -= 1
			self.clear_input()
			self.type(self.history[self.history_pos])
		else:
			self.clear_input()

	def start(self) -> None:
		"""
		Main function -- Start the REPL.
		"""

		while True:
			match get_key():
				case MagicKey.Esc:
					write_out("\x1b[39m")
					write_out_new_line()
					return
				case MagicKey.Newline:
					write_out("\x1b[39m")
					write_out_new_line()
					if buffer_value := self.buffer.getvalue():
						if self.is_command_mode:
							self.run_command()
						else:
							self.eval_input()
							if not self.error_status or self.STORE_INVALID_INPUT:
								self.history.insert(0, buffer_value)
					self.reset()
				case MagicKey.Tab | MagicKey.Right | MagicKey.Left:
					ring_bell()
				case MagicKey.BackWord:
					self.clear_input()
				case MagicKey.Up:
					self.history_up()
				case MagicKey.Down:
					self.history_down()
				case MagicKey.Backspace:
					if self.pos > 0:
						self.unwrite()
					elif self.is_command_mode:
						self.is_command_mode = False
						write_out("\b \b\x1b[39m")
				case char:
					if char == "!" and self.pos == 0:
						self.is_command_mode = not self.is_command_mode
						if self.is_command_mode:
							write_out("\x1b[35m!")
						else:
							write_out("\b \b\x1b[39m")
					else:
						self.write(char)


def start(**kwargs: bool) -> int:
	"""
	Convenient function to set up a REPL and start it.
	When exiting, save the history into a file.
	"""

	RAISE_PYTHON_EXCEPTIONS = kwargs.get("raise_python_exceptions", False)
	STORE_INVALID_INPUT = kwargs.get("store_invalid_input", False)

	r = REPL(store_invalid_input=STORE_INVALID_INPUT)

	exit_code = 0
	exc: Exception | None = None

	try:
		r.start()
	except Exception as e:
		if not isinstance(e, (KeyboardInterrupt, SystemExit)):
			report_panic(e)
			exit_code = 1
			exc = e
	finally:
		write_file_lines(REPL_HISTORY_FILE, list(reversed(r.history)))
		write_out_new_line()
		print(light(f"Saved session history in {REPL_HISTORY_FILE!r}."))
		write_out_new_line()
		print(color("👋️ Goodbye!", 3))

		if exc is not None and RAISE_PYTHON_EXCEPTIONS:
			raise exc

		return exit_code
