"""Average axial normal stress calculation."""

import math
from numbers import Real
from typing import Any

CALCULATOR_ID = "stress.axial"
CALCULATOR_NAME = "Axial Stress Calculator"
CALCULATOR_VERSION = "0.1.0"
GOVERNING_EQUATION = "σ = F / A"

_FORCE_TO_NEWTONS = {
    "N": 1.0,
    "kN": 1_000.0,
    "lbf": 4.4482216152605,
    "kip": 4_448.2216152605,
}

_AREA_TO_SQUARE_MILLIMETRES = {
    "mm²": 1.0,
    "cm²": 100.0,
    "m²": 1_000_000.0,
    "in²": 645.16,
}

_MEGAPASCALS_TO_OUTPUT = {
    "Pa": 1_000_000.0,
    "kPa": 1_000.0,
    "MPa": 1.0,
    "GPa": 0.001,
    "psi": 145.03773773020923,
    "ksi": 0.14503773773020923,
}

_ASSUMPTIONS = [
    "The applied force is axial and passes through the centroid of the resisting cross-section.",
    "The member is straight and prismatic in the region being evaluated.",
    "The reported area is the net area resisting the load.",
    "Stress is represented by its average value over the cross-section.",
    "The material is continuous and homogeneous at the scale of the calculation.",
    "The member is in static or quasi-static equilibrium.",
    "The evaluated section is sufficiently far from load introduction points and discontinuities.",
    "Deformation is small enough that the original cross-sectional area remains appropriate.",
]


def calculate_axial_stress(
    force_value: Real,
    force_unit: str,
    area_value: Real,
    area_unit: str,
    output_unit: str = "MPa",
) -> dict[str, Any]:
    """Calculate signed average axial stress using ``σ = F / A``."""
    force = _validate_number("force_value", force_value)
    area = _validate_number("area_value", area_value)

    if area <= 0:
        raise ValueError("area_value must be greater than zero")

    force_factor = _conversion_factor(
        "force_unit", force_unit, _FORCE_TO_NEWTONS
    )
    area_factor = _conversion_factor(
        "area_unit", area_unit, _AREA_TO_SQUARE_MILLIMETRES
    )
    output_factor = _conversion_factor(
        "output_unit", output_unit, _MEGAPASCALS_TO_OUTPUT
    )

    force_newtons = _require_finite_result(
        "converted force", force * force_factor
    )
    area_square_millimetres = _require_finite_result(
        "converted area", area * area_factor
    )
    stress_megapascals = _require_finite_result(
        "calculated stress", force_newtons / area_square_millimetres
    )
    stress = _require_finite_result(
        "converted output stress", stress_megapascals * output_factor
    )

    if force_newtons > 0:
        loading_state = "tension"
    elif force_newtons < 0:
        loading_state = "compression"
    else:
        loading_state = "unloaded"
        stress = 0.0

    return {
        "calculator": {
            "id": CALCULATOR_ID,
            "name": CALCULATOR_NAME,
            "version": CALCULATOR_VERSION,
        },
        "inputs": {
            "force": {"value": force, "unit": force_unit},
            "area": {"value": area, "unit": area_unit},
        },
        "results": {
            "axial_stress": {"value": stress, "unit": output_unit},
            "loading_state": loading_state,
        },
        "governing_equation": {
            "symbolic": GOVERNING_EQUATION,
            "substitution": (
                f"σ = {force_newtons:.17g} N / "
                f"{area_square_millimetres:.17g} mm²"
            ),
        },
        "assumptions": list(_ASSUMPTIONS),
        "warnings": [],
    }


def _validate_number(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    return numeric_value


def _require_finite_result(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    return value


def _conversion_factor(
    name: str,
    unit: str,
    conversions: dict[str, float],
) -> float:
    if not isinstance(unit, str):
        raise TypeError(f"{name} must be a string")

    try:
        return conversions[unit]
    except KeyError:
        supported_units = ", ".join(conversions)
        raise ValueError(
            f"unsupported {name} {unit!r}; supported units: {supported_units}"
        ) from None
