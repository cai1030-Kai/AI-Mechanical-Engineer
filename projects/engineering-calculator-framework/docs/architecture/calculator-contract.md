# Calculator Contract v0.1

## 1. Purpose

The Calculator Contract defines the minimum behavior shared by mechanical
engineering calculators in the Engineering Calculator Framework.

Its purpose is to make calculators:

- Consistent for users.
- Predictable for tests and future interfaces.
- Traceable from inputs to engineering results.
- Independently implementable without a class hierarchy.
- Simple to review against an engineering specification.

The contract defines observable behavior, not an implementation framework. A
calculator may be implemented as a module-level function. Version 0.1 does not
require classes, abstract base classes, inheritance, plugins, decorators,
automatic registration, or a shared result model.

Each calculator must also have its own engineering specification describing its
equations, assumptions, supported units, validation rules, and limitations.

## 2. Required calculator metadata

Every calculator specification must define the following metadata. Every
successful result must repeat the same metadata in its canonical `calculator`
object:

| Field | Requirement |
| --- | --- |
| `id` | Required stable machine-readable identifier |
| `name` | Required human-readable calculator name |
| `version` | Required calculator behavior version |
| `category` | Required high-level calculation category |
| `engineering_domain` | Required engineering discipline or subject area |
| `purpose` | Required concise statement of what the calculator determines |
| `reference_equation` | Required symbolic governing equation or equations |

### 2.1 Calculator ID

The calculator ID must:

- Use lowercase dot-separated names.
- Identify one calculation type.
- Remain stable after release.
- Be unique within the project.

Recommended format:

```text
<category>.<calculation>
```

Example:

```text
stress.axial
```

User interfaces may display the calculator name, but stored results and future
integrations must use the calculator ID as the stable identity.

### 2.2 Calculator version

The calculator version describes the behavior of one calculator. It is separate
from the Python package version.

The version must be included in every successful result so a calculation can be
traced to the equation, assumptions, validation rules, and output meaning that
produced it.

## 3. Input schema requirements

Every calculator specification must define each input before implementation.

Each input definition must include:

| Property | Requirement |
| --- | --- |
| `name` | Stable machine-readable input name |
| `description` | Engineering meaning of the input |
| `quantity_type` | Dimensional scalar, dimensionless scalar, categorical value, or another explicitly defined type |
| `required` | Whether the input is required or optional |
| `accepted_units` | Explicit list of accepted units for dimensional inputs; `not applicable` otherwise |
| `sign_convention` | Meaning of positive, negative, and zero when applicable; `not applicable` otherwise |

An input definition should also document calculator-specific constraints, such
as valid numerical ranges, allowed categorical values, and an optional default
when one is technically unambiguous.

Dimensional inputs must contain a numeric value and an explicit unit:

```json
{
  "value": 10.0,
  "unit": "kN"
}
```

The calculator must not silently guess the unit of a dimensional input.

Defaults are permitted only when they do not change the physical meaning of the
problem. An output display unit may have a default. A required engineering load,
geometry, material property, or boundary condition should not.

Calculator implementations may use direct function arguments in Version 0.1.
A runtime input-schema framework is not required.

## 4. Validation behavior

Validation must occur before the governing calculation is accepted as
successful.

Each calculator must validate, as applicable:

1. Required inputs are present.
2. Numeric inputs are real and finite.
3. Values satisfy calculator-specific physical constraints.
4. Units are supported and dimensionally appropriate.
5. Categorical values are members of the documented allowed set.
6. Converted intermediate quantities remain finite.
7. Calculated and output-converted results remain finite.

Examples of calculator-specific physical constraints include:

- Area must be greater than zero.
- Elastic modulus must be greater than zero.
- A supported end condition must be selected.
- A denominator must not be zero.

Validation must not:

- Replace invalid inputs with fallback values.
- Guess missing dimensional units.
- Clamp values silently.
- Return a partial numerical result after a validation failure.

### 4.1 Errors and warnings

An error prevents calculation because the input or numerical result is invalid.

A warning allows calculation but identifies an engineering applicability
concern or interpretation risk.

Warnings must not be used as substitutes for errors. Errors and warnings must
remain distinguishable in calculator behavior and output.

## 5. Calculation execution requirements

Every calculator must:

1. Use the governing equation documented in its engineering specification.
2. Preserve documented sign conventions.
3. Convert accepted inputs to clearly defined internal units.
4. Perform calculations without premature display rounding.
5. Produce the same result for the same calculator version and inputs.
6. Avoid network access, generative AI, hidden mutable state, and
   environment-dependent assumptions during the calculation.
7. Keep deterministic engineering calculations separate from presentation and
   CLI behavior.
8. Make assumptions, warnings, limitations, and engineering references
   available to the caller.

The implementation should remain local and direct. Shared helpers should be
introduced only after multiple calculators demonstrate the same requirement.

The calculator must not imply that it evaluates failure modes outside its
documented scope. For example, a nominal compression stress calculation must
not be presented as a buckling assessment.

## 6. Output schema requirements

A successful calculator result must use one canonical structure containing:

| Field | Requirement |
| --- | --- |
| `calculator` | Complete calculator identity and metadata |
| `inputs` | Original input values and units |
| `results` | Named engineering results with values and units |
| `governing_equation` | Symbolic equation and substituted normalized values |
| `assumptions` | Human-readable array of applied assumptions |
| `warnings` | Human-readable array of warnings |
| `limitations` | Human-readable array of calculation limitations |
| `references` | Human-readable array of engineering sources |

Canonical successful calculation result:

```json
{
  "calculator": {
    "id": "<calculator-id>",
    "name": "<calculator-name>",
"version": "<calculator-version>",
    "category": "<calculator-category>",
    "engineering_domain": "<engineering-domain>",
    "purpose": "<calculator-purpose>",
    "reference_equation": "<reference-equation>"
  },
  "inputs": {
    "<input-name>": {
      "value": 0.0,
      "unit": "<input-unit>"
    }
  },
  "results": {
    "<result-name>": {
      "value": 0.0,
      "unit": "<result-unit>"
    }
  },
  "governing_equation": {
    "symbolic": "<symbolic-equation>",
    "substitution": "<equation-with-normalized-values>"
  },
  "assumptions": [],
  "warnings": [],
  "limitations": [],
  "references": []
}
```

### 6.1 Output rules

- Dimensional values must store numeric value and unit separately.
- Input units must preserve the units supplied by the caller.
- Result units must identify the units of the returned values.
- Result values must preserve documented sign conventions.
- The symbolic equation must match the calculator specification.
- The substitution must contain sufficient precision for traceability.
- Assumptions must not be omitted.
- Warnings must not be omitted.
- Limitations must not be omitted.
- References must not be omitted.
- A successful calculation with no warnings must return an empty warnings
  array.
- A calculator with no additional runtime limitations must still return the
  limitations documented by its engineering specification.
- References must identify the source used to verify the governing equation or
  calculation method. A textbook title, standard designation, or other
  traceable engineering source is sufficient for Version 0.1.
- Internal values may use different units, but internal-unit choices must not
  change the physical result.

The output must be serializable to JSON without requiring custom object
serialization. Version 0.1 may return a plain dictionary.

## 7. Error handling expectations

Calculator modules must fail clearly and locally.

For Version 0.1:

- `TypeError` is appropriate when an input has an unsupported Python type.
- `ValueError` is appropriate when a value, unit, category, intermediate
  quantity, or result is invalid.
- Error messages must identify the affected input or calculation stage.
- Expected caller errors must not be converted into valid-looking results.
- Calculator modules must not print errors.
- Calculator modules must not terminate the process.

CLI and future API layers are responsible for converting calculator exceptions
into user-facing messages, exit codes, or error response schemas.

Custom exception classes are not required in Version 0.1. They should be added
only if multiple interfaces demonstrate a concrete need to distinguish error
categories programmatically.

## 8. Verification requirements

Every calculator must have automated verification covering:

### 8.1 Reference calculations

- At least one independently checked engineering calculation.
- Expected intermediate values when they are important to traceability.
- A documented source or hand derivation for the expected result.
- A numerical tolerance appropriate to the calculation.

The production equation must not be the only source used to create the expected
test result.

### 8.2 Unit equivalence tests

- At least one calculation expressed in two compatible unit systems.
- Equivalent physical inputs must produce equivalent physical results within a
  documented floating-point tolerance.
- Every accepted unit must participate in a test before the calculator is
  designated as a reference implementation.

### 8.3 Boundary tests

- Zero values when zero is permitted.
- Values at documented positive or negative limits.
- Values immediately outside valid ranges.
- Numerical overflow, underflow, or non-finite intermediate results when
  applicable.
- Sign-transition behavior when the calculator defines a sign convention.

### 8.4 Invalid input tests

- Missing required inputs.
- Unsupported Python input types.
- `NaN`, positive infinity, and negative infinity for numerical inputs.
- Unsupported or dimensionally incorrect units.
- Calculator-specific invalid values and categorical choices.

Verification may use direct function calls and parameterized tests. Version 0.1
does not require a shared test base class, schema framework, or custom test
runner.

## 9. Versioning rules

Calculator versions use:

```text
MAJOR.MINOR.PATCH
```

### MAJOR

Increment when a released change is incompatible with previous calculator
behavior, such as:

- Changing the governing equation or physical interpretation.
- Reversing a sign convention.
- Renaming or removing required inputs or result fields.
- Changing the meaning of an existing result.
- Removing previously accepted units.

### MINOR

Increment when adding backward-compatible behavior, such as:

- Adding an optional input.
- Adding an accepted unit.
- Adding a new result field without changing existing fields.
- Adding a new warning based on existing inputs.

### PATCH

Increment when correcting behavior without intentionally changing the public
contract, such as:

- Fixing an incorrect conversion factor.
- Correcting numerical precision or validation defects.
- Improving an error message without changing the error condition.

A calculator version change must be accompanied by updated specification and
tests. Documentation-only clarification does not require a version change when
it does not alter observable behavior.

## 10. Axial Stress Calculator example

The existing Axial Stress Calculator applies this contract as follows.

### 10.1 Metadata

```text
ID: stress.axial
Name: Axial Stress Calculator
Version: 0.1.0
Category: Stress Analysis
Engineering Domain: Mechanics of Materials
Purpose: Calculate signed average normal stress under concentric axial load
Reference Equation: σ = F / A
```

### 10.2 Inputs

```json
{
  "force": {
    "value": 10.0,
    "unit": "kN"
  },
  "area": {
    "value": 500.0,
    "unit": "mm²"
  },
  "output_unit": "MPa"
}
```

Validation requires:

- Force is a finite real number.
- Area is a finite real number greater than zero.
- Force, area, and output units are supported.
- Converted quantities and calculated results remain finite.

### 10.3 Execution

```text
F = 10 kN = 10,000 N
A = 500 mm²
σ = F / A
σ = 10,000 N / 500 mm²
σ = 20 MPa
```

Positive stress represents tension. Negative stress represents compression.

### 10.4 Successful output

```json
{
  "calculator": {
    "id": "stress.axial",
    "name": "Axial Stress Calculator",
"version": "0.1.0",
    "category": "Stress Analysis",
    "engineering_domain": "Mechanics of Materials",
    "purpose": "Calculate signed average normal stress under concentric axial load",
    "reference_equation": "σ = F / A"
  },
  "inputs": {
    "force": {
      "value": 10.0,
      "unit": "kN"
    },
    "area": {
      "value": 500.0,
      "unit": "mm²"
    }
  },
  "results": {
    "axial_stress": {
      "value": 20.0,
      "unit": "MPa"
    },
    "loading_state": "tension"
  },
  "governing_equation": {
    "symbolic": "σ = F / A",
    "substitution": "σ = 10000 N / 500 mm²"
  },
  "assumptions": [
    "The force is axial and passes through the section centroid.",
    "The supplied area is the net area resisting the load.",
    "Stress is represented by its average value over the cross-section."
  ],
  "warnings": [],
  "limitations": [
    "The calculation does not account for bending caused by eccentric loading.",
    "The calculation does not evaluate buckling under compression.",
    "The calculation does not evaluate local stress concentrations."
  ],
  "references": [
    "Mechanics of materials: average normal stress, σ = F / A."
  ]
}
```

The Axial Stress Calculator remains responsible for its engineering-specific
details. This contract only defines the common shape and behavior future
calculators should follow.

## 11. Lightweight calculator checklist

Before implementing a new calculator:

1. Write its engineering specification.
2. Assign stable metadata.
3. Define each input's description, quantity type, required status, units, and
   sign convention.
4. Define the governing equation and internal units.
5. Define assumptions, warnings, limitations, and references.
6. Use the canonical successful output structure.
7. Implement one direct calculation function.
8. Add reference calculations, unit equivalence tests, boundary tests, and
   invalid input tests.
9. Confirm the calculator follows this contract.

No additional abstraction is required unless repeated implementations provide
evidence that a shared component will reduce risk or duplication.
