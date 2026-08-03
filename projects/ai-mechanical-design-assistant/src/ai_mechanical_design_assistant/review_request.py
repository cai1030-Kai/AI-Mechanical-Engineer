"""Immutable domain representation of a validated engineering review request."""

from collections.abc import Mapping
from dataclasses import dataclass

from ai_mechanical_design_assistant._freezing import freeze_value
from ai_mechanical_design_assistant.component import Component


_ABSENT = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewRequest:
    """A deeply immutable, already-validated review request."""

    contract_version: str
    request_id: str
    review_scope: str
    request_text: str
    component: object
    provided_data: object
    requested_checks: object
    constraints: object = _ABSENT
    references: object = _ABSENT

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "contract_version", freeze_value(self.contract_version)
        )
        object.__setattr__(self, "request_id", freeze_value(self.request_id))
        object.__setattr__(self, "review_scope", freeze_value(self.review_scope))
        object.__setattr__(self, "request_text", freeze_value(self.request_text))
        if not isinstance(self.component, Component):
            object.__setattr__(self, "component", freeze_value(self.component))
        object.__setattr__(self, "provided_data", freeze_value(self.provided_data))
        object.__setattr__(
            self, "requested_checks", freeze_value(self.requested_checks)
        )
        if self.constraints is not _ABSENT:
            object.__setattr__(self, "constraints", freeze_value(self.constraints))
        if self.references is not _ABSENT:
            object.__setattr__(self, "references", freeze_value(self.references))

    @property
    def has_constraints(self) -> bool:
        """Whether constraints were present in the source mapping."""
        return self.constraints is not _ABSENT

    @property
    def has_references(self) -> bool:
        """Whether references were present in the source mapping."""
        return self.references is not _ABSENT

    @classmethod
    def from_validated_mapping(
        cls,
        request: Mapping[str, object],
    ) -> "ReviewRequest":
        """Construct from a mapping that was already normalized and validated."""
        optional_fields = {
            field: request[field] if field in request else _ABSENT
            for field in ("constraints", "references")
        }
        component = request["component"]
        if request["contract_version"] == "0.2":
            component = Component.from_validated_mapping(component)  # type: ignore[arg-type]

        return cls(
            contract_version=request["contract_version"],
            request_id=request["request_id"],
            review_scope=request["review_scope"],
            request_text=request["request_text"],
            component=component,
            provided_data=request["provided_data"],
            requested_checks=request["requested_checks"],
            **optional_fields,
        )
