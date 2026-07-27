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


def test_calculation_error_is_reported_as_cli_error(capsys) -> None:
    with pytest.raises(SystemExit, match="2"):
        main(["axial-stress", "100", "kN", "0", "mm²"])

    assert "area_value must be greater than zero" in capsys.readouterr().err


def test_command_is_required(capsys) -> None:
    with pytest.raises(SystemExit, match="2"):
        main([])

    assert "required" in capsys.readouterr().err
