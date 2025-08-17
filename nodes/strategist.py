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
        self.on_event("intel_report", self._record_intel)

    # ------------------------------------------------------------------
    def _record_intel(self, _origin: SimNode, _event: str, payload: Dict) -> None:
        """Store an intel report."""
        self.intel_reports.append(payload)

    # ------------------------------------------------------------------
    def get_intel(self) -> List[Dict]:
        """Return recorded intel reports."""
        return list(self.intel_reports)


register_node_type("StrategistNode", StrategistNode)
