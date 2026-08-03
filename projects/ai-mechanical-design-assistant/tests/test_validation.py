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


def make_v02_request() -> dict[str, object]:
    return {
        "contract_version": "0.2",
        "request_id": "shaft-review_002",
        "review_scope": "preliminary",
        "request_text": "Review this component.",
        "component": {
            "component_id": "shaft-1",
            "name": "Drive Shaft",
            "component_type": "shaft",
            "properties": {},
        },
        "provided_data": [],
        "requested_checks": [],
    }


def test_v01_arbitrary_nested_values_remain_valid() -> None:
    request = {
        "contract_version": "0.1",
        "request_id": "legacy-1",
        "review_scope": "preliminary",
        "request_text": "Legacy request.",
        "component": None,
        "provided_data": "not validated",
        "requested_checks": 42,
    }

    assert Validator().validate(request).is_valid
    request["component"] = {"arbitrary": {"nested": "value"}}
    assert Validator().validate(request).is_valid


def test_v02_is_accepted_and_unknown_versions_remain_invalid() -> None:
    assert Validator().validate(make_v02_request()).is_valid

    request = make_v02_request()
    request["contract_version"] = "9.9"
    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        ("/contract_version", "INVALID_VALUE")
    ]


@pytest.mark.parametrize("version", ["0.1", "9.9", None])
def test_component_validation_runs_only_for_exact_v02(version: object) -> None:
    request = make_v02_request()
    request["contract_version"] = version
    request["component"] = None

    issues = Validator().validate(request).issues

    assert not any(issue.path.startswith("/component") for issue in issues)


def test_v02_non_mapping_component_produces_only_component_type_issue() -> None:
    request = make_v02_request()
    request["component"] = None

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        ("/component", "INVALID_TYPE")
    ]


@pytest.mark.parametrize(
    "field",
    ["component_id", "name", "component_type", "properties"],
)
def test_each_missing_component_field_is_reported(field: str) -> None:
    request = make_v02_request()
    del request["component"][field]  # type: ignore[index]

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        (f"/component/{field}", "REQUIRED_FIELD_MISSING")
    ]


def test_multiple_missing_component_fields_are_collected_deterministically() -> None:
    request = make_v02_request()
    request["component"] = {}

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        ("/component/component_id", "REQUIRED_FIELD_MISSING"),
        ("/component/component_type", "REQUIRED_FIELD_MISSING"),
        ("/component/name", "REQUIRED_FIELD_MISSING"),
        ("/component/properties", "REQUIRED_FIELD_MISSING"),
    ]


def test_unknown_component_field_is_rejected_with_pointer_escaping() -> None:
    request = make_v02_request()
    request["component"]["unexpected~/field"] = True  # type: ignore[index]

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        ("/component/unexpected~0~1field", "UNKNOWN_FIELD")
    ]


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("component_id", 1, "INVALID_TYPE"),
        ("component_id", "invalid id", "INVALID_FORMAT"),
        ("name", 1, "INVALID_TYPE"),
        ("name", " \t\n", "EMPTY_VALUE"),
        ("component_type", 1, "INVALID_TYPE"),
        ("component_type", " \t\n", "EMPTY_VALUE"),
        ("properties", [], "INVALID_TYPE"),
    ],
)
def test_invalid_component_members_are_reported(
    field: str,
    value: object,
    expected_code: str,
) -> None:
    request = make_v02_request()
    request["component"][field] = value  # type: ignore[index]

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        (f"/component/{field}", expected_code)
    ]


def test_empty_and_arbitrary_opaque_properties_are_valid() -> None:
    request = make_v02_request()
    assert Validator().validate(request).is_valid

    request["component"]["properties"] = {  # type: ignore[index]
        "anything": {"nested": [None, True, 3.5, "value"]},
        "unknown/unit": {"not": "semantically validated"},
    }
    assert Validator().validate(request).is_valid


def test_component_validation_collects_and_sorts_independent_issues() -> None:
    request = make_v02_request()
    request["component"] = {
        "properties": 42,
        "name": " ",
        "component_id": "invalid id",
        "unexpected": True,
    }

    assert [(issue.path, issue.code) for issue in Validator().validate(request).issues] == [
        ("/component/component_id", "INVALID_FORMAT"),
        ("/component/component_type", "REQUIRED_FIELD_MISSING"),
        ("/component/name", "EMPTY_VALUE"),
        ("/component/properties", "INVALID_TYPE"),
        ("/component/unexpected", "UNKNOWN_FIELD"),
    ]


def test_component_validation_does_not_mutate_input() -> None:
    from copy import deepcopy

    request = make_v02_request()
    request["component"]["properties"] = {"nested": [1, 2]}  # type: ignore[index]
    before = deepcopy(request)

    Validator().validate(request)

    assert request == before
