from typing import LiteralString

from pyvism.backend.instructions import ADD
from pyvism.backend.instructions import DIFF
from pyvism.backend.instructions import DIVMOD
from pyvism.backend.instructions import INTDIV
from pyvism.backend.instructions import MEMCH
from pyvism.backend.instructions import MODULO
from pyvism.backend.instructions import MUL
from pyvism.backend.instructions import PATHJOIN
from pyvism.backend.instructions import PRINTV
from pyvism.backend.instructions import REPLIC
from pyvism.backend.instructions import SFLUSH
from pyvism.backend.instructions import SUB
from pyvism.backend.instructions import SWRITE
from pyvism.backend.instructions import UNION
from pyvism.backend.tools import IRI
from pyvism.frontend.tools import TargetFrontEnd
from pyvism.frontend.vmbc.instructions import add
from pyvism.frontend.vmbc.instructions import divmod
from pyvism.frontend.vmbc.instructions import flush
from pyvism.frontend.vmbc.instructions import intdiv
from pyvism.frontend.vmbc.instructions import modulo
from pyvism.frontend.vmbc.instructions import mov
from pyvism.frontend.vmbc.instructions import mul
from pyvism.frontend.vmbc.instructions import pathjoin
from pyvism.frontend.vmbc.instructions import print
from pyvism.frontend.vmbc.instructions import seqdiff
from pyvism.frontend.vmbc.instructions import strdiff
from pyvism.frontend.vmbc.instructions import sub
from pyvism.frontend.vmbc.instructions import union
from pyvism.frontend.vmbc.instructions import write
from pyvism.frontend.vmbc.tools import AnyInstruction
from pyvism.frontend.vmbc.tools import mnemonic


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
			raise ValueError(f'ir instruction {iri.mnemonic.name!r} is not supported')

		bytecode.append(bc_mnemonic(iri.dest, *iri.args))

	return bytecode
