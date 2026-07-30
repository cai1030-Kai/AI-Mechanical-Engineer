"""Immutable result of a deterministic engineering review."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewResult:
    """The result produced by the review engine."""

    status: str = "NOT_REVIEWED"
    findings: tuple = ()
