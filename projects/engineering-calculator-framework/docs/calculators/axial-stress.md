# Axial Stress Calculator Specification

## 1. Engineering purpose

The Axial Stress Calculator determines the average normal stress in a member
subjected to a concentric axial force.

It is intended for preliminary analysis, education, and verification of simple
axially loaded components such as rods, bars, links, and uniform structural
members. The calculator must return a deterministic engineering result that can
be independently checked from the reported inputs and equation.

This calculator evaluates stress only. It does not determine deformation,
material failure, factor of safety, buckling, fatigue life, or code compliance.

## 2. Calculator Metadata

| Field | Value |
| --- | --- |
| Calculator ID | `stress.axial` |
| Name | `Axial Stress Calculator` |
| Version | `0.1.0` |
| Category | `Stress Analysis` |
| Engineering Domain | `Mechanics of Materials` |
| Purpose | Calculate the signed average normal stress in a member subjected to a concentric axial force |
| Reference Equation | `σ = F / A` |

The Calculator ID is a stable, machine-readable identifier. User interfaces may
display the calculator name, but stored results and future integrations must use
`stress.axial` to identify this calculation type.

The calculator version identifies the engineering behavior defined by this
specification. It is independent of the overall package version and must change
when the equation, sign convention, validation behavior, assumptions, or output
meaning changes incompatibly.

## 3. Governing equation

The average axial normal stress is:

```text
σ = F / A
```

where:

| Symbol | Variable | Definition |
| --- | --- | --- |
| `σ` | Axial stress | Average normal stress acting over the cross-section |
| `F` | Axial force | Resultant force acting perpendicular to the cross-section |
| `A` | Cross-sectional area | Net area resisting the axial force |

### Sign convention

- Tension is positive: `F > 0` and `σ > 0`.
- Compression is negative: `F < 0` and `σ < 0`.
- Zero force produces zero stress.
- Cross-sectional area is always positive.

The calculator must preserve the sign of the applied force. It must not report
only the absolute stress magnitude, because the sign communicates the physical
loading state.

## 4. Inputs and units

### 4.1 Axial force

| Property | Requirement |
| --- | --- |
| Name | `force` |
| Physical dimension | Force |
| Required | Yes |
| Accepted initial units | `N`, `kN`, `lbf`, `kip` |
| Valid values | Any finite real number, including zero |
| Sign meaning | Positive for tension; negative for compression |

The input must include an explicit unit. A unitless force must not be silently
interpreted.

### 4.2 Cross-sectional area

| Property | Requirement |
| --- | --- |
| Name | `area` |
| Physical dimension | Area |
| Required | Yes |
| Accepted initial units | `mm²`, `cm²`, `m²`, `in²` |
| Valid values | Any finite real number greater than zero |

The user is responsible for supplying the net resisting area. If holes,
threads, grooves, or other area reductions are relevant, the reduced area must
be calculated before calling this calculator.

### 4.3 Requested output unit

| Property | Requirement |
| --- | --- |
| Name | `output_unit` |
| Physical dimension | Pressure or stress |
| Required | No |
| Accepted initial units | `Pa`, `kPa`, `MPa`, `GPa`, `psi`, `ksi` |
| Default | `MPa` |

The requested output unit affects presentation only. It must not change the
underlying physical result.

## 5. Outputs

The calculator must return:

| Output | Definition |
| --- | --- |
| `axial_stress` | Signed average normal stress in the requested output unit |
| `loading_state` | `tension`, `compression`, or `unloaded` |
| `equation` | The governing equation `σ = F / A` |
| `inputs` | Original force and area values with their units |
| `assumptions` | Assumptions applied to the calculation |
| `warnings` | Applicability or interpretation warnings, if any |

The numerical stress result must retain full calculation precision internally.
Rounding is a presentation concern and must not be applied before the division
is complete.

The loading state is determined as follows:

| Condition | Loading state |
| --- | --- |
| `F > 0` | `tension` |
| `F < 0` | `compression` |
| `F = 0` | `unloaded` |

## 6. Output Schema

A successful calculation must be representable by the following JSON-like
structure:

```json
{
  "calculator": {
    "id": "stress.axial",
    "name": "Axial Stress Calculator",
    "version": "0.1.0"
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
  "warnings": []
}
```

### 6.1 Schema rules

- `calculator.id`, `calculator.name`, and `calculator.version` are required.
- `calculator.id` must equal `stress.axial` for this calculator.
- Each dimensional input and result must store `value` and `unit` separately.
- Input values and units must preserve the values supplied by the user.
- `results.axial_stress.value` must preserve the force sign.
- `results.loading_state` must be `tension`, `compression`, or `unloaded`.
- `governing_equation.symbolic` must contain the general equation.
- `governing_equation.substitution` must show the normalized values used in the
  calculation.
- `assumptions` must be an array of human-readable statements and must not be
  omitted.
- `warnings` must be an array. A successful calculation with no warnings must
  return an empty array rather than omit the field.
- The structure above defines successful calculation output only. Validation
  error output will be specified separately before CLI implementation.

This schema separates numeric values from unit strings so consumers do not need
to parse formatted engineering text. It also keeps the result traceable by
including calculator identity, equation, assumptions, and warnings in the same
record.

## 7. Assumptions

The calculation is valid under the following assumptions:

1. The applied force is axial and passes through the centroid of the resisting
   cross-section.
2. The member is straight and prismatic in the region being evaluated.
3. The reported area is the net area resisting the load.
4. Stress is represented by its average value over the cross-section.
5. The material is treated as continuous and homogeneous at the scale of the
   calculation.
6. The member is in static or quasi-static equilibrium.
7. The evaluated section is sufficiently far from load introduction points,
   abrupt geometry changes, and local contact regions for average stress to be
   meaningful.
8. Deformation is small enough that the original cross-sectional area remains
   appropriate for this calculation.

The calculator must make these assumptions visible to the user rather than
leaving them only in source code.

## 8. Validation rules

Validation must occur before the stress calculation.

### 8.1 Required-value validation

- `force` is required.
- `area` is required.
- Missing required values must produce an actionable error naming the missing
  input.

### 8.2 Numerical validation

- `force` must be a finite real number.
- `area` must be a finite real number.
- `NaN`, positive infinity, and negative infinity are invalid.
- `area` must be strictly greater than zero.
- Zero force is valid and must return zero stress.

### 8.3 Dimensional validation

- `force` must have the physical dimension of force.
- `area` must have the physical dimension of area.
- `output_unit` must have the physical dimension of pressure or stress.
- Unitless dimensional inputs are invalid.
- Dimensionally incompatible units must be rejected rather than converted or
  guessed.

### 8.4 Error behavior

Validation errors must:

- Identify the invalid input.
- State the violated rule.
- Preserve the user's original value where safe to display.
- Avoid returning a numerical stress result.
- Avoid exposing an internal stack trace during normal CLI use.

### 8.5 Warning behavior

The calculator should emit a warning, while still allowing calculation, when:

- The user indicates or a future interface detects that the load may be
  eccentric.
- The supplied area may not represent the net section.
- The calculation is being interpreted close to a discontinuity or load
  application point.

Version 0.1 does not infer these conditions from force and area alone. They are
documented applicability checks for the user and future interfaces.

## 9. Limitations

The calculator does not account for:

- Bending caused by eccentric loading.
- Shear stress or torsional stress.
- Stress concentrations at holes, notches, shoulders, threads, or fillets.
- Local bearing, contact, or crushing stress.
- Nonuniform stress distributions near load introduction points.
- Buckling of members under compression.
- Plastic deformation or nonlinear material behavior.
- Large deformation or changes in cross-sectional area.
- Residual, thermal, dynamic, impact, or cyclic stresses.
- Fatigue, fracture, creep, or stress relaxation.
- Material strength, allowable stress, or factor of safety.
- Design-code or regulatory compliance.

For compression members, a low calculated axial stress does not establish
safety because buckling may govern the design.

The result is suitable for educational use and preliminary engineering checks.
It does not replace detailed analysis, applicable standards, testing, or
professional engineering review.

## 10. Verified example calculation

### Problem

A straight member with a uniform cross-sectional area of `500 mm²` carries a
concentric tensile force of `10 kN`. Calculate the average axial normal stress
in `MPa`.

### Given

```text
F = +10 kN
A = 500 mm²
```

### Unit conversion

```text
10 kN = 10,000 N
1 MPa = 1 N/mm²
```

### Calculation

```text
σ = F / A
σ = 10,000 N / 500 mm²
σ = 20 N/mm²
σ = 20 MPa
```

### Verified result

```text
axial_stress = +20 MPa
loading_state = tension
```

Independent reverse check:

```text
F = σA
F = (20 N/mm²)(500 mm²)
F = 10,000 N
F = 10 kN
```

The reverse calculation reproduces the original applied force, and the unit
identity `1 N/mm² = 1 MPa` confirms the reported stress unit.

## 11. Design decisions

### Signed stress instead of magnitude-only stress

The force sign is preserved so downstream calculations can distinguish tension
from compression. This prevents loss of physical meaning and supports future
combined-load calculations.

### Explicit units instead of implicit defaults

Force and area require units because silently assuming a unit system can create
errors of several orders of magnitude. Only the optional output unit has a
default because it changes presentation rather than the physical input.

### Net area supplied by the user

Version 0.1 accepts area directly instead of adding geometry-specific inputs.
This keeps the first calculator small and usable for many section shapes without
introducing premature geometry abstractions.

### Average stress only

The equation `σ = F / A` is intentionally implemented as an average-stress
calculation. Stress concentration, bending, buckling, and material failure are
separate engineering problems and must not be implied by this result.

### Validation errors separated from engineering warnings

Invalid dimensions or nonpositive area prevent a calculation. Applicability
concerns, such as eccentric loading, are warnings because the numerical inputs
alone may still form a mathematically valid calculation. Keeping these concepts
separate produces clearer and safer software behavior.
