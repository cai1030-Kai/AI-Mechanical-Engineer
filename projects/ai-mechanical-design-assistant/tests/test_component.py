from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from ai_mechanical_design_assistant.component import Component


def make_component_mapping() -> dict[str, object]:
    return {
        "component_id": "shaft-1",
        "name": "  Drive Shaft  ",
        "component_type": " shaft ",
        "properties": {
            "geometry": {"diameters": [30, 35]},
            "metadata": {"finish": "ground"},
        },
    }


def test_construction_preserves_all_fields_exactly() -> None:
    component = Component.from_validated_mapping(make_component_mapping())

    assert component.component_id == "shaft-1"
    assert component.name == "  Drive Shaft  "
    assert component.component_type == " shaft "
    assert component.properties["metadata"]["finish"] == "ground"  # type: ignore[index]


def test_fields_are_immutable() -> None:
    component = Component.from_validated_mapping(make_component_mapping())

    with pytest.raises(FrozenInstanceError):
        component.name = "changed"  # type: ignore[misc]


def test_slots_prevent_dynamic_attributes() -> None:
    component = Component.from_validated_mapping(make_component_mapping())

    assert not hasattr(component, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        component.extra = True  # type: ignore[attr-defined]


def test_nested_properties_are_recursively_frozen() -> None:
    component = Component.from_validated_mapping(make_component_mapping())

    assert isinstance(component.properties, MappingProxyType)
    assert isinstance(component.properties["geometry"], MappingProxyType)  # type: ignore[index]
    assert component.properties["geometry"]["diameters"] == (30, 35)  # type: ignore[index]
    with pytest.raises(TypeError):
        component.properties["new"] = True  # type: ignore[index]


def test_other_mutable_builtins_are_frozen_recursively() -> None:
    mapping = make_component_mapping()
    mapping["properties"] = {
        "tuple": ([1],),
        "set": {1, 2},
        "frozenset": frozenset({3, 4}),
        "bytes": bytearray(b"shaft"),
    }

    component = Component.from_validated_mapping(mapping)

    assert component.properties["tuple"] == ((1,),)  # type: ignore[index]
    assert component.properties["set"] == frozenset({1, 2})  # type: ignore[index]
    assert component.properties["frozenset"] == frozenset({3, 4})  # type: ignore[index]
    assert component.properties["bytes"] == b"shaft"  # type: ignore[index]


def test_source_mutation_does_not_affect_component() -> None:
    mapping = make_component_mapping()
    component = Component.from_validated_mapping(mapping)

    mapping["properties"]["geometry"]["diameters"].append(40)  # type: ignore[index,union-attr]

    assert component.properties["geometry"]["diameters"] == (30, 35)  # type: ignore[index]


def test_equivalent_inputs_produce_equal_components() -> None:
    assert Component.from_validated_mapping(
        make_component_mapping()
    ) == Component.from_validated_mapping(make_component_mapping())


def test_missing_required_field_raises_key_error() -> None:
    mapping = make_component_mapping()
    del mapping["component_id"]

    with pytest.raises(KeyError):
        Component.from_validated_mapping(mapping)


def test_component_performs_no_string_trimming() -> None:
    component = Component.from_validated_mapping(make_component_mapping())

    assert component.name == "  Drive Shaft  "
    assert component.component_type == " shaft "
