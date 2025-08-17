"""General node representing a military leader in the war simulation."""
from __future__ import annotations

from typing import Dict, List
import random
import time

from core.simnode import SimNode
from core.plugins import register_node_type
from nodes.strategist import StrategistNode


class GeneralNode(SimNode):
    """Represent a general with tactical preferences and command helpers.

    Parameters
    ----------
    style:
        Tactical approach of the general: ``"aggressive"``, ``"defensive"``
        or ``"balanced"``.
    flank_success_chance:
        Probability in ``[0, 1]`` that a flanking manoeuvre succeeds.
    caution_level:
        Risk aversion in ``[0, 1]``; high values make the general more
        conservative.
    intel_confidence:
        Confidence in reconnaissance intel in ``[0, 1]``.
    command_delay_s:
        Delay in seconds applied when issuing orders.
    """

    def __init__(
        self,
        style: str,
        flank_success_chance: float = 0.25,
        *,
        caution_level: float = 0.5,
        intel_confidence: float = 1.0,
        command_delay_s: float = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.style = style
        self.flank_success_chance = flank_success_chance
        self.caution_level = caution_level
        self.intel_confidence = intel_confidence
        self.command_delay_s = command_delay_s
        self.reports: List[Dict] = []
        self.on_event("battlefield_event", self._record_report)

    # ------------------------------------------------------------------
    def _record_report(self, _origin: SimNode, _event: str, payload: Dict) -> None:
        """Store a partial battlefield report in ``reports``."""

        self.reports.append(payload)

    # ------------------------------------------------------------------
    def get_armies(self) -> List[SimNode]:
        """Return direct child nodes considered armies."""

        return [c for c in self.children if c.__class__.__name__ == "ArmyNode"]

    # ------------------------------------------------------------------
    def attempt_flank(self, army: SimNode) -> bool:
        """Attempt a flanking manoeuvre with *army*.

        Returns ``True`` if the manoeuvre succeeds and the army's goal is
        changed to ``"flank"``.
        """

        success = random.random() < self.flank_success_chance
        if success:
            army.change_goal("flank")
        return success


    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Update child nodes then run simple decision logic."""

        super().update(dt)
        self._decide()

    # ------------------------------------------------------------------
    def _score_action(self, action: str, terrain_bonus: float) -> float:
        base = {"advance": 1.0, "flank": 0.9, "hold": 0.6, "retreat": 0.3}[action]
        score = base * self.intel_confidence * (1 - self.caution_level)
        score += terrain_bonus
        if action == "retreat":
            score += self.caution_level
        elif action == "hold":
            score += self.caution_level * 0.5
        if self.style == "aggressive" and action in {"advance", "flank"}:
            score += 0.1
        if self.style == "defensive" and action in {"hold", "retreat"}:
            score += 0.1
        return score

    # ------------------------------------------------------------------
    def _decide(self) -> None:
        """Adjust armies' goals based on strategist intel."""

        strategist = next((c for c in self.children if isinstance(c, StrategistNode)), None)
        if strategist is None:
            return

        intel = strategist.get_enemy_estimates()
        if not intel:
            return

        terrain_bonus = 0.0
        if intel:
            terrain_bonus = sum(r.get("terrain_bonus", 0.0) for r in intel) / len(intel)

        actions = ["advance", "flank", "hold", "retreat"]
        scores = {a: self._score_action(a, terrain_bonus) for a in actions}
        goal = max(scores, key=scores.get)

        for army in self.get_armies():
            if getattr(army, "goal", None) != goal:
                army.change_goal(goal)

        self.reports.clear()

    # ------------------------------------------------------------------
    def issue_orders(self, orders: List[Dict]) -> None:
        """Emit ``order_issued`` events for each dict in *orders*.

        The payload is enriched with ``issuer_id`` and ``time_issued`` then
        bubbled upward so that the :class:`~systems.command.CommandSystem`
        can dispatch it with the appropriate delay and reliability.
        """

        now = time.time()
        for order in orders:
            order.setdefault("issuer_id", id(self))
            order.setdefault("time_issued", now)
            self.emit("order_issued", order, direction="up")


register_node_type("GeneralNode", GeneralNode)
