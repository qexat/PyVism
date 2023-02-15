from argparse import ArgumentParser, FileType, Namespace

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
			raise NotImplementedError("repl")
			# return repl()


def main() -> int:
	return main_debug()
