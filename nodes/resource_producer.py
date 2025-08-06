"""Node producing resources each tick."""
from __future__ import annotations

from typing import Dict, Optional

from core.simnode import SimNode
from core.plugins import register_node_type
from .inventory import InventoryNode


class ResourceProducerNode(SimNode):
    """Produce a resource at a fixed rate, consuming optional inputs."""

    def __init__(
        self,
        resource: str,
        rate_per_tick: int,
        inputs: Optional[Dict[str, int]] = None,
        output_inventory: Optional[InventoryNode] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.resource = resource
        self.rate_per_tick = rate_per_tick
        self.inputs = inputs or {}
        self.output_inventory = output_inventory

    def update(self, dt: float) -> None:
        inv = self.output_inventory or self._find_inventory()
        if inv is None:
            return
        if all(inv.items.get(name, 0) >= qty for name, qty in self.inputs.items()):
            for name, qty in self.inputs.items():
                inv.remove_item(name, qty)
            inv.add_item(self.resource, self.rate_per_tick)
            self.emit("resource_produced", {"resource": self.resource, "amount": self.rate_per_tick})
        super().update(dt)

    def _find_inventory(self) -> Optional[InventoryNode]:
        for child in self.children:
            if isinstance(child, InventoryNode):
                self.output_inventory = child
                return child
        return None


register_node_type("ResourceProducerNode", ResourceProducerNode)
