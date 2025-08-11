import json
from pathlib import Path

import config
from core.loader import load_simulation_from_file
from nodes.well import WellNode
import pytest


def test_loader_applies_class_defaults(tmp_path: Path):
    data = {
        "world": {
            "type": "WorldNode",
            "children": [
                {"type": "WellNode", "id": "well", "config": {}}
            ],
        }
    }
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps(data))
    root = load_simulation_from_file(str(path))
    well = root.children[0]
    assert well.width == config.BUILDING_SIZE
    assert well.height == config.BUILDING_SIZE


def test_well_validation():
    with pytest.raises(ValueError):
        WellNode(width=0, height=10)
