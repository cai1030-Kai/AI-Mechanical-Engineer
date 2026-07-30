"""Deterministic review engine foundation."""

from ai_mechanical_design_assistant.review_request import ReviewRequest
from ai_mechanical_design_assistant.review_result import ReviewResult


class ReviewEngine:
    """Produce a review result from an already validated review request."""

    __slots__ = ()

    def review(self, request: ReviewRequest) -> ReviewResult:
        """Return the deterministic foundation result for a review request."""
        return ReviewResult()
