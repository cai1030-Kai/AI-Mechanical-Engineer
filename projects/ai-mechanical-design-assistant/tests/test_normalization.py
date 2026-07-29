from copy import deepcopy

from ai_mechanical_design_assistant.normalization import Normalizer


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
