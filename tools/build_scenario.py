"""Utilities to turn a map layout into a runnable scenario.

Currently only a *farm* profile is provided but additional profiles can be
added to :data:`SCENARIOS` to support other genres such as quests or battles.
"""

import json
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class ScenarioProfile:
    """Defines extra nodes injected when building a scenario."""

    inventory_buildings: Iterable[str]
    system_nodes: List[dict]


SCENARIOS: Dict[str, ScenarioProfile] = {
    "farm": ScenarioProfile(
        inventory_buildings={
            "HouseNode",
            "BarnNode",
            "SiloNode",
            "PastureNode",
            "FarmNode",
            "WellNode",
            "WarehouseNode",
        },
        system_nodes=[
            {"type": "TimeSystem"},
            {"type": "EconomySystem"},
            {"type": "LoggingSystem"},
            {"type": "DistanceSystem"},
            {"type": "PygameViewerSystem"},
        ],
    )
}


def build(map_file: str, output: str, scenario: str = "farm") -> None:
    """Combine a layout exported from the map editor with scenario extras.

    Parameters
    ----------
    map_file:
        Path to the JSON file produced by ``map_editor.py``.
    output:
        Location where the enriched scenario should be written.
    scenario:
        Key of the scenario profile to apply.
    """

    profile = SCENARIOS.get(scenario)
    if profile is None:
        raise ValueError(f"Unknown scenario profile: {scenario}")

    with open(map_file, "r", encoding="utf8") as fh:
        data = json.load(fh)

    world = data["world"]
    children = world.setdefault("children", [])

    for node in children:
        if node.get("type") in profile.inventory_buildings:
            inv_id = f"{node.get('id', 'node')}_inventory"
            node.setdefault("children", []).append(
                {"type": "InventoryNode", "id": inv_id, "config": {"items": {}}}
            )

    children.extend(profile.system_nodes)

    with open(output, "w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)

    print(f"Wrote {scenario} scenario to {output}")


if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "custom_map.json"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "scenario.json"
    scenario = sys.argv[3] if len(sys.argv) > 3 else "farm"
    build(in_file, out_file, scenario)
