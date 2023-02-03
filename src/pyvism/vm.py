from typing import Any

from pyvism.constants import MEMORY_MAX_ADDR, REGISTER_MAX_ADDR
from pyvism.runtime.builtins import VMState, instruction


class VM:
    def __init__(self) -> None:
        if MEMORY_MAX_ADDR < REGISTER_MAX_ADDR:
            raise RuntimeError("illegal register max address")

        self.state = VMState()

    def run(self, bytecode: list[instruction[*tuple[Any, ...]]]) -> None:
        for instr in bytecode:
            self.state = instr.run(self.state)
