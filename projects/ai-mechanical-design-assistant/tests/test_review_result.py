from dataclasses import FrozenInstanceError

import pytest

from ai_mechanical_design_assistant.review_finding import ReviewFinding
from ai_mechanical_design_assistant.review_result import ReviewResult


def test_default_construction() -> None:
    result = ReviewResult()

    assert result.status == "NOT_REVIEWED"
    assert result.findings == ()


@pytest.mark.parametrize("status", ["REVIEWED", "REVIEWED_WITH_FINDINGS"])
def test_custom_supported_status(status: str) -> None:
    result = ReviewResult(status=status)

    assert result.status == status


def test_findings_accept_tuple_of_review_findings() -> None:
    finding = ReviewFinding(
        rule_id="test-rule",
        code="TEST_CODE",
        severity="informational",
        message="Test finding.",
    )

    result = ReviewResult(findings=(finding,))

    assert result.findings == (finding,)


def test_fields_are_immutable() -> None:
    result = ReviewResult()

    with pytest.raises(FrozenInstanceError):
        result.status = "CHANGED"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.findings = ()  # type: ignore[misc]


def test_slots_prevent_dynamic_attributes() -> None:
    result = ReviewResult()

    assert not hasattr(result, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        result.extra = True  # type: ignore[attr-defined]
