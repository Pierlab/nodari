"""Unit node representing a group of soldiers."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class UnitNode(SimNode):
    """Represent a unit group with morale, speed and state.

    Parameters
    ----------
    size:
        Number of soldiers in this unit.
    state:
        Current state of the unit: ``"idle"``, ``"moving"``, ``"fighting"`` or ``"fleeing"``.
    speed:
        Movement speed of the unit.
    morale:
        Morale value of the unit.
    target:
        Optional ``[x, y]`` coordinates the unit is moving toward.
    """

    def __init__(
        self,
        size: int = 100,
        state: str = "idle",
        speed: float = 1.0,
        morale: int = 100,
        target: list[int] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.size = size
        self.state = state
        self.speed = speed
        self.morale = morale
        self.target = target

    # ------------------------------------------------------------------
    def engage(self, enemy: str | SimNode | None = None) -> None:
        """Set state to ``fighting`` and emit ``unit_engaged``."""

        self.state = "fighting"
        payload = {"enemy": enemy} if enemy is not None else {}
        self.emit("unit_engaged", payload, direction="up")

    # ------------------------------------------------------------------
    def route(self, loss: int = 1) -> None:
        """Set state to ``fleeing`` and emit ``unit_routed`` with *loss*."""

        self.state = "fleeing"
        self.emit("unit_routed", {"loss": loss}, direction="up")


register_node_type("UnitNode", UnitNode)
