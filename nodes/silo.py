"""Silo node for storing harvested crops."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class SiloNode(SimNode):
    """Tall structure storing bulk goods like grain."""

    def __init__(self, capacity: int | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.capacity = capacity


register_node_type("SiloNode", SiloNode)

