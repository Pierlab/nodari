"""Farm node composed of inventory and producer."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class FarmNode(SimNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


register_node_type("FarmNode", FarmNode)
