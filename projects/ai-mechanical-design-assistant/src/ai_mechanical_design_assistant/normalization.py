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

    def normalize(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Return a semantics-preserving copy in canonical top-level order."""
        normalized: dict[str, Any] = {}

        for field in self._REQUIRED_FIELDS:
            value = request[field]
            if field in self._TRIMMED_STRING_FIELDS and isinstance(value, str):
                normalized[field] = value.strip()
            else:
                normalized[field] = deepcopy(value)

        for field in self._OPTIONAL_FIELDS:
            if field in request:
                normalized[field] = deepcopy(request[field])

        return normalized
