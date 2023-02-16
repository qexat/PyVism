from io import StringIO

from pyvism.compiler.compiler import Compiler
from pyvism.constants import REPL_HISTORY_FILE
from pyvism.constants import REPL_PROMPT
from pyvism.constants import REPL_SYNOPSIS
from pyvism.frontend.map import CompilationTarget
from pyvism.py_utils import color
from pyvism.py_utils import light
from pyvism.py_utils import ends_with_new_line
from pyvism.py_utils import get_key
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
		self.last_entered = ""
		self.is_command_mode: bool = False
		self.pos = 0
		write_out(prompt)

		self.stdout = StringIO()

		self.compiler = Compiler(self.buffer)
		self.vm = VM(self.stdout)

	def print_stdout(self) -> None:
		stdout_contents = self.stdout.getvalue()
		write_out(stdout_contents)

		if not ends_with_new_line(stdout_contents):
			write_out_new_line()

	def run_command(self) -> None:
		if (cmd := self.buffer.getvalue()) in Commands.keys():
			Commands[cmd].value.run()
		else:
			print(color(f"Error: {cmd!r} is not a valid command", 1))

	def eval_input(self) -> None:
		self.compiler.change_file(self.buffer)
		match self.compiler.compile(CompilationTarget.Bytecode):
			case Ok(bytecode):
				self.vm.run(bytecode)
				self.print_stdout()
			case Err(errors):
				for error in errors:
					error.throw(verbose=False)

	def highlight(self, string: str) -> str:
		final_string = string
		if string in {"&", "$", "^"}:
			final_string = color(string, 1)
		elif string.isdigit():
			final_string = color(string, 6)
		return final_string

	def write(self, string: str) -> None:
		write_out(self.highlight(string))
		self.buffer.write(string)
		self.last_entered = string
		self.pos += len(string)

	def unwrite(self) -> None:
		unwrite_out(len(self.last_entered))
		new_buffer_value = self.buffer.getvalue()[:-1]
		self.buffer = StringIO()
		self.buffer.write(new_buffer_value)
		self.pos -= 1

	def reset(self) -> None:
		self.history_pos = 0
		self.buffer = StringIO()
		self.is_command_mode = False
		self.pos = 0
		write_out(self.prompt)

	def clear_line(self) -> None:
		for _ in range(self.pos):
			self.unwrite()
		self.buffer = StringIO()

	def type(self, string: str) -> None:
		for char in string:
			self.write(char)

	def history_up(self) -> None:
		if self.history_pos < len(self.history):
			self.clear_line()
			self.type(self.history[self.history_pos])
			self.history_pos += 1
		else:
			ring_bell()

	def history_down(self) -> None:
		if self.history_pos > 0:
			self.history_pos -= 1
			self.clear_line()
			self.type(self.history[self.history_pos])
		else:
			ring_bell()

	def start(self) -> None:
		while True:
			match get_key():
				case MagicKey.Esc:
					write_out_new_line()
					return
				case MagicKey.Newline:
					write_out("\x1b[39m\n")
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
					self.clear_line()
				case MagicKey.Up:
					self.history_up()
				case MagicKey.Down:
					self.history_down()
				case MagicKey.Backspace:
					if self.pos > 0:
						self.unwrite()
				case char:
					if char == "!" and self.pos == 0:
						self.is_command_mode = not self.is_command_mode
						if self.is_command_mode:
							write_out("\x1b[35m!")
						else:
							write_out("\b \b\x1b[39m")
					else:
						self.write(char)


def start() -> int:
	r = REPL()
	try:
		r.start()
	finally:
		write_file_lines(REPL_HISTORY_FILE, list(reversed(r.history)))
		print(light(f"Saved session history in {REPL_HISTORY_FILE!r}."))
		print(color("👋️ Goodbye!", 3))
		return 0
