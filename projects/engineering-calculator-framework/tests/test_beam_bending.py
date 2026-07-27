"""Tests for the beam bending stress calculator."""

import json

import pytest

from engineering_calculator.calculators.beam_bending import (
    calculate_beam_bending,
)


def _base_arguments() -> dict[str, object]:
    return {
        "bending_moment_value": 5_000,
        "bending_moment_unit": "N·m",
        "distance_from_neutral_axis_value": 50,
        "distance_from_neutral_axis_unit": "mm",
        "second_moment_of_area_value": 8_000_000,
        "second_moment_of_area_unit": "mm^4",
        "output_unit": "MPa",
    }


def test_si_reference_example() -> None:
    result = calculate_beam_bending(**_base_arguments())

    assert result["results"] == {
        "bending_stress": {"value": 31.25, "unit": "MPa"},
        "stress_state": "tension",
    }


def test_us_customary_reference_example() -> None:
    result = calculate_beam_bending(
        -12_000,
        "lbf·in",
        3,
        "in",
        200,
        "in^4",
        "psi",
    )

    assert result["results"] == {
        "bending_stress": {
            "value": pytest.approx(-180.0),
            "unit": "psi",
        },
        "stress_state": "compression",
    }


def test_reverse_verification_recovers_si_moment() -> None:
    result = calculate_beam_bending(**_base_arguments())
    stress_mpa = result["results"]["bending_stress"]["value"]
    recovered_moment_n_mm = stress_mpa * 8_000_000 / 50

    assert recovered_moment_n_mm == pytest.approx(5_000_000)
    assert recovered_moment_n_mm / 1_000 == pytest.approx(5_000)


@pytest.mark.parametrize(
    ("moment", "expected_state", "expected_sign"),
    [(1_000, "tension", 1), (-1_000, "compression", -1)],
)
def test_moment_sign_controls_stress(
    moment: float,
    expected_state: str,
    expected_sign: int,
) -> None:
    result = calculate_beam_bending(moment, "N·mm", 10, "mm", 100, "mm^4")

    assert result["results"]["bending_stress"]["value"] == 100 * expected_sign
    assert result["results"]["stress_state"] == expected_state


def test_zero_moment_returns_exact_zero() -> None:
    result = calculate_beam_bending(0, "N·mm", 10, "mm", 100, "mm^4")

    assert result["results"] == {
        "bending_stress": {"value": 0.0, "unit": "MPa"},
        "stress_state": "zero",
    }


def test_zero_distance_returns_exact_zero() -> None:
    result = calculate_beam_bending(1_000, "N·mm", 0, "mm", 100, "mm^4")

    assert result["results"] == {
        "bending_stress": {"value": 0.0, "unit": "MPa"},
        "stress_state": "zero",
    }


@pytest.mark.parametrize(
    ("value", "unit"),
    [
        (1.0, "N·mm"),
        (0.001, "N·m"),
        (1.0 / 112.9848290276167, "lbf·in"),
        (1.0 / 1_355.8179483314004, "lbf·ft"),
    ],
)
def test_every_accepted_moment_unit(value: float, unit: str) -> None:
    result = calculate_beam_bending(value, unit, 1, "mm", 1, "mm^4")

    assert result["results"]["bending_stress"]["value"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("value", "unit"),
    [(1.0, "mm"), (0.1, "cm"), (0.001, "m"), (1.0 / 25.4, "in")],
)
def test_every_accepted_distance_unit(value: float, unit: str) -> None:
    result = calculate_beam_bending(1, "N·mm", value, unit, 1, "mm^4")

    assert result["results"]["bending_stress"]["value"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("value", "unit"),
    [
        (1.0, "mm^4"),
        (0.0001, "cm^4"),
        (1e-12, "m^4"),
        (1.0 / 416_231.4256, "in^4"),
    ],
)
def test_every_accepted_second_moment_unit(value: float, unit: str) -> None:
    result = calculate_beam_bending(1, "N·mm", 1, "mm", value, unit)

    assert result["results"]["bending_stress"]["value"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        ("Pa", 1_000_000.0),
        ("kPa", 1_000.0),
        ("MPa", 1.0),
        ("GPa", 0.001),
        ("psi", 145.03773773020923),
        ("ksi", 0.14503773773020923),
    ],
)
def test_every_accepted_stress_output_unit(unit: str, expected: float) -> None:
    result = calculate_beam_bending(1, "N·mm", 1, "mm", 1, "mm^4", unit)

    assert result["results"]["bending_stress"] == {
        "value": pytest.approx(expected),
        "unit": unit,
    }


def test_equivalent_si_and_us_customary_inputs() -> None:
    si_result = calculate_beam_bending(**_base_arguments())
    us_result = calculate_beam_bending(
        5_000_000 / 112.9848290276167,
        "lbf·in",
        50 / 25.4,
        "in",
        8_000_000 / 416_231.4256,
        "in^4",
        "MPa",
    )

    assert si_result["results"]["bending_stress"]["value"] == pytest.approx(
        us_result["results"]["bending_stress"]["value"]
    )


def test_canonical_contract_structure() -> None:
    result = calculate_beam_bending(**_base_arguments())

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
        "id": "stress.beam_bending",
        "name": "Beam Bending Stress Calculator",
        "version": "0.1.0",
        "category": "Stress Analysis",
        "engineering_domain": "Mechanics of Materials",
        "purpose": (
            "Calculate signed linear-elastic normal stress at a specified "
            "distance from the neutral axis of a straight beam in pure "
            "bending about one principal centroidal axis"
        ),
        "reference_equation": "σ = My / I",
    }
    assert result["inputs"] == {
        "bending_moment": {"value": 5_000.0, "unit": "N·m"},
        "distance_from_neutral_axis": {"value": 50.0, "unit": "mm"},
        "second_moment_of_area": {"value": 8_000_000.0, "unit": "mm^4"},
        "output_unit": "MPa",
    }


def test_required_warnings_are_returned() -> None:
    warnings = calculate_beam_bending(**_base_arguments())["warnings"]

    assert any(
        "same bending axis and section orientation" in warning
        for warning in warnings
    )
    assert any(
        "different bending-moment sign conventions" in warning
        for warning in warnings
    )


def test_assumptions_limitations_and_references_are_returned() -> None:
    result = calculate_beam_bending(**_base_arguments())

    assert any("straight beam" in item for item in result["assumptions"])
    assert any("pure bending" in item for item in result["assumptions"])
    assert any("section geometry" in item for item in result["limitations"])
    assert any("combined axial" in item for item in result["limitations"])
    assert any("deflection" in item for item in result["limitations"])
    assert any("Hibbeler" in item for item in result["references"])
    assert len(result["references"]) == 2


def test_result_is_json_serializable() -> None:
    result = calculate_beam_bending(**_base_arguments())

    assert json.loads(json.dumps(result)) == result


def test_missing_required_input_is_rejected() -> None:
    with pytest.raises(TypeError, match="second_moment_of_area_unit"):
        calculate_beam_bending(
            bending_moment_value=5_000,
            bending_moment_unit="N·m",
            distance_from_neutral_axis_value=50,
            distance_from_neutral_axis_unit="mm",
            second_moment_of_area_value=8_000_000,
        )


@pytest.mark.parametrize(
    "input_name",
    [
        "bending_moment_value",
        "distance_from_neutral_axis_value",
        "second_moment_of_area_value",
    ],
)
@pytest.mark.parametrize("invalid", ["not-a-number", None])
def test_non_numeric_inputs_are_rejected(input_name: str, invalid: object) -> None:
    arguments = _base_arguments()
    arguments[input_name] = invalid

    with pytest.raises(TypeError, match=f"{input_name} must be a real number"):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize(
    "input_name",
    [
        "bending_moment_value",
        "distance_from_neutral_axis_value",
        "second_moment_of_area_value",
    ],
)
def test_boolean_inputs_are_rejected(input_name: str) -> None:
    arguments = _base_arguments()
    arguments[input_name] = True

    with pytest.raises(TypeError, match=f"{input_name} must be a real number"):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize(
    "input_name",
    [
        "bending_moment_value",
        "distance_from_neutral_axis_value",
        "second_moment_of_area_value",
    ],
)
def test_nonfinite_inputs_are_rejected(input_name: str, invalid: float) -> None:
    arguments = _base_arguments()
    arguments[input_name] = invalid

    with pytest.raises(ValueError, match=f"{input_name} must be finite"):
        calculate_beam_bending(**arguments)


def test_integer_to_float_overflow_is_rejected() -> None:
    arguments = _base_arguments()
    arguments["bending_moment_value"] = 10**400

    with pytest.raises(ValueError, match="representable as a finite float"):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize(
    ("unit_name", "invalid", "message"),
    [
        ("bending_moment_unit", "kN·m", "unsupported bending_moment_unit"),
        (
            "distance_from_neutral_axis_unit",
            "ft",
            "unsupported distance_from_neutral_axis_unit",
        ),
        (
            "second_moment_of_area_unit",
            "mm⁴",
            "unsupported second_moment_of_area_unit",
        ),
        ("output_unit", "N", "unsupported output_unit"),
    ],
)
def test_invalid_units_are_rejected(
    unit_name: str,
    invalid: str,
    message: str,
) -> None:
    arguments = _base_arguments()
    arguments[unit_name] = invalid

    with pytest.raises(ValueError, match=message):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize(
    "unit_name",
    [
        "bending_moment_unit",
        "distance_from_neutral_axis_unit",
        "second_moment_of_area_unit",
        "output_unit",
    ],
)
def test_non_string_units_are_rejected(unit_name: str) -> None:
    arguments = _base_arguments()
    arguments[unit_name] = None

    with pytest.raises(TypeError, match=f"{unit_name} must be a string"):
        calculate_beam_bending(**arguments)


def test_negative_distance_is_rejected() -> None:
    arguments = _base_arguments()
    arguments["distance_from_neutral_axis_value"] = -1

    with pytest.raises(ValueError, match="distance_from_neutral_axis_value"):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize("invalid", [0, -1])
def test_nonpositive_second_moment_is_rejected(invalid: float) -> None:
    arguments = _base_arguments()
    arguments["second_moment_of_area_value"] = invalid

    with pytest.raises(ValueError, match="second_moment_of_area_value"):
        calculate_beam_bending(**arguments)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {"bending_moment_value": 1e308, "bending_moment_unit": "N·m"},
            "converted bending moment must be finite",
        ),
        (
            {
                "distance_from_neutral_axis_value": 1e308,
                "distance_from_neutral_axis_unit": "m",
            },
            "converted distance from neutral axis must be finite",
        ),
        (
            {
                "second_moment_of_area_value": 1e308,
                "second_moment_of_area_unit": "m^4",
            },
            "converted second moment of area must be finite",
        ),
        (
            {
                "bending_moment_value": 1e308,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 2,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 1,
            },
            "bending stress numerator must be finite",
        ),
        (
            {
                "bending_moment_value": 5e-324,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 0.5,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 1,
            },
            "bending stress numerator must not underflow to zero",
        ),
        (
            {
                "bending_moment_value": 1e308,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 1,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 5e-324,
                "second_moment_of_area_unit": "mm^4",
            },
            "calculated bending stress must be finite",
        ),
        (
            {
                "bending_moment_value": 5e-324,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 1,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 2,
                "second_moment_of_area_unit": "mm^4",
            },
            "calculated bending stress must not underflow to zero",
        ),
        (
            {
                "bending_moment_value": 1e303,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 1,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 1,
                "second_moment_of_area_unit": "mm^4",
                "output_unit": "Pa",
            },
            "converted bending stress must be finite",
        ),
        (
            {
                "bending_moment_value": 1e-321,
                "bending_moment_unit": "N·mm",
                "distance_from_neutral_axis_value": 1,
                "distance_from_neutral_axis_unit": "mm",
                "second_moment_of_area_value": 1,
                "second_moment_of_area_unit": "mm^4",
                "output_unit": "GPa",
            },
            "converted bending stress must not underflow to zero",
        ),
    ],
)
def test_numerical_overflow_and_underflow_boundaries(
    overrides: dict[str, object],
    message: str,
) -> None:
    arguments = _base_arguments()
    arguments.update(overrides)

    with pytest.raises(ValueError, match=message):
        calculate_beam_bending(**arguments)


def test_substitution_preserves_traceable_precision() -> None:
    result = calculate_beam_bending(
        1,
        "lbf·in",
        1,
        "in",
        1,
        "in^4",
    )

    assert result["governing_equation"]["substitution"] == (
        "σ = (112.9848290276167 N·mm)(25.399999999999999 mm) / "
        "416231.42560000002 mm^4"
    )


def test_repeated_execution_is_deterministic() -> None:
    arguments = _base_arguments()

    assert calculate_beam_bending(**arguments) == calculate_beam_bending(
        **arguments
    )
