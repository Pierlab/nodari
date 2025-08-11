"""Schema validation utilities for simulation configuration files."""
from __future__ import annotations

from typing import Any

try:  # optional dependency
    from jsonschema import Draft7Validator, ValidationError  # type: ignore
except Exception:  # pragma: no cover - jsonschema not installed
    Draft7Validator = None  # type: ignore

    class ValidationError(Exception):
        """Raised when configuration validation fails."""


CONFIG_SCHEMA = {
    "type": "object",
    "minProperties": 1,
    "maxProperties": 1,
    "patternProperties": {"^.+$": {"$ref": "#/definitions/node"}},
    "additionalProperties": False,
    "definitions": {
        "node": {
            "type": "object",
            "required": ["type"],
            "properties": {
                "type": {"type": "string"},
                "id": {"type": "string"},
                "config": {"type": "object"},
                "children": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/node"},
                },
            },
            "additionalProperties": False,
        }
    },
}

if Draft7Validator is not None:  # pragma: no cover - exercised in environments with jsonschema
    _validator = Draft7Validator(CONFIG_SCHEMA)

    def validate_simulation_config(data: Any) -> None:
        """Validate configuration using :mod:`jsonschema` if available."""

        _validator.validate(data)

else:

    def validate_simulation_config(data: Any) -> None:
        """Validate configuration using a simple Python implementation."""

        _validate_root(data)


def _validate_root(data: Any) -> None:
    if not isinstance(data, dict) or len(data) != 1:
        raise ValidationError("Configuration must contain a single root node")
    for spec in data.values():
        _validate_node(spec)


def _validate_node(spec: Any) -> None:
    if not isinstance(spec, dict):
        raise ValidationError("Node specification must be a mapping")
    required = {"type"}
    allowed = {"type", "id", "config", "children"}
    missing = required - spec.keys()
    if missing:
        raise ValidationError(f"Missing keys in node specification: {missing}")
    if not isinstance(spec["type"], str):
        raise ValidationError("'type' must be a string")
    extra = set(spec) - allowed
    if extra:
        raise ValidationError(f"Unknown keys in node specification: {extra}")
    if "config" in spec and not isinstance(spec["config"], dict):
        raise ValidationError("'config' must be a mapping")
    if "children" in spec:
        children = spec["children"]
        if not isinstance(children, list):
            raise ValidationError("'children' must be a list")
        for child in children:
            _validate_node(child)


__all__ = ["validate_simulation_config", "ValidationError", "CONFIG_SCHEMA"]

