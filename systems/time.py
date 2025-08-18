"""Time management system."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type


class TimeSystem(SystemNode):
    """Emit a `tick` event based on elapsed time and track the day cycle.

    All durations are expressed in **seconds**. The system supports time
    scaling to run simulations in real time or at an accelerated pace.
    """

    def __init__(
        self,
        tick_duration: float = 1.0,
        phase_length: int = 10,
        start_time: float = 0.0,
        time_scale: float = 1.0,
        **kwargs,
    ) -> None:
        """Parameters
        ----------
        tick_duration:
            Interval in seconds between emitted ``tick`` events.
        phase_length:
            Number of ticks that make up a day phase (e.g. day/night).
        start_time:
            Simulation start time in seconds since the beginning of the day.
        time_scale:
            Multiplier applied to ``dt`` to accelerate or slow down time.
        """

        super().__init__(**kwargs)
        self.tick_duration = tick_duration
        self.phase_length = phase_length
        self.current_tick = 0
        self.phase = 0
        self.current_time = start_time  # seconds since start of day
        self._accumulator = 0.0
        self.day_length = 24 * 3600.0
        self.time_scale = time_scale

    def update(self, dt: float) -> None:
        """Advance the simulation clock by ``dt`` seconds."""

        self._accumulator += dt * self.time_scale
        while self._accumulator >= self.tick_duration:
            self._accumulator -= self.tick_duration
            self.current_tick += 1
            self.current_time = (self.current_time + self.tick_duration) % self.day_length
            self.emit("tick", {"tick": self.current_tick}, direction="down")
            new_phase = (self.current_tick // self.phase_length) % 2
            if new_phase != self.phase:
                self.phase = new_phase
                self.emit("phase_changed", {"phase": self.phase}, direction="down")

    def set_time_scale(self, scale: float) -> None:
        """Set a new time scale to accelerate or slow the simulation."""
        self.time_scale = scale


register_node_type("TimeSystem", TimeSystem)
