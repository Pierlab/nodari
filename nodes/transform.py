"""Optional transform node storing position."""
from __future__ import annotations

from typing import List

from core.simnode import SimNode
from core.plugins import register_node_type


class TransformNode(SimNode):
    """Store 2D position."""

    def __init__(self, position: List[float] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.position = position or [0.0, 0.0]


register_node_type("TransformNode", TransformNode)
