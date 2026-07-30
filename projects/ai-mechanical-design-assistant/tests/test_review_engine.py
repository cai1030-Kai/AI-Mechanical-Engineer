import pytest

from ai_mechanical_design_assistant.review_engine import ReviewEngine
from ai_mechanical_design_assistant.review_request import ReviewRequest
from ai_mechanical_design_assistant.review_result import ReviewResult


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


def test_accepts_review_request_and_returns_review_result() -> None:
    result = ReviewEngine().review(make_review_request())

    assert isinstance(result, ReviewResult)


def test_output_equals_expected_deterministic_result() -> None:
    result = ReviewEngine().review(make_review_request())

    assert result == ReviewResult(status="NOT_REVIEWED", findings=())


def test_same_input_produces_same_output() -> None:
    engine = ReviewEngine()
    request = make_review_request()

    assert engine.review(request) == engine.review(request)


def test_input_review_request_is_not_modified() -> None:
    request = make_review_request()
    before = make_review_request()

    ReviewEngine().review(request)

    assert request == before


def test_engine_has_no_mutable_state() -> None:
    engine = ReviewEngine()

    assert not hasattr(engine, "__dict__")
    with pytest.raises(AttributeError):
        engine.state = "mutable"  # type: ignore[attr-defined]
