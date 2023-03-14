"""
Utilitaries and classes for the error system.
"""
import os
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar

from pyvism.py_utils import bold
from pyvism.py_utils import color
from pyvism.py_utils import eprint


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
        """
        Return a colorful human-readable representation of the related code line.
        """

        return (
            color(f"{self.number} | ", 4)
            + self.content[: self.spos]
            + bold(color(self.content[self.spos : self.epos], self.color))
            + self.content[self.epos :]
        )

    def get_subline(self) -> str:
        """
        Return a colorful human-readable representation of the subline, that underlines the exact
        topic position and details the message.
        """

        return (
            " " * self._ruler_size
            + color("| ", 4)
            + " " * self.spos
            + bold(color(self.char * (self.epos - self.spos), self.color))
            + bold(color(f" {self.message}", self.color))
        )

    def __repr__(self) -> str:
        return os.linesep.join((self.get_line(), self.get_subline()))


class InfoLine(MessageLine):
    color = 4
    char = "-"


class ErrorLine(MessageLine):
    color = 1
    char = "^"


@dataclass
class Error:
    """
    Represents a compilation error.
    Embeds a lot of handy methods to easily print a nice error message.
    """

    id: str

    summary: str
    source_file: str

    error_line: ErrorLine
    info_lines: list[InfoLine] = field(default_factory=list)

    hint_message: str | None = None
    candidate_messages: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.source_file = os.path.abspath(os.path.join(os.getcwd(), self.source_file))

    def _get_ruler_size(self) -> int:
        lines: list[MessageLine] = [*self.info_lines, self.error_line]
        return len(str(max(line.number for line in lines))) + 1

    def _get_ruler_space(self, *, minus_one: bool = False) -> str:
        return " " * (self._get_ruler_size() - minus_one)

    def _padding_line(self) -> str:
        return color(f"{self._get_ruler_space()}|", 4)

    @property
    def name(self) -> str:
        return color(self.id, 1)

    def synopsis(self) -> str:
        """
        The synopsis is the error code followed by a summary of the issue, with fancy text decorations.
        """

        return bold(f"error[{self.name}]: {self.summary}")

    def source(self) -> str:
        """
        The source is the path of the file where the error comes from, with fancy text decorations.
        """

        arrow = color(self._get_ruler_space(minus_one=True) + "-->", 4)
        path = f"{self.source_file}:{self.error_line.number}:{self.error_line.spos+1}"
        return " ".join((arrow, path))

    @property
    def lines(self) -> list[MessageLine]:
        """
        The lines are a list of the fancy-wrapped code lines sorted by their number.
        """

        lines: list[MessageLine] = [*self.info_lines, self.error_line]
        return sorted(lines, key=lambda line: line.number)

    def _help_line(self, message: str, *, is_indented: bool = False) -> str:
        """
        Util to get a pretty help message line.
        """

        base = " ".join((color(self._get_ruler_space() + "=", 4), bold("help:")))
        indent = "  " * is_indented + " "
        return indent.join((base, message))

    def hint(self) -> str:
        if not self.hint_message:
            return ""
        return self._help_line(self.hint_message)

    def candidates(self) -> list[str]:
        return [self._help_line(msg) for msg in self.candidate_messages]

    def throw(self, *, verbose: bool = True) -> None:
        """
        Print the error to stderr.
        """

        eprint(self.synopsis())

        if verbose:
            eprint(self.source())
            eprint(self._padding_line())
            for line in self.lines:
                eprint(line)
            eprint(self._padding_line())

            if self.hint_message:
                eprint(self.hint())

                for candidate in self.candidates():
                    eprint(candidate)

            eprint()


def report_abortion() -> None:
    """
    Report in the stderr that since there were errors, the program aborted.

    Similar to `report_panic()`, but for Vism compilation errors.
    """

    eprint(bold(color("error", 1) + ": aborting due to previous error"))


def report_panic(reason: Exception) -> None:
    """
    Report in the stderr that since there was an internal error (= uncaught Python exception),
    the program panicked and stopped.

    Similar to `report_abortion()`, but for internal Python exceptions.
    """

    message = f"[Error] Internal process panicked for the following reasons: '{reason}'"
    eprint(bold(color(message, 1)))
