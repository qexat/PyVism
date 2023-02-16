"""
REPL for POSIX-based systems.
"""
from io import StringIO

from pyvism import qtheme
from pyvism.compiler.compiler import Compiler
from pyvism.constants import REPL_HISTORY_FILE
from pyvism.constants import REPL_PROMPT
from pyvism.constants import REPL_SYNOPSIS
from pyvism.errsys.tools import report_panic
from pyvism.frontend.map import CompilationTarget
from pyvism.py_utils import color
from pyvism.py_utils import color_rgb
from pyvism.py_utils import ends_with_new_line
from pyvism.py_utils import get_key
from pyvism.py_utils import light
from pyvism.py_utils import MagicKey
from pyvism.py_utils import read_file_lines
from pyvism.py_utils import ring_bell
from pyvism.py_utils import unwrite_out
from pyvism.py_utils import write_file_lines
from pyvism.py_utils import write_out
from pyvism.py_utils import write_out_new_line
from pyvism.repl.commands import Commands
from pyvism.vm.vm import VM
from result import Err
from result import Ok


class REPL:
	def __init__(self, synopsis: str = REPL_SYNOPSIS, prompt: str = REPL_PROMPT) -> None:
		print(synopsis)
		self.prompt = prompt

		self.history = read_file_lines(REPL_HISTORY_FILE)
		self.history.reverse()
		self.history_pos = 0

		self.buffer = StringIO()
		self.last_entered = ''
		self.is_command_mode: bool = False
		self.pos = 0
		self.error_status: bool = False
		self.write_prompt()

		self.stdout = StringIO()

		self.compiler = Compiler(self.buffer)
		self.vm = VM(self.stdout)

	def write_prompt(self) -> None:
		prompt_color = qtheme.RED if self.error_status else qtheme.WHITE
		write_out(color_rgb(self.prompt, prompt_color))

	def print_stdout(self) -> None:
		"""
		Convenient method to print the caught output from executed Vism code
		to the actual stdout.
		"""

		stdout_contents = self.stdout.getvalue()
		write_out(stdout_contents)

		if not ends_with_new_line(stdout_contents):
			write_out(light('⏎'))
			write_out_new_line()

	def run_command(self) -> None:
		"""
		Run a REPL command (starting with `!`)
		"""

		if (cmd := self.buffer.getvalue()) in Commands.keys():
			Commands[cmd].value()
			self.error_status = False
		else:
			print(color(f'Error: {cmd!r} is not a valid command', 1))
			self.error_status = True

	def eval_input(self) -> None:
		"""
		Evaluate the input by using the compiler.

		Notes:
		- the standard output is redirected to `REPL.stdout`
		- the state of the compiler and VM are saved across the lines
		"""

		self.compiler.change_file(self.buffer)
		match self.compiler.compile(CompilationTarget.Bytecode):
			case Ok(bytecode):
				self.vm.run(bytecode)
				self.print_stdout()
				self.error_status = False
			case Err(errors):
				for error in errors:
					error.throw(verbose=False)
				self.error_status = True

	def highlight(self, string: str) -> str:
		"""
		Basic inline syntax highlighting of the live input.
		"""

		final_string = string
		if string in {'&', '$', '^'}:
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
		self.buffer = StringIO()
		self.is_command_mode = False
		self.pos = 0
		self.write_prompt()

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
					write_out('\x1b[39m')
					write_out_new_line()
					return
				case MagicKey.Newline:
					write_out('\x1b[39m')
					write_out_new_line()
					if buffer_value := self.buffer.getvalue():
						if self.is_command_mode:
							self.run_command()
						else:
							self.history.insert(0, buffer_value)
							self.eval_input()
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
						write_out('\b \b\x1b[39m')
				case char:
					if char == '!' and self.pos == 0:
						self.is_command_mode = not self.is_command_mode
						if self.is_command_mode:
							write_out('\x1b[35m!')
						else:
							write_out('\b \b\x1b[39m')
					else:
						self.write(char)


def start(*, raise_python_exceptions: bool = False) -> int:
	"""
	Convenient function to set up a REPL and start it.
	When exiting, save the history into a file.
	"""

	r = REPL()
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
		print(light(f'Saved session history in {REPL_HISTORY_FILE!r}.'))
		write_out_new_line()
		print(color('👋️ Goodbye!', 3))

		if exc is not None and raise_python_exceptions:
			raise exc

		return exit_code
