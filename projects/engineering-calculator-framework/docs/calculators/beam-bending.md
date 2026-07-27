# Beam Bending Stress Calculator Specification

## 1. Engineering purpose

The Beam Bending Stress Calculator determines the signed linear-elastic normal
stress at a user-specified distance from the neutral axis of a straight beam in
pure bending about one principal centroidal axis.

It is intended for preliminary analysis, education, and independent
verification when the caller already knows the applicable section second
moment of area and the location of the evaluated fiber. The calculator does not
derive section properties from geometry.

The calculator evaluates nominal bending stress only. It does not evaluate
combined loading, transverse shear stress, deflection, material strength,
yielding, factor of safety, fatigue, or design-code compliance.

## 2. Calculator metadata

| Field | Value |
| --- | --- |
| Calculator ID | `stress.beam_bending` |
| Name | `Beam Bending Stress Calculator` |
| Version | `0.1.0` |
| Category | `Stress Analysis` |
| Engineering Domain | `Mechanics of Materials` |
| Purpose | Calculate signed linear-elastic normal stress at a specified distance from the neutral axis of a straight beam in pure bending about one principal centroidal axis |
| Reference Equation | `σ = My / I` |

The calculator ID is the stable machine-readable identity. Stored results and
future integrations must use `stress.beam_bending`.

The calculator version is independent of the Python package version. Every
successful result must include the version so the governing equation, sign
convention, validation behavior, assumptions, and output meaning remain
traceable.

## 3. Scope

Version 0.1 applies only when all of the following are true:

- The member is a straight beam.
- The material response is linear elastic.
- The evaluated section is under pure bending about one principal centroidal
  axis.
- The caller supplies the applicable section second moment of area, `I`.
- The caller supplies the nonnegative distance, `y`, from that axis's neutral
  axis to the evaluated fiber.
- The supplied `I` and `y` describe the same bending axis and section
  orientation.

Version 0.1 does not:

- Calculate `I`, the neutral-axis location, or any other section property from
  section geometry.
- Accept section dimensions or section-shape categories.
- Superimpose axial, torsional, transverse-shear, or biaxial bending loads.
- Determine deflection, curvature, rotation, or stiffness of the beam system.
- Compare stress with material strength or determine yielding, fatigue, factor
  of safety, or compliance.

## 4. Inputs and units

### 4.1 Bending moment

| Property | Requirement |
| --- | --- |
| Name | `bending_moment` |
| Description | Signed internal bending moment at the evaluated beam section about the selected principal centroidal axis |
| Quantity type | Dimensional scalar: moment |
| Required | Required |
| Accepted units | `N·mm`, `N·m`, `lbf·in`, `lbf·ft` |
| Sign convention | Positive moment produces positive tensile stress at the evaluated fiber; negative moment produces negative compressive stress; zero represents no bending moment |
| Valid values | Any finite real number, including positive, negative, and zero |
| Default | None |

The sign is meaningful only with the selected bending axis, section
orientation, and evaluated fiber held fixed. Reversing the evaluated side of
the neutral axis requires reversing the bending-moment sign supplied under this
calculator's convention.

### 4.2 Distance from neutral axis

| Property | Requirement |
| --- | --- |
| Name | `distance_from_neutral_axis` |
| Description | Nonnegative perpendicular distance from the selected neutral axis to the evaluated fiber |
| Quantity type | Dimensional scalar: length |
| Required | Required |
| Accepted units | `mm`, `cm`, `m`, `in` |
| Sign convention | Nonnegative distance magnitude; zero identifies the neutral axis and negative values are invalid |
| Valid values | Any finite real number greater than or equal to zero |
| Default | None |

This input is a distance magnitude, not a signed coordinate. A zero distance
must produce zero bending stress for every valid bending moment.

### 4.3 Section second moment of area

| Property | Requirement |
| --- | --- |
| Name | `second_moment_of_area` |
| Description | Section second moment of area about the same principal centroidal bending axis used for the moment and neutral-axis distance |
| Quantity type | Dimensional scalar: length to the fourth power |
| Required | Required |
| Accepted units | `mm^4`, `cm^4`, `m^4`, `in^4` |
| Sign convention | Not applicable; the value must be strictly positive |
| Valid values | Any finite real number greater than zero |
| Default | None |

The caller must obtain `I` independently. The calculator must not infer a
section shape, calculate a centroid, rotate section properties, or select a
principal axis.

### 4.4 Requested stress output unit

| Property | Requirement |
| --- | --- |
| Name | `output_unit` |
| Description | Unit used to present the calculated bending normal stress |
| Quantity type | Categorical unit selection: stress |
| Required | Optional |
| Accepted units | `Pa`, `kPa`, `MPa`, `GPa`, `psi`, `ksi` |
| Sign convention | Not applicable |
| Valid values | One of the accepted stress units |
| Default | `MPa` |

The requested unit changes presentation only and must not change the physical
result.

## 5. Governing equation

The signed bending normal stress at the evaluated fiber is:

```text
σ = My / I
```

where:

| Symbol | Variable | Definition |
| --- | --- | --- |
| `σ` | Bending stress | Signed nominal normal stress at the evaluated fiber |
| `M` | Bending moment | Signed internal moment about the selected principal centroidal axis |
| `y` | Distance from neutral axis | Nonnegative distance from the selected neutral axis to the evaluated fiber |
| `I` | Second moment of area | Section second moment of area about the same selected axis |

The equation must be evaluated without premature rounding.

## 6. Sign convention

Version 0.1 uses the following explicit convention:

- Positive `σ` is tensile stress.
- Negative `σ` is compressive stress.
- Positive `M` produces positive stress at the evaluated fiber.
- Negative `M` produces negative stress at the evaluated fiber.
- `M = 0` produces `σ = 0`.
- `y = 0` produces `σ = 0` because the evaluated point lies on the neutral
  axis.
- `y` is never negative, and `I` is always positive, so a nonzero stress must
  preserve the sign of `M`.

This convention defines the evaluated fiber relative to the selected axis. It
does not infer a global coordinate system or the stress on the opposite side
of the neutral axis.

## 7. Internal canonical units

Version 0.1 must normalize inputs locally to:

| Quantity | Canonical unit |
| --- | --- |
| Bending moment | `N·mm` |
| Distance from neutral axis | `mm` |
| Second moment of area | `mm^4` |
| Calculated stress | `N/mm²`, equivalent to `MPa` |

### 7.1 Moment conversions

| Input unit | Conversion to `N·mm` |
| --- | --- |
| `N·mm` | `1` |
| `N·m` | `1,000` |
| `lbf·in` | `112.9848290276167` |
| `lbf·ft` | `1,355.8179483314004` |

### 7.2 Length conversions

| Input unit | Conversion to `mm` |
| --- | --- |
| `mm` | `1` |
| `cm` | `10` |
| `m` | `1,000` |
| `in` | `25.4` |

### 7.3 Second-moment conversions

| Input unit | Conversion to `mm^4` |
| --- | --- |
| `mm^4` | `1` |
| `cm^4` | `10,000` |
| `m^4` | `1,000,000,000,000` |
| `in^4` | `416,231.4256` |

### 7.4 Stress conversions

The canonical relationship is:

```text
1 N/mm² = 1 MPa
```

The finite canonical stress may be converted to `Pa`, `kPa`, `MPa`, `GPa`,
`psi`, or `ksi` using explicit conversion factors.

## 8. Outputs and units

A successful result must contain:

| Output | Definition |
| --- | --- |
| `calculator` | Complete calculator identity and metadata |
| `inputs` | Original moment, distance, and second-moment values with caller-supplied units, plus the requested output unit |
| `results.bending_stress` | Signed bending normal stress in the requested output unit |
| `results.stress_state` | `tension`, `compression`, or `zero` |
| `governing_equation` | Symbolic equation and substituted canonical values |
| `assumptions` | Assumptions applied to the calculation |
| `warnings` | Engineering interpretation warnings |
| `limitations` | Limitations that remain applicable to the result |
| `references` | Traceable engineering sources |

`results.stress_state` is determined from the final canonical stress:

| Condition | Stress state |
| --- | --- |
| `σ > 0` | `tension` |
| `σ < 0` | `compression` |
| `σ = 0` | `zero` |

## 9. Validation requirements

Validation must occur before a result is accepted as successful.

### 9.1 Required inputs

- `bending_moment`, `distance_from_neutral_axis`, and
  `second_moment_of_area` are required.
- Each dimensional input requires an explicit unit.
- Missing required arguments must fail with an actionable error naming the
  missing input.
- `output_unit` is optional and defaults to `MPa`.
- The implementation must not guess or silently supply required engineering
  inputs.

### 9.2 Numeric inputs

- Each numeric input must be a supported real number and representable as a
  finite calculation value.
- Python `bool` values must not be accepted as engineering numbers.
- Non-numeric inputs must raise `TypeError` naming the affected input.
- `NaN`, positive infinity, and negative infinity must raise `ValueError`
  naming the affected input.
- Bending moment may be positive, negative, or zero.
- Distance must be greater than or equal to zero.
- Second moment of area must be strictly greater than zero.
- Overflow while converting an accepted numeric input to the implementation's
  finite numeric representation must be translated into an actionable
  `ValueError`, not exposed as an unclassified `OverflowError`.

### 9.3 Units

- Moment, distance, second-moment, and output units must be strings.
- A non-string unit must raise `TypeError` naming the affected unit argument.
- A string outside the applicable allowlist must raise `ValueError` naming the
  affected unit argument and unsupported unit.
- Dimensionally incorrect units must be rejected rather than converted or
  guessed.
- Unit matching is case-sensitive in Version 0.1.

### 9.4 Conversion and calculation boundaries

The implementation must validate each numerical stage and reject:

- Moment conversion that overflows to a non-finite value.
- Distance conversion that overflows to a non-finite value.
- Second-moment conversion that overflows, underflows to zero, or produces a
  nonpositive or non-finite value.
- Multiplication `M × y` that overflows to a non-finite value.
- Multiplication underflow when both normalized `M` and `y` are nonzero but
  their product becomes zero.
- Division by an invalid or zero normalized `I`.
- Division that overflows to a non-finite stress.
- Division underflow when the normalized numerator is nonzero but the
  calculated canonical stress becomes zero.
- A final canonical stress that is not finite.
- Output conversion that overflows to a non-finite value.
- Output-conversion underflow when canonical stress is nonzero but the
  converted stress becomes zero.

Exact zero is valid only when the supplied bending moment is zero or the
supplied distance is zero. A numerical underflow must not be reported as a
physically exact zero.

No partial or valid-looking result may be returned after any validation
failure. The implementation must not clamp values, print errors, terminate the
process, or silently replace invalid values.

### 9.5 Error behavior

- Unsupported Python types and non-string unit arguments should raise
  `TypeError`.
- Invalid values, units, converted quantities, intermediate quantities, and
  results should raise `ValueError`.
- Error messages must identify the input or numerical stage that failed.
- Custom exceptions are not required.

## 10. Warning conditions

Every successful result must include this warning:

> The calculation is valid only when the supplied second moment of area, I, and
> distance from the neutral axis, y, correspond to the same bending axis and
> section orientation.

The calculator cannot verify this condition from the three numerical inputs.
It must not infer section geometry or suppress the warning based on input
values.

Version 0.1 has no additional data from which to infer load combinations,
non-principal bending, stress concentrations, yielding, or beam curvature.
Those conditions remain documented limitations rather than guessed runtime
warnings.

## 11. Engineering assumptions

Every successful result must return these assumptions:

1. The member is a straight beam at the evaluated section.
2. The section is subjected to pure bending about one principal centroidal
   axis.
3. Plane sections remain plane after bending.
4. The longitudinal normal strain varies linearly with distance from the
   neutral axis.
5. The material is continuous, homogeneous, and linearly elastic in the region
   evaluated.
6. The elastic modulus is uniform across the section.
7. Deformations and rotations are small enough for linear beam theory.
8. The supplied `I` is the section second moment of area about the selected
   principal centroidal axis.
9. The supplied `y` is measured perpendicular to that same neutral axis in the
   same section orientation.
10. The evaluated section is sufficiently far from load introduction points,
    abrupt discontinuities, and local contact regions.

## 12. Limitations

The calculator does not account for or determine:

- Section geometry, centroid location, principal-axis orientation, neutral-axis
  location, or second moment of area.
- Bending about two axes or bending about a non-principal axis.
- Combined axial force, torsion, transverse shear, pressure, or other loads.
- Shear stress or transverse-shear deformation.
- Curved-beam behavior.
- Deep-beam effects or other cases where elementary linear beam theory is not
  applicable.
- Local stress concentrations, holes, notches, welds, fillets, cracks, or local
  load introduction.
- Residual, thermal, dynamic, impact, or cyclic stress.
- Nonlinear elasticity or plastic behavior.
- Material strength, allowable stress, yielding, or factor of safety.
- Fatigue, fracture, creep, or stress relaxation.
- Beam curvature, rotation, deflection, or system stiffness.
- Lateral-torsional buckling, local buckling, or other stability modes.
- Design-code or regulatory compliance.

The calculated stress is a nominal linear-elastic bending stress, not a finding
that the beam is safe. The documented limitations must be returned with every
successful result.

## 13. References

- R. C. Hibbeler, *Mechanics of Materials*, 10th Edition, flexure formula for
  straight beams.
- F. P. Beer, E. R. Johnston Jr., J. T. DeWolf, and D. F. Mazurek,
  *Mechanics of Materials*, 8th Edition, stresses in beams under pure bending.

Every successful result must return traceable references supporting the
flexure formula and stated assumptions.

## 14. Verification requirements

Automated verification must cover reference calculations, unit equivalence,
boundaries, invalid inputs, deterministic output, and the canonical result
schema. Expected values must be independently hand-derived or checked against a
traceable mechanics-of-materials source. The production implementation must not
be the sole source of expected values.

### 14.1 SI reference example

#### Problem

A straight beam section is under a positive bending moment of `5,000 N·m`. The
supplied second moment of area about the selected principal centroidal axis is
`8,000,000 mm^4`, and the evaluated fiber is `50 mm` from the neutral axis.
Calculate the bending stress in `MPa`.

#### Normalization and calculation

```text
M = 5,000 N·m = 5,000,000 N·mm
y = 50 mm
I = 8,000,000 mm^4

σ = My / I
σ = (5,000,000 N·mm)(50 mm) / 8,000,000 mm^4
σ = 31.25 N/mm²
σ = 31.25 MPa
```

Verified result:

```text
bending_stress = 31.25 MPa
stress_state = tension
```

The result is positive because the positive-moment convention defines the
evaluated fiber as being in tension.

### 14.2 US customary reference example

#### Problem

A straight beam section is under a negative bending moment of `12,000 lbf·in`.
The supplied second moment of area about the selected principal centroidal axis
is `200 in^4`, and the evaluated fiber is `3 in` from the neutral axis. Calculate
the bending stress in `psi`.

#### Calculation

```text
M = -12,000 lbf·in
y = 3 in
I = 200 in^4

σ = My / I
σ = (-12,000 lbf·in)(3 in) / 200 in^4
σ = -180 lbf/in²
σ = -180 psi
```

Verified result:

```text
bending_stress = -180 psi
stress_state = compression
```

### 14.3 Reverse-verification check

For the SI reference example, solve the flexure equation for moment:

```text
M = σI / y
M = (31.25 N/mm²)(8,000,000 mm^4) / 50 mm
M = 5,000,000 N·mm
M = 5,000 N·m
```

The recovered moment exactly matches the supplied moment. Reverse verification
requires `y > 0`; it is not defined for an evaluated point on the neutral axis.

### 14.4 Unit-equivalence verification

The test suite must express at least one physical case in both SI and US
customary units and verify equivalent stress within a documented
floating-point tolerance. Before reference-implementation status, every
accepted moment, distance, second-moment, and output-stress unit must
participate in an automated equivalence test.

### 14.5 Boundary and invalid-input verification

Implementation tests must cover at minimum:

| Case | Expected behavior |
| --- | --- |
| Positive `M`, valid `y`, valid `I` | Return positive tensile stress |
| Negative `M`, valid `y`, valid `I` | Return negative compressive stress |
| `M = 0` | Return exact zero stress and `stress_state = zero` |
| `y = 0` | Return exact zero stress and `stress_state = zero` |
| `y < 0` | Raise `ValueError` naming the distance input |
| `I = 0` or `I < 0` | Raise `ValueError` naming the second-moment input |
| Non-numeric input or `bool` | Raise `TypeError` naming the input |
| `NaN` or positive/negative infinity | Raise `ValueError` naming the input |
| Missing required input | Raise `TypeError` naming the input |
| Unsupported or dimensionally incorrect unit | Raise `ValueError` naming the unit argument |
| Non-string unit | Raise `TypeError` naming the unit argument |
| Unit-conversion overflow | Raise `ValueError` naming the conversion stage |
| Multiplication overflow or underflow | Raise `ValueError` naming the numerator stage |
| Division overflow or underflow | Raise `ValueError` naming the stress calculation stage |
| Invalid final stress | Raise `ValueError` naming the final stress stage |
| Output-conversion overflow or underflow | Raise `ValueError` naming the output conversion stage |
| Repeated identical calculation | Return identical JSON-serializable content |

### 14.6 Canonical schema verification

Tests must verify:

- Exact required top-level keys.
- Complete calculator metadata.
- Preservation of supplied input values and unit strings.
- Signed result behavior and `stress_state` classification.
- Symbolic and substituted governing equations.
- Presence and content of assumptions, warnings, limitations, and references.
- The mandatory axis-and-orientation warning.
- JSON serialization without custom encoders.
- Deterministic repeated execution.
- Sufficient substitution precision for traceability.

## 15. Canonical result schema expectations

A successful calculation must use all eight Calculator Contract v0.1 top-level
fields:

```json
{
  "calculator": {
    "id": "stress.beam_bending",
    "name": "Beam Bending Stress Calculator",
    "version": "0.1.0",
    "category": "Stress Analysis",
    "engineering_domain": "Mechanics of Materials",
    "purpose": "Calculate signed linear-elastic normal stress at a specified distance from the neutral axis of a straight beam in pure bending about one principal centroidal axis",
    "reference_equation": "σ = My / I"
  },
  "inputs": {
    "bending_moment": {
      "value": 5000.0,
      "unit": "N·m"
    },
    "distance_from_neutral_axis": {
      "value": 50.0,
      "unit": "mm"
    },
    "second_moment_of_area": {
      "value": 8000000.0,
      "unit": "mm^4"
    },
    "output_unit": "MPa"
  },
  "results": {
    "bending_stress": {
      "value": 31.25,
      "unit": "MPa"
    },
    "stress_state": "tension"
  },
  "governing_equation": {
    "symbolic": "σ = My / I",
    "substitution": "σ = (5000000 N·mm)(50 mm) / 8000000 mm^4"
  },
  "assumptions": [
    "The member is a straight beam at the evaluated section.",
    "The section is subjected to pure bending about one principal centroidal axis.",
    "The supplied I and y correspond to that same axis and section orientation."
  ],
  "warnings": [
    "The calculation is valid only when the supplied second moment of area, I, and distance from the neutral axis, y, correspond to the same bending axis and section orientation."
  ],
  "limitations": [
    "The calculation does not determine section geometry or section properties.",
    "The calculation does not evaluate combined axial, torsional, transverse-shear, or biaxial loading.",
    "The calculation does not evaluate material strength, yielding, fatigue, factor of safety, or deflection."
  ],
  "references": [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, flexure formula for straight beams.",
    "F. P. Beer, E. R. Johnston Jr., J. T. DeWolf, and D. F. Mazurek, Mechanics of Materials, 8th Edition, stresses in beams under pure bending."
  ]
}
```

### 15.1 Output rules

- All eight canonical top-level fields are required.
- The `calculator` object must repeat every metadata field defined in Section 2.
- `inputs` must preserve caller-supplied numeric values and unit strings.
- `results.bending_stress` must contain a finite signed value and the requested
  output unit.
- `results.stress_state` must be `tension`, `compression`, or `zero`.
- The stress sign must follow the documented moment convention.
- `governing_equation.symbolic` must exactly match `σ = My / I`.
- `governing_equation.substitution` must show canonical values with sufficient
  precision for independent traceability.
- `assumptions`, `warnings`, `limitations`, and `references` must always be
  present as arrays.
- The mandatory axis-and-orientation warning must be present in every successful
  result.
- The complete result must be JSON-serializable without custom object
  serialization.
- Numerical rounding is a presentation concern and must not occur during the
  calculation.

## 16. Lightweight design decision

Version 0.1 should be implemented as one direct deterministic calculation
function with small local validation and conversion helpers only when needed.
The specification does not require or propose classes, registries, plugins,
shared frameworks, or automatic section-property calculators. Section-property
calculation remains explicitly outside scope.
