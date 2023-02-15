import os
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar


stderr = sys.__stderr__


@dataclass
class MessageLine:
	content: str
	number: int

	spos: int
	epos: int
	message: str

	color: ClassVar[int]
	char: ClassVar[str]

	@property
	def _ruler_size(self) -> int:
		return len(str(self.number)) + 1

	def get_line(self) -> str:
		return (
			"\x1b[34m"
			+ f"{self.number} | "
			+ "\x1b[39m"
			+ self.content[: self.spos]
			+ f"\x1b[1;3{self.color}m"
			+ self.content[self.spos : self.epos]
			+ "\x1b[22;39m"
			+ self.content[self.epos :]
		)

	def get_subline(self) -> str:
		return (
			" " * self._ruler_size
			+ "\x1b[34m| \x1b[39m"
			+ " " * self.spos
			+ f"\x1b[1;3{self.color}m"
			+ self.char * (self.epos - self.spos)
			+ f" {self.message}"
			+ "\x1b[22;39m"
		)

	def __repr__(self) -> str:
		return f"{self.get_line()}{os.linesep}{self.get_subline()}"


class InfoLine(MessageLine):
	color = 4
	char = "-"


class ErrorLine(MessageLine):
	color = 1
	char = "^"


@dataclass
class Error:
	id: str

	summary: str
	source_file: str

	error_line: ErrorLine
	info_lines: list[InfoLine] = field(default_factory=list)

	hint_message: str | None = None
	candidate_messages: list[str] = field(default_factory=list)

	def __post_init__(self) -> None:
		os.path.abspath
		self.source_file = os.path.abspath(os.path.join(os.getcwd(), self.source_file))

	def _get_ruler_size(self) -> int:
		return len(str(max(line.number for line in [*self.info_lines, self.error_line]))) + 1  # type: ignore

	def _get_ruler_space(self, *, minus_one: bool = False) -> str:
		return " " * (self._get_ruler_size() - minus_one)

	def _padding_line(self) -> str:
		return color(f"{self._get_ruler_space()}|", 4)

	@property
	def name(self) -> str:
		return color(self.id, 1)

	@property
	def synopsis(self) -> str:
		return bold(f"[{self.name}]: {self.summary}")

	@property
	def source(self) -> str:
		arrow = color(self._get_ruler_space(minus_one=True) + "-->", 4)
		path = f"{self.source_file}:{self.error_line.number}:{self.error_line.spos+1}"
		return f"{arrow} {path}"

	@property
	def lines(self) -> list[MessageLine]:
		return sorted([*self.info_lines, self.error_line], key=lambda line: line.number)

	def _help_line(self, message: str, *, indent: bool = False) -> str:
		bullet = color(self._get_ruler_space() + "=", 4)
		base = f"{bullet} {bold('help:')} "
		return f"{base}{'  ' * indent}{message}"

	@property
	def hint(self) -> str:
		if not self.hint_message:
			return ""
		return self._help_line(self.hint_message)

	@property
	def candidates(self) -> list[str]:
		return [self._help_line(msg) for msg in self.candidate_messages]

	def throw(self, *, verbose: bool = True) -> None:
		err_write(self.synopsis)

		if verbose:
			err_write(self.source)
			err_write(self._padding_line())
			for line in self.lines:
				err_write(str(line))
			err_write(self._padding_line())

			if self.hint_message:
				err_write(self.hint)

				for candidate in self.candidates:
					err_write(candidate)

			err_write()


def err_write(s: str = "") -> None:
	print(s, file=stderr)


def report_abortion() -> None:
	err_write(bold(color("error", 1) + ": aborting due to previous error"))


# -- We don't need a dependency -- #
def bold(s: str) -> str:
	return f"\x1b[1m{s}\x1b[22m"


def color(s: str, c: int) -> str:
	return f"\x1b[3{c}m{s}\x1b[39m"
