"""Inventory node managing resources."""
from __future__ import annotations

from typing import Dict, Optional

from core.simnode import SimNode
from core.plugins import register_node_type


class InventoryNode(SimNode):
    """Node holding a dictionary of item quantities."""

    def __init__(self, items: Optional[Dict[str, int]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.items: Dict[str, int] = items or {}

    def add_item(self, name: str, qty: int) -> None:
        self.items[name] = self.items.get(name, 0) + qty
        self.emit("inventory_changed", {"name": name, "quantity": self.items[name]}, direction="down")

    def remove_item(self, name: str, qty: int) -> None:
        if self.items.get(name, 0) < qty:
            raise ValueError("Not enough items")
        self.items[name] -= qty
        self.emit("inventory_changed", {"name": name, "quantity": self.items[name]}, direction="down")

    def transfer_to(self, other: "InventoryNode", name: str, qty: int) -> None:
        self.remove_item(name, qty)
        other.add_item(name, qty)


register_node_type("InventoryNode", InventoryNode)
