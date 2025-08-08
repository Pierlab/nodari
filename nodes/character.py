"""Composite character node."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class CharacterNode(SimNode):
    """Node representing a character (farmer)."""

    def __init__(self, gender: str = "male", **kwargs) -> None:
        super().__init__(**kwargs)
        self.gender = gender


register_node_type("CharacterNode", CharacterNode)
