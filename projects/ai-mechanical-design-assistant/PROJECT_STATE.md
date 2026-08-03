# Project State

## Current project status

Current Milestone: Milestone 6 Implemented — Awaiting Architecture Review

This document is the canonical record of the current frozen architecture and
completed milestones for AI Mechanical Design Assistant.

## Current frozen pipeline

```text
Raw Request
    ↓
Normalizer
    ↓
Validator
    ↓
ReviewRequest
    ↓
ReviewEngine
    ↓
ordered Review Rules
    ↓
ReviewFinding tuple
    ↓
ReviewResult
    ↓
Future Engineering Report
```

Normalization runs before validation. A `ReviewRequest` is constructed only
from a mapping that has already been normalized and successfully validated.
The `ReviewEngine` receives a `ReviewRequest`, executes its configured
`ReviewRule` objects in order, aggregates their `ReviewFinding` tuples in
execution order, and produces a `ReviewResult`.

## Completed milestones

### Milestone 3B — ReviewRequest Domain Model

Status: Complete

Established the immutable `ReviewRequest` domain object for Engineering Review
Contract v0.1.

The model:

- preserves the frozen contract field order;
- preserves the difference between an absent optional field and an optional
  field present with `None`;
- recursively freezes nested built-in containers;
- does not normalize or validate its input;
- is constructed from an already normalized and validated mapping.

No nested domain models or nested schemas were introduced.

### Milestone 4 — Review Engine Foundation v0.1

Status: Complete

Commit:

```text
755acd3 feat(review-engine): add review engine foundation
```

Established the deterministic boundary:

```text
ReviewRequest
    ↓
ReviewEngine
    ↓
ReviewResult
```

Current behavior:

Every valid `ReviewRequest` returns:

```python
ReviewResult(
    status="NOT_REVIEWED",
    findings=(),
)
```

This behavior is intentional. No engineering intelligence is implemented.

## Milestone 5 implementation status

### Milestone 5 — Deterministic Rule Execution Foundation v0.1

Status: Complete

Established the structural `ReviewRule` contract, immutable `ReviewFinding`
domain object, ordered rule execution, deterministic finding aggregation, and
rule-execution status semantics.

No concrete engineering rules exist.

## Milestone 6 implementation status

### Milestone 6 — Engineering Component Contract v0.2

Status: Implemented — Awaiting Architecture Review

Engineering Review Contract v0.1 remains unchanged and backward compatible.
Its `component` value remains arbitrary and receives no nested validation.

Engineering Review Contract v0.2 is newly supported with the same top-level
request shape. For v0.2 only, `component` is validated with these required
fields in frozen order:

- `component_id`;
- `name`;
- `component_type`;
- `properties`.

`properties` remains an opaque mapping. Unknown keys are allowed inside it, and
no engineering semantics are validated or inferred.

`Component` is an immutable domain object constructed from an already validated
v0.2 component mapping. `ReviewRequest` preserves its version-specific behavior:
v0.1 component values remain arbitrary and recursively frozen, while valid v0.2
component mappings become `Component` objects.

No concrete rules, engineering calculations, unit system, standards,
serialization, LLM, prompts, or report generation were introduced.

## Current domain objects

### Component

`Component` is the immutable representation of an already validated Contract
v0.2 component. It preserves `component_id`, `name`, `component_type`, and
`properties` exactly and recursively freezes `properties`. It does not
normalize, validate, repair, serialize, or infer engineering meaning.

### ReviewRequest

`ReviewRequest` is an immutable representation of an already normalized and
successfully validated Engineering Review Contract v0.1 or v0.2 request.

For Contract v0.1, its component remains arbitrary. For Contract v0.2, its
component is an immutable `Component`. It preserves all contract field values
and optional-field presence. Its nested
built-in containers are recursively frozen. It does not normalize, validate,
repair, or infer meaning.

### ReviewFinding

`ReviewFinding` is an immutable finding returned by a `ReviewRule`.

It preserves the rule identifier, code, severity, and message exactly. It does
not normalize or validate those values and contains no business behavior.

### ReviewResult

`ReviewResult` is the immutable output of the `ReviewEngine`.

It contains:

- `status: str`, defaulting to `"NOT_REVIEWED"`;
- `findings: tuple[ReviewFinding, ...]`, defaulting to `()`.

It supports the literal status semantics `NOT_REVIEWED`, `REVIEWED`, and
`REVIEWED_WITH_FINDINGS`. It contains no business logic or status validation.

## Current responsibilities

### Normalizer

- Receives raw input.
- Produces a deeply copied, representation-preserving canonical form.
- Orders known top-level fields in frozen contract order.
- Preserves unknown top-level fields for validation.
- Does not validate, repair data, or infer engineering meaning.

### Validator

- Owns validation of Engineering Review Contracts v0.1 and v0.2.
- Preserves v0.1 top-level-only validation behavior.
- Validates only the nested component contract for v0.2.
- Reports validation issues deterministically.
- Does not normalize input.

### Component

`Component` is the immutable representation of an already validated Contract
v0.2 component. It preserves `component_id`, `name`, `component_type`, and
`properties` exactly and recursively freezes `properties`. It does not
normalize, validate, repair, serialize, or infer engineering meaning.

### ReviewRequest

- Represents an already normalized and successfully validated request.
- Preserves contract values and optional-field presence.
- Provides deep immutability for nested built-in containers.

### ReviewRule

- Defines the runtime-checkable structural rule boundary.
- Exposes a `rule_id`.
- Evaluates one `ReviewRequest` and returns a tuple of `ReviewFinding` objects.
- Defines no implementation behavior, priority, registry, or lifecycle.

### ReviewEngine

- Receives a `ReviewRequest`.
- Executes its explicitly configured immutable rule tuple in supplied order.
- Executes each rule exactly once unless a rule raises an exception.
- Aggregates findings in rule order and then each rule's finding order.
- Enforces only the rule output container and element types.
- Allows rule exceptions to propagate unchanged and stops execution.
- Derives the deterministic `ReviewResult` status from rule execution.
- Has no hidden mutable state.
- Does not mutate its input.

### ReviewResult

- Represents the immutable result produced by the `ReviewEngine`.
- Contains an immutable tuple of `ReviewFinding` objects.
- Reports `NOT_REVIEWED` when no rules execute.
- Reports `REVIEWED` when rules execute without findings.
- Reports `REVIEWED_WITH_FINDINGS` when rules produce findings.

## Current exclusions

The current architecture does not include:

- engineering intelligence;
- engineering calculations;
- engineering standards;
- LLMs or prompts;
- report generation;
- file output;
- databases;
- plugins;
- factories;
- registries;
- service layers;
- dependency injection.

The `ReviewEngine` does not perform normalization or validation.

## Current rule-library exclusions

No concrete engineering rules exist. Engineering calculators, standards, LLMs,
reports, registries, plugins, priorities, and additional nested engineering
schemas remain excluded.
