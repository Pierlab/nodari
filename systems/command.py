"""System managing propagation of military orders with delays and reliability."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.transform import TransformNode
from nodes.officer import OfficerNode
from nodes.unit import UnitNode


@dataclass
class _PendingOrder:
    deliver_at: float
    order: Dict
    recipient: SimNode


class CommandSystem(SystemNode):
    """Handle command dispatching with delays and potential loss."""

    def __init__(
        self,
        *,
        base_delay_s: float = 0.0,
        distance_delay_factor: float = 0.0,
        reliability: float = 1.0,
        rng: random.Random | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.base_delay_s = base_delay_s
        self.distance_delay_factor = distance_delay_factor
        self.reliability = reliability
        self._rng = rng or random
        self._time = 0.0
        self._pending: List[_PendingOrder] = []
        self.on_event("order_issued", self._on_order_issued)

    # ------------------------------------------------------------------
    def _on_order_issued(self, origin: SimNode, _event: str, order: Dict) -> None:
        recipients = self._resolve_recipients(origin, order)
        if not recipients:
            return
        for recipient in recipients:
            if self._rng.random() > self.reliability:
                continue  # order lost
            delay = self._compute_delay(origin, recipient)
            order = dict(order)
            order.setdefault("issuer_id", id(origin))
            order.setdefault("recipient_id", id(recipient))
            order.setdefault("time_issued", time.time())
            order["recipient"] = recipient
            self._pending.append(
                _PendingOrder(self._time + delay, order, recipient)
            )

    # ------------------------------------------------------------------
    def _resolve_recipients(self, issuer: SimNode, order: Dict) -> List[SimNode]:
        if recipient := order.get("recipient"):
            return [recipient]
        group = order.get("recipient_group")
        if group == "officers":
            officers: List[SimNode] = []
            self._collect_officers(issuer, officers)
            return officers
        if group == "units":
            units: List[SimNode] = []
            self._collect_units(issuer, units)
            return units
        return []

    def _collect_units(self, node: SimNode, out: List[SimNode]) -> None:
        for child in node.children:
            if isinstance(child, UnitNode):
                out.append(child)
            self._collect_units(child, out)

    def _collect_officers(self, node: SimNode, out: List[SimNode]) -> None:
        for child in node.children:
            if isinstance(child, OfficerNode):
                out.append(child)
            self._collect_officers(child, out)

    # ------------------------------------------------------------------
    def _compute_delay(self, a: SimNode, b: SimNode) -> float:
        transform_a = self._get_transform(a)
        transform_b = self._get_transform(b)
        if not transform_a or not transform_b:
            return self.base_delay_s
        ax, ay = transform_a.position
        bx, by = transform_b.position
        dist = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
        return self.base_delay_s + dist * self.distance_delay_factor

    def _get_transform(self, node: SimNode) -> TransformNode | None:
        if isinstance(node, TransformNode):
            return node
        for child in node.children:
            if isinstance(child, TransformNode):
                return child
        return None

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self._time += dt
        to_deliver = [p for p in self._pending if p.deliver_at <= self._time]
        self._pending = [p for p in self._pending if p.deliver_at > self._time]
        for pending in to_deliver:
            pending.recipient.emit("order_received", pending.order, direction="down")
        super().update(dt)


register_node_type("CommandSystem", CommandSystem)
