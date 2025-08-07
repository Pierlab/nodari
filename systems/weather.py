"""Simple weather system emitting weather change events."""
from __future__ import annotations

import random
from typing import List

from core.simnode import SystemNode
from core.plugins import register_node_type


class WeatherSystem(SystemNode):
    """Cycle through weather states and emit events on change."""

    def __init__(
        self,
        states: List[str] | None = None,
        change_interval: float = 3600.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.states = states or ["sunny", "rainy"]
        self.change_interval = change_interval
        self.current_state = random.choice(self.states)
        self._acc = 0.0

    def update(self, dt: float) -> None:
        self._acc += dt
        if self._acc >= self.change_interval:
            self._acc -= self.change_interval
            state = random.choice(self.states)
            if state != self.current_state:
                self.current_state = state
                self.emit("weather_changed", {"state": state})
        super().update(dt)


register_node_type("WeatherSystem", WeatherSystem)
