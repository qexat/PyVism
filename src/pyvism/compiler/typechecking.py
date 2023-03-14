from typing import Any

from pyvism.compiler.types import MemoryValue
from pyvism.compiler.types import UnsetType


def static_type_check(target_type: type[MemoryValue], value: Any) -> bool:
    """
    Statically type-check the value against the current target type.

    Return whether it results in a success or not.
    """

    return target_type is UnsetType or isinstance(value, target_type)
