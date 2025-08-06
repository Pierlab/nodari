"""Time management system."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type


class TimeSystem(SystemNode):
    """Emit ``tick`` events and manage day/night phases.

    The system now models a 24h cycle.  Each call to :meth:`update` accumulates
    ``dt`` until ``tick_duration`` is reached, at which point the current hour is
    incremented and a ``tick`` event is emitted with the hour of the day.  After
    ``phase_length`` hours the day/night phase toggles and a ``phase_changed``
    event is emitted.
    """

    def __init__(self, tick_duration: float = 1.0, phase_length: int = 12, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tick_duration = tick_duration
        self.phase_length = phase_length
        self.current_tick = 0
        self.phase = 0
        self.day = 0
        self._accum = 0.0

    def update(self, dt: float) -> None:
        self._accum += dt
        while self._accum >= self.tick_duration:
            self._accum -= self.tick_duration
            self.current_tick += 1
            hour = self.current_tick % (2 * self.phase_length)
            if hour == 0 and self.current_tick > 0:
                self.day += 1
            self.emit("tick", {"tick": hour, "day": self.day}, direction="down")
            new_phase = (hour // self.phase_length) % 2
            if new_phase != self.phase:
                self.phase = new_phase
                self.emit("phase_changed", {"phase": self.phase}, direction="down")
        super().update(dt)


register_node_type("TimeSystem", TimeSystem)
