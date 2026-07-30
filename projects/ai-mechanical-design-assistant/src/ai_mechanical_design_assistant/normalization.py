"""Representation-preserving canonicalization before contract validation.

The normalizer accepts raw contract-shaped input and performs deterministic
canonicalization before validation. It does not repair data, infer engineering
meaning, apply business rules, or otherwise replace the validator.
"""

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


class Normalizer:
    """Create a canonical copy of raw contract-shaped input."""

    _REQUIRED_FIELDS = (
        "contract_version",
        "request_id",
        "review_scope",
        "request_text",
        "component",
        "provided_data",
        "requested_checks",
    )
    _OPTIONAL_FIELDS = ("constraints", "references")
    _TRIMMED_STRING_FIELDS = frozenset(
        {
            "contract_version",
            "request_id",
            "review_scope",
            "request_text",
        }
    )

    def normalize(self, request: Any) -> Any:
        """Return a semantics-preserving copy with known fields canonically ordered."""
        if not isinstance(request, Mapping):
            return deepcopy(request)

        normalized: dict[str, Any] = {}
        known_fields = self._REQUIRED_FIELDS + self._OPTIONAL_FIELDS

        for field in known_fields:
            if field not in request:
                continue
            value = request[field]
            if field in self._TRIMMED_STRING_FIELDS and isinstance(value, str):
                normalized[field] = value.strip()
            else:
                normalized[field] = deepcopy(value)

        for field in request:
            if field not in known_fields:
                normalized[field] = deepcopy(request[field])

        return normalized
