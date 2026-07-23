# Solid Circular Shaft Torsional Stress Calculator Specification

## 1. Engineering purpose

The Solid Circular Shaft Torsional Stress Calculator determines:

- The polar moment of inertia of a solid circular cross-section.
- The maximum elastic torsional shear stress at the shaft surface.

It is intended for preliminary analysis, education, and verification of
straight, solid circular shafts subjected to pure torque.

The calculator evaluates nominal torsional shear stress only. It does not
determine angle of twist, combined stress, stress concentration, fatigue
strength, yielding, factor of safety, or design-code compliance.

## 2. Calculator metadata

| Field | Value |
| --- | --- |
| Calculator ID | `stress.shaft_torsion` |
| Name | `Solid Circular Shaft Torsional Stress Calculator` |
| Version | `0.1.0` |
| Category | `Stress Analysis` |
| Engineering Domain | `Mechanics of Materials` |
| Purpose | Calculate the polar moment of inertia and maximum elastic torsional shear stress in a solid circular shaft subjected to pure torque |
| Reference Equation | `J = πd⁴ / 32; τmax = Tc / J = 16T / (πd³)` |

The Calculator ID is the stable machine-readable identity. Stored results and
future integrations must use `stress.shaft_torsion`.

The calculator version is independent of the Python package version. A
successful result must include the calculator version so its equation,
validation rules, assumptions, and output meaning remain traceable.

## 3. Input schema

### 3.1 Applied torque magnitude

| Property | Requirement |
| --- | --- |
| Name | `torque` |
| Description | Magnitude of the resultant torque applied about the shaft axis |
| Quantity type | Dimensional scalar: torque |
| Required | Required |
| Accepted units | `N·mm`, `N·m`, `lbf·in`, `lbf·ft` |
| Sign convention | Nonnegative magnitude; zero represents an unloaded shaft and negative values are invalid |
| Valid values | Any finite real number greater than or equal to zero |
| Default | None |

The calculator accepts torque magnitude rather than signed torque. A negative
torque has no unambiguous physical meaning without a declared shaft axis and
right-hand coordinate convention.

### 3.2 Shaft diameter

| Property | Requirement |
| --- | --- |
| Name | `diameter` |
| Description | Actual outside diameter of the solid circular shaft at the evaluated section |
| Quantity type | Dimensional scalar: length |
| Required | Required |
| Accepted units | `mm`, `cm`, `m`, `in` |
| Sign convention | Not applicable; diameter must be strictly positive |
| Valid values | Any finite real number greater than zero |
| Default | None |

The diameter must describe a solid circular section. A nominal diameter must
not be used when a thread root, keyway, groove, corrosion loss, or other local
geometry controls the resisting section.

### 3.3 Requested stress output unit

| Property | Requirement |
| --- | --- |
| Name | `output_unit` |
| Description | Unit used to present the calculated maximum shear stress |
| Quantity type | Categorical unit selection: stress |
| Required | Optional |
| Accepted units | `Pa`, `kPa`, `MPa`, `GPa`, `psi`, `ksi` |
| Sign convention | Not applicable |
| Valid values | One of the accepted stress units |
| Default | `MPa` |

The output-unit selection changes presentation only. It must not change the
underlying physical result.

## 4. Accepted units and normalization

Version 0.1 uses explicit unit allowlists. Unitless dimensional inputs are
invalid.

### 4.1 Torque units

| Unit | Normalization to `N·mm` |
| --- | --- |
| `N·mm` | `1 N·mm = 1 N·mm` |
| `N·m` | `1 N·m = 1,000 N·mm` |
| `lbf·in` | `1 lbf·in = 112.9848290276167 N·mm` |
| `lbf·ft` | `1 lbf·ft = 1,355.8179483314004 N·mm` |

### 4.2 Diameter units

| Unit | Normalization to `mm` |
| --- | --- |
| `mm` | `1 mm = 1 mm` |
| `cm` | `1 cm = 10 mm` |
| `m` | `1 m = 1,000 mm` |
| `in` | `1 in = 25.4 mm` |

### 4.3 Stress units

The normalized stress unit is:

```text
1 N/mm² = 1 MPa
```

The normalized result may be converted to `Pa`, `kPa`, `MPa`, `GPa`, `psi`, or
`ksi`.

### 4.4 Polar moment output unit

The polar moment of inertia must be returned in the fourth power of the
diameter input unit:

| Diameter unit | Polar moment unit |
| --- | --- |
| `mm` | `mm⁴` |
| `cm` | `cm⁴` |
| `m` | `m⁴` |
| `in` | `in⁴` |

This rule avoids an additional output-unit input while keeping the geometric
result intuitive for the caller.

## 5. Governing equations

For a solid circular shaft:

```text
J = πd⁴ / 32
```

The maximum torsional shear stress occurs at the outer surface, where
`c = d / 2`:

```text
τmax = Tc / J
```

Substituting `c = d / 2` and `J = πd⁴ / 32`:

```text
τmax = 16T / (πd³)
```

Version 0.1 treats `T` as a nonnegative torque magnitude. Therefore `τmax` is a
nonnegative stress magnitude.

## 6. Variables

| Symbol | Variable | Definition |
| --- | --- | --- |
| `J` | Polar moment of inertia | Geometric resistance of the solid circular cross-section to torsion |
| `d` | Shaft diameter | Outside diameter of the solid circular shaft |
| `c` | Outer radius | Distance from the shaft center to its outer surface, `c = d / 2` |
| `T` | Applied torque magnitude | Resultant torque acting about the shaft axis |
| `τmax` | Maximum shear stress | Maximum nominal elastic torsional shear stress at the shaft surface |
| `π` | Pi | Mathematical constant |

The shear stress distribution is zero at the shaft center and increases
linearly with radius under the stated assumptions.

## 7. Output schema

A successful calculation must use the Calculator Contract v0.1 canonical
structure:

```json
{
  "calculator": {
    "id": "stress.shaft_torsion",
    "name": "Solid Circular Shaft Torsional Stress Calculator",
    "version": "0.1.0",
    "category": "Stress Analysis",
    "engineering_domain": "Mechanics of Materials",
    "purpose": "Calculate the polar moment of inertia and maximum elastic torsional shear stress in a solid circular shaft subjected to pure torque",
    "reference_equation": "J = πd⁴ / 32; τmax = Tc / J = 16T / (πd³)"
  },
  "inputs": {
    "torque": {
      "value": 500.0,
      "unit": "N·m"
    },
    "diameter": {
      "value": 40.0,
      "unit": "mm"
    },
    "output_unit": "MPa"
  },
  "results": {
    "polar_moment_of_inertia": {
      "value": 251327.412287183,
      "unit": "mm⁴"
    },
    "maximum_shear_stress": {
      "value": 39.7887357729738,
      "unit": "MPa"
    }
  },
  "governing_equation": {
    "symbolic": "J = πd⁴ / 32; τmax = Tc / J = 16T / (πd³)",
    "substitution": "J = π(40 mm)⁴ / 32; τmax = 16(500000 N·mm) / (π(40 mm)³)"
  },
  "assumptions": [
    "The shaft is straight, solid, circular, and prismatic at the evaluated section.",
    "The applied load is pure torque about the shaft centroidal axis.",
    "The material is homogeneous, isotropic, and linearly elastic.",
    "Saint-Venant torsion applies and deformation is small.",
    "The evaluated section is away from load introduction points and geometric discontinuities."
  ],
  "warnings": [],
  "limitations": [
    "The calculation does not apply to hollow or noncircular shafts.",
    "The calculation does not include stress concentration from keyways, splines, shoulders, grooves, holes, or cracks.",
    "The calculation does not evaluate angle of twist.",
    "The calculation does not evaluate combined loading.",
    "The calculation does not evaluate yielding, factor of safety, fatigue, fracture, or code compliance."
  ],
  "references": [
    "R. C. Hibbeler, Mechanics of Materials, 10th Edition, torsion of circular shafts.",
    "R. G. Budynas and J. K. Nisbett, Shigley's Mechanical Engineering Design, 11th Edition, torsional shear stress in circular shafts."
  ]
}
```

### 7.1 Output rules

- All eight canonical top-level fields are required.
- The `calculator` object must contain all metadata defined in Section 2.
- `inputs` must preserve the caller's numeric values and unit strings.
- `results.polar_moment_of_inertia` must contain a finite nonnegative value and
  its fourth-power length unit.
- `results.maximum_shear_stress` must contain a finite nonnegative value and the
  requested stress unit.
- `governing_equation.symbolic` must contain both governing equations.
- `governing_equation.substitution` must show normalized torque and diameter
  with sufficient precision for traceability.
- `assumptions`, `warnings`, `limitations`, and `references` must always be
  present as arrays.
- A successful calculation with no warnings must return an empty warnings
  array.
- The complete result must be JSON-serializable without custom object
  serialization.
- Numerical rounding must occur only in presentation, not during calculation.

## 8. Validation rules

Validation must occur before a result is accepted as successful.

### 8.1 Required inputs

- `torque` is required.
- `diameter` is required.
- Their corresponding units are required.
- Missing required inputs must produce an actionable error naming the missing
  input.
- `output_unit` is optional and defaults to `MPa`.

### 8.2 Numerical validation

- Torque must be a real, finite number.
- Torque must be greater than or equal to zero.
- Diameter must be a real, finite number.
- Diameter must be strictly greater than zero.
- `NaN`, positive infinity, and negative infinity are invalid.
- Python `bool` values must not be accepted as engineering numbers.

### 8.3 Unit validation

- Torque units must come from the torque allowlist.
- Diameter units must come from the diameter allowlist.
- Output units must come from the stress allowlist.
- Unit arguments must be strings.
- Unitless dimensional inputs are invalid.
- Dimensionally incorrect units must be rejected, not guessed or coerced.
- Unit matching is case-sensitive in Version 0.1.

### 8.4 Intermediate and result validation

The calculator must reject:

- Non-finite normalized torque.
- Non-finite or nonpositive normalized diameter.
- Non-finite, zero, or negative calculated polar moment of inertia.
- Non-finite calculated maximum shear stress.
- Non-finite output-converted maximum shear stress.
- Numerical underflow that makes a positive diameter or polar moment equal to
  zero.

No partial result may be returned after a validation failure.

### 8.5 Error behavior

- Unsupported Python input types must raise `TypeError`.
- Invalid values, units, intermediate quantities, and results must raise
  `ValueError`.
- Error messages must identify the affected input or calculation stage.
- The calculation module must not print, terminate the process, clamp values,
  or silently substitute valid-looking defaults.

## 9. Engineering assumptions

The calculation is valid under the following assumptions:

1. The shaft is straight and prismatic at the evaluated section.
2. The cross-section is solid and circular.
3. The applied load is pure torque about the shaft centroidal axis.
4. The torque is static or quasi-static.
5. The material is continuous, homogeneous, and isotropic.
6. The material remains within the linearly elastic range.
7. Saint-Venant torsion is applicable.
8. Deformation and angle of twist are small.
9. Plane cross-sections remain plane and rotate without significant warping.
10. The evaluated section is sufficiently far from load application points,
    abrupt geometry changes, and local contact regions.
11. The supplied diameter represents the actual resisting solid section.

These assumptions must be returned in every successful result.

## 10. Warnings

The Version 0.1 inputs do not contain enough information to infer keyways,
eccentric loading, combined loading, material yielding, or dynamic effects.
Therefore, a normal successful result returns:

```json
{
  "warnings": []
}
```

Future interfaces may add warnings when additional caller-provided context
indicates:

- The shaft may contain a keyway, spline, groove, shoulder, hole, or crack.
- The shaft may be hollow or noncircular.
- Bending, axial force, or transverse shear may act with torque.
- Loading may be cyclic, dynamic, or impact-driven.
- The calculated stress may be compared with incomplete or inappropriate
  material strength data.

These conditions must not be inferred from torque and diameter alone.

## 11. Limitations

The calculator does not account for:

- Hollow shafts.
- Noncircular sections.
- Thin-walled torsion.
- Warping torsion outside the stated assumptions.
- Keyways, splines, grooves, shoulders, holes, cracks, or other stress
  concentrations.
- Local load introduction or contact stress.
- Combined bending, axial, transverse-shear, or pressure loading.
- Angle of twist or torsional stiffness of the complete shaft.
- Nonlinear elasticity or plastic torsion.
- Residual, thermal, dynamic, or impact stress.
- Material strength, yielding, or factor of safety.
- Fatigue, fracture, creep, or stress relaxation.
- Stability or vibration.
- Design-code or regulatory compliance.

The nominal maximum shear stress must not be interpreted as proof that the
shaft is safe. The result is suitable for education and preliminary engineering
checks and does not replace detailed analysis, applicable standards, testing,
or professional engineering review.

The documented limitations must be returned with every successful result.

## 12. References

- R. C. Hibbeler, *Mechanics of Materials*, 10th Edition, torsion of circular
  shafts.
- R. G. Budynas and J. K. Nisbett, *Shigley's Mechanical Engineering Design*,
  11th Edition, torsional shear stress in circular shafts.

The implementation must return these traceable engineering references with
every successful result.

## 13. Verification examples

### 13.1 SI reference calculation

#### Problem

A solid circular shaft with diameter `40 mm` carries a torque magnitude of
`500 N·m`. Calculate `J` and `τmax`.

#### Given and normalization

```text
T = 500 N·m = 500,000 N·mm
d = 40 mm
c = 20 mm
```

#### Polar moment calculation

```text
J = πd⁴ / 32
J = π(40 mm)⁴ / 32
J = 251,327.412287183 mm⁴
```

#### Maximum shear stress calculation

```text
τmax = Tc / J
τmax = (500,000 N·mm)(20 mm) / 251,327.412287183 mm⁴
τmax = 39.7887357729738 N/mm²
τmax = 39.7887357729738 MPa
```

Equivalent direct-equation check:

```text
τmax = 16T / (πd³)
τmax = 16(500,000 N·mm) / (π(40 mm)³)
τmax = 39.7887357729738 MPa
```

Reverse torque check:

```text
T = τmaxπd³ / 16
T = (39.7887357729738 N/mm²)π(40 mm)³ / 16
T = 500,000 N·mm
T = 500 N·m
```

Verified result:

```text
polar_moment_of_inertia = 251,327.412287183 mm⁴
maximum_shear_stress = 39.7887357729738 MPa
```

### 13.2 US customary reference calculation

#### Problem

A solid circular shaft with diameter `2 in` carries a torque magnitude of
`1,000 lbf·in`. Calculate `J` and `τmax`.

#### Polar moment calculation

```text
J = πd⁴ / 32
J = π(2 in)⁴ / 32
J = 1.5707963267949 in⁴
```

#### Maximum shear stress calculation

```text
τmax = 16T / (πd³)
τmax = 16(1,000 lbf·in) / (π(2 in)³)
τmax = 636.619772367581 lbf/in²
τmax = 636.619772367581 psi
```

Reverse torque check:

```text
T = τmaxπd³ / 16
T = (636.619772367581 lbf/in²)π(2 in)³ / 16
T = 1,000 lbf·in
```

Verified result:

```text
polar_moment_of_inertia = 1.5707963267949 in⁴
maximum_shear_stress = 636.619772367581 psi
```

### 13.3 SI and US customary equivalence

The SI reference inputs are physically equivalent to:

```text
500 N·m = 4,425.37288368934 lbf·in
40 mm = 1.5748031496063 in
```

Equivalent results:

```text
251,327.412287183 mm⁴ = 0.603816523283636 in⁴
39.7887357729738 MPa = 5,770.86822365717 psi
```

Calculations expressed in either unit system must agree within the documented
floating-point tolerance.

### 13.4 Boundary and invalid-input verification

Implementation tests must cover at minimum:

| Case | Expected behavior |
| --- | --- |
| `T = 0` with valid diameter | Return `J > 0` and `τmax = 0` |
| `T < 0` | Raise `ValueError` |
| `d = 0` | Raise `ValueError` |
| `d < 0` | Raise `ValueError` |
| `NaN` or infinity | Raise `ValueError` |
| Non-numeric value | Raise `TypeError` |
| Missing required input | Raise `TypeError` naming the input |
| Unsupported unit | Raise `ValueError` naming the unit argument |
| Non-string unit | Raise `TypeError` naming the unit argument |
| Non-finite normalized quantity | Raise `ValueError` naming the calculation stage |
| Polar-moment underflow or overflow | Raise `ValueError` |
| Stress underflow or overflow | Raise `ValueError` |

Before the calculator is designated as a reference implementation, every
accepted torque, diameter, and output-stress unit must participate in an
automated unit-equivalence test.

## 14. Design decisions

### Torque is a magnitude

Version 0.1 rejects negative torque rather than inventing a coordinate system.
This makes `τmax` an unambiguous nonnegative maximum stress magnitude.

### Solid circular geometry only

The solid-shaft equation is not generalized to hollow or noncircular sections.
Those geometries require different equations and should be separate
calculators or future explicitly scoped extensions.

### Explicit local unit support

The specification defines a small accepted unit set. Implementation should keep
conversion behavior local until repeated calculator code demonstrates a need
for a shared unit component.

### Polar moment follows the diameter unit

Returning `J` in the fourth power of the caller's diameter unit keeps the result
readable without adding another input or output-unit abstraction.

### No material-strength judgment

The calculator returns nominal stress but does not label a shaft safe or
unsafe. Material failure and factor of safety require additional inputs,
criteria, and assumptions.
