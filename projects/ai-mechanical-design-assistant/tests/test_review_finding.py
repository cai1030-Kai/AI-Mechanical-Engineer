from dataclasses import FrozenInstanceError

import pytest

from ai_mechanical_design_assistant.review_finding import ReviewFinding


def make_finding() -> ReviewFinding:
    return ReviewFinding(
        rule_id="test-rule",
        code="TEST_CODE",
        severity="informational",
        message="  Preserve this message exactly.  ",
    )


def test_construction_preserves_all_values() -> None:
    finding = make_finding()

    assert finding.rule_id == "test-rule"
    assert finding.code == "TEST_CODE"
    assert finding.severity == "informational"
    assert finding.message == "  Preserve this message exactly.  "


def test_equality_is_value_based() -> None:
    assert make_finding() == make_finding()


def test_fields_are_immutable() -> None:
    finding = make_finding()

    with pytest.raises(FrozenInstanceError):
        finding.message = "changed"  # type: ignore[misc]


def test_slots_prevent_dynamic_attributes() -> None:
    finding = make_finding()

    assert not hasattr(finding, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        finding.extra = True  # type: ignore[attr-defined]
