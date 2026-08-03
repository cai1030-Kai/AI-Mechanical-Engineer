"""Top-level validation for engineering review requests."""

from collections.abc import Mapping
from dataclasses import dataclass
import json
import re
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    """One validation problem at a JSON Pointer path."""

    path: str
    code: str
    message: str
    expected: str
    received: str


@dataclass(frozen=True)
class ValidationResult:
    """The result of validating a review request."""

    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


class Validator:
    """Validate the supported engineering review request contracts."""

    _REQUIRED_FIELDS = (
        "contract_version", "request_id", "review_scope", "request_text",
        "component", "provided_data", "requested_checks",
    )
    _OPTIONAL_FIELDS = ("constraints", "references")
    _COMPONENT_FIELDS = ("component_id", "name", "component_type", "properties")
    _REVIEW_SCOPES = frozenset({
        "concept", "preliminary", "detailed", "manufacturing", "failure_analysis",
    })
    _REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")

    def validate(self, request: Any) -> ValidationResult:
        """Return all independently detectable validation issues."""
        if not isinstance(request, dict):
            return ValidationResult((ValidationIssue(
                path="", code="INVALID_TYPE",
                message="The review request must be a JSON object.",
                expected="object", received=self._received(request),
            ),))

        issues: list[ValidationIssue] = []
        allowed_fields = set(self._REQUIRED_FIELDS) | set(self._OPTIONAL_FIELDS)
        for field in self._REQUIRED_FIELDS:
            if field not in request:
                issues.append(ValidationIssue(
                    path=f"/{field}", code="REQUIRED_FIELD_MISSING",
                    message=f"Required field '{field}' is missing.",
                    expected="required field", received="missing",
                ))
        for field in sorted(set(request) - allowed_fields):
            issues.append(ValidationIssue(
                path=f"/{self._escape_pointer_token(field)}", code="UNKNOWN_FIELD",
                message=f"Unknown top-level field '{field}'.",
                expected="known top-level field", received=self._received(field),
            ))

        self._validate_contract_version(request, issues)
        self._validate_review_scope(request, issues)
        self._validate_request_id(request, issues)
        self._validate_request_text(request, issues)
        if request.get("contract_version") == "0.2":
            self._validate_component_v02(request, issues)
        return ValidationResult(tuple(sorted(issues, key=lambda issue: (issue.path, issue.code))))

    @staticmethod
    def _escape_pointer_token(value: str) -> str:
        return value.replace("~", "~0").replace("/", "~1")

    @staticmethod
    def _received(value: Any) -> str:
        if isinstance(value, str) and len(value) <= 80:
            return json.dumps(value, ensure_ascii=False)
        return type(value).__name__

    @staticmethod
    def _validate_contract_version(request: dict[str, Any], issues: list[ValidationIssue]) -> None:
        if "contract_version" not in request:
            return
        value = request["contract_version"]
        if not isinstance(value, str):
            issues.append(ValidationIssue("/contract_version", "INVALID_TYPE", "contract_version must be a string.", "string", Validator._received(value)))
        elif value not in {"0.1", "0.2"}:
            issues.append(ValidationIssue("/contract_version", "INVALID_VALUE", 'contract_version must equal "0.1" or "0.2".', '"0.1" or "0.2"', Validator._received(value)))

    def _validate_review_scope(self, request: dict[str, Any], issues: list[ValidationIssue]) -> None:
        if "review_scope" not in request:
            return
        value = request["review_scope"]
        if not isinstance(value, str):
            issues.append(ValidationIssue("/review_scope", "INVALID_TYPE", "review_scope must be a string.", "string", self._received(value)))
        elif value not in self._REVIEW_SCOPES:
            issues.append(ValidationIssue("/review_scope", "INVALID_VALUE", "review_scope is not a permitted value.", "concept, preliminary, detailed, manufacturing, or failure_analysis", self._received(value)))

    def _validate_request_id(self, request: dict[str, Any], issues: list[ValidationIssue]) -> None:
        if "request_id" not in request:
            return
        value = request["request_id"]
        if not isinstance(value, str):
            issues.append(ValidationIssue("/request_id", "INVALID_TYPE", "request_id must be a string.", "string", self._received(value)))
        elif self._REQUEST_ID_PATTERN.fullmatch(value) is None:
            expected = "1-100 ASCII letters, digits, underscores, hyphens, or periods"
            issues.append(ValidationIssue("/request_id", "INVALID_FORMAT", f"request_id must contain {expected}.", expected, self._received(value)))

    @staticmethod
    def _validate_request_text(request: dict[str, Any], issues: list[ValidationIssue]) -> None:
        if "request_text" not in request:
            return
        value = request["request_text"]
        if not isinstance(value, str):
            issues.append(ValidationIssue("/request_text", "INVALID_TYPE", "request_text must be a string.", "string", Validator._received(value)))
        elif not value.strip():
            issues.append(ValidationIssue("/request_text", "EMPTY_VALUE", "request_text must not be blank.", "nonblank string", Validator._received(value)))

    def _validate_component_v02(
        self,
        request: dict[str, Any],
        issues: list[ValidationIssue],
    ) -> None:
        if "component" not in request:
            return
        component = request["component"]
        if not isinstance(component, Mapping):
            issues.append(ValidationIssue(
                "/component", "INVALID_TYPE", "component must be a mapping.",
                "mapping", self._received(component),
            ))
            return

        allowed_fields = set(self._COMPONENT_FIELDS)
        for field in self._COMPONENT_FIELDS:
            if field not in component:
                issues.append(ValidationIssue(
                    f"/component/{field}", "REQUIRED_FIELD_MISSING",
                    f"Required component field '{field}' is missing.",
                    "required field", "missing",
                ))
        for field in sorted(set(component) - allowed_fields):
            escaped = self._escape_pointer_token(field)
            issues.append(ValidationIssue(
                f"/component/{escaped}", "UNKNOWN_FIELD",
                f"Unknown component field '{field}'.",
                "known component field", self._received(field),
            ))

        self._validate_component_id(component, issues)
        self._validate_nonblank_component_string(component, "name", issues)
        self._validate_nonblank_component_string(component, "component_type", issues)
        if "properties" in component and not isinstance(component["properties"], Mapping):
            issues.append(ValidationIssue(
                "/component/properties", "INVALID_TYPE",
                "component properties must be a mapping.", "mapping",
                self._received(component["properties"]),
            ))

    def _validate_component_id(
        self,
        component: Mapping[str, Any],
        issues: list[ValidationIssue],
    ) -> None:
        if "component_id" not in component:
            return
        value = component["component_id"]
        if not isinstance(value, str):
            issues.append(ValidationIssue(
                "/component/component_id", "INVALID_TYPE",
                "component_id must be a string.", "string", self._received(value),
            ))
        elif self._REQUEST_ID_PATTERN.fullmatch(value) is None:
            expected = "1-100 ASCII letters, digits, underscores, hyphens, or periods"
            issues.append(ValidationIssue(
                "/component/component_id", "INVALID_FORMAT",
                f"component_id must contain {expected}.", expected,
                self._received(value),
            ))

    def _validate_nonblank_component_string(
        self,
        component: Mapping[str, Any],
        field: str,
        issues: list[ValidationIssue],
    ) -> None:
        if field not in component:
            return
        value = component[field]
        path = f"/component/{field}"
        if not isinstance(value, str):
            issues.append(ValidationIssue(
                path, "INVALID_TYPE", f"{field} must be a string.",
                "string", self._received(value),
            ))
        elif not value.strip():
            issues.append(ValidationIssue(
                path, "EMPTY_VALUE", f"{field} must not be blank.",
                "nonblank string", self._received(value),
            ))
