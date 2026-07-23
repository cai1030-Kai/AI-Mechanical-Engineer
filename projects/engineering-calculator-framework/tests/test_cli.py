"""Smoke tests for the command-line entry point."""

from engineering_calculator.cli import main


def test_main_reports_empty_framework(capsys) -> None:
    main()

    output = capsys.readouterr().out
    assert "Engineering Calculator Framework 0.1.0" in output
    assert "No calculators are available yet." in output
