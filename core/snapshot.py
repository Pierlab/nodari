"""Utilities to save and load full simulation state snapshots."""
from __future__ import annotations

import inspect
from typing import Any, Dict, Optional

from .plugins import get_node_type
from .simnode import SimNode


def serialize_world(root: SimNode) -> Dict[str, Any]:
    """Serialise the whole simulation tree starting at *root*."""
    return root.serialize()


def _deserialize_node(data: Dict[str, Any], parent: Optional[SimNode] = None) -> SimNode:
    cls = get_node_type(data["type"])
    state: Dict[str, Any] = dict(data.get("state", {}))

    sig = inspect.signature(cls.__init__)
    init_kwargs: Dict[str, Any] = {}
    for name, param in list(sig.parameters.items())[1:]:
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        ):
            continue
        if name in state:
            init_kwargs[name] = state.pop(name)
        elif param.default is inspect._empty:
            raise TypeError(f"Missing required parameter '{name}' for {cls.__name__}")

    node = cls(name=data.get("name"), parent=parent, **init_kwargs)

    for key, value in state.items():
        setattr(node, key, value)

    for child_data in data.get("children", []):
        _deserialize_node(child_data, node)
    return node


def deserialize_world(data: Dict[str, Any]) -> SimNode:
    """Rebuild a simulation tree from previously serialised *data*.

    After constructing the full tree, nodes exposing a ``resolve_references``
    method will have it invoked once so that expensive lookups are avoided
    during the first update.
    """

    root = _deserialize_node(data, None)

    def _walk(node: SimNode):
        yield node
        for child in node.children:
            yield from _walk(child)

    for node in _walk(root):
        resolver = getattr(node, "resolve_references", None)
        if callable(resolver):
            resolver()

    return root
