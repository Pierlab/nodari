"""Resource node representing a stockpile of materials."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class ResourceNode(SimNode):
    """Track the quantity of a single resource type.

    Parameters
    ----------
    kind:
        Type of resource stored (e.g., ``"wood"``, ``"grain"``).
    quantity:
        Current amount of the resource.
    max_quantity:
        Maximum capacity for the resource.
    """

    def __init__(self, kind: str, quantity: int = 0, max_quantity: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kind = kind
        self.quantity = quantity
        self.max_quantity = max_quantity

    # ------------------------------------------------------------------
    def add(self, amount: int) -> int:
        """Add ``amount`` to the stockpile and return the added amount."""

        if amount < 0:
            raise ValueError("amount must be non-negative")
        space = self.max_quantity - self.quantity
        added = min(space, amount) if self.max_quantity else amount
        self.quantity += added
        return added

    # ------------------------------------------------------------------
    def remove(self, amount: int) -> int:
        """Remove up to ``amount`` from the stockpile and return removed."""

        if amount < 0:
            raise ValueError("amount must be non-negative")
        removed = min(self.quantity, amount)
        self.quantity -= removed
        return removed


register_node_type("ResourceNode", ResourceNode)
