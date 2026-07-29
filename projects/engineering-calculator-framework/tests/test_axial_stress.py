"""Unit tests for the axial stress calculator."""

import json

import pytest

from engineering_calculator.calculators.axial_stress import (
    calculate_axial_stress,
)

SQUARE_MILLIMETRES = "mm\u00b2"


def test_calculates_normal_tensile_loading() -> None:
    result = calculate_axial_stress(
        force_value=10,
        force_unit="kN",
        area_value=500,
        area_unit=SQUARE_MILLIMETRES,
    )

    assert result["calculator"] == {
        "id": "stress.axial",
        "name": "Axial Stress Calculator",
        "version": "0.1.0",
        "category": "Stress Analysis",
        "engineering_domain": "Mechanics of Materials",
        "purpose": (
            "Calculate the signed average normal stress in a member subjected "
            "to a concentric axial force"
        ),
        "reference_equation": "σ = F / A",
    }
    assert result["inputs"] == {
        "force": {"value": 10.0, "unit": "kN"},
        "area": {"value": 500.0, "unit": SQUARE_MILLIMETRES},
    }
    assert result["results"] == {
        "axial_stress": {"value": 20.0, "unit": "MPa"},
        "loading_state": "tension",
    }
    assert result["governing_equation"]["symbolic"] == "\u03c3 = F / A"
    assert result["assumptions"]
    assert result["warnings"] == []
    assert result["limitations"]
    assert result["references"]


def test_preserves_compression_sign_convention() -> None:
    result = calculate_axial_stress(
        force_value=-10,
        force_unit="kN",
        area_value=500,
        area_unit=SQUARE_MILLIMETRES,
    )

    assert result["results"]["axial_stress"] == {
        "value": -20.0,
        "unit": "MPa",
    }
    assert result["results"]["loading_state"] == "compression"


def test_zero_load_returns_zero_stress() -> None:
    result = calculate_axial_stress(
        force_value=0,
        force_unit="N",
        area_value=500,
        area_unit=SQUARE_MILLIMETRES,
    )

    assert result["results"]["axial_stress"] == {
        "value": 0.0,
        "unit": "MPa",
    }
    assert result["results"]["loading_state"] == "unloaded"


@pytest.mark.parametrize("invalid_area", [0, -1])
def test_rejects_nonpositive_area(invalid_area: int) -> None:
    with pytest.raises(
        ValueError,
        match="area_value must be greater than zero",
    ):
        calculate_axial_stress(
            force_value=10,
            force_unit="kN",
            area_value=invalid_area,
            area_unit=SQUARE_MILLIMETRES,
        )


@pytest.mark.parametrize(
    ("unit_argument", "invalid_unit", "expected_message"),
    [
        ("force_unit", "kg", "unsupported force_unit"),
        ("area_unit", "mm", "unsupported area_unit"),
        ("output_unit", "N", "unsupported output_unit"),
    ],
)
def test_rejects_invalid_units(
    unit_argument: str,
    invalid_unit: str,
    expected_message: str,
) -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
        "output_unit": "MPa",
    }
    arguments[unit_argument] = invalid_unit

    with pytest.raises(ValueError, match=expected_message):
        calculate_axial_stress(**arguments)

def test_si_and_us_customary_inputs_are_equivalent() -> None:
    si_result = calculate_axial_stress(
        force_value=4_448.2216152605,
        force_unit="N",
        area_value=1_290.32,
        area_unit=SQUARE_MILLIMETRES,
        output_unit="psi",
    )
    us_result = calculate_axial_stress(
        force_value=1_000,
        force_unit="lbf",
        area_value=2,
        area_unit="in\u00b2",
        output_unit="psi",
    )

    assert si_result["results"]["axial_stress"]["value"] == pytest.approx(500)
    assert us_result["results"]["axial_stress"]["value"] == pytest.approx(500)
    assert si_result["results"]["axial_stress"]["value"] == pytest.approx(
        us_result["results"]["axial_stress"]["value"]
    )


@pytest.mark.parametrize(
    ("output_unit", "expected_value"),
    [
        ("Pa", 1_000_000),
        ("kPa", 1_000),
        ("MPa", 1),
        ("GPa", 0.001),
        ("psi", 145.03773773020923),
        ("ksi", 0.14503773773020923),
    ],
)
def test_converts_to_each_accepted_output_unit(
    output_unit: str,
    expected_value: float,
) -> None:
    result = calculate_axial_stress(
        force_value=1,
        force_unit="N",
        area_value=1,
        area_unit=SQUARE_MILLIMETRES,
        output_unit=output_unit,
    )

    assert result["results"]["axial_stress"] == {
        "value": pytest.approx(expected_value),
        "unit": output_unit,
    }


@pytest.mark.parametrize(
    "invalid_value",
    [float("nan"), float("inf"), -float("inf")],
)
@pytest.mark.parametrize("input_name", ["force_value", "area_value"])
def test_rejects_nonfinite_inputs(
    input_name: str,
    invalid_value: float,
) -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
    }
    arguments[input_name] = invalid_value

    with pytest.raises(ValueError, match=f"{input_name} must be finite"):
        calculate_axial_stress(**arguments)


@pytest.mark.parametrize("input_name", ["force_value", "area_value"])
def test_rejects_oversized_integer_inputs(input_name: str) -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
    }
    arguments[input_name] = 10**400

    with pytest.raises(
        ValueError,
        match=rf"^{input_name} must be representable as a finite float$",
    ) as exc_info:
        calculate_axial_stress(**arguments)

    assert isinstance(exc_info.value.__cause__, OverflowError)


@pytest.mark.parametrize("input_name", ["force_value", "area_value"])
@pytest.mark.parametrize("invalid_value", ["not-a-number", None])
def test_rejects_non_numeric_inputs(
    input_name: str,
    invalid_value: object,
) -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
    }
    arguments[input_name] = invalid_value

    with pytest.raises(TypeError, match=f"{input_name} must be a real number"):
        calculate_axial_stress(**arguments)


@pytest.mark.parametrize(
    (
        "force_value",
        "force_unit",
        "area_value",
        "area_unit",
        "output_unit",
        "message",
    ),
    [
        (1e308, "kN", 1, SQUARE_MILLIMETRES, "MPa", "converted force"),
        (1e308, "N", 1e-300, SQUARE_MILLIMETRES, "MPa", "calculated stress"),
        (1e308, "N", 1, SQUARE_MILLIMETRES, "Pa", "converted output stress"),
    ],
)
def test_rejects_nonfinite_intermediate_results(
    force_value: float,
    force_unit: str,
    area_value: float,
    area_unit: str,
    output_unit: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=f"{message} must be finite"):
        calculate_axial_stress(
            force_value=force_value,
            force_unit=force_unit,
            area_value=area_value,
            area_unit=area_unit,
            output_unit=output_unit,
        )

def test_canonical_result_contract() -> None:
    result = calculate_axial_stress(10, "kN", 500, SQUARE_MILLIMETRES)

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
    assert set(result["calculator"]) == {
        "id",
        "name",
        "version",
        "category",
        "engineering_domain",
        "purpose",
        "reference_equation",
    }
    assert result["limitations"]
    assert result["references"]
    assert json.loads(json.dumps(result)) == result


@pytest.mark.parametrize(
    ("force_value", "force_unit"),
    [
        (1.0, "N"),
        (0.001, "kN"),
        (1.0 / 4.4482216152605, "lbf"),
        (1.0 / 4_448.2216152605, "kip"),
    ],
)
def test_each_accepted_force_unit_is_equivalent(
    force_value: float,
    force_unit: str,
) -> None:
    result = calculate_axial_stress(
        force_value,
        force_unit,
        1,
        SQUARE_MILLIMETRES,
    )

    assert result["results"]["axial_stress"]["value"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("area_value", "area_unit"),
    [
        (1.0, "mm\u00b2"),
        (0.01, "cm\u00b2"),
        (0.000001, "m\u00b2"),
        (1.0 / 645.16, "in\u00b2"),
    ],
)
def test_each_accepted_area_unit_is_equivalent(
    area_value: float,
    area_unit: str,
) -> None:
    result = calculate_axial_stress(1, "N", area_value, area_unit)

    assert result["results"]["axial_stress"]["value"] == pytest.approx(1.0)


def test_rejects_nonfinite_converted_area() -> None:
    with pytest.raises(ValueError, match="converted area must be finite"):
        calculate_axial_stress(1, "N", 1e308, "m\u00b2")


@pytest.mark.parametrize(
    ("unit_argument", "expected_message"),
    [
        ("force_unit", "force_unit must be a string"),
        ("area_unit", "area_unit must be a string"),
        ("output_unit", "output_unit must be a string"),
    ],
)
def test_rejects_non_string_unit_types(
    unit_argument: str,
    expected_message: str,
) -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
        "output_unit": "MPa",
    }
    arguments[unit_argument] = None

    with pytest.raises(TypeError, match=expected_message):
        calculate_axial_stress(**arguments)


def test_rejects_missing_required_input() -> None:
    with pytest.raises(TypeError, match="area_unit"):
        calculate_axial_stress(
            force_value=10,
            force_unit="kN",
            area_value=500,
        )


def test_substitution_preserves_traceable_precision() -> None:
    result = calculate_axial_stress(1, "lbf", 1, SQUARE_MILLIMETRES)
    converted_force = 4.4482216152605

    assert result["governing_equation"]["substitution"] == (
        f"σ = {converted_force:.17g} N / 1 mm²"
    )


def test_repeated_execution_is_deterministic() -> None:
    arguments = {
        "force_value": 10,
        "force_unit": "kN",
        "area_value": 500,
        "area_unit": SQUARE_MILLIMETRES,
        "output_unit": "MPa",
    }

    assert calculate_axial_stress(**arguments) == calculate_axial_stress(
        **arguments
    )
