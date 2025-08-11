import json
from pathlib import Path

import pytest

from core.loader import load_simulation_from_file
from core.schema import ValidationError
from nodes.world import WorldNode  # ensure plugin registration


def test_missing_type_raises_validation_error(tmp_path: Path) -> None:
    config = {"world": {"config": {}}}
    path = tmp_path / "world.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValidationError):
        load_simulation_from_file(str(path))


def test_multiple_roots_raises_validation_error(tmp_path: Path) -> None:
    config = {
        "world": {"type": "WorldNode"},
        "other": {"type": "WorldNode"},
    }
    path = tmp_path / "world.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValidationError):
        load_simulation_from_file(str(path))

