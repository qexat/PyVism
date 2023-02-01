from io import StringIO
import readline  # type: ignore
from typing import Callable

from result import Err, Ok

from pyvism.compiler import Compiler
from pyvism.constants import REPL_PROMPT, __version__
from pyvism.vm import VM


# -- This whole file needs to be significantly improved -- #


def _unknown_cmd(self: dict[str, Callable[[], None]]):
    print("\x1b[1;31mUnknown command.\x1b[39m")
    _help(self)


def _help(self: dict[str, Callable[[], None]]):
    print("\x1b[1;34mAvailable commands:\x1b[22;39m")
    for cmd in filter(None, self.keys()):
        print(f"• \x1b[37m#{cmd}\x1b[39m")


def _exit(_: dict[str, Callable[[], None]]) -> None:
    raise SystemExit(0)


commands = {
    "help": lambda: _help(commands),
    "exit": lambda: _exit(commands),
    "version": lambda: print(__version__),
}


def _info_message() -> None:
    print("Type \x1b[34m#help\x1b[39m to show the available commands.")


def repl() -> int:
    _info_message()
    vm = VM()
    while True:
        try:
            line = input(REPL_PROMPT)
            if line.startswith("#"):
                command = commands.get(line[1:], None)

                if command is not None:
                    command()
                else:
                    _unknown_cmd(commands)

            else:
                try:
                    compiler = Compiler(StringIO(line), repl_mode=True)
                    match compiler.compile():
                        case Ok(bytecode):
                            vm.run(bytecode)
                        case Err(errors):

                            hidden_errors = len(errors[5:])
                            for error in errors[:5]:
                                error.throw(verbose=False)
                            if hidden_errors > 0:
                                print(f"(+ {hidden_errors} errors not shown)")
                            if line in commands.keys():
                                print(f"\nDid you mean: '#{line}'?")
                except Exception as e:
                    print(f"\x1b[31m{type(e).__name__}\x1b[39m: {e}")
                    raise e
        except KeyboardInterrupt:
            return 0
