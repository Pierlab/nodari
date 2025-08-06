"""World root node."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class WorldNode(SimNode):
    """Root container of the simulation."""

    def __init__(self, width: int = 100, height: int = 100, **kwargs) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height


register_node_type("WorldNode", WorldNode)
