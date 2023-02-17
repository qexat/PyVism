from collections.abc import Callable
from typing import Any
from typing import TextIO
from typing import TypeVar

from pyvism.backend.instructions import MEMCH
from pyvism.backend.instructions import SWRITE
from pyvism.backend.interface import get_pseudo_mnemonic
from pyvism.compiler.macros import macro_map
from pyvism.compiler.tools import CompilerState
from pyvism.compiler.tools import is_identifier_defined
from pyvism.compiler.tools import is_matching_number_of_operands
from pyvism.compiler.typechecking import static_type_check
from pyvism.constants import ESCAPABLE_CHARS
from pyvism.errsys.errors import E001
from pyvism.errsys.errors import E002
from pyvism.errsys.errors import E003
from pyvism.errsys.errors import E004
from pyvism.errsys.errors import E005
from pyvism.errsys.errors import E006
from pyvism.errsys.errors import E007
from pyvism.errsys.errors import E008
from pyvism.errsys.errors import E009
from pyvism.errsys.errors import E010
from pyvism.errsys.errors import E011
from pyvism.errsys.tools import Error
from pyvism.frontend.map import CompilationTarget
from pyvism.parser.tools import CARET_MODES
from pyvism.parser.tools import DataStorageKind
from pyvism.parser.tools import discarded_char
from pyvism.parser.tools import FileHandler
from pyvism.parser.tools import macro_mode_request
from pyvism.parser.tools import MacroKind
from pyvism.parser.tools import Mode
from pyvism.parser.tools import OPERATION_MODES
from pyvism.parser.tools import program_mode_request
from result import Err
from result import Ok
from result import Result


T = TypeVar("T")


# *- Compiler -* #


class Compiler:
	"""
	Class representing the compiler for a specified Vism code file.
	"""

	def __init__(self, file: TextIO) -> None:
		self.file = FileHandler(file)
		self.state: CompilerState = CompilerState()

	def change_file(self, new_file: TextIO) -> None:
		"""
		Convenient function to change the file while keeping the compilation state.
		"""

		self.file = FileHandler(new_file)
		self.state.reset()
		self.state.errors = []

	def push_error(self, error: Callable[[FileHandler, CompilerState], Error]) -> None:
		"""
		Convenient function to easily push an error to the error stack.
		"""

		self.state.errors.append(error(self.file, self.state))

	def process_buffered(self) -> None:
		"""
		Process the current mode's buffer.

		Potential compilation errors:
		- E001: if the selector type is invalid
		- E002: if the buffered literal to assign did not pass evaluation
		- E003: if the type of the assignment target does not match with value's one

		Unreachable exceptions:
		- Assignment: the target id is not defined

		Note: the latter exist in the case where there is a bug, to make it easier to track.
		"""

		mode_buffer = self.state.read_buffer()

		match self.state.mode:
			case Mode.Select:
				if not self.state.update_target_id(mode_buffer):
					self.push_error(E001)  # E001: invalid selector type
					return
			case Mode.Assign:
				match self.state.evaluate_buffer():
					case Ok(value):
						pass
					case Err(undef_target_exc):
						if undef_target_exc:  # !UNREACHABLE
							raise RuntimeError("undefined target id")
						self.push_error(E002)  # E002: invalid literal
						return

				target_type = self.state.get_target_typedef().type

				if not static_type_check(target_type, value):
					self.push_error(E003)  # E003: mismatched types
					return

				target = self.state.target.clone()

				match target.kind:
					case DataStorageKind.Memory:
						value_t = type(value)
						# Remember the implicit type definition
						self.state.set_target_typedef(self.file, value_t)
						iri = MEMCH(self.state.target.id, value_t, (value,), (value_t,))
						self.state.ir.append(iri)
					case DataStorageKind.Register:
						if not is_identifier_defined(self.state.typedefs.get_from_identifier(value)):
							self.push_error(E011)  # E011: undefined identifier
							return

						self.state.registers[target.id] = value
						# Do NOTHING, registers = compile time only
					case DataStorageKind.Stream:
						value = str(value)
						iri = SWRITE(self.state.target.id, str, (value,), (str,))
						self.state.ir.append(iri)
			case _:
				# if Mode is Normal: we ignore
				pass

		self.state.clear_buffer()

	def change_mode(self) -> None:
		"""
		Change the current mode.

		Potential compilation errors:
		- E004: if it expects a character, but reached the end of line
		- E005: if the character does not correspond to a valid mode
		"""

		if self.file.is_eol:
			self.push_error(E004)  # E004: unexpected EOL
			return

		mode = CARET_MODES.get(self.file.current_char, None)

		if mode is None:
			self.push_error(E005)  # E005: invalid mode
			return

		self.state.update_mode(mode, at=self.file.pos + 1)
		self.state.update_mode_type(self.file.current_char)

	def run_macro(self) -> None:
		"""
		Run a given macro -- it happens at compilation, not during runtime.

		Potential compilation errors:
		- E004: if it expects a character, but reached the end of line
		- E005: if the character does not correspond to a defined macro
		"""

		if self.file.is_eol:
			self.push_error(E004)  # E004: unexpected EOL
			return

		if not MacroKind.contains(self.file.current_char):
			self.push_error(E006)  # E006: undefined macro
			return

		macro_map[MacroKind(self.file.current_char)](self.file, self.state)

	def process_char(self) -> None:
		"""
		Process the current character.

		If it is a selector symbol, we change to the corresponding mode.
		Otherwise it is probably an operation.

		Potential compilation errors:
		- E008: the symbol is unknown
		- E009: the number of operands does not match with expected one
		- E010: the number of operands are correct, but not their types
		"""

		current_char = self.file.current_char

		if DataStorageKind.contains(current_char):
			self.state.mode = Mode.Select
			self.state.update_target_kind(current_char)
		else:
			pseudo_mnemonic = get_pseudo_mnemonic(current_char)

			if pseudo_mnemonic is None:
				self.push_error(E008)  # E008: unknown symbol
				return

			operands = list(self.state.get_operands(pseudo_mnemonic.kinds))

			if not is_matching_number_of_operands(operands):
				self.push_error(E009)  # E009: unmatching number of operands
				return

			operands_types = tuple(self.state.get_operands_types(operands))
			mnemonic = pseudo_mnemonic.get_overload(operands_types)

			if mnemonic is None:
				self.push_error(E010)  # E010: no overload for operator
				return

			dest, *args = operands
			dest_type, *args_types = operands_types

			self.state.ir.append(mnemonic(dest, dest_type, (*args,), (*args_types,)))

	def buffer_char(self) -> None:
		"""
		Push the current character to the current mode's buffer.

		Potential compilation errors:
		- E007: if the current character is being escaped, but that it is an invalid escape sequence.
		"""

		current_char = self.file.current_char

		if self.state.should_escape(current_char):
			self.state.char_escaping = True
			return

		final_char = current_char

		if self.state.char_escaping:
			if not current_char in ESCAPABLE_CHARS:
				self.push_error(E007)  # E007: invalid escape character
				return
			final_char = ESCAPABLE_CHARS[current_char]
			self.state.char_escaping = False

		self.state.write_buffer(final_char)

	def compile(self, target: CompilationTarget) -> Result[list[Any], list[Error]]:
		"""
		Compile the file code into the specified compilation target.

		This is a two-step compilation:
		- First, it walks along the code and generate intermediate representation instructions (IRIs).
		- Second, it sends the IRIs to the compilation target object that transforms it into the final result.

		Return either a list of elements (instructions or LOC) or a list of errors.
		"""

		frontend = target.value

		while not self.file.is_eof:
			while not self.file.is_eol:
				if program_mode_request(self.file, self.state):
					self.process_buffered()
					self.file.pos += 1
					self.change_mode()
				elif macro_mode_request(self.file, self.state):
					self.process_buffered()
					self.file.pos += 1
					self.run_macro()
				elif not discarded_char(self.file, self.state):
					if self.state.mode in OPERATION_MODES:
						self.process_char()
						pass
					else:
						self.buffer_char()

				if self.state.errors:
					return Err(self.state.errors)

				self.file.pos += 1

			self.process_buffered()
			self.file.move_next_line()

		return Ok(frontend(self.state.ir))


def compile(file: TextIO, target: CompilationTarget) -> Result[list[Any], list[Error]]:
	"""
	Compile the file code into the specified compilation target.
	"""

	return Compiler(file).compile(target)
