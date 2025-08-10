"""Simple house node."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class HouseNode(SimNode):
    """Represents a house where characters live and store resources."""
    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        position: list[int] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.position = position or [0, 0]


register_node_type("HouseNode", HouseNode)
