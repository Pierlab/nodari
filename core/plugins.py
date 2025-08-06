"""Simple plugin registry for simulation nodes."""
from __future__ import annotations

import importlib
from typing import Dict, Iterable, Type

from .simnode import SimNode


_registry: Dict[str, Type[SimNode]] = {}


def register_node_type(name: str, cls: Type[SimNode]) -> None:
    """Register *cls* under *name*."""
    if not issubclass(cls, SimNode):
        raise TypeError("Registered class must inherit from SimNode")
    _registry[name] = cls


def get_node_type(name: str) -> Type[SimNode]:
    """Return the class registered under *name*."""
    return _registry[name]


def load_plugins(module_names: Iterable[str]) -> None:
    """Import modules to register their node types."""
    for module in module_names:
        importlib.import_module(module)
