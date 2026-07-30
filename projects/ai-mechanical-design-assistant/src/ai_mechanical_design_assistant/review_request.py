"""Immutable domain representation of a validated engineering review request."""

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


_ABSENT = object()


def _freeze_value(value: Any) -> Any:
    """Return a recursively frozen copy of a value."""
    if value is _ABSENT:
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({
            key: _freeze_value(nested_value)
            for key, nested_value in value.items()
        })
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_value(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(_freeze_value(item) for item in value)
    if isinstance(value, bytearray):
        return bytes(value)
    return deepcopy(value)


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
            self, "contract_version", _freeze_value(self.contract_version)
        )
        object.__setattr__(self, "request_id", _freeze_value(self.request_id))
        object.__setattr__(self, "review_scope", _freeze_value(self.review_scope))
        object.__setattr__(self, "request_text", _freeze_value(self.request_text))
        object.__setattr__(self, "component", _freeze_value(self.component))
        object.__setattr__(
            self, "provided_data", _freeze_value(self.provided_data)
        )
        object.__setattr__(
            self, "requested_checks", _freeze_value(self.requested_checks)
        )
        object.__setattr__(self, "constraints", _freeze_value(self.constraints))
        object.__setattr__(self, "references", _freeze_value(self.references))

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
        return cls(
            contract_version=request["contract_version"],
            request_id=request["request_id"],
            review_scope=request["review_scope"],
            request_text=request["request_text"],
            component=request["component"],
            provided_data=request["provided_data"],
            requested_checks=request["requested_checks"],
            **optional_fields,
        )
