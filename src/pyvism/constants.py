__all__ = (
    "__version__",
    "MEMORY_MAX_ADDR",
    "REGISTER_MAX_ADDR",
    "NULL",
    "REPL_PROMPT",
)


__version__ = "1.0.0"

MEMORY_MAX_ADDR = 0x10
REGISTER_MAX_ADDR = 0x10

NULL = -1

REPL_PROMPT = "\x1b[1;37mVISM\x1b[22m ~> \x1b[0m"
