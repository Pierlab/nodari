"""Building node representing structures in the simulation."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class BuildingNode(SimNode):
    """Represent a building such as a farm or warehouse.

    Parameters
    ----------
    type:
        Type of building (e.g., ``"farm"``, ``"warehouse"``).
    capacity:
        Maximum capacity of units or resources handled by the building.
    hit_points:
        Structural durability used in combat interactions.
    strategic:
        When ``True`` the loss of this building can trigger defeat
        conditions.
    """

    def __init__(
        self,
        type: str,
        capacity: int = 0,
        hit_points: int = 100,
        strategic: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.type = type
        self.capacity = capacity
        self.hit_points = hit_points
        self.strategic = strategic


register_node_type("BuildingNode", BuildingNode)
