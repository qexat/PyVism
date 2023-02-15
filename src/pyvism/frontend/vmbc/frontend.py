from typing import LiteralString

from pyvism.frontend.tools import TargetFrontEnd
from pyvism.frontend.vmbc.instructions import (
	add,
	divmod,
	flush,
	intdiv,
	modulo,
	mov,
	mul,
	pathjoin,
	print,
	seqdiff,
	strdiff,
	sub,
	union,
	write,
)
from pyvism.frontend.vmbc.tools import AnyInstruction, mnemonic
from pyvism.ir.instructions import (
	ADD,
	DIFF,
	DIVMOD,
	INTDIV,
	MEMCH,
	MODULO,
	MUL,
	PATHJOIN,
	PRINTV,
	REPLIC,
	SFLUSH,
	SUB,
	SWRITE,
	UNION,
)
from pyvism.ir.tools import IRI


# PascalCase because FrontEnd is secretly a class
@TargetFrontEnd
def frontend(ir: list[IRI[LiteralString]]) -> list[AnyInstruction]:
	bytecode: list[AnyInstruction] = []

	for iri in ir:
		ir_mnemonic = iri.mnemonic
		bc_mnemonic: mnemonic | None = None
		if ir_mnemonic == MEMCH:
			bc_mnemonic = mov
		elif ir_mnemonic == ADD:
			bc_mnemonic = add
		elif ir_mnemonic == UNION:
			bc_mnemonic = union if iri.dest_type is set else add
		elif ir_mnemonic == SUB:
			bc_mnemonic = sub
		elif ir_mnemonic == DIFF:
			if iri.dest_type is str:
				bc_mnemonic = strdiff
			elif iri.dest_type is set:
				bc_mnemonic = sub
			else:
				bc_mnemonic = seqdiff
		elif ir_mnemonic in {MUL, REPLIC}:
			bc_mnemonic = mul
		elif ir_mnemonic == INTDIV:
			bc_mnemonic = intdiv
		elif ir_mnemonic == PATHJOIN:
			bc_mnemonic = pathjoin
		elif ir_mnemonic == MODULO:
			bc_mnemonic = modulo
		elif ir_mnemonic == DIVMOD:
			bc_mnemonic = divmod
		elif ir_mnemonic == PRINTV:
			bc_mnemonic = print
		elif ir_mnemonic == SWRITE:
			bc_mnemonic = write
		elif ir_mnemonic == SFLUSH:
			bc_mnemonic = flush
		else:
			raise ValueError(f"ir instruction {iri.mnemonic.name!r} is not supported")

		bytecode.append(bc_mnemonic(iri.dest, *iri.args))

	return bytecode
