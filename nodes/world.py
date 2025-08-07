"""World root node."""
from __future__ import annotations

import random

from core.simnode import SimNode
from core.plugins import register_node_type


class WorldNode(SimNode):
    """Root container of the simulation.

    Parameters
    ----------
    width:
        Width of the world map.
    height:
        Height of the world map.
    seed:
        Optional seed for global random number generation to make
        simulations deterministic.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 100,
        seed: int | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)


register_node_type("WorldNode", WorldNode)
