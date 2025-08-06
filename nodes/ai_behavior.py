"""Simple AI behaviour reacting to needs."""
from __future__ import annotations

from typing import List, Optional
import math
import random

from core.simnode import SimNode
from core.plugins import register_node_type
from .inventory import InventoryNode
from .need import NeedNode
from .transform import TransformNode
from systems.time import TimeSystem


class AIBehaviorNode(SimNode):
    """Very small behaviour for a farmer.

    When hunger reaches its threshold, the AI takes wheat from a target
    inventory and satisfies the hunger need.
    """

    def __init__(
        self,
        target_inventory: Optional[InventoryNode] = None,
        speed: float = 10.0,
        home: Optional[str | SimNode] = None,
        work: Optional[str | SimNode] = None,
        home_inventory: Optional[str | InventoryNode] = None,
        lunch_position: Optional[List[float]] = None,
        wage: float = 1.0,
        idle_chance: float = 0.1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.target_inventory = target_inventory
        self.speed = speed
        self.home = home
        self.work = work
        self.home_inventory = home_inventory
        self.lunch_position = lunch_position or [0.0, 0.0]
        self.wage = wage
        self.idle_chance = idle_chance
        self._money_acc = 0.0
        self._idle = False
        self._sleeping = False
        self._resolved = False
        self.on_event("need_threshold_reached", self._on_need)

    def update(self, dt: float) -> None:
        transform = self._find_transform()
        if transform is not None and (self.home or self.work):
            self._resolve_references()
            target = self._determine_target()
            if target is not None:
                self._move_towards(transform, target, dt)
                if self._is_at_position(transform.position, target):
                    self._apply_idle_jitter(transform, target)
                self._handle_work(transform, target, dt)
        elif transform is not None:
            # fallback random walk
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

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------
    def _root(self) -> SimNode:
        node: SimNode = self
        while node.parent is not None:
            node = node.parent
        return node

    def _resolve_references(self) -> None:
        if self._resolved:
            return
        root = self._root()
        if isinstance(self.home, str):
            self.home = self._find_by_name(root, self.home)
        if isinstance(self.work, str):
            self.work = self._find_by_name(root, self.work)
        if isinstance(self.home_inventory, str):
            node = self._find_by_name(root, self.home_inventory)
            if isinstance(node, InventoryNode):
                self.home_inventory = node
        self._resolved = True

    def _find_by_name(self, node: SimNode, name: str) -> Optional[SimNode]:
        if node.name == name:
            return node
        for child in node.children:
            found = self._find_by_name(child, name)
            if found is not None:
                return found
        return None

    def _time_system(self) -> Optional[TimeSystem]:
        root = self._root()
        for child in self._walk(root):
            if isinstance(child, TimeSystem):
                return child
        return None

    def _walk(self, node: SimNode):  # type: ignore[override]
        yield node
        for child in node.children:
            yield from self._walk(child)

    def _get_position(self, node: SimNode | None) -> Optional[List[float]]:
        if node is None:
            return None
        for child in node.children:
            if isinstance(child, TransformNode):
                return child.position
        return None

    def _determine_target(self) -> Optional[List[float]]:
        time_sys = self._time_system()
        if time_sys is None:
            return None
        t = time_sys.current_time % 86400
        wake = 6 * 3600
        work_start = 8 * 3600
        lunch = 12 * 3600
        lunch_end = 14 * 3600
        work_end = 18 * 3600
        sleep = 22 * 3600

        if t < wake or t >= sleep:
            self._sleeping = True
            self._idle = False
            return self._get_position(self.home)
        self._sleeping = False
        if wake <= t < work_start:
            self._idle = False
            return self._get_position(self.home)
        if work_start <= t < lunch:
            self._idle = False
            return self._get_position(self.work)
        if lunch <= t < lunch_end:
            if not self._idle and random.random() < self.idle_chance:
                self._idle = True
            return self.lunch_position
        if lunch_end <= t < work_end:
            if self._idle:
                return self.lunch_position
            return self._get_position(self.work)
        return self._get_position(self.home)

    def _move_towards(self, transform: TransformNode, target: List[float], dt: float) -> None:
        dx = target[0] - transform.position[0]
        dy = target[1] - transform.position[1]
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return
        step = self.speed * dt
        if step >= dist:
            transform.position[0], transform.position[1] = target[0], target[1]
        else:
            transform.position[0] += dx / dist * step
            transform.position[1] += dy / dist * step

    def _handle_work(self, transform: TransformNode, target: List[float], dt: float) -> None:
        time_sys = self._time_system()
        if time_sys is None:
            return
        t = time_sys.current_time % 86400
        work_start = 8 * 3600
        lunch = 12 * 3600
        lunch_end = 14 * 3600
        work_end = 18 * 3600
        sleep = 22 * 3600
        if work_start <= t < lunch or (lunch_end <= t < work_end and not self._idle):
            work_pos = self._get_position(self.work)
            if work_pos is not None:
                dx = transform.position[0] - work_pos[0]
                dy = transform.position[1] - work_pos[1]
                if math.hypot(dx, dy) < 1.0:
                    self._money_acc += self.wage * dt
                    inv = self._find_inventory()
                    if inv is not None and self._money_acc >= 1.0:
                        amount = int(self._money_acc)
                        self._money_acc -= amount
                        inv.add_item("money", amount)
        if t >= work_end or t < work_start:
            inv = self._find_inventory()
            if inv and self.home_inventory and isinstance(self.home_inventory, InventoryNode):
                amt = inv.items.get("money", 0)
                if amt > 0:
                    inv.transfer_to(self.home_inventory, "money", amt)

    def _is_at_position(self, pos: List[float], target: List[float], threshold: float = 0.5) -> bool:
        dx = pos[0] - target[0]
        dy = pos[1] - target[1]
        return math.hypot(dx, dy) <= threshold

    def _apply_idle_jitter(self, transform: TransformNode, target: List[float]) -> None:
        if self._sleeping:
            transform.position[0], transform.position[1] = target[0], target[1]
            return
        jitter = 0.5
        transform.position[0] = target[0] + random.uniform(-jitter, jitter)
        transform.position[1] = target[1] + random.uniform(-jitter, jitter)


register_node_type("AIBehaviorNode", AIBehaviorNode)
