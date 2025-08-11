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


def test_map_editor_export_types(tmp_path: Path):
    import pygame
    from tools.map_editor import export
    from nodes.barn import BarnNode
    from nodes.house import HouseNode
    from nodes.pasture import PastureNode
    from nodes.silo import SiloNode
    from nodes.warehouse import WarehouseNode
    from nodes.well import WellNode
    from nodes.transform import TransformNode  # noqa: F401
    import config

    types = [
        ("HouseNode", HouseNode),
        ("BarnNode", BarnNode),
        ("SiloNode", SiloNode),
        ("PastureNode", PastureNode),
        ("WellNode", WellNode),
        ("WarehouseNode", WarehouseNode),
    ]
    buildings = []
    for i, (name, _) in enumerate(types):
        rect = pygame.Rect(i * 10, 0, 10, 10)
        buildings.append((rect, name))
    path = tmp_path / "map.json"
    export(buildings, path)
    root = load_simulation_from_file(str(path))
    assert isinstance(root, WorldNode)
    for i, (node, (_, cls)) in enumerate(zip(root.children, types)):
        assert isinstance(node, cls)
        expected_x = (i * 10) // config.SCALE
        assert node.position == [expected_x, 0]
        expected_size = 10 // config.SCALE
        assert node.width == expected_size
        assert node.height == expected_size
