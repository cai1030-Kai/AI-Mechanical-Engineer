from copy import deepcopy

from ai_mechanical_design_assistant.normalization import Normalizer
from ai_mechanical_design_assistant.validation import Validator


def make_request() -> dict[str, object]:
    return {
        "requested_checks": [
            {"check_type": "torsion", "description": "Review shaft torsion"}
        ],
        "request_text": "  Review  the Shaft.\nKeep internal spacing.  ",
        "provided_data": [
            {
                "name": "shaft_diameter",
                "category": "geometry",
                "value": 30,
                "unit": "mm",
            }
        ],
        "review_scope": " preliminary ",
        "component": {
            "name": "  Drive Shaft  ",
            "details": {"finish": "As Machined"},
        },
        "request_id": " shaft-review_001 ",
        "contract_version": " 0.1 ",
    }


def test_top_level_fields_are_returned_in_canonical_order() -> None:
    request = make_request()
    request["references"] = ["Drawing DS-104"]
    request["constraints"] = ["Diameter fixed"]

    result = Normalizer().normalize(request)

    assert list(result) == [
        "contract_version",
        "request_id",
        "review_scope",
        "request_text",
        "component",
        "provided_data",
        "requested_checks",
        "constraints",
        "references",
    ]


def test_supported_top_level_strings_are_trimmed() -> None:
    result = Normalizer().normalize(make_request())

    assert result["contract_version"] == "0.1"
    assert result["request_id"] == "shaft-review_001"
    assert result["review_scope"] == "preliminary"
    assert result["request_text"] == "Review  the Shaft.\nKeep internal spacing."


def test_internal_whitespace_and_case_are_preserved() -> None:
    result = Normalizer().normalize(make_request())

    assert result["request_text"] == "Review  the Shaft.\nKeep internal spacing."


def test_absent_optional_fields_remain_absent() -> None:
    result = Normalizer().normalize(make_request())

    assert "constraints" not in result
    assert "references" not in result


def test_present_optional_fields_are_preserved_exactly() -> None:
    request = make_request()
    request["constraints"] = ["  Keep  original spacing  "]
    request["references"] = ["Drawing DS-104", {"revision": " A "}]

    result = Normalizer().normalize(request)

    assert result["constraints"] == ["  Keep  original spacing  "]
    assert result["references"] == ["Drawing DS-104", {"revision": " A "}]


def test_nested_values_are_deep_copied() -> None:
    request = make_request()
    request["constraints"] = [{"limit": [1, 2]}]

    result = Normalizer().normalize(request)

    assert result["component"] is not request["component"]
    assert result["provided_data"] is not request["provided_data"]
    assert result["requested_checks"] is not request["requested_checks"]
    assert result["constraints"] is not request["constraints"]

    result["component"]["details"]["finish"] = "Ground"  # type: ignore[index]
    result["provided_data"][0]["value"] = 40  # type: ignore[index]
    result["constraints"][0]["limit"].append(3)  # type: ignore[index,union-attr]

    assert request["component"]["details"]["finish"] == "As Machined"  # type: ignore[index]
    assert request["provided_data"][0]["value"] == 30  # type: ignore[index]
    assert request["constraints"][0]["limit"] == [1, 2]  # type: ignore[index]


def test_normalization_does_not_mutate_input() -> None:
    request = make_request()
    request["constraints"] = ["  Keep exact  "]
    before = deepcopy(request)

    Normalizer().normalize(request)

    assert request == before


def test_normalization_is_idempotent() -> None:
    normalizer = Normalizer()
    once = normalizer.normalize(make_request())

    assert normalizer.normalize(once) == once

def test_non_string_trimmed_fields_are_preserved_for_validation() -> None:
    request = make_request()
    request["contract_version"] = 1
    request["review_scope"] = None
    request["request_id"] = False

    result = Normalizer().normalize(request)

    assert result["contract_version"] == 1
    assert result["review_scope"] is None
    assert result["request_id"] is False


def test_mutable_non_string_trimmed_field_is_deep_copied() -> None:
    request = make_request()
    request["request_text"] = ["raw", {"value": " unchanged "}]

    result = Normalizer().normalize(request)

    assert result["request_text"] == ["raw", {"value": " unchanged "}]
    assert result["request_text"] is not request["request_text"]

    result["request_text"][1]["value"] = "changed"  # type: ignore[index]

    assert request["request_text"][1]["value"] == " unchanged "  # type: ignore[index]


def test_non_mapping_input_is_returned_as_an_equal_deep_copy() -> None:
    request = ["raw", {"nested": [1, 2]}]

    result = Normalizer().normalize(request)

    assert result == request
    assert result is not request
    assert result[1] is not request[1]
    assert result[1]["nested"] is not request[1]["nested"]


def test_missing_required_fields_do_not_crash_and_known_fields_are_ordered() -> None:
    request = {
        "requested_checks": [],
        "request_text": " Review ",
        "contract_version": " 0.1 ",
    }

    result = Normalizer().normalize(request)

    assert list(result) == ["contract_version", "request_text", "requested_checks"]
    assert result["contract_version"] == "0.1"
    assert result["request_text"] == "Review"


def test_unknown_top_level_fields_are_preserved_after_known_fields() -> None:
    request = {
        "extension": {"values": [1, 2]},
        "request_text": "Review",
        "contract_version": "0.1",
        "another_extension": "unchanged",
    }

    result = Normalizer().normalize(request)

    assert list(result) == [
        "contract_version",
        "request_text",
        "extension",
        "another_extension",
    ]
    assert result["extension"] == {"values": [1, 2]}
    assert result["extension"] is not request["extension"]


def test_preserved_unknown_fields_remain_visible_to_validator() -> None:
    request = make_request()
    request["unexpected"] = {"raw": True}

    result = Normalizer().normalize(request)
    validation = Validator().validate(result)

    assert any(
        issue.path == "/unexpected" and issue.code == "UNKNOWN_FIELD"
        for issue in validation.issues
    )


def test_invalid_known_field_values_pass_through_unchanged() -> None:
    request = {
        "contract_version": {"invalid": ["value"]},
        "component": None,
        "provided_data": False,
        "requested_checks": 42,
    }

    result = Normalizer().normalize(request)

    assert result == request
    assert result["contract_version"] is not request["contract_version"]


def test_unknown_nested_values_are_deep_copied_without_mutating_input() -> None:
    request = make_request()
    request["extension"] = {"nested": [" original "]}
    before = deepcopy(request)

    result = Normalizer().normalize(request)
    result["extension"]["nested"].append("changed")  # type: ignore[index]

    assert request == before
    assert result["extension"] is not request["extension"]


def test_normalization_with_missing_and_unknown_fields_is_idempotent() -> None:
    normalizer = Normalizer()
    request = {
        "unknown": {"nested": [1]},
        "request_text": " Review ",
        "contract_version": " 0.1 ",
    }

    once = normalizer.normalize(request)
    twice = normalizer.normalize(once)

    assert twice == once
    assert list(twice) == list(once)
    assert twice["unknown"] is not once["unknown"]
