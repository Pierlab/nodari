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


register_node_type("GeneralNode", GeneralNode)
