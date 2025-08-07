"""Optional transform node storing position and velocity in meters."""
from __future__ import annotations

from typing import List

from core.simnode import SimNode
from core.plugins import register_node_type


class TransformNode(SimNode):
    """Store 2D position and velocity.

    Parameters
    ----------
    position:
        Initial position in meters. Defaults to ``[0.0, 0.0]``.
    velocity:
        Initial velocity in meters per second. Defaults to ``[0.0, 0.0]``.
    """

    def __init__(
        self,
        position: List[float] | None = None,
        velocity: List[float] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.position = position or [0.0, 0.0]
        self.velocity = velocity or [0.0, 0.0]

    def update(self, dt: float) -> None:  # pragma: no cover - simple integration
        """Advance position based on velocity."""
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        super().update(dt)


register_node_type("TransformNode", TransformNode)
