"""Internal recursive freezing for immutable domain objects."""

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType
from typing import Any


def freeze_value(value: Any) -> Any:
    """Return a recursively frozen copy of a value."""
    if isinstance(value, Mapping):
        return MappingProxyType({
            key: freeze_value(nested_value)
            for key, nested_value in value.items()
        })
    if isinstance(value, list):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(freeze_value(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(freeze_value(item) for item in value)
    if isinstance(value, bytearray):
        return bytes(value)
    return deepcopy(value)
