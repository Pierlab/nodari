"""Warehouse node for storing goods."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class WarehouseNode(SimNode):
    """Represents a storage building."""

    def __init__(self, width: int | None = None, height: int | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height


register_node_type("WarehouseNode", WarehouseNode)
