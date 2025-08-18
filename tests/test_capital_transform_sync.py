from pathlib import Path
import json

def test_north_capital_and_transform_match_center():
    config_path = Path(__file__).resolve().parents[1] / "example" / "war_simulation_config.json"
    with config_path.open(encoding="utf8") as fh:
        data = json.load(fh)
    world = data["war_world"]
    width = world["config"]["width"]
    height = world["config"]["height"]
    center = [width // 2, height // 2]

    north = next(child for child in world["children"] if child.get("id") == "north")
    assert north["config"]["capital_position"] == center

    general = next(child for child in north["children"] if child.get("id") == "north_general")
    transform = next(child for child in general["children"] if child.get("type") == "TransformNode")
    assert transform["config"]["position"] == center
