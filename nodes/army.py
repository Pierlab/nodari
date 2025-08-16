"""Army node grouping units and tracking objectives."""
from __future__ import annotations

from typing import List

from core.simnode import SimNode
from core.plugins import register_node_type


class ArmyNode(SimNode):
    """Represent an army with a goal and current size.

    Parameters
    ----------
    goal:
        Current objective of the army: ``"advance"``, ``"defend"`` or ``"retreat"``.
    size:
        Number of unit groups in the army.
    """

    def __init__(self, goal: str, size: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.goal = goal
        self.size = size
        self.on_event("unit_engaged", self._handle_unit_event)
        self.on_event("unit_routed", self._handle_unit_event)

    # ------------------------------------------------------------------
    def _handle_unit_event(self, origin: SimNode, event: str, payload: dict) -> None:
        """Forward unit events as battlefield reports and adjust size."""

        if event == "unit_routed":
            loss = payload.get("loss", 1)
            self.size = max(0, self.size - loss)

        self.emit("battlefield_event", {"type": event, **payload}, direction="up")

    # ------------------------------------------------------------------
    def change_goal(self, new_goal: str) -> None:
        """Update the army's goal and emit ``goal_changed``."""

        previous = self.goal
        self.goal = new_goal
        self.emit(
            "goal_changed",
            {"previous": previous, "goal": new_goal},
            direction="down",
        )

    # ------------------------------------------------------------------
    def get_units(self) -> List[SimNode]:
        """Return direct child nodes considered units."""

        return [c for c in self.children if c.__class__.__name__ == "UnitNode"]


register_node_type("ArmyNode", ArmyNode)
