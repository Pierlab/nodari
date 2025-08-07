import random

from nodes.world import WorldNode
from systems.weather import WeatherSystem


def test_weather_emits_changes():
    random.seed(0)
    world = WorldNode(name="world")
    weather = WeatherSystem(states=["sunny", "rain"], change_interval=1.0, parent=world)
    changes = []
    world.on_event("weather_changed", lambda _e, _n, p: changes.append(p["state"]))

    for _ in range(5):
        world.update(1.0)

    assert len(changes) >= 1
    assert weather.current_state in ["sunny", "rain"]
