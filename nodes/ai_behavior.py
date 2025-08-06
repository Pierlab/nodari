"""Simple AI behaviour reacting to needs."""
from __future__ import annotations

from typing import Optional
import random

from core.simnode import SimNode
from core.plugins import register_node_type
from .inventory import InventoryNode
from .need import NeedNode
from .transform import TransformNode


class AIBehaviorNode(SimNode):
    """Very small behaviour for a farmer.

    When hunger reaches its threshold, the AI takes wheat from a target
    inventory and satisfies the hunger need.
    """

    def __init__(self, target_inventory: Optional[InventoryNode] = None, speed: float = 10.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.target_inventory = target_inventory
        self.speed = speed
        self.on_event("need_threshold_reached", self._on_need)

    def update(self, dt: float) -> None:
        transform = self._find_transform()
        if transform is not None:
            transform.position[0] += random.uniform(-1, 1) * self.speed * dt
            transform.position[1] += random.uniform(-1, 1) * self.speed * dt
        super().update(dt)

    def _on_need(self, emitter: SimNode, event_name: str, payload) -> None:
        if payload.get("need") != "hunger":
            return
        my_inv = self._find_inventory()
        hunger = self._find_need("hunger")
        if my_inv is None or hunger is None or self.target_inventory is None:
            return
        if self.target_inventory.items.get("wheat", 0) > 0:
            self.target_inventory.transfer_to(my_inv, "wheat", 1)
            hunger.satisfy(50)

    def _find_inventory(self) -> Optional[InventoryNode]:
        for child in self.parent.children:
            if isinstance(child, InventoryNode):
                return child
        return None

    def _find_need(self, name: str) -> Optional[NeedNode]:
        for child in self.parent.children:
            if isinstance(child, NeedNode) and child.need_name == name:
                return child
        return None

    def _find_transform(self) -> Optional[TransformNode]:
        for child in self.parent.children:
            if isinstance(child, TransformNode):
                return child
        return None


register_node_type("AIBehaviorNode", AIBehaviorNode)
