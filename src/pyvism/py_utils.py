"""
Some utils to extend Python.
"""
import os
import sys
from enum import Enum
from typing import Any

if os.name == "posix":
	import termios
	import tty

	SPECIAL_FN_KEY = "\x1b["
else:
	SPECIAL_FN_KEY = "\xe0["


class MapLikeEnum(Enum):
	@classmethod
	def keys(cls):
		for member in cls:
			yield member.name

	@classmethod
	def values(cls):
		for member in cls:
			yield member.value

	@classmethod
	def contains(cls, value: Any) -> bool:
		return value in {member.value for member in cls}

	@classmethod
	def get(cls, value: Any, default: Any) -> Any:
		if cls.contains(value):
			return cls(value)
		return default


def bold(s: str) -> str:
	return f"\x1b[1m{s}\x1b[22m"


def light(s: str) -> str:
	return f"\x1b[2m{s}\x1b[22m"


def color(s: str, c: int) -> str:
	return f"\x1b[3{c}m{s}\x1b[39m"


def color_rgb(s: str, c: tuple[int, int, int]) -> str:
	r, g, b = c
	return f"\x1b[38;2;{r};{g};{b}m{s}\x1b[39m"


def read_file_lines(path: str) -> list[str]:
	if not os.path.exists(path):
		return []
	return open(path, "r").read().splitlines()


def write_file_lines(path: str, lines: list[str]) -> None:
	if not os.path.exists((file_dir := os.path.dirname(path))):
		os.makedirs(file_dir)

	with open(path, "w+") as f:
		for line in lines:
			f.write(line + os.linesep)


def write_out(string: str) -> None:
	os.write(sys.stdout.fileno(), string.encode())


def unwrite_out(number: int) -> None:
	for _ in range(number):
		write_out("\b \b")


def write_out_new_line() -> None:
	write_out(os.linesep)


def ring_bell() -> None:
	write_out("\a")


def ends_with_new_line(string: str) -> bool:
	return string.endswith(os.linesep) or not string


# Heavily based on: https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-a-script-from-the-termina/47197390#47197390


class MagicKey(MapLikeEnum):
	EOT = False, 4
	Tab = False, 9
	Newline = False, 10
	BackWord = False, 23
	Esc = False, 27
	Up = True, 65
	Down = True, 66
	Right = True, 67
	Left = True, 68
	Backspace = False, 127


if os.name == "posix":

	def get_key() -> str | MagicKey:
		old_state = termios.tcgetattr(sys.stdin)
		tty.setcbreak(sys.stdin.fileno())

		try:
			byteseq = os.read(sys.stdin.fileno(), 3).decode()
			is_special = False
			if len(byteseq) == 1:
				key = ord(byteseq)
			else:
				key = ord(byteseq[-1])
				is_special = byteseq[:-1] == SPECIAL_FN_KEY
			return MagicKey.get((is_special, key), chr(key))
		finally:
			termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_state)

else:

	def get_key() -> str | MagicKey:
		raise NotImplementedError
