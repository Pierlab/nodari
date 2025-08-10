"""Silo node for storing harvested crops."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class SiloNode(SimNode):
    """Tall structure storing bulk goods like grain."""

    def __init__(
        self,
        capacity: int | None = None,
        width: int | None = None,
        height: int | None = None,
        position: list[int] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.capacity = capacity
        self.width = width
        self.height = height
        self.position = position or [0, 0]


register_node_type("SiloNode", SiloNode)

