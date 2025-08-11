"""Well node producing water."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type
import config


class WellNode(SimNode):
    """Simple well where characters can collect water."""

    DEFAULT_CONFIG = {"width": config.BUILDING_SIZE, "height": config.BUILDING_SIZE}

    def __init__(
        self,
        width: int = DEFAULT_CONFIG["width"],
        height: int = DEFAULT_CONFIG["height"],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self.width = width
        self.height = height


register_node_type("WellNode", WellNode)
