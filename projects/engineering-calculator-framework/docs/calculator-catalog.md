# Calculator Catalog

## Purpose

This catalog is the concise index of calculators available in the Engineering
Calculator Framework. It summarizes each calculator's public engineering scope
and links to the authoritative specification; it does not replace or duplicate
those specifications.

## Current framework scope

Version 0.2 provides deterministic mechanics-of-materials calculations for
simple stress-analysis cases. Each calculator validates explicit numeric values
and units, applies a documented governing equation, and returns the canonical
JSON structure defined by [Calculator Contract v0.1](architecture/calculator-contract.md).
The framework supports direct Python calls and command-line execution.

## Implemented calculators

### Axial Stress Calculator

| Field | Summary |
| --- | --- |
| Calculator ID | `stress.axial` |
| Name | Axial Stress Calculator |
| Version | `0.1.0` |
| Engineering domain | Mechanics of Materials |
| Purpose | Calculate signed average normal stress in a member subjected to a concentric axial force. |
| Inputs | Axial force (`N`, `kN`, `lbf`, `kip`); net cross-sectional area (`mm²`, `cm²`, `m²`, `in²`); optional stress output unit. |
| Outputs | Signed axial stress and loading state (`tension`, `compression`, or `unloaded`). |
| Governing equation | `σ = F / A` |
| Key assumptions | Concentric axial loading; straight prismatic member; net resisting area; average stress; static or quasi-static equilibrium; small deformation. |
| Main limitations | Excludes eccentric bending, buckling, stress concentrations, plasticity, fatigue, material strength, factor of safety, and code compliance. |
| Detailed specification | [Axial Stress Calculator Specification](calculators/axial-stress.md) |

### Solid Circular Shaft Torsional Stress Calculator

| Field | Summary |
| --- | --- |
| Calculator ID | `stress.shaft_torsion` |
| Name | Solid Circular Shaft Torsional Stress Calculator |
| Version | `0.1.0` |
| Engineering domain | Mechanics of Materials |
| Purpose | Calculate polar moment of inertia and maximum elastic torsional shear stress for a solid circular shaft under pure torque. |
| Inputs | Nonnegative torque magnitude (`N·mm`, `N·m`, `lbf·in`, `lbf·ft`); shaft diameter (`mm`, `cm`, `m`, `in`); optional stress output unit. |
| Outputs | Polar moment of inertia in the fourth power of the input diameter unit and maximum shear stress. |
| Governing equations | `J = πd⁴ / 32`; `τmax = Tc / J = 16T / (πd³)` |
| Key assumptions | Straight, solid, circular, prismatic shaft; pure static or quasi-static torque; homogeneous isotropic linear elasticity; Saint-Venant torsion; small deformation. |
| Main limitations | Excludes hollow or noncircular shafts, warping, stress concentrations, combined loading, angle of twist, yielding, fatigue, factor of safety, and code compliance. |
| Detailed specification | [Solid Circular Shaft Torsional Stress Calculator Specification](calculators/shaft-torsion.md) |

### Beam Bending Stress Calculator

| Field | Summary |
| --- | --- |
| Calculator ID | `stress.beam_bending` |
| Name | Beam Bending Stress Calculator |
| Version | `0.1.0` |
| Engineering domain | Mechanics of Materials |
| Purpose | Calculate signed linear-elastic normal stress at a specified distance from the neutral axis of a straight beam in pure bending about one principal centroidal axis. |
| Inputs | Signed bending moment (`N·mm`, `N·m`, `lbf·in`, `lbf·ft`); nonnegative distance from the neutral axis (`mm`, `cm`, `m`, `in`); positive caller-supplied second moment of area (`mm^4`, `cm^4`, `m^4`, `in^4`); stress output unit. |
| Outputs | Signed bending stress and stress state (`tension`, `compression`, or `zero`). |
| Governing equation | `σ = My / I` |
| Sign convention | Positive moment produces positive tensile stress; negative moment produces negative compressive stress; zero moment or zero distance produces zero stress. |
| Key assumptions | Straight beam; linear-elastic pure bending about one principal centroidal axis; plane sections remain plane; small deformation; caller-supplied `I` and `y`. |
| Main limitations | Excludes automatic section-property calculation, biaxial or combined loading, shear stress, material strength, yielding, factor of safety, fatigue, deflection, and code compliance. |
| Required warning | The supplied `I` and `y` must correspond to the same bending axis and section orientation; external tools may use different bending-moment sign conventions. |
| Detailed specification | [Beam Bending Stress Calculator Specification](calculators/beam-bending.md) |

## Planned calculators

The following calculators are planned and are not part of v0.2:

- Euler buckling
- Factor of safety
