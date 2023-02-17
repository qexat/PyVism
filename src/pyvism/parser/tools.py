"""
Parsing tools.
"""
from abc import ABC
from abc import abstractmethod
from ast import literal_eval
from dataclasses import dataclass
from enum import auto
from enum import Enum
from functools import cached_property
from io import StringIO
from typing import Any
from typing import Generic
from typing import Self
from typing import TextIO
from typing import TypeVar

from pyvism.compiler.internal import Address
from pyvism.compiler.internal import Identifier
from pyvism.compiler.internal import Integer
from pyvism.compiler.internal import InternalType
from pyvism.constants import DISCARDED_CHARS
from pyvism.constants import ESCAPABLE_CHARS
from pyvism.constants import MACRO_MODE_CHAR
from pyvism.constants import NULL
from pyvism.constants import PRGM_MODE_CHAR
from pyvism.constants import STREAM_IDS
from pyvism.py_utils import MapLikeEnum
from result import Err
from result import Ok
from result import Result

T = TypeVar("T")
KT = TypeVar("KT")


def get_buffer_lines(buffer: TextIO) -> list[str]:
	"""
	Return the buffer contents split by lines.

	Reason of existence:
	In the REPL, `buffer.read()` will return an empty string.
	Therefore, we need to `buffer.getvalue()` instead.
	"""

	contents = buffer.getvalue() if isinstance(buffer, StringIO) else buffer.read()

	return contents.splitlines()


class FileHandler:
	@property
	def name(self) -> str:
		"""
		Get the file name.

		Note: it might be a relative path.
		"""

		return self.buffer.name

	@property
	def lines(self) -> list[str]:
		"""
		Get a list of the file lines.
		"""

		return self.__lines

	@cached_property
	def file_end(self) -> int:
		return len(self.lines)

	@property
	def line_end(self) -> int:
		return len(self.current_line)

	@property
	def is_eof(self) -> bool:
		"""
		`True` if the file has reached its end, else `False`.
		"""

		return self.line_index >= self.file_end

	@property
	def is_eol(self) -> bool:
		"""
		`True` if the current line has reached its end, else `False`.
		"""

		return self.pos >= self.line_end

	@property
	def line_number(self) -> int:
		"""
		Line index + 1.
		Useful for user-friendly displaying.
		"""

		return self.line_index + 1

	@property
	def current_line(self) -> str:
		"""
		Get the current line.
		"""

		return self.lines[self.line_index]

	@property
	def current_char(self) -> str:
		"""
		Get the current char.
		"""

		return self.current_line[self.pos]

	def get_line(self, index: int) -> str:
		"""
		Get the line at a specific index.
		Remember to substract one if you have a line **number**.
		"""

		return self.lines[index]

	def __init__(self, file: TextIO) -> None:
		self.buffer: TextIO = file

		# StringIO is marked as having a `name` property
		# but in reality it does not at runtime
		if isinstance(self.buffer, StringIO):
			self.buffer.name = "<stdin>"

		self.__lines = get_buffer_lines(self.buffer)

		self.line_index: int = 0
		self.pos: int = 0

	def move_next_line(self) -> None:
		"""
		Convenient function to go the next line.
		Increment to line index, and move the line position to 0.
		"""

		self.line_index += 1
		self.pos = 0

	def freeze_position(self, spos: int) -> tuple[str, int, int, int]:
		"""
		Handy method to get a tuple of the current state of the file.
		Return, in order: the current line, its **number**, the given `spos`, the line position.
		"""

		return self.current_line, self.line_number, spos, self.pos


# *- TARGETS, KINDS, MODES -* #


class DataStorageKind(MapLikeEnum):
	"""
	Abstract enum that maps data storage kinds to their symbols.
	"""

	Memory = "&"
	Register = "$"
	Stream = ":"


DataStorageTypeMap: dict[DataStorageKind, InternalType[Any]] = {
	DataStorageKind.Memory: Identifier,
	DataStorageKind.Register: Address,
	DataStorageKind.Stream: Integer,
}


@dataclass
class DataStorage(Generic[T]):
	kind: DataStorageKind
	id: T

	def __repr__(self):
		return f"\x1b[37m{self.kind.name}\x1b[39m[\x1b[36m{self.id}\x1b[39m]"

	@abstractmethod
	def get_name(self) -> str:
		"""
		This method should always be overriden by the subclasses.
		"""

		pass

	def clone(self):
		"""
		Helper to store a frozen version of a data storage.
		"""

		return type(self)(self.kind, self.id)

	@classmethod
	def default(cls):
		"""
		Returns the default data storage.

		By default, it is the null stream (kind: `Stream`, id: `-1`).
		"""
		return cls(DataStorageKind.Stream, NULL)


"""
The following classes, map and function exist for convenience.
DataStorage objects get their name differently according to their kind ;
unfortunately, enums do not support generics, so this is kind of a workaround.
"""


class DataStorageByAddress(DataStorage[int]):
	def get_name(self) -> str:
		"""
		Get the name of the data storage that represents its ID by an hexadecimal address, such as registers.
		"""

		return f"{self.kind.name}[{self.id:#04x}"


class DataStorageByInteger(DataStorage[int]):
	def get_name(self) -> str:
		"""
		Get the name of the data storage that represents its ID by an integer, such as streams.
		"""

		if self.kind is DataStorageKind.Stream and self.id in STREAM_IDS.values():
			return list(STREAM_IDS.keys())[self.id + 1]
		return f"{self.kind.name}[{self.id}]"


class DataStorageByIdentifier(DataStorage[str]):
	def get_name(self) -> str:
		"""
		Get the name of the data storage that represents its ID by an identifier, such as memory slots.
		"""

		return f"{self.kind.name}[{self.id}]"


data_storage_map: dict[InternalType[Any], type[DataStorage[Any]]] = {
	Address: DataStorageByAddress,
	Integer: DataStorageByInteger,
	Identifier: DataStorageByIdentifier,
}


def get_data_storage_type(itype: InternalType[T]) -> type[DataStorage[T]]:
	return data_storage_map[itype]


# *- Parsing built-ins & constants -* #


class MacroKind(MapLikeEnum):
	Debug = "d"


class ModeType(MapLikeEnum):
	"""
	Mode type for Assign mode.
	"""

	String = "s"
	Literal = "l"


class Mode(Enum):
	Normal = auto()
	Select = auto()
	Assign = auto()


# End user modes (i.e. `^mode` syntax)
CARET_MODES = {
	"n": Mode.Normal,
	**{akchar: Mode.Assign for akchar in ModeType.values()},
}


OPERATION_MODES = {Mode.Normal}


class BufferMap(dict[KT, StringIO], ABC):
	"""
	A convenient abstract class to map each value of a type to a buffer, represented by
	a `TextIO` object.
	"""

	def add(self, id: KT) -> KT:
		"""
		Create a new StringIO stream and return the key ID.
		"""

		if id in self.keys():
			raise ValueError(f"stream {id} already exists")

		self[id] = StringIO()
		return id

	def reset_buffer(self, id: KT) -> None:
		"""
		Reset the stream of key `id`.
		"""

		stream = self.get(id)

		if stream is None:
			raise ValueError(f"{id}: no stream")

		self[id] = StringIO()


class ModeBufferMap(BufferMap[Mode]):
	"""
	A convenient subclass of `BufferMap` that maps `Mode`s to a buffer represented
	by a `StringIO` object.
	"""

	@classmethod
	def new(cls) -> Self:
		buffer_map = cls()

		for mode in Mode:
			buffer_map.add(mode)

		return buffer_map


class ParsingState:
	"""
	A special class to keep track of parsing data.
	Technically a finite state machine.
	"""

	def __init__(self) -> None:
		self.mode: Mode = Mode.Normal
		self.mode_type: ModeType | None = None
		# Default target is the null stream
		self.target: DataStorage[Any] = DataStorage.default()

		self.mode_buffers = ModeBufferMap.new()
		self.mode_spos: int = 0

		self.char_escaping: bool = False

	def reset(self) -> None:
		self.__init__()

	# *- MODE OPERATIONS -* #

	def update_mode_type(self, char: str) -> None:
		"""
		Handy method to update the mode type if `char` is a valid one.

		If `char` is not a valid mode type: essentially a no-op.
		"""

		self.mode_type = ModeType(char) if ModeType.contains(char) else self.mode_type

	def update_mode(self, new_mode: Mode, *, at: int) -> None:
		"""
		Handy method to update the mode and its starting position.
		"""

		self.mode = new_mode
		self.mode_spos = at

	# *- TARGET OPERATIONS -* #

	def update_target_kind(self, char: str) -> None:
		"""
		Update target kind.

		Change `target` type to a `DataStorage` generic subclass.
		It is done essentially for type-dependent representation.
		"""

		target_kind = DataStorageKind(char)
		itype = DataStorageTypeMap[target_kind]
		self.target = get_data_storage_type(itype)(target_kind, self.target.id)

	def _update_target_parsed_id(self, target_id: Any) -> None:
		"""
		**This method is private and should not be called directly.**

		It is used to update the target once `target_id` is parsed to a valid value.
		"""

		itype = self.get_target_kind_type()
		self.target = get_data_storage_type(itype)(self.target.kind, target_id)

	def update_target_id(self, unparsed_new_id: str) -> bool:
		"""
		Update the current target ID.
		"""

		target_kind_type: InternalType[Any] = self.get_target_kind_type()

		match target_kind_type.evaluate(unparsed_new_id.rstrip()):
			case Ok(parsed_value):
				self._update_target_parsed_id(parsed_value)
				return True
			case Err():
				return False

	# *- MODE BUFFER OPERATIONS -* #

	def read_buffer(self) -> str:
		"""
		Return the current mode's buffer value as a string.
		"""

		return self.mode_buffers[self.mode].getvalue()

	def write_buffer(self, char: str) -> None:
		"""
		Write a given char to the current mode's buffer value.
		"""

		self.mode_buffers[self.mode].write(char)

	def clear_buffer(self) -> None:
		"""
		Reset the current mode's buffer value.
		"""

		self.mode_buffers.reset_buffer(self.mode)

	def evaluate_buffer(self) -> Result[Any, bool]:
		"""
		Read the current mode's buffer and attempt to evaluate it.

		The result is wrapped in a special object:
		- if success, `Ok(result)`
		- if failure, `Err(boolean)`

		The value of Err's wrapped indicates the source of the error:
		- True: `mode_type` is neither `String` or `Literal` (supposedly unreachable)
		- False: `mode_type` is `Literal`, but the literal evaluation failed.
		"""

		mode_buffer = self.read_buffer()

		match self.mode_type:
			case ModeType.String:
				return Ok(mode_buffer)
			case ModeType.Literal:
				escaped_buffer = escape_literal(mode_buffer)
				if not is_valid_literal(escaped_buffer):
					return Err(False)
				return Ok(literal_eval(escaped_buffer))
			case None:
				return Err(True)

	# *- PREDICATES -* #

	def should_escape(self, char: str) -> bool:
		"""
		Return whether it should enter character escape mode.
		"""

		return not self.char_escaping and char == "\\" and self.mode is Mode.Assign

	# *- OTHER ABSTRACTIONS -* #

	def get_target_kind_type(self) -> InternalType[Any]:
		"""
		Handy method to easily get the new `DataStorage` generic internal type.
		"""

		return DataStorageTypeMap[self.target.kind]


# *- Parsing predicates -* #


def mode_request(file: FileHandler, state: ParsingState, char: str) -> bool:
	"""
	Return whether the program asks to change to a given `char` mode.
	"""

	return file.current_char == char and not state.char_escaping


def program_mode_request(file: FileHandler, state: ParsingState) -> bool:
	"""
	Return whether the program asks to change to a caret mode.

	`True` when the current character is `^`* and not being escaped.

	(*) defined in `constants.py`, can be changed.
	"""

	return mode_request(file, state, PRGM_MODE_CHAR)


def macro_mode_request(file: FileHandler, state: ParsingState) -> bool:
	"""
	Return whether the program asks to change to a macro mode.

	`True` when the current character is `?`* and not being escaped.

	(*) defined in `constants.py`, can be changed.
	"""

	return mode_request(file, state, MACRO_MODE_CHAR)


def discarded_char(file: FileHandler, state: ParsingState) -> bool:
	"""
	In normal mode, some characters are ignored, such as the whitespace.
	This function returns whether the current character is one of those.

	"""
	return state.mode is not Mode.Assign and file.current_char in DISCARDED_CHARS


# *- Utils -* #


def is_valid_literal(s: str) -> bool:
	"""
	Dirty way to check whether `literal_eval()` will succeed with `s`.
	"""

	try:
		literal_eval(s)
	except (ValueError, SyntaxError):
		return False
	else:
		return True


def escape_literal(literal: str) -> str:
	"""
	When the literal is a string, we need to escape some characters to avoid
	messing everything up. This escaping process is reversed when generating
	intermediate code -- it should not affect the program output.
	"""

	escaped = literal
	for key, value in ESCAPABLE_CHARS.items():
		if key != value:
			escaped = escaped.replace(value, f"\\{key}")
	return escaped
