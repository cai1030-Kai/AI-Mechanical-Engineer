from collections.abc import Iterator
from typing import Any

import pytest

from ai_mechanical_design_assistant.normalization import Normalizer
from ai_mechanical_design_assistant.review_engine import ReviewEngine
from ai_mechanical_design_assistant.review_finding import ReviewFinding
from ai_mechanical_design_assistant.review_request import ReviewRequest
from ai_mechanical_design_assistant.review_result import ReviewResult
from ai_mechanical_design_assistant.validation import Validator


def make_review_request() -> ReviewRequest:
    return ReviewRequest.from_validated_mapping({
        "contract_version": "0.1",
        "request_id": "shaft-review_001",
        "review_scope": "preliminary",
        "request_text": "Review this shaft.",
        "component": {"name": "Drive Shaft"},
        "provided_data": [],
        "requested_checks": [],
    })


def make_finding(code: str, rule_id: str = "test-rule") -> ReviewFinding:
    return ReviewFinding(
        rule_id=rule_id,
        code=code,
        severity="informational",
        message=f"Finding {code}.",
    )


class FakeRule:
    def __init__(
        self,
        rule_id: str,
        findings: tuple[ReviewFinding, ...] = (),
        execution_log: list[str] | None = None,
    ) -> None:
        self.rule_id = rule_id
        self.findings = findings
        self.execution_log = execution_log
        self.call_count = 0

    def evaluate(
        self,
        request: ReviewRequest,
    ) -> tuple[ReviewFinding, ...]:
        self.call_count += 1
        if self.execution_log is not None:
            self.execution_log.append(self.rule_id)
        return self.findings


class InvalidOutputRule:
    def __init__(self, rule_id: str, output: Any) -> None:
        self.rule_id = rule_id
        self.output = output

    def evaluate(self, request: ReviewRequest) -> Any:
        return self.output


class RuleFailure(RuntimeError):
    pass


class RaisingRule:
    def __init__(
        self,
        rule_id: str,
        error: Exception,
        execution_log: list[str],
    ) -> None:
        self.rule_id = rule_id
        self.error = error
        self.execution_log = execution_log

    def evaluate(
        self,
        request: ReviewRequest,
    ) -> tuple[ReviewFinding, ...]:
        self.execution_log.append(self.rule_id)
        raise self.error


def finding_generator() -> Iterator[ReviewFinding]:
    yield make_finding("GENERATED")


def test_zero_rules_preserve_milestone_four_behavior() -> None:
    result = ReviewEngine().review(make_review_request())

    assert result == ReviewResult(status="NOT_REVIEWED", findings=())


def test_one_rule_is_executed_exactly_once() -> None:
    rule = FakeRule("rule-one")

    ReviewEngine((rule,)).review(make_review_request())

    assert rule.call_count == 1


def test_multiple_rules_execute_in_supplied_order() -> None:
    execution_log: list[str] = []
    rules = (
        FakeRule("rule-two", execution_log=execution_log),
        FakeRule("rule-one", execution_log=execution_log),
    )

    ReviewEngine(rules).review(make_review_request())

    assert execution_log == ["rule-two", "rule-one"]


def test_findings_preserve_order_within_each_rule() -> None:
    findings = (make_finding("SECOND"), make_finding("FIRST"))

    result = ReviewEngine((FakeRule("rule", findings),)).review(
        make_review_request()
    )

    assert result.findings == findings


def test_findings_are_flattened_in_rule_order() -> None:
    first_findings = (
        make_finding("A", "first"),
        make_finding("B", "first"),
    )
    second_findings = (make_finding("C", "second"),)
    rules = (
        FakeRule("first", first_findings),
        FakeRule("second", second_findings),
    )

    result = ReviewEngine(rules).review(make_review_request())

    assert result.findings == first_findings + second_findings


def test_configured_rules_with_zero_findings_return_reviewed() -> None:
    result = ReviewEngine((FakeRule("empty"),)).review(make_review_request())

    assert result.status == "REVIEWED"
    assert result.findings == ()


def test_any_findings_return_reviewed_with_findings() -> None:
    finding = make_finding("FOUND")

    result = ReviewEngine((FakeRule("rule", (finding,)),)).review(
        make_review_request()
    )

    assert result.status == "REVIEWED_WITH_FINDINGS"


def test_returned_findings_are_a_tuple() -> None:
    result = ReviewEngine((FakeRule("empty"),)).review(make_review_request())

    assert isinstance(result.findings, tuple)


def test_input_review_request_is_not_modified() -> None:
    request = make_review_request()
    before = make_review_request()

    ReviewEngine((FakeRule("empty"),)).review(request)

    assert request == before


def test_same_request_and_rules_produce_equal_results() -> None:
    finding = make_finding("STABLE")
    rules = (FakeRule("stable", (finding,)),)
    engine = ReviewEngine(rules)
    request = make_review_request()

    assert engine.review(request) == engine.review(request)


def test_rule_exception_propagates_unchanged() -> None:
    error = RuleFailure("rule failed")
    rule = RaisingRule("raising", error, [])

    with pytest.raises(RuleFailure) as caught:
        ReviewEngine((rule,)).review(make_review_request())

    assert caught.value is error


def test_execution_stops_after_rule_exception() -> None:
    execution_log: list[str] = []
    rules = (
        RaisingRule("raising", RuleFailure("rule failed"), execution_log),
        FakeRule("after", execution_log=execution_log),
    )

    with pytest.raises(RuleFailure):
        ReviewEngine(rules).review(make_review_request())

    assert execution_log == ["raising"]


@pytest.mark.parametrize(
    "output",
    [
        [make_finding("LIST")],
        None,
        finding_generator(),
    ],
)
def test_non_tuple_rule_output_raises_type_error(output: Any) -> None:
    rule = InvalidOutputRule("invalid-container", output)

    with pytest.raises(TypeError):
        ReviewEngine((rule,)).review(make_review_request())


def test_tuple_containing_non_finding_raises_type_error() -> None:
    rule = InvalidOutputRule("invalid-element", ("not-a-finding",))

    with pytest.raises(TypeError):
        ReviewEngine((rule,)).review(make_review_request())


def test_type_error_identifies_violating_rule_id() -> None:
    rule = InvalidOutputRule("violating-rule", [])

    with pytest.raises(TypeError, match="violating-rule"):
        ReviewEngine((rule,)).review(make_review_request())


def test_engine_keeps_rule_storage_private_and_preserves_order() -> None:
    execution_log: list[str] = []
    rules = (
        FakeRule("first", execution_log=execution_log),
        FakeRule("second", execution_log=execution_log),
    )
    engine = ReviewEngine(rules)

    engine.review(make_review_request())

    assert execution_log == ["first", "second"]
    assert not hasattr(engine, "rules")


def test_engine_has_no_dynamic_mutable_attributes() -> None:
    engine = ReviewEngine()

    assert not hasattr(engine, "__dict__")
    with pytest.raises(AttributeError):
        engine.state = "mutable"  # type: ignore[attr-defined]


def test_engine_does_not_call_normalization_or_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("boundary must not be called")

    monkeypatch.setattr(Normalizer, "normalize", fail)
    monkeypatch.setattr(Validator, "validate", fail)

    result = ReviewEngine((FakeRule("empty"),)).review(make_review_request())

    assert result.status == "REVIEWED"
