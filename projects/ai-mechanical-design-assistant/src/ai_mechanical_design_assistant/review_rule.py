"""Structural contract for deterministic review rules."""

from typing import Protocol, runtime_checkable

from ai_mechanical_design_assistant.review_finding import ReviewFinding
from ai_mechanical_design_assistant.review_request import ReviewRequest


@runtime_checkable
class ReviewRule(Protocol):
    """A deterministic rule that evaluates one review request."""

    rule_id: str

    def evaluate(
        self,
        request: ReviewRequest,
    ) -> tuple[ReviewFinding, ...]: ...
