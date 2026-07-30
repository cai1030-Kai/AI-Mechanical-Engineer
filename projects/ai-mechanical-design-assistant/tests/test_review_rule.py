import pytest

from ai_mechanical_design_assistant.review_finding import ReviewFinding
from ai_mechanical_design_assistant.review_request import ReviewRequest
from ai_mechanical_design_assistant.review_rule import ReviewRule


class CompatibleRule:
    rule_id = "compatible"

    def evaluate(
        self,
        request: ReviewRequest,
    ) -> tuple[ReviewFinding, ...]:
        return ()


class MissingEvaluate:
    rule_id = "missing-evaluate"


class MissingRuleId:
    def evaluate(
        self,
        request: ReviewRequest,
    ) -> tuple[ReviewFinding, ...]:
        return ()


def test_structurally_compatible_rule_satisfies_protocol() -> None:
    assert isinstance(CompatibleRule(), ReviewRule)


def test_object_missing_evaluate_does_not_satisfy_protocol() -> None:
    assert not isinstance(MissingEvaluate(), ReviewRule)


def test_object_missing_rule_id_does_not_satisfy_protocol() -> None:
    assert not isinstance(MissingRuleId(), ReviewRule)


def test_protocol_declares_no_instantiable_behavior() -> None:
    with pytest.raises(TypeError):
        ReviewRule()
