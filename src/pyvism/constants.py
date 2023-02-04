__all__ = (
	"__version__",
	"MEMORY_MAX_ADDR",
	"REGISTER_MAX_ADDR",
	"NULL",
	"REPL_PROMPT",
	"get_name",
	"confusable_symbols",
)


__version__ = "1.2.0"

MEMORY_MAX_ADDR = 0x10
REGISTER_MAX_ADDR = 0x10

NULL = -1

REPL_PROMPT = "\x1b[1;37mVISM\x1b[22m ~> \x1b[0m"


def get_name(t: type) -> str:
	return t.__name__


confusable_symbols: dict[str, str] = {"*": "×"}
