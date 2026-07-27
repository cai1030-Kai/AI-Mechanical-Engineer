# Calculator Catalog

## Purpose

This catalog is the concise index of calculators available in the Engineering
Calculator Framework. It summarizes each calculator's public engineering scope
and links to the authoritative specification; it does not replace or duplicate
those specifications.

## Current framework scope

Version 0.1 provides deterministic mechanics-of-materials calculations for
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

## Planned calculators

The following calculators are planned and are not part of v0.1:

- Beam bending stress
- Euler buckling
- Factor of safety
