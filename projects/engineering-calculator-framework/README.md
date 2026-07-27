# Engineering Calculator Framework

A small, traceable Python package for deterministic mechanical engineering
calculations. Version 0.2 provides direct Python APIs and a command-line
interface, with results represented as canonical JSON containing inputs, units,
equations, assumptions, warnings, limitations, and references.

## Current features

- Three mechanics-of-materials stress calculators, including beam bending
- Explicit SI and US customary input units
- Stress output in `Pa`, `kPa`, `MPa`, `GPa`, `psi`, or `ksi`
- Input, unit, intermediate-value, and result validation
- Deterministic, JSON-serializable results
- Governing-equation substitutions for calculation traceability
- Shared behavior defined by [Calculator Contract v0.1](docs/architecture/calculator-contract.md)
- Python API and CLI access

## Supported calculators

| Calculator ID | Calculator | Result |
| --- | --- | --- |
| `stress.axial` | Axial Stress Calculator | Signed average axial stress and loading state |
| `stress.shaft_torsion` | Solid Circular Shaft Torsional Stress Calculator | Polar moment of inertia and maximum torsional shear stress |
| `stress.beam_bending` | Beam Bending Stress Calculator | Signed linear-elastic bending stress and stress state |

See the [Calculator Catalog](docs/calculator-catalog.md) for scope, assumptions,
limitations, and links to the detailed specifications.

## Requirements

- Python 3.11 or newer

## Installation

From this directory, install the package and development dependencies:

```powershell
py -m pip install -e ".[dev]"
```

On platforms where `python` is the configured interpreter, use
`python -m pip` instead of `py -m pip`.

## Python API

Calculate signed axial stress:

```python
from engineering_calculator.calculators.axial_stress import calculate_axial_stress

result = calculate_axial_stress(
    force_value=100,
    force_unit="kN",
    area_value=500,
    area_unit="mm²",
    output_unit="MPa",
)
print(result["results"]["axial_stress"])
# {'value': 200.0, 'unit': 'MPa'}
```

Calculate torsional stress in a solid circular shaft:

```python
from engineering_calculator.calculators.shaft_torsion import calculate_shaft_torsion

result = calculate_shaft_torsion(
    torque_value=500,
    torque_unit="N·m",
    diameter_value=40,
    diameter_unit="mm",
    output_unit="MPa",
)
print(result["results"]["maximum_shear_stress"])
# {'value': 39.78873577297384, 'unit': 'MPa'}
```

Calculate linear-elastic beam bending stress:

```python
from engineering_calculator.calculators.beam_bending import calculate_beam_bending

result = calculate_beam_bending(
    bending_moment_value=5_000,
    bending_moment_unit="N·m",
    distance_from_neutral_axis_value=50,
    distance_from_neutral_axis_unit="mm",
    second_moment_of_area_value=8_000_000,
    second_moment_of_area_unit="mm^4",
    output_unit="MPa",
)
print(result["results"]["bending_stress"])
# {'value': 31.25, 'unit': 'MPa'}
```

## CLI usage

Calculate axial stress (`100 kN / 500 mm²`):

```powershell
engineering-calculator axial-stress 100 kN 500 mm² --output-unit MPa
```

Calculate torsional stress for a solid shaft:

```powershell
engineering-calculator shaft-torsion 500 "N·m" 40 mm --output-unit MPa
```

Calculate bending stress using caller-supplied section properties:

```powershell
engineering-calculator beam-bending --moment 5000 --moment-unit "N·m" --distance 50 --distance-unit mm --second-moment 8000000 --second-moment-unit "mm^4" --stress-unit MPa
```

Run `engineering-calculator --help` or a subcommand with `--help` for all
accepted input units. The package-module form is also supported:

```powershell
py -m engineering_calculator --help
```

## Example canonical JSON output

An axial-stress calculation returns the canonical structure below. Arrays are
shortened here for readability; calculator results contain the complete
assumption, limitation, and reference statements.

```json
{
  "calculator": {
    "id": "stress.axial",
    "name": "Axial Stress Calculator",
    "version": "0.1.0",
    "category": "Stress Analysis",
    "engineering_domain": "Mechanics of Materials",
    "purpose": "Calculate the signed average normal stress in a member subjected to a concentric axial force",
    "reference_equation": "σ = F / A"
  },
  "inputs": {
    "force": {"value": 100.0, "unit": "kN"},
    "area": {"value": 500.0, "unit": "mm²"}
  },
  "results": {
    "axial_stress": {"value": 200.0, "unit": "MPa"},
    "loading_state": "tension"
  },
  "governing_equation": {
    "symbolic": "σ = F / A",
    "substitution": "σ = 100000 N / 500 mm²"
  },
  "assumptions": ["..."],
  "warnings": [],
  "limitations": ["..."],
  "references": ["..."]
}
```

## Testing

Run the complete test suite:

```powershell
py -m pytest
```

The current v0.2 milestone has **176 passing tests** covering engineering
examples, units, validation, schemas, serialization, determinism, and CLI
behavior.

## Project structure

```text
engineering-calculator-framework/
├── docs/
│   ├── architecture/          # Calculator Contract v0.1
│   ├── calculators/           # Detailed calculator specifications
│   ├── releases/              # Milestone release notes
│   └── calculator-catalog.md  # Concise calculator index
├── src/engineering_calculator/
│   ├── calculators/           # Axial, shaft-torsion, and beam-bending modules
│   ├── cli.py                 # CLI parser and subcommand dispatch
│   └── __main__.py            # python -m entry point
├── tests/                     # Calculator and CLI verification
├── pyproject.toml
└── README.md
```

## Roadmap

Beam bending is complete in v0.2. Planned calculators for the next milestones:

- Euler buckling
- Factor of safety

See the [v0.2.0 release notes](docs/releases/v0.2.0.md) for the current milestone
summary and known limitations.

## Engineering disclaimer

This software is intended for preliminary analysis, education, and independent
verification. It does not replace engineering judgment, material data review,
applicable design codes, safety assessment, or review by a qualified engineer.
Users are responsible for confirming inputs, units, assumptions, load cases,
failure modes, and the suitability of every result for its intended use.
