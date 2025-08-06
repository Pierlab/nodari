import json
from pathlib import Path

from core.loader import load_simulation_from_file
from nodes.inventory import InventoryNode
from nodes.world import WorldNode


def test_load_json(tmp_path: Path):
    config = {
        "world": {
            "type": "WorldNode",
            "config": {"width": 50, "height": 50},
            "children": [
                {"type": "InventoryNode", "id": "inv", "config": {"items": {"wheat": 1}}}
            ],
        }
    }
    cfg_path = tmp_path / "world.json"
    cfg_path.write_text(json.dumps(config))
    root = load_simulation_from_file(str(cfg_path))
    assert isinstance(root, WorldNode)
    assert isinstance(root.children[0], InventoryNode)
    assert root.children[0].items["wheat"] == 1
