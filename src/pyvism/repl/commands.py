from collections.abc import Callable

from pyvism.constants import __version__
from pyvism.py_utils import bold
from pyvism.py_utils import color
from pyvism.py_utils import light
from pyvism.py_utils import MapLikeEnum


class replc:
	def __init__(self, func: Callable[[], None]) -> None:
		self.func = func
		self.__doc__ = self.func.__doc__

	def run(self) -> None:
		self.func()


@replc
def help() -> None:
	"""Prints the available commands."""

	print(bold(color("Available commands:", 4)))
	for cmd in Commands:
		print("•", color(f"!{cmd.name}", 7), light(f"-- {cmd.value.__doc__}"))


@replc
def exit() -> None:
	"""Quits the REPL. Can also be done by pressing `ESC`."""

	raise SystemExit(0)


@replc
def version() -> None:
	"""Prints PyVism version."""

	print(color(__version__, 4))


class Commands(MapLikeEnum):
	help = help
	exit = exit
	version = version
