"""Simple AI behaviour reacting to needs."""
from __future__ import annotations

from typing import List, Optional
import math
import random

from core.simnode import SimNode
from core.plugins import register_node_type
from core.units import kmh_to_mps
from .inventory import InventoryNode
from .need import NeedNode
from .transform import TransformNode
from systems.time import TimeSystem

# Reference random speed used to scale idle jitter (2 km/h)
_REF_RANDOM_SPEED = kmh_to_mps(2.0)
_IDLE_JITTER_DISTANCE = 0.5  # meters when random_speed is 2 km/h


class AIBehaviorNode(SimNode):
    """Very small behaviour for a farmer.

    When hunger reaches its threshold, the AI takes wheat from a target
    inventory and satisfies the hunger need.
    """

    def __init__(
        self,
        target_inventory: Optional[InventoryNode] = None,
        speed: float = 5.0,
        random_speed: float = 2.0,
        home: Optional[str | SimNode] = None,
        work: Optional[str | SimNode] = None,
        home_inventory: Optional[str | InventoryNode] = None,
        work_inventory: Optional[str | InventoryNode] = None,
        well_inventory: Optional[str | InventoryNode] = None,
        warehouse_inventory: Optional[str | InventoryNode] = None,
        lunch_position: Optional[List[float]] = None,
        wage: float = 1.0,
        idle_chance: float = 0.1,
        water_per_fetch: int = 5,
        wheat_threshold: int = 20,
        **kwargs,
    ) -> None:
        """Create the AI behaviour.

        Parameters
        ----------
        target_inventory:
            Inventory from which wheat is taken when hungry.
        speed:
            Movement speed in kilometres per hour.
        random_speed:
            Maximum random walk speed in kilometres per hour.
        home, work, ...:
            References to important nodes within the simulation tree.
        """
        super().__init__(**kwargs)
        self.target_inventory = target_inventory
        # Speeds are provided in km/h and converted to m/s for simulation
        self.speed = kmh_to_mps(speed)
        self.random_speed = kmh_to_mps(random_speed)
        self.home = home
        self.work = work
        self.home_inventory = home_inventory
        self.work_inventory = work_inventory
        self.well_inventory = well_inventory
        self.warehouse_inventory = warehouse_inventory
        self.lunch_position = lunch_position or [0.0, 0.0]
        self.wage = wage
        self.idle_chance = idle_chance
        self.water_per_fetch = water_per_fetch
        self.wheat_threshold = wheat_threshold
        self._money_acc = 0.0
        self._idle = False
        self._sleeping = False
        self._resolved = False
        self._task: Optional[str] = None
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
            transform.position[0] += random.uniform(-1, 1) * self.random_speed * dt
            transform.position[1] += random.uniform(-1, 1) * self.random_speed * dt
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

    def _find_producer(self, node: SimNode | None) -> Optional[SimNode]:
        if node is None:
            return None
        for child in node.children:
            from .resource_producer import ResourceProducerNode

            if isinstance(child, ResourceProducerNode):
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
        if isinstance(self.work_inventory, str):
            node = self._find_by_name(root, self.work_inventory)
            if isinstance(node, InventoryNode):
                self.work_inventory = node
        if isinstance(self.well_inventory, str):
            node = self._find_by_name(root, self.well_inventory)
            if isinstance(node, InventoryNode):
                self.well_inventory = node
        if isinstance(self.warehouse_inventory, str):
            node = self._find_by_name(root, self.warehouse_inventory)
            if isinstance(node, InventoryNode):
                self.warehouse_inventory = node
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
            self._task = None
            return self._get_position(self.home)
        self._sleeping = False
        if wake <= t < work_start:
            self._idle = False
            self._task = None
            return self._get_position(self.home)
        if work_start <= t < lunch:
            self._idle = False
            if self._task == "fetch_water" and isinstance(self.well_inventory, InventoryNode):
                return self._get_position(self.well_inventory.parent)
            if self._task == "deliver_water":
                return self._get_position(self.work)
            if self._task == "deliver_wheat" and isinstance(
                self.warehouse_inventory, InventoryNode
            ):
                return self._get_position(self.warehouse_inventory.parent)
            return self._get_position(self.work)
        if lunch <= t < lunch_end:
            if not self._idle and random.random() < self.idle_chance:
                self._idle = True
            return self.lunch_position
        if lunch_end <= t < work_end:
            self._idle = False
            if self._task == "fetch_water" and isinstance(self.well_inventory, InventoryNode):
                return self._get_position(self.well_inventory.parent)
            if self._task == "deliver_water":
                return self._get_position(self.work)
            if self._task == "deliver_wheat" and isinstance(
                self.warehouse_inventory, InventoryNode
            ):
                return self._get_position(self.warehouse_inventory.parent)
            return self._get_position(self.work)
        self._task = None
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
        inv = self._find_inventory()
        farm_inv = self.work_inventory if isinstance(self.work_inventory, InventoryNode) else None
        well_inv = self.well_inventory if isinstance(self.well_inventory, InventoryNode) else None
        warehouse_inv = self.warehouse_inventory if isinstance(self.warehouse_inventory, InventoryNode) else None
        producer = self._find_producer(self.work)
        if not (work_start <= t < lunch or (lunch_end <= t < work_end and not self._idle)):
            if inv:
                if farm_inv:
                    amt = inv.items.get("water", 0)
                    if amt > 0:
                        inv.transfer_to(farm_inv, "water", amt)
                if warehouse_inv:
                    amt = inv.items.get("wheat", 0)
                    if amt > 0:
                        inv.transfer_to(warehouse_inv, "wheat", amt)
                if (t >= work_end or t < work_start) and self.home_inventory and isinstance(self.home_inventory, InventoryNode):
                    amt = inv.items.get("money", 0)
                    if amt > 0:
                        inv.transfer_to(self.home_inventory, "money", amt)
            return
        work_pos = self._get_position(self.work)
        well_pos = self._get_position(well_inv.parent) if well_inv else None
        warehouse_pos = self._get_position(warehouse_inv.parent) if warehouse_inv else None

        if self._task == "fetch_water" and well_inv and well_pos and self._is_at_position(transform.position, well_pos):
            well_producer = self._find_producer(well_inv.parent)
            if well_producer:
                well_producer.work(self.water_per_fetch)
            qty = min(self.water_per_fetch, well_inv.items.get("water", 0))
            if inv and qty > 0:
                well_inv.transfer_to(inv, "water", qty)
            self._task = "deliver_water"
            return

        if self._task == "deliver_water" and work_pos and self._is_at_position(transform.position, work_pos):
            if inv and farm_inv:
                amt = inv.items.get("water", 0)
                if amt > 0:
                    inv.transfer_to(farm_inv, "water", amt)
            self._task = None

        if self._task == "deliver_wheat" and warehouse_pos and self._is_at_position(transform.position, warehouse_pos):
            if inv and warehouse_inv:
                amt = inv.items.get("wheat", 0)
                if amt > 0:
                    inv.transfer_to(warehouse_inv, "wheat", amt)
            self._task = None

        if work_pos and self._is_at_position(transform.position, work_pos):
            if inv and farm_inv:
                if inv.items.get("water", 0) > 0:
                    amt = inv.items.get("water", 0)
                    inv.transfer_to(farm_inv, "water", amt)
                if farm_inv.items.get("wheat", 0) >= self.wheat_threshold and inv.items.get("wheat", 0) == 0 and warehouse_inv:
                    qty = farm_inv.items.get("wheat", 0)
                    farm_inv.transfer_to(inv, "wheat", qty)
                    self._task = "deliver_wheat"
                    return
                if farm_inv.items.get("water", 0) < 1 and well_inv and inv.items.get("water", 0) == 0:
                    self._task = "fetch_water"
                    return
            if producer is not None and farm_inv:
                producer.work()

            self._money_acc += self.wage * dt
            if inv is not None and self._money_acc >= 1.0:
                amount = int(self._money_acc)
                self._money_acc -= amount
                inv.add_item("money", amount)

    def _is_at_position(self, pos: List[float], target: List[float], threshold: float = 0.5) -> bool:
        dx = pos[0] - target[0]
        dy = pos[1] - target[1]
        return math.hypot(dx, dy) <= threshold

    def _apply_idle_jitter(self, transform: TransformNode, target: List[float]) -> None:
        if self._sleeping:
            transform.position[0], transform.position[1] = target[0], target[1]
            return
        jitter = (self.random_speed / _REF_RANDOM_SPEED) * _IDLE_JITTER_DISTANCE
        transform.position[0] = target[0] + random.uniform(-jitter, jitter)
        transform.position[1] = target[1] + random.uniform(-jitter, jitter)


register_node_type("AIBehaviorNode", AIBehaviorNode)
