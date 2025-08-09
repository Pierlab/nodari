"""Barn node for housing animals."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class BarnNode(SimNode):
    """Simple barn used to shelter animals and equipment."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


register_node_type("BarnNode", BarnNode)
