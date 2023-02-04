from argparse import ArgumentParser, FileType, Namespace

from result import Err, Ok

from pyvism.compiler import Compiler
from pyvism.repl import repl
from pyvism.runtime.errors import report_abortion
from pyvism.vm import VM


def get_args(argv: list[str] | None = None) -> Namespace:
	parser = ArgumentParser()
	subparsers = parser.add_subparsers(dest="subcommand", required=False)

	parser_run = subparsers.add_parser("run", description="Run a Vism file.")
	parser_run.add_argument("file", type=FileType("r+"))

	return parser.parse_args()


def main_debug(argv: list[str] | None = None) -> int:
	args = get_args(argv)

	match args.subcommand:
		case "run":
			compiler = Compiler(args.file)
			vm = VM()
			match (result := compiler.compile()):
				case Ok(bytecode):
					vm.run(bytecode)
				case Err(errors):
					for error in errors:
						error.throw()
					report_abortion()
					return 1
		case _:
			return repl()

	return 0


def main() -> int:
	return main_debug()
