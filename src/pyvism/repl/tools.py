"""
Tools to build the REPL variants.
"""
from abc import ABC
from abc import abstractmethod
from io import StringIO

from pyvism import qtheme
from pyvism.compiler.compiler import Compiler
from pyvism.constants import REPL_PROMPT
from pyvism.constants import REPL_SYNOPSIS
from pyvism.frontend.map import CompilationTarget
from pyvism.py_utils import color
from pyvism.py_utils import color_rgb
from pyvism.py_utils import ends_with_new_line
from pyvism.py_utils import light
from pyvism.py_utils import write_out
from pyvism.py_utils import write_out_new_line
from pyvism.repl.commands import Commands
from pyvism.vm.vm import VM
from result import Err
from result import Ok


class BaseREPL(ABC):
	def __init__(
		self,
		synopsis: str = REPL_SYNOPSIS,
		prompt: str = REPL_PROMPT,
		**kwargs: bool,
	) -> None:
		print(synopsis)
		self.prompt = prompt

		self.buffer = StringIO()
		self.error_status: bool = False
		self.write_prompt()

		self.stdout = StringIO()

		self.compiler = Compiler(self.buffer)
		self.vm = VM(self.stdout)

		self.__post_init__(**kwargs)

	@abstractmethod
	def __post_init__(self, **kwargs: bool) -> None:
		"""
		Overwrite this method for platform-dependant setup.
		"""

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
			write_out(light("⏎"))
			write_out_new_line()

	def run_command(self) -> None:
		"""
		Run a REPL command (starting with `!`)
		"""

		if (cmd := self.buffer.getvalue()) in Commands.keys():
			Commands[cmd].value()
			self.error_status = False
		else:
			print(color(f"Error: {cmd!r} is not a valid command", 1))
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

	@abstractmethod
	def write(self, string: str) -> None:
		"""
		Handy function to write the input to the buffer + stdout.
		"""

	def reset(self) -> None:
		"""
		Reset the REPL to its initial state.
		"""

		self.buffer = StringIO()
		self.write_prompt()

	@abstractmethod
	def start(self) -> None:
		"""
		Main function -- Start the REPL.
		"""
