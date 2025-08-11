"""Loader for simulation configuration files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import inspect

from .plugins import get_node_type
from .schema import validate_simulation_config

try:  # optional YAML support
    import yaml  # type: ignore
except Exception:  # pragma: no cover - yaml not installed
    yaml = None  # type: ignore


def load_simulation_from_file(path: str) -> Any:
    """Load a simulation tree from a JSON or YAML file."""
    data = _load_data(Path(path))
    validate_simulation_config(data)
    root_name, spec = next(iter(data.items()))
    return _build_node(spec, root_name)


def _load_data(path: Path) -> Any:
    if path.suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("YAML support requires PyYAML")
        with path.open("r", encoding="utf8") as fh:
            return yaml.safe_load(fh)
    else:
        with path.open("r", encoding="utf8") as fh:
            return json.load(fh)


def _build_node(spec: Dict[str, Any], default_name: str) -> Any:
    node_type = spec["type"]
    cls = get_node_type(node_type)
    config = spec.get("config", {})
    # merge class level defaults if provided
    if hasattr(cls, "DEFAULT_CONFIG"):
        defaults = dict(getattr(cls, "DEFAULT_CONFIG"))
        defaults.update(config)
        config = defaults

    # Basic validation: reject unknown parameters to help catch typos
    sig = inspect.signature(cls.__init__)
    valid_params = set(sig.parameters)
    if "kwargs" not in sig.parameters:
        unknown = set(config) - (valid_params - {"self"})
        if unknown:
            raise TypeError(f"Unknown config parameters for {cls.__name__}: {unknown}")

    name = spec.get("id", default_name)
    node = cls(name=name, **config)
    for child_spec in spec.get("children", []):
        child_name = child_spec.get("id", child_spec.get("type"))
        child = _build_node(child_spec, child_name)
        node.add_child(child)
    return node
