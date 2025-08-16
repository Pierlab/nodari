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
    retreat_threshold:
        Morale value below which the unit will retreat toward its nation's
        capital.
    """

    def __init__(
        self,
        size: int = 100,
        state: str = "idle",
        speed: float = 1.0,
        morale: int = 100,
        target: list[int] | None = None,
        retreat_threshold: int = 30,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.size = size
        self.state = state
        self.speed = speed
        self.morale = morale
        self.target = target
        self.retreat_threshold = retreat_threshold

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
        home = self._get_home_position()
        if home is not None:
            self.target = list(home)
        self.emit("unit_routed", {"loss": loss}, direction="up")

    # ------------------------------------------------------------------
    def _get_home_position(self) -> list[int] | None:
        """Return the capital position of the owning nation if available."""

        cur = self.parent
        while cur is not None:
            if cur.__class__.__name__ == "NationNode":
                return getattr(cur, "capital_position", None)
            cur = cur.parent
        return None

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Check morale and initiate retreat if it falls too low."""

        if self.morale < self.retreat_threshold and self.state != "fleeing":
            # no loss when retreating due to low morale
            self.route(loss=0)
        super().update(dt)


register_node_type("UnitNode", UnitNode)
