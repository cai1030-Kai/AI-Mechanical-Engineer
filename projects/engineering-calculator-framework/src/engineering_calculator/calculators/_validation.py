"""Internal validation helpers shared by calculator implementations."""

import math
from collections.abc import Mapping


def conversion_factor(
    name: str,
    unit: str,
    conversions: Mapping[str, float],
) -> float:
    """Return an explicitly supported unit conversion factor."""
    if not isinstance(unit, str):
        raise TypeError(f"{name} must be a string")

    try:
        return conversions[unit]
    except KeyError:
        supported_units = ", ".join(conversions)
        raise ValueError(
            f"unsupported {name} {unit!r}; supported units: {supported_units}"
        ) from None


def require_finite(name: str, value: float) -> float:
    """Return a finite value or identify the failed calculation stage."""
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    return value


def require_positive_finite(name: str, value: float) -> float:
    """Return a positive finite value or identify the failed stage."""
    finite_value = require_finite(name, value)
    if finite_value <= 0:
        raise ValueError(f"{name} must be greater than zero")

    return finite_value


def checked_positive_power(
    name: str,
    value: float,
    exponent: int,
) -> float:
    """Raise a positive value to a power with controlled validation."""
    try:
        result = value**exponent
    except OverflowError:
        raise ValueError(f"{name} must be finite") from None

    return require_positive_finite(name, result)
