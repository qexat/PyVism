from builtins import divmod as _divmod
from io import StringIO
from typing import Any

from pyvism.compiler.tools import stream_endpoints
from pyvism.frontend.vmbc.tools import VMState, mnemonic


def _get_stream(ms: VMState, fd: int) -> StringIO:
	stream = ms.streams.get(fd)

	if stream is None:
		raise ValueError(f"stream {stream!r} does not exist or is closed")

	return stream


@mnemonic
def mov(vms: VMState, memdest: str, value: Any) -> VMState:
	vms.memory[memdest] = value

	return vms


@mnemonic
def write(vms: VMState, fd: int, value: str) -> VMState:
	stream = _get_stream(vms, fd)

	stream.write(value)

	return vms


@mnemonic
def flush(vms: VMState, fd: int) -> VMState:
	stream = _get_stream(vms, fd)

	endpoint = stream_endpoints[fd]

	endpoint.write(stream.getvalue())
	endpoint.flush()

	vms.streams.reset_buffer(fd)

	return vms


@mnemonic
def print(vms: VMState, memsrc1: str) -> VMState:
	value = vms.memory[memsrc1]

	if value is not None:
		vms = (write(vms.stdout, str(value)) >> flush(vms.stdout)).run(vms)

	return vms


@mnemonic
def add(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] + vms.memory[memsrc2]

	return vms


@mnemonic
def sub(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] - vms.memory[memsrc2]

	return vms


@mnemonic
def mul(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] * vms.memory[memsrc2]

	return vms


@mnemonic
def intdiv(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] // vms.memory[memsrc2]

	return vms


@mnemonic
def modulo(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] % vms.memory[memsrc2]

	return vms


@mnemonic
def divmod(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = _divmod(vms.memory[memsrc1], vms.memory[memsrc2])

	return vms


@mnemonic
def union(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1] | vms.memory[memsrc2]

	return vms


@mnemonic
def strdiff(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	vms.memory[memdest] = vms.memory[memsrc1].replace(memsrc2, "")

	return vms


@mnemonic
def seqdiff(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	slot1, slot2 = vms.memory[memsrc1], vms.memory[memsrc2]
	vms.memory[memdest] = type(vms.memory[memdest])(v for v in slot1 if v not in slot2)

	return vms


@mnemonic
def pathjoin(vms: VMState, memdest: str, memsrc1: str, memsrc2: str) -> VMState:
	slot1, slot2 = vms.memory[memsrc1], vms.memory[memsrc2]
	vms.memory[memdest] = f"{slot1}/{slot2}"

	return vms
