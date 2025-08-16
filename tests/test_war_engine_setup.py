import json

from core.loader import load_simulation_from_file
from nodes.world import WorldNode  # ensure plugin registration
from systems.time import TimeSystem


def test_war_engine_setup(tmp_path):
    config = {
        "war_world": {
            "type": "WorldNode",
            "children": [
                {"type": "TimeSystem", "id": "time"}
            ],
        }
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    world = load_simulation_from_file(str(config_path))
    assert isinstance(world, WorldNode)

    time_system = next(child for child in world.children if isinstance(child, TimeSystem))
    ticks: list[int] = []
    time_system.on_event("tick", lambda _o, _e, payload: ticks.append(payload["tick"]))

    world.update(1.0)
    assert ticks == [1]
