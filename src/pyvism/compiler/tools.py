import sys
from abc import ABC
from collections import defaultdict
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any
from typing import LiteralString
from typing import TypeGuard

from pyvism.backend.tools import IdentifierLike
from pyvism.backend.tools import IRI
from pyvism.backend.tools import StreamIDLike
from pyvism.compiler.types import MemoryValue
from pyvism.compiler.types import UnsetType
from pyvism.constants import REGISTER_MAX_ADDR
from pyvism.errsys.tools import Error
from pyvism.parser.tools import DataStorage
from pyvism.parser.tools import DataStorageKind
from pyvism.parser.tools import FileHandler
from pyvism.parser.tools import ParsingState


# *- TYPING -* #


@dataclass
class TypeDef(ABC):
	"""
	Abstract type definition.
	"""

	type: type[MemoryValue]


class FreeTypeDef(TypeDef):
	"""
	Used for non-positional type definitions.
	"""


@dataclass
class PosTypeDef(TypeDef):
	"""
	Used for type definitions that have been set
	somewhere in the program ; the added fields
	are used by the compiler to keep track of them
	and to print more precise errors.
	"""

	line_number: int
	spos: int
	epos: int

	@property
	def data(self) -> tuple[int, int, int]:
		"""
		Handy property to retreive the positional data as a tuple.
		Especially used in the error system.
		"""

		return self.line_number, self.spos, self.epos


class TypeDefTracker(dict[str, TypeDef]):
	"""
	Special class that extends a list of TypeDef objects (`dict[str, TypeDef]`).

	## Additions

	- `get_from_target` (method)
	- `get_from_targets` (method)
	- `set` (method)
	"""

	def get_from_identifier(self, identifier: IdentifierLike) -> TypeDef:
		return self.get(identifier, FreeTypeDef(UnsetType))

	def get_from_target(self, target: DataStorage[Any]) -> TypeDef:
		"""
		Return the type definition of a given target.
		"""

		match target.kind:
			case DataStorageKind.Memory:
				return self.get_from_identifier(target.id)
			case DataStorageKind.Register:
				return FreeTypeDef(str)
			case DataStorageKind.Stream:
				return FreeTypeDef(UnsetType)

	def set(
		self,
		target: DataStorage[Any],
		new_type: type,
		line: int,
		spos: int,
		epos: int,
	):
		"""
		Interface to easily set a type definition.

		Acts as a no-op if:
		- The new type is UnsetType
		- The current type is the same as the new type

		Warning: this function might seem confusing. The type definition actually cannot change except
		if its current type is UnsetType because of strong typing. However, if the new type is the same
		as the current one and that it is not UnsetType, this means that the identifier type was defined
		at a certain point of the program -- we do not want to lose that information by overriding it.
		"""

		if new_type is UnsetType:
			return

		current_typedef = self.get_from_target(target)

		if current_typedef.type is new_type:
			return

		self[target.id] = PosTypeDef(new_type, line, spos, epos)


#


# *- Compiler utils -* #


class CompilerState(ParsingState):
	"""
	A special class for the compiler to keep track of parsing data.
	Technically a finite state machine.
	"""

	def __init__(self) -> None:
		self.typedefs: TypeDefTracker = TypeDefTracker()
		self.registers: list[IdentifierLike | None] = [None] * REGISTER_MAX_ADDR

		super(CompilerState, self).__init__()

		# Intermediate Representation Instructions
		self.ir: list[IRI[LiteralString]] = []

		# TODO: add warnings support
		# TODO: add bool @property to check whether there is an error
		self.errors: list[Error] = []

	# *- TYPE DEFINITIONS OPERATIONS -* #

	def get_target_typedef(self) -> TypeDef:
		"""
		Get current target type definition.
		"""

		return self.typedefs.get_from_target(self.target)

	def set_target_typedef(self, file: FileHandler, new_type: type) -> None:
		"""
		Set the type definition for the current target at the given position using the provided `new_type`.

		Note: the underlying method, `typedefs.set()`, acts as a no-op if the target's type definition is already set.
		Therefore, it is required to check whether there is a type mismatch between the current and the new definition
		before calling this function.
		"""

		_, *data = file.freeze_position(self.mode_spos)
		self.typedefs.set(self.target, new_type, *data)

	def get_operand_type(self, operand: IdentifierLike | StreamIDLike) -> type:
		"""
		Convenient method to easily get the type of a given operand regardless of it's an identifier or not.
		"""

		if isinstance(operand, IdentifierLike):
			return self.typedefs.get_from_identifier(operand).type
		return int

	def get_operands_types(
		self,
		operands: list[IdentifierLike | StreamIDLike],
	) -> Generator[type, None, None]:
		"""
		Convenient method to easily get types of multiple operands at the same time.
		"""

		for operand in operands:
			yield self.get_operand_type(operand)

	# *- REGISTERS OPERATIONS -* #

	def get_operands(
		self,
		kinds: tuple[type, *tuple[type, ...]],
	) -> Generator[IdentifierLike | StreamIDLike | None, None, None]:
		"""
		Convenient method to easily get operands given pseudo-mnemonic kinds.

		It can be used as a template mapping for `get_operands_types()`.
		"""

		arg_n: int = 0

		for kind in kinds:
			if kind is IdentifierLike:
				yield self.registers[arg_n]
				arg_n += 1
			else:
				yield self.target.id


# *- Compiler predicates -* #


def is_matching_number_of_operands(
	operands: list[IdentifierLike | StreamIDLike | None],
) -> TypeGuard[list[IdentifierLike | StreamIDLike]]:
	"""
	Hacky function -- it only exists for the type guard, because static typecheckers
	cannot ensure that `operands` does not contain a `None` with a `if` statement.
	"""

	return None not in operands


def is_identifier_defined(typedef: TypeDef) -> TypeGuard[PosTypeDef]:
	return isinstance(typedef, PosTypeDef)


# *- CUSTOM I/O -* #


stream_endpoints = defaultdict(
	lambda: sys.stdout,
	{
		0: sys.stdout,
		1: sys.stderr,
	},
)
