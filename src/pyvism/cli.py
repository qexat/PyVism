"""
Command Line Interface of PyVism.

## REPL

```sh
vism
```

## Run a Vism file

```sh
vism run /path/to/file.vism
```
"""
from argparse import ArgumentParser
from argparse import FileType
from argparse import Namespace

from pyvism.repl.repl import start
from pyvism.vm.runner import run


def get_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--force-universal", action="store_true")
    parser.add_argument("--raise-python-exceptions", action="store_true")
    parser.add_argument("--store-invalid-input", action="store_true")

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
            return start(
                force_universal=args.force_universal,
                raise_python_exceptions=args.raise_python_exceptions,
                store_invalid_input=args.store_invalid_input,
            )


def main() -> int:
    return main_debug()
