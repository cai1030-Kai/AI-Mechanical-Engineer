# AI Mechanical Design Assistant

An early-stage Python project for a deterministic, typed, and JSON-serializable
mechanical design review assistant.

The current scaffold contains package metadata and a packaging smoke test only.
It does not yet implement review workflows, command-line interfaces,
calculators, or other business logic.

The current scaffold has no runtime dependency on
engineering-calculator-framework. Future integration may be introduced through
an explicit tool boundary.

## Development

Python 3.11 or newer is required.

Install the optional development dependencies:

```console
python -m pip install -e ".[dev]"
```

Run the test suite:

```console
python -m pytest
```

