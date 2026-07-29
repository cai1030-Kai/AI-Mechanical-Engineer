# Project Definition

## Purpose

AI Mechanical Design Assistant is intended to support deterministic mechanical
design review. The initial scaffold establishes only the project boundary,
package, documentation, and test setup.

## Current scope

- Standalone Python packaging
- Package metadata
- Import and version smoke testing

## Current exclusions

- Business logic
- Review workflow implementation
- Command-line interfaces
- Engineering calculators
- LLM APIs
- Databases
- Web servers
- Plugin systems

## Engineering principles

Future functionality should be:

- Deterministic
- Typed
- JSON serializable
- Validated at explicit boundaries
- Covered by focused tests

The current scaffold has no runtime dependency on
engineering-calculator-framework. Future integration may be introduced through
an explicit tool boundary.

