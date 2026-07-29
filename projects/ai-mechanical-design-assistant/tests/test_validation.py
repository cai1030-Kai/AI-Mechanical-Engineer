import pytest

from ai_mechanical_design_assistant.validation import ValidationIssue, Validator


@pytest.fixture
def valid_request() -> dict[str, object]:
    return {
        "contract_version": "0.1", "request_id": "shaft-review_001",
        "review_scope": "preliminary", "request_text": "Review this shaft.",
        "component": {"nested": "content is not validated yet"},
        "provided_data": [], "requested_checks": [],
    }


def test_valid_top_level_request_has_no_issues(valid_request: dict[str, object]) -> None:
    result = Validator().validate(valid_request)
    assert result.is_valid
    assert result.issues == ()


def test_missing_required_fields_are_reported_in_path_order() -> None:
    result = Validator().validate({})
    assert not result.is_valid
    assert [issue.path for issue in result.issues] == [
        "/component", "/contract_version", "/provided_data", "/request_id",
        "/request_text", "/requested_checks", "/review_scope",
    ]
    assert {issue.code for issue in result.issues} == {"REQUIRED_FIELD_MISSING"}
    assert {issue.received for issue in result.issues} == {"missing"}


def test_unknown_top_level_fields_are_rejected(valid_request: dict[str, object]) -> None:
    valid_request["unexpected"] = True
    result = Validator().validate(valid_request)
    assert result.issues == (ValidationIssue(
        path="/unexpected", code="UNKNOWN_FIELD",
        message="Unknown top-level field 'unexpected'.",
        expected="known top-level field", received='"unexpected"',
    ),)


@pytest.mark.parametrize(("field", "expected_path"), [
    ("load/case", "/load~1case"), ("source~name", "/source~0name"),
    ("a~/b", "/a~0~1b"),
])
def test_unknown_field_paths_use_rfc_6901_escaping(valid_request: dict[str, object], field: str, expected_path: str) -> None:
    valid_request[field] = True
    issue = Validator().validate(valid_request).issues[0]
    assert issue.path == expected_path
    assert issue.received == f'"{field}"'


@pytest.mark.parametrize(("field", "value", "expected_code"), [
    ("contract_version", "0.2", "INVALID_VALUE"),
    ("contract_version", 0.1, "INVALID_TYPE"),
    ("review_scope", "design", "INVALID_VALUE"),
    ("review_scope", None, "INVALID_TYPE"),
    ("request_id", "shaft review", "INVALID_FORMAT"),
    ("request_id", 123, "INVALID_TYPE"),
    ("request_text", " \t\n", "EMPTY_VALUE"),
    ("request_text", False, "INVALID_TYPE"),
])
def test_invalid_scalar_fields_are_reported(valid_request: dict[str, object], field: str, value: object, expected_code: str) -> None:
    valid_request[field] = value
    result = Validator().validate(valid_request)
    assert [(issue.path, issue.code) for issue in result.issues] == [(f"/{field}", expected_code)]


@pytest.mark.parametrize("review_scope", [
    "concept", "preliminary", "detailed", "manufacturing", "failure_analysis",
])
def test_each_review_scope_is_valid(valid_request: dict[str, object], review_scope: str) -> None:
    valid_request["review_scope"] = review_scope
    assert Validator().validate(valid_request).is_valid


def test_nested_content_is_not_validated_yet(valid_request: dict[str, object]) -> None:
    valid_request["component"] = None
    valid_request["provided_data"] = "not validated"
    valid_request["requested_checks"] = 42
    assert Validator().validate(valid_request).is_valid


def test_non_object_request_is_rejected() -> None:
    result = Validator().validate([])
    assert result.issues == (ValidationIssue(
        path="", code="INVALID_TYPE",
        message="The review request must be a JSON object.",
        expected="object", received="list",
    ),)


def test_missing_field_issue_matches_contract_error_shape() -> None:
    issue = next(issue for issue in Validator().validate({}).issues if issue.path == "/request_id")
    assert issue == ValidationIssue(
        path="/request_id", code="REQUIRED_FIELD_MISSING",
        message="Required field 'request_id' is missing.",
        expected="required field", received="missing",
    )


def test_invalid_type_received_value_is_only_the_type_name(valid_request: dict[str, object]) -> None:
    valid_request["request_text"] = {"large": "value" * 1_000}
    assert Validator().validate(valid_request).issues[0].received == "dict"


def test_long_invalid_string_received_value_is_not_exposed(valid_request: dict[str, object]) -> None:
    valid_request["request_id"] = "invalid " + ("x" * 1_000)
    assert Validator().validate(valid_request).issues[0].received == "str"
