import os
from argparse import ArgumentParser
from argparse import FileType
from argparse import Namespace

from pyvism.py_utils import color
from pyvism.repl.repl import start
from pyvism.vm.runner import run


def get_args(argv: list[str] | None = None) -> Namespace:
	parser = ArgumentParser()
	subparsers = parser.add_subparsers(dest="subcommand", required=False)

	parser_run = subparsers.add_parser("run", description="Run a Vism file.")
	parser_run.add_argument("file", type=FileType("r+"))

	return parser.parse_args(argv)


def main_debug(argv: list[str] | None = None) -> int:
	args = get_args(argv)

	match args.subcommand:
		case "run":
			return run(args.file)
		case _:
			if os.name != "posix":
				print(
					color(
						"Sorry, the REPL is currently not available for your OS. (required: POSIX)", 1
					)
				)
				return 1
			return start()


def main() -> int:
	return main_debug()
