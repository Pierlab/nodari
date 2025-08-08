"""Simple AI behaviour reacting to needs."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional
import random

from core.simnode import SimNode
from core.plugins import register_node_type
from core.units import kmh_to_mps
from .inventory import InventoryNode
from .transform import TransformNode
from . import ai_utils

_DEFAULT_IDLE_JITTER_DISTANCE = 0.5  # meters when random_speed is 2 km/h


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
        wake_hour: float = 6.0,
        work_start_hour: float = 8.0,
        lunch_hour: float = 12.0,
        lunch_end_hour: float = 14.0,
        work_end_hour: float = 18.0,
        sleep_hour: float = 22.0,
        idle_jitter_distance: float = _DEFAULT_IDLE_JITTER_DISTANCE,
        water_per_fetch: int = 5,
        wheat_threshold: int = 20,
        update_interval: float | None = None,
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
        wake_hour, work_start_hour, ...:
            Daily schedule in hours since midnight controlling movement and work.
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
        # Convert daily schedule (hours) to seconds
        self.wake_time = wake_hour * 3600
        self.work_start_time = work_start_hour * 3600
        self.lunch_time = lunch_hour * 3600
        self.lunch_end_time = lunch_end_hour * 3600
        self.work_end_time = work_end_hour * 3600
        self.sleep_time = sleep_hour * 3600
        self.idle_jitter_distance = idle_jitter_distance
        self.water_per_fetch = water_per_fetch
        self.wheat_threshold = wheat_threshold
        self._money_acc = 0.0
        self._idle = False
        self._sleeping = False
        self._resolved = False
        self._task: Optional[str] = None
        # simple configurable state machine
        self.state: str = "idle"
        self.state_handlers: Dict[str, Callable[[float, TransformNode], None]] = {
            "idle": self._state_idle,
            "moving": self._state_moving,
            "working": self._state_working,
        }
        self.on_event("need_threshold_reached", self._on_need)
        self.update_interval = update_interval
        if update_interval:
            scheduler = ai_utils.scheduler_system(self)
            if scheduler:
                scheduler.schedule(self, update_interval)

    def update(self, dt: float) -> None:
        transform = ai_utils.find_transform(self.parent)
        if transform is None:
            super().update(dt)
            return
        if self.home or self.work:
            self.resolve_references()
            target = self.plan(transform)
            self.navigate(transform, target, dt)
            self.interact(transform, target, dt)
        else:
            # fallback random walk
            transform.position[0] += random.uniform(-1, 1) * self.random_speed * dt
            transform.position[1] += random.uniform(-1, 1) * self.random_speed * dt
        super().update(dt)

    # ------------------------------------------------------------------
    # Public helpers for state machine
    # ------------------------------------------------------------------
    def change_state(self, new_state: str) -> None:
        self.state = new_state

    def resolve_references(self) -> None:
        self._resolve_references()

    # Planning / Navigation / Economic interactions --------------------
    def plan(self, transform: TransformNode) -> Optional[List[float]]:
        target = ai_utils.determine_target(self)
        if target is None:
            self.change_state("idle")
        else:
            self.change_state("moving")
        return target

    def navigate(self, transform: TransformNode, target: Optional[List[float]], dt: float) -> None:
        if target is None:
            return
        ai_utils.move_towards(transform, target, self.speed, dt)
        if ai_utils.is_at_position(transform.position, target):
            ai_utils.apply_idle_jitter(
                transform,
                target,
                self.random_speed,
                self.idle_jitter_distance,
                self._sleeping,
            )
            self.change_state("working")

    def interact(self, transform: TransformNode, target: Optional[List[float]], dt: float) -> None:
        if target is None:
            return
        handler = self.state_handlers.get(self.state)
        if handler:
            handler(dt, transform)

    # State handlers ----------------------------------------------------
    def _state_idle(self, dt: float, transform: TransformNode) -> None:  # pragma: no cover - trivial
        pass

    def _state_moving(self, dt: float, transform: TransformNode) -> None:  # pragma: no cover - handled in navigate
        pass

    def _state_working(self, dt: float, transform: TransformNode) -> None:
        target = self._determine_target()
        if target is not None:
            self._handle_work(transform, target, dt)

    def _on_need(self, emitter: SimNode, event_name: str, payload) -> None:
        if payload.get("need") != "hunger":
            return
        my_inv = ai_utils.find_inventory(self.parent)
        hunger = ai_utils.find_need(self.parent, "hunger")
        if my_inv is None or hunger is None or self.target_inventory is None:
            return
        if self.target_inventory.items.get("wheat", 0) > 0:
            self.target_inventory.transfer_to(my_inv, "wheat", 1)
            hunger.satisfy(50)

    # Backward compatibility wrappers ---------------------------------
    def _determine_target(self) -> Optional[List[float]]:
        return ai_utils.determine_target(self)

    def _handle_work(self, transform: TransformNode, target: List[float], dt: float) -> None:
        ai_utils.handle_work(self, transform, target, dt)

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------
    def _resolve_references(self) -> None:
        if self._resolved:
            return
        root = ai_utils.root(self)
        if isinstance(self.home, str):
            self.home = ai_utils.find_by_name(root, self.home)
        if isinstance(self.work, str):
            self.work = ai_utils.find_by_name(root, self.work)
        if isinstance(self.home_inventory, str):
            node = ai_utils.find_by_name(root, self.home_inventory)
            if isinstance(node, InventoryNode):
                self.home_inventory = node
        if isinstance(self.work_inventory, str):
            node = ai_utils.find_by_name(root, self.work_inventory)
            if isinstance(node, InventoryNode):
                self.work_inventory = node
        if isinstance(self.well_inventory, str):
            node = ai_utils.find_by_name(root, self.well_inventory)
            if isinstance(node, InventoryNode):
                self.well_inventory = node
        if isinstance(self.warehouse_inventory, str):
            node = ai_utils.find_by_name(root, self.warehouse_inventory)
            if isinstance(node, InventoryNode):
                self.warehouse_inventory = node
        self._resolved = True


register_node_type("AIBehaviorNode", AIBehaviorNode)
