"""Command-line interface for the engineering calculators."""

import argparse
import json
from collections.abc import Sequence

from engineering_calculator.calculators.axial_stress import calculate_axial_stress
from engineering_calculator.calculators.shaft_torsion import calculate_shaft_torsion


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="engineering-calculator",
        description="Run traceable mechanical engineering calculations.",
    )
    subparsers = parser.add_subparsers(dest="calculator", required=True)

    axial = subparsers.add_parser(
        "axial-stress", help="calculate signed average axial stress"
    )
    axial.add_argument("force", type=float, help="signed axial force")
    axial.add_argument("force_unit", choices=("N", "kN", "lbf", "kip"))
    axial.add_argument("area", type=float, help="positive resisting area")
    axial.add_argument("area_unit", choices=("mm²", "cm²", "m²", "in²"))
    axial.add_argument(
        "--output-unit",
        choices=("Pa", "kPa", "MPa", "GPa", "psi", "ksi"),
        default="MPa",
    )

    torsion = subparsers.add_parser(
        "shaft-torsion", help="calculate stress in a solid circular shaft"
    )
    torsion.add_argument("torque", type=float, help="nonnegative applied torque")
    torsion.add_argument(
        "torque_unit", choices=("N·mm", "N·m", "lbf·in", "lbf·ft")
    )
    torsion.add_argument("diameter", type=float, help="positive shaft diameter")
    torsion.add_argument("diameter_unit", choices=("mm", "cm", "m", "in"))
    torsion.add_argument(
        "--output-unit",
        choices=("Pa", "kPa", "MPa", "GPa", "psi", "ksi"),
        default="MPa",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse arguments, run the selected calculator, and print JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.calculator == "axial-stress":
            result = calculate_axial_stress(
                args.force, args.force_unit, args.area, args.area_unit, args.output_unit
            )
        else:
            result = calculate_shaft_torsion(
                args.torque,
                args.torque_unit,
                args.diameter,
                args.diameter_unit,
                args.output_unit,
            )
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, ensure_ascii=True))
