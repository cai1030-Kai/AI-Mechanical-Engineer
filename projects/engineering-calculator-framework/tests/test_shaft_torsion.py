"""Tests for the solid circular shaft torsion calculator."""

import json
import math

import pytest

from engineering_calculator.calculators.shaft_torsion import (
    calculate_shaft_torsion,
)


def test_si_reference_calculation() -> None:
    result = calculate_shaft_torsion(500, "N·m", 40, "mm")

    assert result["results"]["polar_moment_of_inertia"] == {
        "value": pytest.approx(251_327.412287183),
        "unit": "mm⁴",
    }
    assert result["results"]["maximum_shear_stress"] == {
        "value": pytest.approx(39.7887357729738),
        "unit": "MPa",
    }


def test_us_customary_reference_calculation() -> None:
    result = calculate_shaft_torsion(
        1_000,
        "lbf·in",
        2,
        "in",
        output_unit="psi",
    )

    assert result["results"]["polar_moment_of_inertia"] == {
        "value": pytest.approx(1.5707963267949),
        "unit": "in⁴",
    }
    assert result["results"]["maximum_shear_stress"] == {
        "value": pytest.approx(636.619772367581),
        "unit": "psi",
    }


def test_returns_canonical_contract_result() -> None:
    result = calculate_shaft_torsion(500, "N·m", 40, "mm")

    assert set(result) == {
        "calculator",
        "inputs",
        "results",
        "governing_equation",
        "assumptions",
        "warnings",
        "limitations",
        "references",
    }
    assert result["calculator"] == {
        "id": "stress.shaft_torsion",
        "name": "Solid Circular Shaft Torsional Stress Calculator",
        "version": "0.1.0",
        "category": "Stress Analysis",
        "engineering_domain": "Mechanics of Materials",
        "purpose": (
            "Calculate the polar moment of inertia and maximum elastic "
            "torsional shear stress in a solid circular shaft subjected to "
            "pure torque"
        ),
        "reference_equation": (
            "J = πd⁴ / 32; τmax = Tc / J = 16T / (πd³)"
        ),
    }
    assert result["inputs"] == {
        "torque": {"value": 500.0, "unit": "N·m"},
        "diameter": {"value": 40.0, "unit": "mm"},
        "output_unit": "MPa",
    }
    assert result["assumptions"]
    assert result["warnings"] == []
    assert result["limitations"]
    assert result["references"]
    assert json.loads(json.dumps(result)) == result


def test_zero_torque_returns_zero_stress_and_positive_polar_moment() -> None:
    result = calculate_shaft_torsion(0, "N·mm", 40, "mm")

    assert result["results"]["polar_moment_of_inertia"]["value"] > 0
    assert result["results"]["maximum_shear_stress"] == {
        "value": 0.0,
        "unit": "MPa",
    }


@pytest.mark.parametrize(
    ("torque_value", "torque_unit"),
    [
        (1.0, "N·mm"),
        (0.001, "N·m"),
        (1.0 / 112.9848290276167, "lbf·in"),
        (1.0 / 1_355.8179483314004, "lbf·ft"),
    ],
)
def test_each_accepted_torque_unit_is_equivalent(
    torque_value: float,
    torque_unit: str,
) -> None:
    result = calculate_shaft_torsion(
        torque_value,
        torque_unit,
        10,
        "mm",
    )
    expected_stress = 16.0 / (math.pi * 10.0**3)

    assert result["results"]["maximum_shear_stress"]["value"] == pytest.approx(
        expected_stress
    )


@pytest.mark.parametrize(
    ("diameter_value", "diameter_unit", "polar_moment_unit"),
    [
        (10.0, "mm", "mm⁴"),
        (1.0, "cm", "cm⁴"),
        (0.01, "m", "m⁴"),
        (10.0 / 25.4, "in", "in⁴"),
    ],
)
def test_each_accepted_diameter_unit_is_equivalent(
    diameter_value: float,
    diameter_unit: str,
    polar_moment_unit: str,
) -> None:
    result = calculate_shaft_torsion(
        1_000,
        "N·mm",
        diameter_value,
        diameter_unit,
    )
    expected_stress = 16_000.0 / (math.pi * 10.0**3)
    expected_polar_moment = math.pi * diameter_value**4 / 32.0

    assert result["results"]["maximum_shear_stress"]["value"] == pytest.approx(
        expected_stress
    )
    assert result["results"]["polar_moment_of_inertia"] == {
        "value": pytest.approx(expected_polar_moment),
        "unit": polar_moment_unit,
    }


@pytest.mark.parametrize(
    ("output_unit", "expected_value"),
    [
        ("Pa", 1_000_000.0),
        ("kPa", 1_000.0),
        ("MPa", 1.0),
        ("GPa", 0.001),
        ("psi", 145.03773773020923),
        ("ksi", 0.14503773773020923),
    ],
)
def test_each_accepted_output_unit_is_equivalent(
    output_unit: str,
    expected_value: float,
) -> None:
    diameter = 10.0
    torque_for_one_mpa = math.pi * diameter**3 / 16.0
    result = calculate_shaft_torsion(
        torque_for_one_mpa,
        "N·mm",
        diameter,
        "mm",
        output_unit,
    )

    assert result["results"]["maximum_shear_stress"] == {
        "value": pytest.approx(expected_value),
        "unit": output_unit,
    }


@pytest.mark.parametrize("invalid_torque", [-1, -0.001])
def test_rejects_negative_torque(invalid_torque: float) -> None:
    with pytest.raises(
        ValueError,
        match="torque_value must be greater than or equal to zero",
    ):
        calculate_shaft_torsion(invalid_torque, "N·mm", 10, "mm")


@pytest.mark.parametrize("invalid_diameter", [0, -1])
def test_rejects_nonpositive_diameter(invalid_diameter: float) -> None:
    with pytest.raises(
        ValueError,
        match="diameter_value must be greater than zero",
    ):
        calculate_shaft_torsion(1_000, "N·mm", invalid_diameter, "mm")


@pytest.mark.parametrize(
    "invalid_value",
    [float("nan"), float("inf"), -float("inf")],
)
@pytest.mark.parametrize("input_name", ["torque_value", "diameter_value"])
def test_rejects_nonfinite_inputs(
    input_name: str,
    invalid_value: float,
) -> None:
    arguments = {
        "torque_value": 1_000,
        "torque_unit": "N·mm",
        "diameter_value": 10,
        "diameter_unit": "mm",
    }
    arguments[input_name] = invalid_value

    with pytest.raises(ValueError, match=f"{input_name} must be finite"):
        calculate_shaft_torsion(**arguments)


@pytest.mark.parametrize("input_name", ["torque_value", "diameter_value"])
@pytest.mark.parametrize("invalid_value", ["not-a-number", None, True])
def test_rejects_non_numeric_inputs(
    input_name: str,
    invalid_value: object,
) -> None:
    arguments = {
        "torque_value": 1_000,
        "torque_unit": "N·mm",
        "diameter_value": 10,
        "diameter_unit": "mm",
    }
    arguments[input_name] = invalid_value

    with pytest.raises(TypeError, match=f"{input_name} must be a real number"):
        calculate_shaft_torsion(**arguments)


@pytest.mark.parametrize(
    ("unit_argument", "invalid_unit", "expected_message"),
    [
        ("torque_unit", "N", "unsupported torque_unit"),
        ("diameter_unit", "mm²", "unsupported diameter_unit"),
        ("output_unit", "N", "unsupported output_unit"),
    ],
)
def test_rejects_invalid_units(
    unit_argument: str,
    invalid_unit: str,
    expected_message: str,
) -> None:
    arguments = {
        "torque_value": 1_000,
        "torque_unit": "N·mm",
        "diameter_value": 10,
        "diameter_unit": "mm",
        "output_unit": "MPa",
    }
    arguments[unit_argument] = invalid_unit

    with pytest.raises(ValueError, match=expected_message):
        calculate_shaft_torsion(**arguments)


@pytest.mark.parametrize(
    ("unit_argument", "expected_message"),
    [
        ("torque_unit", "torque_unit must be a string"),
        ("diameter_unit", "diameter_unit must be a string"),
        ("output_unit", "output_unit must be a string"),
    ],
)
def test_rejects_non_string_units(
    unit_argument: str,
    expected_message: str,
) -> None:
    arguments = {
        "torque_value": 1_000,
        "torque_unit": "N·mm",
        "diameter_value": 10,
        "diameter_unit": "mm",
        "output_unit": "MPa",
    }
    arguments[unit_argument] = None

    with pytest.raises(TypeError, match=expected_message):
        calculate_shaft_torsion(**arguments)


def test_rejects_missing_required_input() -> None:
    with pytest.raises(TypeError, match="diameter_unit"):
        calculate_shaft_torsion(
            torque_value=1_000,
            torque_unit="N·mm",
            diameter_value=10,
        )


@pytest.mark.parametrize(
    (
        "torque_value",
        "torque_unit",
        "diameter_value",
        "diameter_unit",
        "output_unit",
        "expected_message",
    ),
    [
        (1e308, "N·m", 10, "mm", "MPa", "converted torque must be finite"),
        (
            1_000,
            "N·mm",
            1e308,
            "m",
            "MPa",
            "converted diameter must be finite",
        ),
        (
            1_000,
            "N·mm",
            1e100,
            "mm",
            "MPa",
            "diameter fourth power must be finite",
        ),
        (
            1,
            "N·mm",
            5e-324,
            "mm",
            "MPa",
            "diameter cubed must be greater than zero",
        ),
        (
            1e308,
            "N·mm",
            1,
            "mm",
            "MPa",
            "calculated maximum shear stress must be finite",
        ),
        (
            math.pi * 1e306 / 16,
            "N·mm",
            1,
            "mm",
            "Pa",
            "converted maximum shear stress must be finite",
        ),
    ],
)
def test_rejects_nonfinite_or_underflowed_calculation_values(
    torque_value: float,
    torque_unit: str,
    diameter_value: float,
    diameter_unit: str,
    output_unit: str,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        calculate_shaft_torsion(
            torque_value,
            torque_unit,
            diameter_value,
            diameter_unit,
            output_unit,
        )


def test_substitution_preserves_traceable_precision() -> None:
    result = calculate_shaft_torsion(1, "lbf·in", 1, "in")

    assert result["governing_equation"]["substitution"] == (
        "J = π(25.399999999999999 mm)⁴ / 32; "
        "τmax = 16(112.9848290276167 N·mm) / "
        "(π(25.399999999999999 mm)³)"
    )


def test_repeated_execution_is_deterministic() -> None:
    arguments = {
        "torque_value": 500,
        "torque_unit": "N·m",
        "diameter_value": 40,
        "diameter_unit": "mm",
        "output_unit": "MPa",
    }

    assert calculate_shaft_torsion(**arguments) == calculate_shaft_torsion(
        **arguments
    )
