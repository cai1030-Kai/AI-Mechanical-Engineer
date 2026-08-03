"""Immutable engineering component for Contract v0.2."""

from collections.abc import Mapping
from dataclasses import dataclass

from ai_mechanical_design_assistant._freezing import freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class Component:
    """An already-validated Contract v0.2 component."""

    component_id: str
    name: str
    component_type: str
    properties: object

    def __post_init__(self) -> None:
        object.__setattr__(self, "properties", freeze_value(self.properties))

    @classmethod
    def from_validated_mapping(
        cls,
        component: Mapping[str, object],
    ) -> "Component":
        """Construct from a mapping that has already passed v0.2 validation."""
        return cls(
            component_id=component["component_id"],  # type: ignore[arg-type]
            name=component["name"],  # type: ignore[arg-type]
            component_type=component["component_type"],  # type: ignore[arg-type]
            properties=component["properties"],
        )
