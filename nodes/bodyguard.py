"""Bodyguard unit specializing in protecting a general."""
from __future__ import annotations

from nodes.unit import UnitNode
from core.plugins import register_node_type


class BodyguardUnitNode(UnitNode):
    """Small elite unit dedicated to protecting a general."""

    def __init__(self, size: int = 5, **kwargs) -> None:
        super().__init__(size=size, **kwargs)


register_node_type("BodyguardUnitNode", BodyguardUnitNode)
