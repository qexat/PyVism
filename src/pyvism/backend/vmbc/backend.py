from typing import LiteralString

from pyvism.backend.tools import TargetBackEnd
from pyvism.backend.vmbc.instructions import add
from pyvism.backend.vmbc.instructions import divmod
from pyvism.backend.vmbc.instructions import flush
from pyvism.backend.vmbc.instructions import intdiv
from pyvism.backend.vmbc.instructions import modulo
from pyvism.backend.vmbc.instructions import mov
from pyvism.backend.vmbc.instructions import mul
from pyvism.backend.vmbc.instructions import pathjoin
from pyvism.backend.vmbc.instructions import print
from pyvism.backend.vmbc.instructions import seqdiff
from pyvism.backend.vmbc.instructions import strdiff
from pyvism.backend.vmbc.instructions import sub
from pyvism.backend.vmbc.instructions import union
from pyvism.backend.vmbc.instructions import write
from pyvism.backend.vmbc.tools import AnyInstruction
from pyvism.backend.vmbc.tools import mnemonic
from pyvism.frontend.instructions import ADD
from pyvism.frontend.instructions import DIFF
from pyvism.frontend.instructions import DIVMOD
from pyvism.frontend.instructions import INTDIV
from pyvism.frontend.instructions import MEMCH
from pyvism.frontend.instructions import MODULO
from pyvism.frontend.instructions import MUL
from pyvism.frontend.instructions import PATHJOIN
from pyvism.frontend.instructions import PRINTV
from pyvism.frontend.instructions import REPLIC
from pyvism.frontend.instructions import SFLUSH
from pyvism.frontend.instructions import SUB
from pyvism.frontend.instructions import SWRITE
from pyvism.frontend.instructions import UNION
from pyvism.frontend.tools import IRI


@TargetBackEnd
def backend(ir: list[IRI[LiteralString]]) -> list[AnyInstruction]:
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
