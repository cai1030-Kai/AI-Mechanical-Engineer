# Euler Buckling Critical Load Calculator Specification

## 1. Engineering purpose

The Euler Buckling Critical Load Calculator determines the ideal elastic
critical buckling load of a slender, straight column about one specified
principal buckling axis.

The calculator is intended for preliminary analysis, education, and independent
verification of ideal Euler column behavior. It returns a deterministic result
that can be checked from the supplied elastic modulus, second moment of area,
unsupported length, effective length factor, units, and formula substitution.

The result is an ideal theoretical bifurcation load. It is not an allowable
load, design strength, or finding that a real column is safe.

## 2. Calculator metadata

| Field | Value |
| --- | --- |
| Calculator ID | `stability.euler_buckling` |
| Name | `Euler Buckling Critical Load Calculator` |
| Version | `0.1.0` |
| Category | `Stability Analysis` |
| Engineering domain | `Structural Stability / Mechanics of Materials` |
| Purpose | Calculate the ideal elastic critical buckling load of a slender, straight column using Euler buckling theory |
| Reference equation | `P_cr = pi^2 * E * I / (K * L)^2` |

The calculator ID is the stable machine-readable identity of this calculation.
The calculator version identifies the engineering behavior defined by this
specification and is independent of the package and Calculator Contract
versions.

## 3. Scope

### 3.1 Supported scope

Version 0.1 supports only:

- Straight, slender columns.
- Ideal elastic Euler buckling.
- Constant cross-section along the unsupported length.
- Homogeneous material.
- Concentric compressive loading through the cross-section centroid.
- Flexural buckling about one specified principal axis.
- Caller-supplied elastic modulus, `E`.
- Caller-supplied second moment of area, `I`, for the evaluated buckling axis.
- Caller-supplied unsupported length, `L`.
- Caller-supplied effective length factor, `K`.

### 3.2 Explicitly unsupported scope

Version 0.1 does not evaluate or support:

- Inelastic buckling.
- The Johnson parabolic formula or other transition-column formulas.
- Local buckling.
- Torsional buckling.
- Flexural-torsional buckling.
- Lateral-torsional buckling of beams.
- Eccentric loading.
- Initial crookedness or geometric imperfections.
- Residual stress.
- Variable cross-section.
- Combined loading.
- Safety factors or allowable loads.
- Design-code or regulatory compliance.
- Material yielding checks.
- Automatic section-property calculations.
- Automatic boundary-condition recognition or effective-length-factor lookup.

The calculator must not silently infer that Euler theory is applicable to a
particular real column. The caller must independently establish that the column
is sufficiently slender and remains elastic up to the predicted critical load.

## 4. Governing equations

The Euler critical load is:

```text
P_cr = pi^2 * E * I / (K * L)^2
```

The equivalent effective-length form is:

```text
L_eff = K * L
P_cr = pi^2 * E * I / L_eff^2
```

where:

| Symbol | Variable | Definition |
| --- | --- | --- |
| `P_cr` | Euler critical load | Ideal elastic bifurcation load for the specified axis |
| `E` | Elastic modulus | Young's modulus of the homogeneous column material |
| `I` | Second moment of area | Section second moment of area about the specified principal buckling axis |
| `K` | Effective length factor | Dimensionless representation of idealized end restraint and bracing effects |
| `L` | Unsupported length | Physical unbraced column length represented by the selected `K` |
| `L_eff` | Effective length | Product `K * L` used in Euler's equation |

`P_cr` is returned as a strictly positive magnitude for every successful
calculation. No signed compression or tension convention is needed because the
calculator accepts positive property and geometry magnitudes and evaluates a
compressive buckling capacity magnitude.

## 5. Inputs and units

### 5.1 Elastic modulus

| Property | Requirement |
| --- | --- |
| Name | `elastic_modulus` |
| Description | Young's modulus of the column material in the elastic range |
| Quantity type | Dimensional scalar: stress or pressure |
| Required | Required |
| Accepted units | `Pa`, `kPa`, `MPa`, `GPa`, `psi`, `ksi` |
| Sign convention | Not applicable; the value must be strictly positive |
| Valid values | Any finite real number greater than zero and representable by the supported numerical implementation |
| Default | None |

### 5.2 Second moment of area

| Property | Requirement |
| --- | --- |
| Name | `second_moment_of_area` |
| Description | Section second moment of area about the principal axis for which buckling is evaluated |
| Quantity type | Dimensional scalar: length to the fourth power |
| Required | Required |
| Accepted units | `mm^4`, `cm^4`, `m^4`, `in^4` |
| Sign convention | Not applicable; the value must be strictly positive |
| Valid values | Any finite real number greater than zero and representable by the supported numerical implementation |
| Default | None |

The supplied `I` must correspond to the actual buckling axis. For a section
that can buckle about more than one axis, the caller must evaluate every
relevant axis independently. The calculator does not calculate section
properties, find principal axes, or automatically select the minimum `I`.

### 5.3 Unsupported length

| Property | Requirement |
| --- | --- |
| Name | `unsupported_length` |
| Description | Physical unbraced column length represented by the selected effective length factor |
| Quantity type | Dimensional scalar: length |
| Required | Required |
| Accepted units | `mm`, `cm`, `m`, `in` |
| Sign convention | Not applicable; the value must be strictly positive |
| Valid values | Any finite real number greater than zero and representable by the supported numerical implementation |
| Default | None |

### 5.4 Effective length factor

| Property | Requirement |
| --- | --- |
| Name | `effective_length_factor` |
| Description | Dimensionless multiplier relating unsupported length to Euler effective length |
| Quantity type | Dimensionless scalar |
| Required | Required |
| Accepted units | Not applicable |
| Sign convention | Not applicable; the value must be strictly positive |
| Valid values | Any finite real number greater than zero and representable by the supported numerical implementation |
| Default | None |

Version 0.1 does not provide a boundary-condition enumeration or assign `K`
automatically. The caller is responsible for selecting a value consistent with
the actual column restraints, bracing, joint stiffness, and frame behavior.

Common textbook idealizations are guidance only:

| Idealized end condition | Common effective length factor |
| --- | ---: |
| Fixed-fixed | `K = 0.5` |
| Fixed-pinned | `K approximately 0.7` |
| Pinned-pinned | `K = 1.0` |
| Fixed-free | `K = 2.0` |

Real structural boundary conditions may not match these idealizations. Partial
restraint, connection flexibility, sway behavior, bracing stiffness, and load
path can materially change the appropriate effective length.

### 5.5 Critical load output unit

| Property | Requirement |
| --- | --- |
| Name | `output_unit` |
| Description | Unit used to present the converted Euler critical load |
| Quantity type | Categorical unit selection: force |
| Required | Optional |
| Accepted units | `N`, `kN`, `MN`, `lbf`, `kip` |
| Sign convention | Not applicable |
| Valid values | One of the accepted force units |
| Default | `kN` |

The output unit affects presentation only and must not change the underlying
physical result.

## 6. Internal canonical units

Version 0.1 normalizes inputs locally to:

| Quantity | Canonical unit |
| --- | --- |
| Elastic modulus, `E` | `MPa`, equivalent to `N/mm^2` |
| Second moment of area, `I` | `mm^4` |
| Unsupported length, `L` | `mm` |
| Effective length factor, `K` | Dimensionless |
| Effective length, `L_eff` | `mm` |
| Critical load, `P_cr` | `N` |

Useful exact or defined conversion relationships include:

```text
1 kPa = 0.001 MPa
1 GPa = 1000 MPa
1 psi = 0.006894757293168361 MPa
1 ksi = 6.894757293168361 MPa

1 cm^4 = 10000 mm^4
1 m^4 = 10^12 mm^4
1 in^4 = 416231.4256 mm^4

1 cm = 10 mm
1 m = 1000 mm
1 in = 25.4 mm

1 kN = 1000 N
1 MN = 1000000 N
1 lbf = 4.4482216152605 N
1 kip = 4448.2216152605 N
```

Unit matching is case-sensitive. Units must be explicit; the calculator must
not guess omitted units or silently reinterpret unsupported strings.

## 7. Outputs

Every successful result must include at least:

| Output | Definition |
| --- | --- |
| `results.effective_length` | Canonical effective length `K * L` in `mm` |
| `results.critical_load_newtons` | Canonical Euler critical load magnitude in `N` |
| `results.critical_load` | Euler critical load magnitude converted to the requested output unit |
| `results.buckling_axis_traceability` | Statement that the result applies only to the axis represented by the caller-supplied `I` |
| `governing_equation` | Symbolic equations and substituted canonical values |

The buckling-axis traceability statement must communicate substantially the
following:

> This result applies to the buckling axis represented by the caller-supplied
> second moment of area, I; other relevant axes must be evaluated separately.

The critical load must remain strictly positive. A nonzero physical result that
underflows to zero is invalid and must not be returned as an exact zero.

## 8. Validation requirements

### 8.1 Required inputs

The implementation must require:

- `elastic_modulus_value`
- `elastic_modulus_unit`
- `second_moment_of_area_value`
- `second_moment_of_area_unit`
- `unsupported_length_value`
- `unsupported_length_unit`
- `effective_length_factor`

`output_unit` may default to `kN`.

### 8.2 Numeric inputs

Each numeric input must:

- Be a supported real number.
- Not be a Boolean value.
- Be representable as a finite value in the supported numerical implementation.
- Not be `NaN`, positive infinity, or negative infinity.
- Be strictly greater than zero.

Missing arguments are rejected by the Python function signature. Unsupported
Python types should raise `TypeError`. Invalid numerical values should raise
`ValueError` identifying the affected input.

### 8.3 Units

Every unit argument must be a string and exactly match an accepted unit.
Non-string unit arguments should raise `TypeError`. Unsupported or
dimensionally inappropriate unit strings should raise `ValueError` identifying
the unit argument.

### 8.4 Conversion and calculation boundaries

The implementation must validate every numerical stage and reject:

1. Elastic-modulus conversion that overflows, underflows to zero, or becomes
   non-finite.
2. Second-moment conversion that overflows, underflows to zero, or becomes
   non-finite.
3. Unsupported-length conversion that overflows, underflows to zero, or becomes
   non-finite.
4. Effective-length multiplication that overflows, underflows to zero, or
   becomes non-finite.
5. Effective-length squaring that overflows, underflows to zero, or becomes
   non-finite.
6. Flexural-rigidity or numerator multiplication that overflows, underflows to
   zero, or becomes non-finite.
7. Final division that overflows, underflows to zero, or becomes non-finite.
8. A canonical critical load that is zero, negative, or non-finite.
9. Output conversion that overflows, underflows to zero, or becomes non-finite.

Expected caller and numerical-boundary failures must be translated into
actionable `TypeError` or `ValueError` exceptions. Raw arithmetic
`OverflowError` exceptions must not escape.

No partial or valid-looking result may be returned after a validation failure.
The calculator must not clamp values, replace invalid inputs, print errors,
terminate the process, or infer missing engineering data.

## 9. Warning conditions

Every successful result must return all of the following warnings:

1. Euler buckling is valid only for sufficiently slender columns that remain
   elastic up to buckling.
2. The supplied second moment of area, `I`, must correspond to the actual
   buckling axis.
3. The effective length factor, `K`, depends on real end restraints and may
   differ from idealized textbook values.
4. This calculator does not determine whether yielding or inelastic buckling
   occurs before Euler buckling.
5. The result is an ideal theoretical critical load, not an allowable design
   load.

These warnings are unconditional because Version 0.1 does not receive all the
section geometry, material strength, imperfection, and restraint data required
to establish applicability.

## 10. Engineering assumptions

Every successful result must return assumptions equivalent to the following:

1. The column is initially straight and slender.
2. The column has a constant cross-section over the unsupported length.
3. The material is homogeneous and remains linearly elastic up to buckling.
4. The compressive load is applied concentrically through the section
   centroid.
5. The supplied `I` is the second moment of area about the specified principal
   buckling axis.
6. The unsupported length and effective length factor represent the same
   braced segment and restraint model.
7. The idealized end-restraint representation remains valid through the onset
   of buckling.
8. Euler small-deflection stability theory is appropriate up to the critical
   state.

## 11. Limitations

The calculator does not determine or account for:

- Column slenderness or a limiting slenderness criterion.
- Radius of gyration or cross-sectional area.
- Yield strength, proportional limit, or material nonlinearity.
- Yielding or inelastic buckling before the Euler load.
- Johnson parabolic or other empirical transition-column behavior.
- Local, torsional, flexural-torsional, or lateral-torsional buckling.
- Initial crookedness, geometric imperfections, residual stress, or accidental
  eccentricity.
- Load eccentricity or combined axial and bending effects.
- Variable section properties, tapered members, built-up behavior, or partial
  composite action.
- Connection flexibility, frame sidesway, bracing deformation, or automatic
  determination of `K`.
- Post-buckling behavior.
- Safety factors, allowable loads, resistance factors, or reliability.
- Design-code or regulatory compliance.
- Automatic section-property or principal-axis calculation.

No slenderness-ratio validity decision is made because Version 0.1 does not
receive every required geometry and strength property. The absence of such a
decision must never be interpreted as confirmation that Euler theory applies.

## 12. References

- R. C. Hibbeler, *Mechanics of Materials*, 10th Edition, chapter on column
  buckling, including the critical load for long slender columns and effective
  length for columns with different supports.
- F. P. Beer, E. R. Johnston Jr., J. T. DeWolf, and D. F. Mazurek,
  *Mechanics of Materials*, 8th Edition, chapter on columns, including Euler's
  formula and columns with various end conditions.
- S. P. Timoshenko and J. M. Gere, *Theory of Elastic Stability*, 2nd Edition,
  chapter on buckling of bars and the Euler column.

The references identify the governing theory and applicability assumptions.
No page numbers are asserted because pagination can vary by printing and
edition format.

## 13. Verification requirements

Automated verification must cover reference calculations, unit equivalence,
reverse verification, sensitivity, boundaries, invalid inputs, deterministic
output, and the canonical result schema. Expected values must be independently
derived or checked against a traceable mechanics-of-materials or structural-
stability source.

### 13.1 SI reference example

#### Problem

A pinned-pinned ideal column has:

```text
E = 200 GPa
I = 8,000,000 mm^4
L = 3 m
K = 1.0
```

Calculate its Euler critical load.

#### Normalization and calculation

```text
E = 200 GPa = 200,000 MPa = 200,000 N/mm^2
I = 8,000,000 mm^4
L = 3 m = 3,000 mm
K = 1.0
L_eff = K * L = 1.0 * 3,000 mm = 3,000 mm

P_cr = pi^2 * E * I / L_eff^2
P_cr = pi^2 * (200,000 N/mm^2) * (8,000,000 mm^4)
       / (3,000 mm)^2
P_cr = 1,754,596.337971 N
P_cr = 1,754.596337971 kN
P_cr = 1.754596337971 MN
```

Expected result to reasonable precision:

```text
effective_length = 3,000 mm
critical_load_newtons = 1,754,596.338 N
critical_load = 1,754.596338 kN
```

### 13.2 US customary reference example

#### Problem

A pinned-pinned ideal column has:

```text
E = 29,000 ksi
I = 10 in^4
L = 120 in
K = 1.0
```

Because `ksi * in^4 / in^2` reduces to `kip`, the calculation can be checked
directly in US customary units:

```text
L_eff = 1.0 * 120 in = 120 in

P_cr = pi^2 * (29,000 kip/in^2) * (10 in^4) / (120 in)^2
P_cr = 198.762866411 kip
P_cr = 198,762.866411 lbf
```

Expected result to reasonable precision:

```text
critical_load = 198.762866 kip
```

### 13.3 Reverse-verification example

Recover the supplied second moment of area from the SI reference result:

```text
I = P_cr * L_eff^2 / (pi^2 * E)

I = (1,754,596.337971 N) * (3,000 mm)^2
    / (pi^2 * 200,000 N/mm^2)

I = 8,000,000 mm^4
```

The recovered `I` matches the original caller-supplied value.

### 13.4 Unit-equivalence example

The US customary reference case can be represented in canonical SI units as:

```text
E = 29,000 ksi = 199,947.961501882 MPa
I = 10 in^4 = 4,162,314.256 mm^4
L = 120 in = 3,048 mm
K = 1.0
```

Both representations must return the same physical critical load within an
appropriate floating-point tolerance:

```text
P_cr = 198.762866411 kip
P_cr = 884.141278680 kN
```

The automated test must compare physical results after conversion rather than
requiring identical decimal representations.

### 13.5 Sensitivity observations

From:

```text
P_cr = pi^2 * E * I / (K * L)^2
```

the following proportional relationships must be verified:

| Change from a reference case | Expected critical-load change |
| --- | --- |
| Double `E` while holding all other inputs constant | `P_cr` doubles |
| Double `I` while holding all other inputs constant | `P_cr` doubles |
| Double `K` while holding all other inputs constant | `P_cr` becomes one quarter |
| Double `L` while holding all other inputs constant | `P_cr` becomes one quarter |

These checks verify equation sensitivity but do not establish Euler-theory
applicability for the altered columns.

### 13.6 Boundary and invalid-input verification

Implementation tests must cover at minimum:

| Case | Expected behavior |
| --- | --- |
| Valid positive inputs | Return positive finite effective length and critical load |
| Missing required input | Raise `TypeError` naming the missing argument |
| Boolean numeric input | Raise `TypeError` naming the input |
| Non-numeric input | Raise `TypeError` naming the input |
| `NaN` or positive/negative infinity | Raise `ValueError` naming the input |
| `E <= 0` | Raise `ValueError` naming the elastic-modulus input |
| `I <= 0` | Raise `ValueError` naming the second-moment input |
| `L <= 0` | Raise `ValueError` naming the length input |
| `K <= 0` | Raise `ValueError` naming the effective-length-factor input |
| Non-string unit | Raise `TypeError` naming the unit input |
| Unsupported or dimensionally incorrect unit | Raise `ValueError` naming the unit input |
| Unit-conversion overflow or underflow | Raise `ValueError` naming the conversion stage |
| Effective-length multiplication overflow or underflow | Raise `ValueError` naming the effective-length stage |
| Effective-length squaring overflow or underflow | Raise `ValueError` naming the squared-effective-length stage |
| Numerator multiplication overflow or underflow | Raise `ValueError` naming the numerator or flexural-rigidity stage |
| Final division overflow or underflow | Raise `ValueError` naming the critical-load stage |
| Invalid or non-finite critical load | Raise `ValueError` naming the critical-load stage |
| Output-conversion overflow or underflow | Raise `ValueError` naming the output-conversion stage |
| Repeated identical calculation | Return identical JSON-serializable content |

### 13.7 Canonical schema verification

Tests must verify:

- Exact required top-level keys.
- Complete calculator metadata.
- Preservation of caller-supplied input values and unit strings.
- Canonical and output-converted critical loads.
- Effective length in canonical units.
- Buckling-axis traceability statement.
- Symbolic equations and substituted canonical values.
- Presence and required content of assumptions, warnings, limitations, and
  references.
- All five mandatory warnings.
- JSON serialization without custom encoders.
- Deterministic repeated execution.
- Sufficient substitution precision for independent traceability.

## 14. Canonical result schema expectations

A successful calculation must return a JSON-serializable dictionary with
exactly these eight top-level sections:

```json
{
  "calculator": {
    "id": "stability.euler_buckling",
    "name": "Euler Buckling Critical Load Calculator",
    "version": "0.1.0",
    "category": "Stability Analysis",
    "engineering_domain": "Structural Stability / Mechanics of Materials",
    "purpose": "Calculate the ideal elastic critical buckling load of a slender, straight column using Euler buckling theory",
    "reference_equation": "P_cr = pi^2 * E * I / (K * L)^2"
  },
  "inputs": {
    "elastic_modulus": {
      "value": 200.0,
      "unit": "GPa"
    },
    "second_moment_of_area": {
      "value": 8000000.0,
      "unit": "mm^4"
    },
    "unsupported_length": {
      "value": 3.0,
      "unit": "m"
    },
    "effective_length_factor": 1.0,
    "output_unit": "kN"
  },
  "results": {
    "effective_length": {
      "value": 3000.0,
      "unit": "mm"
    },
    "critical_load_newtons": {
      "value": 1754596.3379714414,
      "unit": "N"
    },
    "critical_load": {
      "value": 1754.5963379714414,
      "unit": "kN"
    },
    "buckling_axis_traceability": "This result applies to the buckling axis represented by the caller-supplied second moment of area, I; other relevant axes must be evaluated separately."
  },
  "governing_equation": {
    "symbolic": "L_eff = K * L; P_cr = pi^2 * E * I / L_eff^2",
    "substitution": "L_eff = 1 * 3000 mm = 3000 mm; P_cr = pi^2 * (200000 N/mm^2) * (8000000 mm^4) / (3000 mm)^2 = 1754596.3379714414 N"
  },
  "assumptions": [
    "The column is initially straight, slender, and has a constant cross-section.",
    "The material remains linearly elastic up to buckling.",
    "The load is concentric and the supplied I represents the evaluated principal buckling axis."
  ],
  "warnings": [
    "Euler buckling is valid only for sufficiently slender columns that remain elastic up to buckling.",
    "The supplied I must correspond to the actual buckling axis.",
    "K depends on real end restraints and may differ from idealized textbook values.",
    "This calculator does not determine whether yielding or inelastic buckling occurs first.",
    "The result is an ideal theoretical critical load, not an allowable design load."
  ],
  "limitations": [
    "The calculation does not evaluate inelastic, local, torsional, or flexural-torsional buckling.",
    "The calculation does not determine section properties, effective length factor, yielding, safety factors, or code compliance."
  ],
  "references": [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, chapter on column buckling.",
    "F. P. Beer et al., Mechanics of Materials, 8th Edition, chapter on columns.",
    "S. P. Timoshenko and J. M. Gere, Theory of Elastic Stability, 2nd Edition, chapter on buckling of bars."
  ]
}
```

### 14.1 Output rules

- All eight Calculator Contract v0.1 top-level sections are required.
- `calculator` must repeat every metadata field defined in Section 2.
- `inputs` must preserve the caller-supplied numeric values and unit strings in
  the supported floating-point representation.
- `results.effective_length` must contain a strictly positive finite value in
  `mm`.
- `results.critical_load_newtons` must contain the strictly positive canonical
  critical load in `N`.
- `results.critical_load` must contain the same physical result in the requested
  output unit.
- `results.buckling_axis_traceability` must identify the relationship between
  the result and the caller-supplied `I`.
- `governing_equation.symbolic` must include both the effective-length and Euler
  critical-load equations.
- `governing_equation.substitution` must show `E`, `I`, `K`, `L`, `L_eff`, and
  `P_cr` in canonical units with sufficient precision for independent checking.
- `assumptions`, `warnings`, `limitations`, and `references` must always be
  present as arrays.
- All five required warnings from Section 9 must be present in every successful
  result.
- The complete result must be JSON-serializable without custom object
  serialization.
- Numerical rounding is a presentation concern and must not occur during the
  calculation.

## 15. Engineering decisions

Version 0.1 deliberately makes the following decisions:

1. Critical load is a nonnegative magnitude; no signed axial-load convention
   is introduced.
2. `K` is a caller-supplied positive dimensionless scalar.
3. No boundary-condition enumeration or automatic `K` assignment is provided.
4. No slenderness-ratio applicability decision is made without the additional
   geometry and strength data required to support it.
5. Applicability is communicated through unconditional warnings and explicit
   limitations rather than a silent validity claim.
6. `I` is caller supplied, and the output preserves buckling-axis traceability.
7. No section-property, material-strength, safety-factor, or design-code logic
   is included.

## 16. Lightweight design decision

Version 0.1 should remain one direct deterministic calculation function with
small local validation and conversion helpers. This specification does not
require or propose classes, base calculators, registries, factories, plugins,
dependency injection, a generic unit engine, a shared framework, automatic
section-property calculations, or automatic end-condition inference.
