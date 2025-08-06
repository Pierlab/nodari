"""Time management system."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type


class TimeSystem(SystemNode):
    """Emit a `tick` event every update and handle day/night phases."""

    def __init__(self, tick_duration: float = 1.0, phase_length: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tick_duration = tick_duration
        self.phase_length = phase_length
        self.current_tick = 0
        self.phase = 0

    def update(self, dt: float) -> None:
        self.current_tick += 1
        self.emit("tick", {"tick": self.current_tick}, direction="down")
        new_phase = (self.current_tick // self.phase_length) % 2
        if new_phase != self.phase:
            self.phase = new_phase
            self.emit("phase_changed", {"phase": self.phase}, direction="down")


register_node_type("TimeSystem", TimeSystem)
