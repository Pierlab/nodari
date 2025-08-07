"""Node producing resources each tick."""
from __future__ import annotations

from typing import Dict, Optional

from core.simnode import SimNode
from core.plugins import register_node_type
from .inventory import InventoryNode


class ResourceProducerNode(SimNode):
    """Produce a resource and optionally require manual activation.

    Parameters
    ----------
    resource:
        Name of the produced resource.
    rate_per_tick:
        Quantity produced each time :meth:`work` is called or per tick when
        ``auto`` is ``True``.
    inputs:
        Resources consumed from the output inventory before producing.
    output_inventory:
        Inventory receiving the produced resource.
    auto:
        If ``True`` (default) production happens automatically every update.
    """

    def __init__(
        self,
        resource: str,
        rate_per_tick: int,
        inputs: Optional[Dict[str, int]] = None,
        output_inventory: Optional[InventoryNode] = None,
        auto: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.resource = resource
        self.rate_per_tick = rate_per_tick
        self.inputs = inputs or {}
        self.output_inventory = output_inventory
        self.auto = auto

    def update(self, dt: float) -> None:
        if self.auto:
            self.work()
        super().update(dt)

    def work(self, times: int = 1) -> None:
        """Produce the resource ``times`` times if inputs are available."""
        inv = self.output_inventory or self._find_inventory()
        if inv is None:
            return
        for _ in range(times):
            if all(inv.items.get(name, 0) >= qty for name, qty in self.inputs.items()):
                for name, qty in self.inputs.items():
                    inv.remove_item(name, qty)
                inv.add_item(self.resource, self.rate_per_tick)
                self.emit(
                    "resource_produced",
                    {"resource": self.resource, "amount": self.rate_per_tick},
                )
            else:
                break

    def _find_inventory(self) -> Optional[InventoryNode]:
        for child in self.children:
            if isinstance(child, InventoryNode):
                self.output_inventory = child
                return child
        return None


register_node_type("ResourceProducerNode", ResourceProducerNode)
