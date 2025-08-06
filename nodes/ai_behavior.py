"""Simple AI behaviour for farmers with daily routines."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from core.simnode import SimNode
from core.plugins import register_node_type
from .inventory import InventoryNode
from .need import NeedNode
from .resource_producer import ResourceProducerNode
from .transform import TransformNode


class AIBehaviorNode(SimNode):
    """Small behaviour node implementing a daily routine.

    Parameters
    ----------
    routine:
        List of dictionaries of the form ``{"start": int, "end": int,
        "action": str}`` describing the action to perform for each hour
        interval. Actions supported are ``"work"``, ``"wander"`` and
        ``"sleep"``.
    home:
        Position ``[x, y]`` where the character sleeps at night.
    work_position:
        Position ``[x, y]`` representing the working area.
    wander_range:
        Maximum distance in pixels travelled in a random direction when
        wandering.
    target_inventory:
        Optional inventory from which the farmer can eat when hungry.
    """

    def __init__(
        self,
        routine: Optional[List[Dict[str, int]]] = None,
        home: Optional[List[float]] = None,
        work_position: Optional[List[float]] = None,
        wander_range: float = 1.0,
        target_inventory: Optional[InventoryNode] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.target_inventory = target_inventory
        self.routine = routine or []
        self.home = home or [0.0, 0.0]
        self.work_position = work_position or self.home
        self.wander_range = wander_range
        self.on_event("need_threshold_reached", self._on_need)
        self.on_event("tick", self._on_tick)
        self._state: Optional[str] = None

    def _action_for_hour(self, hour: int) -> Optional[str]:
        for entry in self.routine:
            if entry["start"] <= hour < entry["end"]:
                return entry["action"]
        return None

    def _on_tick(self, emitter: SimNode, event_name: str, payload) -> None:
        hour = payload.get("tick", 0)
        action = self._action_for_hour(hour)
        self._apply_action(action)

    def _apply_action(self, action: Optional[str]) -> None:
        transform = self._find_transform()
        producer = self._find_producer()
        if action == "work":
            if transform:
                transform.position = list(self.work_position)
            if producer:
                producer.active = True
        elif action == "wander":
            if producer:
                producer.active = False
            if transform:
                transform.position[0] += random.uniform(-self.wander_range, self.wander_range)
                transform.position[1] += random.uniform(-self.wander_range, self.wander_range)
        elif action == "sleep":
            if producer:
                producer.active = False
            if transform:
                transform.position = list(self.home)
        else:
            if producer:
                producer.active = False

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

    def _find_transform(self) -> Optional[TransformNode]:
        for child in self.parent.children:
            if isinstance(child, TransformNode):
                return child
        return None

    def _find_producer(self) -> Optional[ResourceProducerNode]:
        for child in self.parent.children:
            if isinstance(child, ResourceProducerNode):
                return child
        return None

    def _find_need(self, name: str) -> Optional[NeedNode]:
        for child in self.parent.children:
            if isinstance(child, NeedNode) and child.need_name == name:
                return child
        return None


register_node_type("AIBehaviorNode", AIBehaviorNode)
