import json
import pygame
from pathlib import Path

import pytest

from core.loader import load_simulation_from_file
from tools.map_editor import export, load_key_mapping
from nodes.world import WorldNode
from nodes.transform import TransformNode  # noqa: F401
from nodes.house import HouseNode
from nodes.barn import BarnNode
import config


def test_export_and_reload_buildings(tmp_path: Path) -> None:
    buildings = []
    rects = [
        pygame.Rect(0, 0, 10, 20),
        pygame.Rect(25, 15, 30, 40),
    ]
    types = ["HouseNode", "BarnNode"]
    for rect, btype in zip(rects, types):
        buildings.append((rect, btype))

    path = tmp_path / "map.json"
    export(buildings, path)
    root = load_simulation_from_file(str(path))

    assert isinstance(root, WorldNode)
    assert len(root.children) == len(buildings)

    for (rect, btype), node in zip(buildings, root.children):
        expected_cls = HouseNode if btype == "HouseNode" else BarnNode
        assert isinstance(node, expected_cls)
        expected_pos = [rect.x // config.SCALE, rect.y // config.SCALE]
        assert node.position == expected_pos
        expected_width = rect.width // config.SCALE
        expected_height = rect.height // config.SCALE
        assert node.width == expected_width
        assert node.height == expected_height


def test_export_rejects_negative_coordinates(tmp_path: Path) -> None:
    buildings = [(pygame.Rect(-10, 0, 10, 20), "HouseNode")]
    with pytest.raises(ValueError):
        export(buildings, tmp_path / "map.json")


def test_export_rejects_out_of_bounds(tmp_path: Path) -> None:
    out_x = config.WORLD_WIDTH * config.SCALE + 1
    buildings = [(pygame.Rect(out_x, 0, 10, 20), "BarnNode")]
    with pytest.raises(ValueError):
        export(buildings, tmp_path / "map.json")


def test_export_rejects_non_positive_size(tmp_path: Path) -> None:
    buildings = [(pygame.Rect(0, 0, 0, 10), "HouseNode")]
    with pytest.raises(ValueError):
        export(buildings, tmp_path / "map.json")


def test_load_key_mapping_from_dict() -> None:
    pygame.init()
    mapping = load_key_mapping({"1": "HouseNode", "2": "BarnNode"})
    assert mapping[pygame.K_1] == "HouseNode"
    assert mapping[pygame.K_2] == "BarnNode"
    pygame.quit()


def test_load_key_mapping_from_file(tmp_path: Path) -> None:
    data = {"1": "HouseNode"}
    path = tmp_path / "keys.json"
    path.write_text(json.dumps(data))
    pygame.init()
    mapping = load_key_mapping(str(path))
    assert mapping[pygame.K_1] == "HouseNode"
    pygame.quit()


def test_load_key_mapping_invalid_type() -> None:
    pygame.init()
    with pytest.raises(KeyError):
        load_key_mapping({"1": "UnknownNode"})
    pygame.quit()
