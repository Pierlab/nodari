"""Officer node commanding several units."""
from __future__ import annotations

from typing import List

from core.simnode import SimNode
from core.plugins import register_node_type


class OfficerNode(SimNode):
    """Command-level node grouping multiple units."""

    # ------------------------------------------------------------------
    def get_units(self) -> List[SimNode]:
        """Return direct child nodes considered units."""
        return [c for c in self.children if c.__class__.__name__ == "UnitNode"]


register_node_type("OfficerNode", OfficerNode)
