"""Deterministic review engine foundation."""

from ai_mechanical_design_assistant.review_finding import ReviewFinding
from ai_mechanical_design_assistant.review_request import ReviewRequest
from ai_mechanical_design_assistant.review_result import ReviewResult
from ai_mechanical_design_assistant.review_rule import ReviewRule


class ReviewEngine:
    """Produce a review result from an already validated review request."""

    __slots__ = ("_rules",)

    def __init__(self, rules: tuple[ReviewRule, ...] = ()) -> None:
        self._rules = rules


    def review(self, request: ReviewRequest) -> ReviewResult:
        """Evaluate configured rules in order and aggregate their findings."""
        if not self._rules:
            return ReviewResult()

        findings: tuple[ReviewFinding, ...] = ()
        for rule in self._rules:
            rule_findings = rule.evaluate(request)
            if (
                not isinstance(rule_findings, tuple)
                or not all(
                    isinstance(finding, ReviewFinding)
                    for finding in rule_findings
                )
            ):
                raise TypeError(
                    f"Rule {rule.rule_id!r} returned invalid findings; "
                    "expected tuple[ReviewFinding, ...]."
                )
            findings += rule_findings

        status = "REVIEWED_WITH_FINDINGS" if findings else "REVIEWED"
        return ReviewResult(status=status, findings=findings)
