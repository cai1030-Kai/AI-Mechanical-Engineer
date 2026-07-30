# Project State

## Current project status

Current Milestone: Milestone 4 Complete

Next Milestone: Milestone 5 Architecture Design

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
ReviewResult
    ↓
Future Engineering Report
```

Normalization runs before validation. A `ReviewRequest` is constructed only
from a mapping that has already been normalized and successfully validated.
The `ReviewEngine` receives a `ReviewRequest` and produces a `ReviewResult`.

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

## Current domain objects

### ReviewRequest

`ReviewRequest` is an immutable representation of an already normalized and
successfully validated Engineering Review Contract v0.1 request.

It preserves all contract field values and optional-field presence. Its nested
built-in containers are recursively frozen. It does not normalize, validate,
repair, or infer meaning.

### ReviewResult

`ReviewResult` is the immutable output of the `ReviewEngine`.

It contains:

- `status: str`, defaulting to `"NOT_REVIEWED"`;
- `findings: tuple`, defaulting to `()`.

It contains no business logic.

## Current responsibilities

### Normalizer

- Receives raw input.
- Produces a deeply copied, representation-preserving canonical form.
- Orders known top-level fields in frozen contract order.
- Preserves unknown top-level fields for validation.
- Does not validate, repair data, or infer engineering meaning.

### Validator

- Owns validation of Engineering Review Contract v0.1.
- Reports validation issues deterministically.
- Does not normalize input.

### ReviewRequest

- Represents an already normalized and successfully validated request.
- Preserves contract values and optional-field presence.
- Provides deep immutability for nested built-in containers.

### ReviewEngine

- Receives a `ReviewRequest`.
- Produces a deterministic `ReviewResult`.
- Has no hidden mutable state.
- Does not mutate its input.

### ReviewResult

- Represents the immutable result produced by the `ReviewEngine`.
- Currently reports only the intentional `NOT_REVIEWED` foundation state.

## Current exclusions

The current architecture does not include:

- engineering intelligence;
- engineering calculations;
- engineering rules;
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

## Next milestone

### Milestone 5 — Engineering Rule Library

Goal:

Introduce deterministic engineering rule execution while preserving
`ReviewEngine` orchestration boundaries.

Explicitly excluded:

- engineering calculators;
- standards library;
- LLM reasoning;
- report generation;
- plugin system;
- dependency injection framework.

Milestone 5 implementation has not begun. Its implementation architecture is
not defined in this document.
