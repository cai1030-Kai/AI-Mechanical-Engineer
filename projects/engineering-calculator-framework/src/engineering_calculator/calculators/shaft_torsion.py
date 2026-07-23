"""Torsional shear stress calculation for a solid circular shaft."""

import math
from numbers import Real
from typing import Any

CALCULATOR_ID = "stress.shaft_torsion"
CALCULATOR_NAME = "Solid Circular Shaft Torsional Stress Calculator"
CALCULATOR_VERSION = "0.1.0"
CALCULATOR_CATEGORY = "Stress Analysis"
ENGINEERING_DOMAIN = "Mechanics of Materials"
CALCULATOR_PURPOSE = (
    "Calculate the polar moment of inertia and maximum elastic torsional "
    "shear stress in a solid circular shaft subjected to pure torque"
)
GOVERNING_EQUATION = "J = πd⁴ / 32; τmax = Tc / J = 16T / (πd³)"

_TORQUE_TO_NEWTON_MILLIMETRES = {
    "N·mm": 1.0,
    "N·m": 1_000.0,
    "lbf·in": 112.9848290276167,
    "lbf·ft": 1_355.8179483314004,
}

_DIAMETER_TO_MILLIMETRES = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1_000.0,
    "in": 25.4,
}

_POLAR_MOMENT_UNITS = {
    "mm": "mm⁴",
    "cm": "cm⁴",
    "m": "m⁴",
    "in": "in⁴",
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
    "The shaft is straight and prismatic at the evaluated section.",
    "The cross-section is solid and circular.",
    "The applied load is pure torque about the shaft centroidal axis.",
    "The torque is static or quasi-static.",
    "The material is continuous, homogeneous, and isotropic.",
    "The material remains within the linearly elastic range.",
    "Saint-Venant torsion is applicable.",
    "Deformation and angle of twist are small.",
    "Plane cross-sections remain plane without significant warping.",
    "The evaluated section is away from load application points and discontinuities.",
    "The supplied diameter represents the actual resisting solid section.",
]

_LIMITATIONS = [
    "The calculation does not apply to hollow shafts.",
    "The calculation does not apply to noncircular sections.",
    "The calculation does not evaluate thin-walled or warping torsion.",
    "The calculation does not include stress concentrations.",
    "The calculation does not evaluate local load introduction or contact stress.",
    "The calculation does not evaluate combined loading.",
    "The calculation does not evaluate angle of twist.",
    "The calculation does not evaluate nonlinear elasticity or plastic torsion.",
    "The calculation does not evaluate residual, thermal, dynamic, or impact stress.",
    "The calculation does not evaluate material strength, yielding, or factor of safety.",
    "The calculation does not evaluate fatigue, fracture, creep, or stress relaxation.",
    "The calculation does not evaluate stability or vibration.",
    "The calculation does not establish design-code or regulatory compliance.",
]

_REFERENCES = [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, torsion of circular shafts.",
    "R. G. Budynas and J. K. Nisbett, Shigley's Mechanical Engineering Design, 11th Edition, torsional shear stress in circular shafts.",
]


def calculate_shaft_torsion(
    torque_value: Real,
    torque_unit: str,
    diameter_value: Real,
    diameter_unit: str,
    output_unit: str = "MPa",
) -> dict[str, Any]:
    """Calculate ``J`` and maximum torsional shear stress for a solid shaft."""
    torque = _validate_number("torque_value", torque_value)
    diameter = _validate_number("diameter_value", diameter_value)

    if torque < 0:
        raise ValueError("torque_value must be greater than or equal to zero")
    if diameter <= 0:
        raise ValueError("diameter_value must be greater than zero")

    torque_factor = _conversion_factor(
        "torque_unit", torque_unit, _TORQUE_TO_NEWTON_MILLIMETRES
    )
    diameter_factor = _conversion_factor(
        "diameter_unit", diameter_unit, _DIAMETER_TO_MILLIMETRES
    )
    output_factor = _conversion_factor(
        "output_unit", output_unit, _MEGAPASCALS_TO_OUTPUT
    )

    torque_newton_millimetres = _require_finite(
        "converted torque", torque * torque_factor
    )
    diameter_millimetres = _require_positive_finite(
        "converted diameter", diameter * diameter_factor
    )
    diameter_cubed = _positive_power(
        "diameter cubed", diameter_millimetres, 3
    )
    diameter_fourth = _positive_power(
        "diameter fourth power", diameter_millimetres, 4
    )

    polar_moment_mm4 = _require_positive_finite(
        "polar moment of inertia", math.pi * diameter_fourth / 32.0
    )
    polar_moment_input_unit = _require_positive_finite(
        "converted polar moment of inertia",
        polar_moment_mm4 / diameter_factor**4,
    )
    stress_megapascals = _require_finite(
        "calculated maximum shear stress",
        16.0
        * torque_newton_millimetres
        / (math.pi * diameter_cubed),
    )
    stress = _require_finite(
        "converted maximum shear stress",
        stress_megapascals * output_factor,
    )

    return {
        "calculator": {
            "id": CALCULATOR_ID,
            "name": CALCULATOR_NAME,
            "version": CALCULATOR_VERSION,
            "category": CALCULATOR_CATEGORY,
            "engineering_domain": ENGINEERING_DOMAIN,
            "purpose": CALCULATOR_PURPOSE,
            "reference_equation": GOVERNING_EQUATION,
        },
        "inputs": {
            "torque": {"value": torque, "unit": torque_unit},
            "diameter": {"value": diameter, "unit": diameter_unit},
            "output_unit": output_unit,
        },
        "results": {
            "polar_moment_of_inertia": {
                "value": polar_moment_input_unit,
                "unit": _POLAR_MOMENT_UNITS[diameter_unit],
            },
            "maximum_shear_stress": {
                "value": stress,
                "unit": output_unit,
            },
        },
        "governing_equation": {
            "symbolic": GOVERNING_EQUATION,
            "substitution": (
                f"J = π({diameter_millimetres:.17g} mm)⁴ / 32; "
                f"τmax = 16({torque_newton_millimetres:.17g} N·mm) / "
                f"(π({diameter_millimetres:.17g} mm)³)"
            ),
        },
        "assumptions": list(_ASSUMPTIONS),
        "warnings": [],
        "limitations": list(_LIMITATIONS),
        "references": list(_REFERENCES),
    }


def _validate_number(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    return numeric_value


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


def _positive_power(name: str, value: float, exponent: int) -> float:
    try:
        result = value**exponent
    except OverflowError:
        raise ValueError(f"{name} must be finite") from None

    return _require_positive_finite(name, result)


def _require_finite(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    return value


def _require_positive_finite(name: str, value: float) -> float:
    finite_value = _require_finite(name, value)
    if finite_value <= 0:
        raise ValueError(f"{name} must be greater than zero")

    return finite_value

