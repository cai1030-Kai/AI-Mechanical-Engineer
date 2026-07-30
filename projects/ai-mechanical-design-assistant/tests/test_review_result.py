from dataclasses import FrozenInstanceError

import pytest

from ai_mechanical_design_assistant.review_result import ReviewResult


def test_default_construction() -> None:
    result = ReviewResult()

    assert result.status == "NOT_REVIEWED"
    assert result.findings == ()


def test_custom_status() -> None:
    result = ReviewResult(status="CUSTOM", findings=("finding",))

    assert result.status == "CUSTOM"
    assert result.findings == ("finding",)


def test_fields_are_immutable() -> None:
    result = ReviewResult()

    with pytest.raises(FrozenInstanceError):
        result.status = "CHANGED"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.findings = ("changed",)  # type: ignore[misc]


def test_slots_prevent_dynamic_attributes() -> None:
    result = ReviewResult()

    assert not hasattr(result, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        result.extra = True  # type: ignore[attr-defined]
