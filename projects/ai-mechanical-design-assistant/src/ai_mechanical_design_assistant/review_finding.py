"""Immutable finding produced by a review rule."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewFinding:
    """One finding returned by deterministic rule execution."""

    rule_id: str
    code: str
    severity: str
    message: str
