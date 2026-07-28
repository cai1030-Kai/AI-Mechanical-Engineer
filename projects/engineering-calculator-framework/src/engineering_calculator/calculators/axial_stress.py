"""Average axial normal stress calculation."""

import math
from numbers import Real
from typing import Any

from engineering_calculator.calculators._validation import (
    conversion_factor,
    require_finite,
    require_positive_finite,
)

CALCULATOR_ID = "stress.axial"
CALCULATOR_NAME = "Axial Stress Calculator"
CALCULATOR_VERSION = "0.1.0"
CALCULATOR_CATEGORY = "Stress Analysis"
ENGINEERING_DOMAIN = "Mechanics of Materials"
CALCULATOR_PURPOSE = (
    "Calculate the signed average normal stress in a member subjected to a "
    "concentric axial force"
)
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

_LIMITATIONS = [
    "The calculation does not account for bending caused by eccentric loading.",
    "The calculation does not evaluate shear stress or torsional stress.",
    "The calculation does not evaluate local stress concentrations.",
    "The calculation does not evaluate local bearing, contact, or crushing stress.",
    "The calculation does not evaluate nonuniform stress near load introduction points.",
    "The calculation does not evaluate buckling under compression.",
    "The calculation does not evaluate plastic or nonlinear material behavior.",
    "The calculation assumes small deformation and unchanged cross-sectional area.",
    "The calculation does not evaluate residual, thermal, dynamic, impact, or cyclic stress.",
    "The calculation does not evaluate fatigue, fracture, creep, or stress relaxation.",
    "The calculation does not evaluate material strength, allowable stress, or factor of safety.",
    "The calculation does not establish design-code or regulatory compliance.",
]

_REFERENCES = [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, normal stress under axial loading.",
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

    force_factor = conversion_factor(
        "force_unit", force_unit, _FORCE_TO_NEWTONS
    )
    area_factor = conversion_factor(
        "area_unit", area_unit, _AREA_TO_SQUARE_MILLIMETRES
    )
    output_factor = conversion_factor(
        "output_unit", output_unit, _MEGAPASCALS_TO_OUTPUT
    )

    force_newtons = require_finite(
        "converted force", force * force_factor
    )
    area_square_millimetres = require_positive_finite(
        "converted area", area * area_factor
    )

    stress_megapascals = require_finite(
        "calculated stress", force_newtons / area_square_millimetres
    )
    stress = require_finite(
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
            "category": CALCULATOR_CATEGORY,
            "engineering_domain": ENGINEERING_DOMAIN,
            "purpose": CALCULATOR_PURPOSE,
            "reference_equation": GOVERNING_EQUATION,
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
