"""Linear-elastic bending stress calculation for a straight beam."""

import math
from numbers import Real
from typing import Any

CALCULATOR_ID = "stress.beam_bending"
CALCULATOR_NAME = "Beam Bending Stress Calculator"
CALCULATOR_VERSION = "0.1.0"
CALCULATOR_CATEGORY = "Stress Analysis"
ENGINEERING_DOMAIN = "Mechanics of Materials"
CALCULATOR_PURPOSE = (
    "Calculate signed linear-elastic normal stress at a specified distance "
    "from the neutral axis of a straight beam in pure bending about one "
    "principal centroidal axis"
)
GOVERNING_EQUATION = "σ = My / I"

_MOMENT_TO_NEWTON_MILLIMETRES = {
    "N·mm": 1.0,
    "N·m": 1_000.0,
    "lbf·in": 112.9848290276167,
    "lbf·ft": 1_355.8179483314004,
}

_DISTANCE_TO_MILLIMETRES = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1_000.0,
    "in": 25.4,
}

_SECOND_MOMENT_TO_MILLIMETRES_FOURTH = {
    "mm^4": 1.0,
    "cm^4": 10_000.0,
    "m^4": 1_000_000_000_000.0,
    "in^4": 416_231.4256,
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
    "The member is a straight beam at the evaluated section.",
    "The section is subjected to pure bending about one principal centroidal axis.",
    "Plane sections remain plane after bending.",
    "The longitudinal normal strain varies linearly with distance from the neutral axis.",
    "The material is continuous, homogeneous, and linearly elastic in the region evaluated.",
    "The elastic modulus is uniform across the section.",
    "Deformations and rotations are small enough for linear beam theory.",
    "The supplied I is the section second moment of area about the selected principal centroidal axis.",
    "The supplied y is measured perpendicular to that same neutral axis in the same section orientation.",
    "The evaluated section is sufficiently far from load introduction points, abrupt discontinuities, and local contact regions.",
]

_WARNINGS = [
    "The calculation is valid only when the supplied second moment of area, I, and distance from the neutral axis, y, correspond to the same bending axis and section orientation.",
    "External structural-analysis tools may use different bending-moment sign conventions; verify the sign convention before comparing results.",
]

_LIMITATIONS = [
    "The calculation does not determine section geometry, centroid location, principal-axis orientation, neutral-axis location, or second moment of area.",
    "The calculation does not evaluate biaxial bending or bending about a non-principal axis.",
    "The calculation does not evaluate combined axial, torsional, transverse-shear, pressure, or other loading.",
    "The calculation does not evaluate shear stress or transverse-shear deformation.",
    "The calculation does not evaluate curved-beam or deep-beam behavior.",
    "The calculation does not include local stress concentrations or local load introduction effects.",
    "The calculation does not evaluate residual, thermal, dynamic, impact, or cyclic stress.",
    "The calculation does not evaluate nonlinear elasticity or plastic behavior.",
    "The calculation does not evaluate material strength, allowable stress, yielding, or factor of safety.",
    "The calculation does not evaluate fatigue, fracture, creep, or stress relaxation.",
    "The calculation does not evaluate beam curvature, rotation, deflection, or system stiffness.",
    "The calculation does not evaluate buckling or other stability modes.",
    "The calculation does not establish design-code or regulatory compliance.",
]

_REFERENCES = [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, flexure formula for straight beams.",
    "F. P. Beer, E. R. Johnston Jr., J. T. DeWolf, and D. F. Mazurek, Mechanics of Materials, 8th Edition, stresses in beams under pure bending.",
]


def calculate_beam_bending(
    bending_moment_value: Real,
    bending_moment_unit: str,
    distance_from_neutral_axis_value: Real,
    distance_from_neutral_axis_unit: str,
    second_moment_of_area_value: Real,
    second_moment_of_area_unit: str,
    output_unit: str = "MPa",
) -> dict[str, Any]:
    """Calculate signed bending stress using ``σ = My / I``."""
    bending_moment = _validate_number(
        "bending_moment_value", bending_moment_value
    )
    distance = _validate_number(
        "distance_from_neutral_axis_value",
        distance_from_neutral_axis_value,
    )
    second_moment = _validate_number(
        "second_moment_of_area_value", second_moment_of_area_value
    )

    if distance < 0:
        raise ValueError(
            "distance_from_neutral_axis_value must be greater than or equal to zero"
        )
    if second_moment <= 0:
        raise ValueError("second_moment_of_area_value must be greater than zero")

    moment_factor = _conversion_factor(
        "bending_moment_unit",
        bending_moment_unit,
        _MOMENT_TO_NEWTON_MILLIMETRES,
    )
    distance_factor = _conversion_factor(
        "distance_from_neutral_axis_unit",
        distance_from_neutral_axis_unit,
        _DISTANCE_TO_MILLIMETRES,
    )
    second_moment_factor = _conversion_factor(
        "second_moment_of_area_unit",
        second_moment_of_area_unit,
        _SECOND_MOMENT_TO_MILLIMETRES_FOURTH,
    )
    output_factor = _conversion_factor(
        "output_unit", output_unit, _MEGAPASCALS_TO_OUTPUT
    )

    moment_newton_millimetres = _require_finite(
        "converted bending moment", bending_moment * moment_factor
    )
    distance_millimetres = _require_nonnegative_finite(
        "converted distance from neutral axis", distance * distance_factor
    )
    second_moment_millimetres_fourth = _require_positive_finite(
        "converted second moment of area",
        second_moment * second_moment_factor,
    )

    numerator = _require_finite(
        "bending stress numerator",
        moment_newton_millimetres * distance_millimetres,
    )
    if (
        moment_newton_millimetres != 0.0
        and distance_millimetres != 0.0
        and numerator == 0.0
    ):
        raise ValueError("bending stress numerator must not underflow to zero")

    stress_megapascals = _require_finite(
        "calculated bending stress",
        numerator / second_moment_millimetres_fourth,
    )
    if numerator != 0.0 and stress_megapascals == 0.0:
        raise ValueError("calculated bending stress must not underflow to zero")

    stress = _require_finite(
        "converted bending stress", stress_megapascals * output_factor
    )
    if stress_megapascals != 0.0 and stress == 0.0:
        raise ValueError("converted bending stress must not underflow to zero")

    if stress_megapascals > 0.0:
        stress_state = "tension"
    elif stress_megapascals < 0.0:
        stress_state = "compression"
    else:
        stress_megapascals = 0.0
        stress = 0.0
        stress_state = "zero"

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
            "bending_moment": {
                "value": bending_moment,
                "unit": bending_moment_unit,
            },
            "distance_from_neutral_axis": {
                "value": distance,
                "unit": distance_from_neutral_axis_unit,
            },
            "second_moment_of_area": {
                "value": second_moment,
                "unit": second_moment_of_area_unit,
            },
            "output_unit": output_unit,
        },
        "results": {
            "bending_stress": {"value": stress, "unit": output_unit},
            "stress_state": stress_state,
        },
        "governing_equation": {
            "symbolic": GOVERNING_EQUATION,
            "substitution": (
                f"σ = ({moment_newton_millimetres:.17g} N·mm)"
                f"({distance_millimetres:.17g} mm) / "
                f"{second_moment_millimetres_fourth:.17g} mm^4"
            ),
        },
        "assumptions": list(_ASSUMPTIONS),
        "warnings": list(_WARNINGS),
        "limitations": list(_LIMITATIONS),
        "references": list(_REFERENCES),
    }


def _validate_number(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    try:
        numeric_value = float(value)
    except OverflowError:
        raise ValueError(f"{name} must be representable as a finite float") from None

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


def _require_finite(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    return value


def _require_nonnegative_finite(name: str, value: float) -> float:
    finite_value = _require_finite(name, value)
    if finite_value < 0.0:
        raise ValueError(f"{name} must be greater than or equal to zero")

    return finite_value


def _require_positive_finite(name: str, value: float) -> float:
    finite_value = _require_finite(name, value)
    if finite_value <= 0.0:
        raise ValueError(f"{name} must be greater than zero")

    return finite_value
