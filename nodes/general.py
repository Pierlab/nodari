"""General node representing a military leader in the war simulation."""
from __future__ import annotations

from typing import List, Dict

from core.simnode import SimNode
from core.plugins import register_node_type


class GeneralNode(SimNode):
    """Represent a general with a tactical style and battlefield reports.

    Parameters
    ----------
    style:
        Tactical approach of the general: ``"aggressive"``, ``"defensive"``
        or ``"balanced"``.
    """

    def __init__(self, style: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.style = style
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
    def update(self, dt: float) -> None:
        """Update child nodes then run simple decision logic."""

        super().update(dt)
        self._decide()

    # ------------------------------------------------------------------
    def _decide(self) -> None:
        """Adjust armies' goals based on latest reports and nation morale.

        The general uses only the most recent battlefield report to make a
        decision. Thresholds depend on ``style``:

        ``aggressive`` -> defend below 40 morale, retreat below 20.
        ``balanced``   -> defend below 60 morale, retreat below 30.
        ``defensive``  -> defend below 80 morale, retreat below 50.
        """

        if not self.reports:
            return

        nation = self.parent if self.parent and self.parent.__class__.__name__ == "NationNode" else None
        morale = getattr(nation, "morale", 0)
        thresholds = {
            "aggressive": {"defend": 40, "retreat": 20},
            "balanced": {"defend": 60, "retreat": 30},
            "defensive": {"defend": 80, "retreat": 50},
        }.get(self.style, {"defend": 60, "retreat": 30})

        last = self.reports[-1]
        defend_th = thresholds["defend"]
        retreat_th = thresholds["retreat"]

        if last.get("type") == "unit_routed":
            goal = "retreat" if morale < retreat_th else "defend"
        else:
            if morale < retreat_th:
                goal = "retreat"
            elif morale < defend_th:
                goal = "defend"
            else:
                goal = "advance"

        for army in self.get_armies():
            if getattr(army, "goal", None) != goal:
                army.change_goal(goal)

        self.reports.clear()


register_node_type("GeneralNode", GeneralNode)
