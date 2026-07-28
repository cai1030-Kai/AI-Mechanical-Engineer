"""Euler elastic column buckling calculation."""

import math
from numbers import Real
from typing import Any

CALCULATOR_ID = "stability.euler_buckling"
CALCULATOR_NAME = "Euler Buckling Critical Load Calculator"
CALCULATOR_VERSION = "0.1.0"
CALCULATOR_CATEGORY = "Stability Analysis"
ENGINEERING_DOMAIN = "Structural Stability / Mechanics of Materials"
CALCULATOR_PURPOSE = (
    "Calculate the ideal elastic critical buckling load of a slender, straight "
    "column using Euler buckling theory"
)
GOVERNING_EQUATION = "L_eff = K * L; P_cr = pi^2 * E * I / L_eff^2"

_MODULUS_TO_MEGAPASCALS = {
    "Pa": 1e-6,
    "kPa": 1e-3,
    "MPa": 1.0,
    "GPa": 1_000.0,
    "psi": 0.006894757293168361,
    "ksi": 6.894757293168361,
}
_SECOND_MOMENT_TO_MM4 = {
    "mm^4": 1.0,
    "cm^4": 10_000.0,
    "m^4": 1e12,
    "in^4": 416_231.4256,
}
_LENGTH_TO_MM = {"mm": 1.0, "cm": 10.0, "m": 1_000.0, "in": 25.4}
_NEWTONS_TO_OUTPUT = {
    "N": 1.0,
    "kN": 0.001,
    "MN": 0.000001,
    "lbf": 0.22480894387096072,
    "kip": 0.00022480894387096072,
}

_ASSUMPTIONS = [
    "The column is initially straight, prismatic, slender, and perfectly aligned.",
    "The load is concentric and compressive through the centroidal axis.",
    "The material is homogeneous, isotropic, and linearly elastic.",
    "Deflections are small before buckling and the column remains elastic.",
    "The supplied second moment of area corresponds to the evaluated buckling axis.",
    "The effective-length factor represents the actual end restraints and bracing.",
]
_WARNINGS = [
    "Euler buckling is valid only for sufficiently slender columns that remain elastic up to buckling.",
    "The supplied second moment of area must correspond to the actual buckling axis.",
    "The effective length factor depends on real end restraints and may differ from idealized textbook values.",
    "The calculator does not determine whether yielding or inelastic buckling occurs first.",
    "The result is an ideal theoretical critical load, not an allowable design load.",
]
_LIMITATIONS = [
    "The calculation does not evaluate yielding, inelastic buckling, the Johnson parabolic formula, local buckling, torsional buckling, or flexural-torsional buckling.",
    "The calculation does not include initial crookedness, load eccentricity, residual stress, variable cross-section, combined loading, imperfections, or second-order design effects.",
    "The calculation does not determine the effective-length factor or section properties.",
    "The result is an ideal bifurcation load, not an allowable load or design strength.",
    "The calculation does not establish a slenderness-ratio validity decision, factor of safety, or design-code compliance.",
]
_REFERENCES = [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, chapter on column buckling.",
    "F. P. Beer, E. R. Johnston Jr., J. T. DeWolf, and D. F. Mazurek, Mechanics of Materials, 8th Edition, chapter on columns.",
    "S. P. Timoshenko and J. M. Gere, Theory of Elastic Stability, 2nd Edition, chapter on buckling of bars.",
]
_BUCKLING_AXIS_TRACEABILITY = (
    "This result applies to the buckling axis represented by the "
    "caller-supplied second moment of area, I; other relevant axes must be "
    "evaluated separately."
)


def calculate_euler_buckling(
    elastic_modulus_value: Real,
    elastic_modulus_unit: str,
    second_moment_of_area_value: Real,
    second_moment_of_area_unit: str,
    unsupported_length_value: Real,
    unsupported_length_unit: str,
    effective_length_factor: Real,
    output_unit: str = "kN",
) -> dict[str, Any]:
    """Calculate ideal Euler critical load using the effective-length form."""
    modulus = _positive_number("elastic_modulus_value", elastic_modulus_value)
    second_moment = _positive_number(
        "second_moment_of_area_value", second_moment_of_area_value
    )
    length = _positive_number("unsupported_length_value", unsupported_length_value)
    factor = _positive_number("effective_length_factor", effective_length_factor)

    modulus_mpa = _checked_product(
        "converted elastic modulus",
        modulus,
        _conversion("elastic_modulus_unit", elastic_modulus_unit, _MODULUS_TO_MEGAPASCALS),
    )
    second_moment_mm4 = _checked_product(
        "converted second moment of area",
        second_moment,
        _conversion("second_moment_of_area_unit", second_moment_of_area_unit, _SECOND_MOMENT_TO_MM4),
    )
    length_mm = _checked_product(
        "converted unsupported length",
        length,
        _conversion("unsupported_length_unit", unsupported_length_unit, _LENGTH_TO_MM),
    )
    output_factor = _conversion("output_unit", output_unit, _NEWTONS_TO_OUTPUT)

    effective_length_mm = _checked_product("effective length", factor, length_mm)
    effective_length_squared = _checked_power(
        "squared effective length", effective_length_mm, 2
    )
    flexural_rigidity = _checked_product(
        "flexural rigidity", modulus_mpa, second_moment_mm4
    )
    numerator = _checked_product(
        "Euler critical load numerator", math.pi**2, flexural_rigidity
    )
    critical_load_newtons = _checked_division(
        "calculated Euler critical load", numerator, effective_length_squared
    )
    critical_load = _checked_product(
        "converted Euler critical load", critical_load_newtons, output_factor
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
            "elastic_modulus": {"value": modulus, "unit": elastic_modulus_unit},
            "second_moment_of_area": {"value": second_moment, "unit": second_moment_of_area_unit},
            "unsupported_length": {"value": length, "unit": unsupported_length_unit},
            "effective_length_factor": factor,
            "output_unit": output_unit,
        },
        "results": {
            "effective_length_mm": {"value": effective_length_mm, "unit": "mm"},
            "critical_load_newtons": {"value": critical_load_newtons, "unit": "N"},
            "critical_load": {"value": critical_load, "unit": output_unit},
            "buckling_axis_traceability": _BUCKLING_AXIS_TRACEABILITY,
        },
        "governing_equation": {
            "symbolic": GOVERNING_EQUATION,
            "substitution": (
                f"L_eff = {factor:.17g} * {length_mm:.17g} mm = "
                f"{effective_length_mm:.17g} mm; "
                f"P_cr = pi^2 * ({modulus_mpa:.17g} MPa) * "
                f"({second_moment_mm4:.17g} mm^4) / "
                f"({effective_length_mm:.17g} mm)^2 = "
                f"{critical_load_newtons:.17g} N"
            ),
        },
        "assumptions": list(_ASSUMPTIONS),
        "warnings": list(_WARNINGS),
        "limitations": list(_LIMITATIONS),
        "references": list(_REFERENCES),
    }


def _positive_number(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    try:
        number = float(value)
    except OverflowError:
        raise ValueError(f"{name} must be representable as a finite float") from None
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if number <= 0.0:
        raise ValueError(f"{name} must be greater than zero")
    return number


def _conversion(name: str, unit: str, conversions: dict[str, float]) -> float:
    if not isinstance(unit, str):
        raise TypeError(f"{name} must be a string")
    try:
        return conversions[unit]
    except KeyError:
        supported_units = ", ".join(conversions)
        raise ValueError(
            f"unsupported {name} {unit!r}; supported units: {supported_units}"
        ) from None


def _positive_finite(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value <= 0.0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _checked_product(name: str, left: float, right: float) -> float:
    return _positive_finite(name, left * right)


def _checked_power(name: str, value: float, exponent: int) -> float:
    try:
        result = value**exponent
    except OverflowError:
        raise ValueError(f"{name} must be finite") from None
    return _positive_finite(name, result)


def _checked_division(name: str, numerator: float, denominator: float) -> float:
    return _positive_finite(name, numerator / denominator)
