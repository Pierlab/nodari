"""Officer node commanding several units."""
from __future__ import annotations

from typing import Dict, List

from core.simnode import SimNode
from core.plugins import register_node_type


class OfficerNode(SimNode):
    """Command-level node grouping multiple units."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_event("order_received", self._on_order_received)

    # ------------------------------------------------------------------
    def _on_order_received(self, _origin: SimNode, _event: str, payload: Dict) -> None:
        """Acknowledge and forward orders to subordinate units."""

        self.emit("order_ack", {"order": payload}, direction="up")
        fwd = dict(payload)
        fwd["issuer_id"] = id(self)
        fwd["recipient_group"] = "units"
        fwd.pop("recipient", None)
        self.emit("order_issued", fwd, direction="up")

    # ------------------------------------------------------------------
    def get_units(self) -> List[SimNode]:
        """Return direct child nodes considered units."""
        return [c for c in self.children if c.__class__.__name__ == "UnitNode"]


register_node_type("OfficerNode", OfficerNode)
