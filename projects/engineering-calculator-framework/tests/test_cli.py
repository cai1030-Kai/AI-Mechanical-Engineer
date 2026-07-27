"""Tests for the command-line interface."""

import json

import pytest

from engineering_calculator.cli import main


def test_axial_stress_command_outputs_json(capsys) -> None:
    main(["axial-stress", "100", "kN", "500", "mm²"])

    result = json.loads(capsys.readouterr().out)
    assert result["calculator"]["id"] == "stress.axial"
    assert result["results"]["axial_stress"] == {
        "value": 200.0,
        "unit": "MPa",
    }


def test_shaft_torsion_command_outputs_json(capsys) -> None:
    main(
        [
            "shaft-torsion",
            "500",
            "N·m",
            "40",
            "mm",
            "--output-unit",
            "MPa",
        ]
    )

    result = json.loads(capsys.readouterr().out)
    assert result["calculator"]["id"] == "stress.shaft_torsion"
    assert result["results"]["maximum_shear_stress"]["value"] == pytest.approx(
        39.7887357729738
    )


def _beam_bending_arguments() -> list[str]:
    return [
        "beam-bending",
        "--moment",
        "5000",
        "--moment-unit",
        "N·m",
        "--distance",
        "50",
        "--distance-unit",
        "mm",
        "--second-moment",
        "8000000",
        "--second-moment-unit",
        "mm^4",
        "--stress-unit",
        "MPa",
    ]


def test_beam_bending_si_command_outputs_canonical_json(capsys) -> None:
    main(_beam_bending_arguments())

    result = json.loads(capsys.readouterr().out)
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
    assert result["calculator"]["id"] == "stress.beam_bending"
    assert result["results"] == {
        "bending_stress": {"value": 31.25, "unit": "MPa"},
        "stress_state": "tension",
    }


def test_beam_bending_us_customary_command(capsys) -> None:
    arguments = [
        "beam-bending",
        "--moment",
        "12000",
        "--moment-unit",
        "lbf·in",
        "--distance",
        "3",
        "--distance-unit",
        "in",
        "--second-moment",
        "200",
        "--second-moment-unit",
        "in^4",
        "--stress-unit",
        "psi",
    ]
    main(arguments)

    result = json.loads(capsys.readouterr().out)
    assert result["results"]["bending_stress"] == {
        "value": pytest.approx(180.0),
        "unit": "psi",
    }


def test_beam_bending_preserves_negative_moment(capsys) -> None:
    arguments = _beam_bending_arguments()
    arguments[2] = "-5000"
    main(arguments)

    result = json.loads(capsys.readouterr().out)
    assert result["inputs"]["bending_moment"]["value"] == -5_000.0
    assert result["results"]["bending_stress"]["value"] == -31.25
    assert result["results"]["stress_state"] == "compression"


@pytest.mark.parametrize(
    ("argument_index", "zero_value"),
    [(2, "0"), (6, "0")],
)
def test_beam_bending_zero_cases(
    argument_index: int,
    zero_value: str,
    capsys,
) -> None:
    arguments = _beam_bending_arguments()
    arguments[argument_index] = zero_value
    main(arguments)

    result = json.loads(capsys.readouterr().out)
    assert result["results"] == {
        "bending_stress": {"value": 0.0, "unit": "MPa"},
        "stress_state": "zero",
    }


def test_beam_bending_invalid_second_moment_reports_cli_error(capsys) -> None:
    arguments = _beam_bending_arguments()
    arguments[10] = "0"

    with pytest.raises(SystemExit, match="2"):
        main(arguments)

    error = capsys.readouterr().err
    assert "second_moment_of_area_value must be greater than zero" in error
    assert error.isascii()


def test_beam_bending_unsupported_unit_reports_cli_error(capsys) -> None:
    arguments = _beam_bending_arguments()
    arguments[4] = "unsupported"

    with pytest.raises(SystemExit, match="2"):
        main(arguments)

    error = capsys.readouterr().err
    assert "unsupported moment unit" in error
    assert error.isascii()


def test_calculation_error_is_reported_as_cli_error(capsys) -> None:
    with pytest.raises(SystemExit, match="2"):
        main(["axial-stress", "100", "kN", "0", "mm²"])

    assert "area_value must be greater than zero" in capsys.readouterr().err


def test_command_is_required(capsys) -> None:
    with pytest.raises(SystemExit, match="2"):
        main([])

    assert "required" in capsys.readouterr().err
