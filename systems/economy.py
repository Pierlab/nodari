"""System handling resource production, consumption and transfers."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type
from nodes.resource import ResourceNode


class EconomySystem(SystemNode):
    """Manage stockpiles and resource exchanges."""

    # ------------------------------------------------------------------
    def produce(self, node: ResourceNode, kind: str, amount: int) -> int:
        """Increase *node* by *amount* of *kind*.

        Returns the actual amount produced and emits ``resource_produced``.
        """

        if node.kind != kind:
            raise ValueError("resource kind mismatch")
        added = node.add(amount)
        if added:
            node.emit("resource_produced", {"kind": kind, "amount": added})
        return added

    # ------------------------------------------------------------------
    def transfer(
        self,
        src: ResourceNode,
        dst: ResourceNode | None,
        kind: str,
        amount: int,
    ) -> int:
        """Move resources from *src* to *dst* or consume them if ``dst`` is ``None``.

        Emits ``resource_consumed`` on the source and ``resource_produced`` on the
        destination. Raises :class:`ValueError` when kinds mismatch, stock is
        insufficient or the destination lacks capacity.
        """

        if src.kind != kind or (dst is not None and dst.kind != kind):
            raise ValueError("resource kind mismatch")
        if src.quantity < amount:
            raise ValueError("insufficient stock")
        src.remove(amount)
        src.emit("resource_consumed", {"kind": kind, "amount": amount})
        if dst is not None:
            added = dst.add(amount)
            if added < amount:
                # roll back both source and destination to maintain conservation
                if added:
                    dst.remove(added)
                src.add(amount)
                raise ValueError("destination lacks capacity")
            dst.emit("resource_produced", {"kind": kind, "amount": added})
        return amount


register_node_type("EconomySystem", EconomySystem)

