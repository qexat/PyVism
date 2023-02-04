from typing import Any

from pyvism.runtime.builtins import VMState, instruction


class VM:
    def __init__(self) -> None:
        self.state = VMState()

    def run(self, bytecode: list[instruction[*tuple[Any, ...]]]) -> None:
        for instr in bytecode:
            self.state = instr.run(self.state)
