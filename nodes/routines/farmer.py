from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional

from .base import BaseRoutine
from .. import ai_utils
from ..transform import TransformNode


class FarmerRoutine(BaseRoutine):
    """Default farmer behaviour used by :class:`AIBehaviorNode`."""

    def __init__(self, ai: "AIBehaviorNode") -> None:
        super().__init__(ai)
        self.state_handlers: Dict[str, Callable[[float, TransformNode], None]] = {
            "idle": self._state_idle,
            "moving": self._state_moving,
            "working": self._state_working,
        }

    # ------------------------------------------------------------------
    # Main routine API
    # ------------------------------------------------------------------
    def update(self, dt: float, transform: TransformNode) -> None:
        ai = self.ai
        if ai.home or ai.work:
            ai.resolve_references()
            target = self.plan(transform)
            self.navigate(transform, target, dt)
            self.interact(transform, target, dt)
        else:
            # fallback random walk when no home/work defined
            transform.position[0] += random.uniform(-1, 1) * ai.random_speed * dt
            transform.position[1] += random.uniform(-1, 1) * ai.random_speed * dt

    def on_need(self, emitter, event_name: str, payload) -> None:
        if payload.get("need") != "hunger":
            return
        my_inv = ai_utils.find_inventory(self.ai.parent)
        hunger = ai_utils.find_need(self.ai.parent, "hunger")
        if my_inv is None or hunger is None or self.ai.target_inventory is None:
            return
        if self.ai.target_inventory.items.get("wheat", 0) > 0:
            self.ai.target_inventory.transfer_to(my_inv, "wheat", 1)
            hunger.satisfy(50)

    # ------------------------------------------------------------------
    # Planning / Navigation / Interactions
    # ------------------------------------------------------------------
    def plan(self, transform: TransformNode) -> Optional[List[float]]:
        target = ai_utils.determine_target(self.ai)
        if target is None:
            self.ai.change_state("idle")
        else:
            self.ai.change_state("moving")
        return target

    def navigate(self, transform: TransformNode, target: Optional[List[float]], dt: float) -> None:
        if target is None:
            return
        ai_utils.move_towards(transform, target, self.ai.speed, dt)
        if ai_utils.is_at_position(transform.position, target):
            ai_utils.apply_idle_jitter(
                transform,
                target,
                self.ai.random_speed,
                self.ai.idle_jitter_distance,
                self.ai._sleeping,
            )
            self.ai.change_state("working")

    def interact(self, transform: TransformNode, target: Optional[List[float]], dt: float) -> None:
        if target is None:
            return
        handler = self.state_handlers.get(self.ai.state)
        if handler:
            handler(dt, transform)

    # ------------------------------------------------------------------
    # State handlers
    # ------------------------------------------------------------------
    def _state_idle(self, dt: float, transform: TransformNode) -> None:  # pragma: no cover - trivial
        pass

    def _state_moving(self, dt: float, transform: TransformNode) -> None:  # pragma: no cover - handled in navigate
        pass

    def _state_working(self, dt: float, transform: TransformNode) -> None:
        target = self._determine_target()
        if target is not None:
            self._handle_work(transform, target, dt)

    # ------------------------------------------------------------------
    # Internal helpers mirroring previous AIBehaviorNode methods
    # ------------------------------------------------------------------
    def _determine_target(self) -> Optional[List[float]]:
        return ai_utils.determine_target(self.ai)

    def _handle_work(self, transform: TransformNode, target: List[float], dt: float) -> None:
        ai_utils.handle_work(self.ai, transform, target, dt)
