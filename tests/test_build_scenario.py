from tools.build_scenario import build
import json
import tempfile
import os

def test_build_adds_systems_and_inventories(tmp_path):
    data = {
        "world": {
            "type": "WorldNode",
            "config": {"width": 10, "height": 10},
            "children": [
                {
                    "type": "HouseNode",
                    "id": "building1",
                    "config": {"width": 1, "height": 1},
                    "children": [
                        {"type": "TransformNode", "config": {"position": [0, 0]}}
                    ],
                }
            ],
        }
    }
    src = tmp_path / "map.json"
    out = tmp_path / "scenario.json"
    src.write_text(json.dumps(data))
    build(str(src), str(out), scenario="farm")
    result = json.loads(out.read_text())
    children = result["world"]["children"]
    house = next(c for c in children if c["type"] == "HouseNode")
    assert any(c["type"] == "InventoryNode" for c in house["children"])
    system_types = {c["type"] for c in children if c["type"].endswith("System")}
    assert {"TimeSystem", "EconomySystem", "LoggingSystem", "DistanceSystem", "PygameViewerSystem"} <= system_types


def test_build_war_km_scenario(tmp_path):
    data = {"world": {"type": "WorldNode", "children": []}}
    src = tmp_path / "map.json"
    out = tmp_path / "scenario.json"
    src.write_text(json.dumps(data))
    build(str(src), str(out), scenario="war_km")
    result = json.loads(out.read_text())
    children = result["world"]["children"]
    system_types = {c["type"] for c in children if c["type"].endswith("System")}
    assert {
        "TimeSystem",
        "MovementSystem",
        "CombatSystem",
        "MoralSystem",
        "VictorySystem",
        "CommandSystem",
        "VisibilitySystem",
        "PathfindingSystem",
        "LoggingSystem",
        "PygameViewerSystem",
    } <= system_types
