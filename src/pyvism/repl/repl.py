"""
Platform independant interface to PyVism REPL.
"""
import os

from pyvism.constants import REPL_HISTORY_FILE
from pyvism.errsys.tools import report_panic
from pyvism.py_utils import color
from pyvism.py_utils import light
from pyvism.py_utils import write_file_lines
from pyvism.py_utils import write_out_new_line

if os.name == "posix":
	from pyvism.repl.posix import REPL as PD_REPL
	from pyvism.repl.universal import REPL as UNI_REPL

	IS_POSIX = True
else:
	from pyvism.repl.universal import REPL as PD_REPL

	UNI_REPL = PD_REPL

	IS_POSIX = False


def start(**kwargs: bool) -> int:
	"""
	Convenient function to set up a REPL and start it.
	When exiting, save the history into a file.
	"""

	FORCE_UNIVERSAL = kwargs.get("force_universal", False)
	RAISE_PYTHON_EXCEPTIONS = kwargs.get("raise_python_exceptions", False)
	STORE_INVALID_INPUT = kwargs.get("store_invalid_input", False)

	REPL = UNI_REPL if FORCE_UNIVERSAL else PD_REPL

	r = REPL(store_invalid_input=STORE_INVALID_INPUT)

	exit_code = 0
	exc: Exception | None = None

	try:
		r.start()
	except Exception as e:
		if not isinstance(e, (EOFError, KeyboardInterrupt, SystemExit)):
			report_panic(e)
			exit_code = 1
			exc = e
	finally:
		if IS_POSIX and not FORCE_UNIVERSAL:
			write_file_lines(REPL_HISTORY_FILE, list(reversed(r.history)))  # type: ignore
			write_out_new_line()
			print(light(f"Saved session history in {REPL_HISTORY_FILE!r}."))
		write_out_new_line()
		print(color("👋️ Goodbye!", 3))

		if exc is not None and RAISE_PYTHON_EXCEPTIONS:
			raise exc

		return exit_code
