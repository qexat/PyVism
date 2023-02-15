from pyvism.compiler.tools import FileHandler, ParsingState, MacroKind


def debug(_: FileHandler, state: ParsingState) -> None:
	print("\x1b[2m" + " DEBUG ".center(80, "=") + "\x1b[22m")
	for instr in state.ir:
		print(instr)
	print("\x1b[2m" + "=" * 80 + "\x1b[22m")


macro_map = {
	MacroKind.Debug: debug,
}
