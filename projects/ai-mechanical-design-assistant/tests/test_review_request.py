from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from ai_mechanical_design_assistant.review_request import ReviewRequest


def make_complete_request() -> dict[str, object]:
    return {
        "contract_version": "0.1",
        "request_id": "shaft-review_001",
        "review_scope": "preliminary",
        "request_text": "Review this shaft.",
        "component": {
            "name": "Drive Shaft",
            "details": {"finishes": ["machined", "ground"]},
        },
        "provided_data": [
            {
                "name": "shaft_diameter",
                "value": 30,
                "metadata": {"sources": ["drawing"]},
            }
        ],
        "requested_checks": [
            {"check_type": "torsion", "options": {"critical": True}}
        ],
        "constraints": [{"limit": [1, 2]}],
        "references": ["Drawing DS-104", {"revision": "A"}],
    }


def test_construction_from_complete_mapping_preserves_fields() -> None:
    request = make_complete_request()

    model = ReviewRequest.from_validated_mapping(request)

    assert model.contract_version == "0.1"
    assert model.request_id == "shaft-review_001"
    assert model.review_scope == "preliminary"
    assert model.request_text == "Review this shaft."
    assert model.component["name"] == "Drive Shaft"  # type: ignore[index]
    assert model.provided_data[0]["name"] == "shaft_diameter"  # type: ignore[index]
    assert model.requested_checks[0]["check_type"] == "torsion"  # type: ignore[index]
    assert model.constraints[0]["limit"] == (1, 2)  # type: ignore[index]
    assert model.references[0] == "Drawing DS-104"  # type: ignore[index]
    assert model.has_constraints
    assert model.has_references


def test_construction_from_mapping_missing_required_fields_raises_key_error() -> None:
    with pytest.raises(KeyError):
        ReviewRequest.from_validated_mapping({})


def test_top_level_fields_are_frozen() -> None:
    model = ReviewRequest.from_validated_mapping(make_complete_request())

    with pytest.raises(FrozenInstanceError):
        model.request_id = "replacement"  # type: ignore[misc]


def test_slots_prevent_new_attributes() -> None:
    model = ReviewRequest.from_validated_mapping(make_complete_request())

    assert not hasattr(model, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        model.extra = True  # type: ignore[attr-defined]


def test_construction_does_not_mutate_source() -> None:
    request = make_complete_request()
    expected = make_complete_request()

    ReviewRequest.from_validated_mapping(request)

    assert request == expected


def test_later_source_mutation_does_not_affect_model() -> None:
    request = make_complete_request()
    model = ReviewRequest.from_validated_mapping(request)

    request["component"]["details"]["finishes"].append("coated")  # type: ignore[index,union-attr]
    request["provided_data"][0]["value"] = 40  # type: ignore[index]

    assert model.component["details"]["finishes"] == ("machined", "ground")  # type: ignore[index]
    assert model.provided_data[0]["value"] == 30  # type: ignore[index]


def test_nested_mappings_cannot_be_modified() -> None:
    model = ReviewRequest.from_validated_mapping(make_complete_request())

    assert isinstance(model.component, MappingProxyType)
    with pytest.raises(TypeError):
        model.component["name"] = "Replacement"  # type: ignore[index]


def test_nested_lists_become_tuples_and_freezing_is_recursive() -> None:
    model = ReviewRequest.from_validated_mapping(make_complete_request())

    assert isinstance(model.provided_data, tuple)
    assert isinstance(model.provided_data[0], MappingProxyType)  # type: ignore[index]
    assert isinstance(model.provided_data[0]["metadata"], MappingProxyType)  # type: ignore[index]
    assert model.provided_data[0]["metadata"]["sources"] == ("drawing",)  # type: ignore[index]
    assert model.component["details"]["finishes"] == ("machined", "ground")  # type: ignore[index]


def test_other_mutable_builtins_are_frozen_recursively() -> None:
    request = make_complete_request()
    request["component"] = {
        "tuple": ([1],),
        "set": {1, 2},
        "frozenset": frozenset({3, 4}),
        "bytes": bytearray(b"shaft"),
    }

    model = ReviewRequest.from_validated_mapping(request)

    assert model.component["tuple"] == ((1,),)  # type: ignore[index]
    assert model.component["set"] == frozenset({1, 2})  # type: ignore[index]
    assert model.component["frozenset"] == frozenset({3, 4})  # type: ignore[index]
    assert model.component["bytes"] == b"shaft"  # type: ignore[index]


def test_absent_optional_fields_remain_distinguishable() -> None:
    request = make_complete_request()
    del request["constraints"]
    del request["references"]

    model = ReviewRequest.from_validated_mapping(request)

    assert not model.has_constraints
    assert not model.has_references


def test_optional_fields_present_with_none_are_present() -> None:
    request = make_complete_request()
    request["constraints"] = None
    request["references"] = None

    model = ReviewRequest.from_validated_mapping(request)

    assert model.has_constraints
    assert model.constraints is None
    assert model.has_references
    assert model.references is None


@pytest.mark.parametrize(
    ("present_field", "absent_field"),
    [("constraints", "references"), ("references", "constraints")],
)
def test_optional_field_presence_is_independent(
    present_field: str,
    absent_field: str,
) -> None:
    request = make_complete_request()
    del request[absent_field]

    model = ReviewRequest.from_validated_mapping(request)

    assert getattr(model, f"has_{present_field}")
    assert not getattr(model, f"has_{absent_field}")


def test_strings_are_not_trimmed() -> None:
    request = make_complete_request()
    request["request_text"] = "  Review this shaft.  "

    model = ReviewRequest.from_validated_mapping(request)

    assert model.request_text == "  Review this shaft.  "


def test_equivalent_requests_are_equal() -> None:
    first = ReviewRequest.from_validated_mapping(make_complete_request())
    second = ReviewRequest.from_validated_mapping(make_complete_request())

    assert first == second
