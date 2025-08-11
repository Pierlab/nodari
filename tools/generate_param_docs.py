#!/usr/bin/env python3
"""Generate Markdown inventory of node and system parameters."""
from __future__ import annotations

import inspect
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List

from core.simnode import SimNode


def iter_simnode_classes(package: str) -> Dict[str, type]:
    """Return mapping of qualified class names to classes for *package*."""
    classes: Dict[str, type] = {}
    pkg = importlib.import_module(package)
    package_path = Path(pkg.__file__).parent
    for modinfo in pkgutil.walk_packages([str(package_path)], prefix=f"{package}."):
        module = importlib.import_module(modinfo.name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, SimNode) and obj.__module__ == module.__name__:
                classes[obj.__name__] = obj
    return classes


def parse_param_docs(doc: str | None) -> Dict[str, str]:
    """Extract a mapping of parameter descriptions from *doc*.

    The parser understands a very small subset of NumPy-style docstrings.
    """
    if not doc:
        return {}
    lines = doc.splitlines()
    params: Dict[str, str] = {}
    in_params = False
    current: str | None = None
    for line in lines:
        stripped = line.strip()
        if not in_params:
            if stripped.lower().startswith("parameters"):
                in_params = True
            continue
        if not stripped:
            current = None
            continue
        if not line.startswith(" ") and ":" in line:
            # New parameter line of form 'name: description'
            name, desc = line.split(":", 1)
            current = name.strip()
            params[current] = desc.strip()
        elif current:
            params[current] += " " + stripped
    return params


def format_defaults(value: inspect._empty | object) -> str:
    if value is inspect._empty:
        return ""
    return repr(value)


def generate_markdown() -> str:
    lines: List[str] = ["# Parameter inventory\n"]
    for package in ["nodes", "systems"]:
        lines.append(f"## {package.capitalize()}\n")
        classes = iter_simnode_classes(package)
        for name, cls in sorted(classes.items()):
            lines.append(f"### {name}\n")
            doc = inspect.getdoc(cls)
            param_docs = parse_param_docs(doc)
            sig = inspect.signature(cls.__init__)
            lines.append("| Parameter | Type | Default | Description |")
            lines.append("| --- | --- | --- | --- |")
            for param in list(sig.parameters.values())[1:]:  # skip self
                lines.append(
                    f"| {param.name} | {getattr(param.annotation, '__name__', param.annotation)} | {format_defaults(param.default)} | {param_docs.get(param.name, '')} |")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "docs" / "parameter_inventory.md"
    out.write_text(generate_markdown(), encoding="utf8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

