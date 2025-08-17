"""Strategist node collecting reconnaissance intel."""
from __future__ import annotations

from typing import Dict, List

from core.simnode import SimNode
from core.plugins import register_node_type


class StrategistNode(SimNode):
    """Collect and provide reconnaissance intel for the general."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.intel_reports: List[Dict] = []
        # Listen to intel events produced by the visibility system
        self.on_event("enemy_spotted", self._record_intel)

    # ------------------------------------------------------------------
    def _record_intel(self, _origin: SimNode, _event: str, payload: Dict) -> None:
        """Store an intel report."""
        self.intel_reports.append(payload)

    # ------------------------------------------------------------------
    def get_enemy_estimates(self, max_age_s: float = 60.0) -> List[Dict]:
        """Return recent intel reports not older than *max_age_s* seconds."""
        if not self.intel_reports:
            return []
        now = max(r.get("timestamp", 0) for r in self.intel_reports)
        return [r for r in self.intel_reports if now - r.get("timestamp", 0) <= max_age_s]


register_node_type("StrategistNode", StrategistNode)
