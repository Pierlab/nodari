import json
import sys

INVENTORY_BUILDINGS = {
    "HouseNode",
    "BarnNode",
    "SiloNode",
    "PastureNode",
    "FarmNode",
    "WellNode",
    "WarehouseNode",
}

SYSTEM_NODES = [
    {"type": "TimeSystem"},
    {"type": "EconomySystem"},
    {"type": "LoggingSystem"},
    {"type": "DistanceSystem"},
    {"type": "PygameViewerSystem"},
]

def build(map_file: str, output: str) -> None:
    with open(map_file, "r", encoding="utf8") as fh:
        data = json.load(fh)
    world = data["world"]
    children = world.setdefault("children", [])
    for node in children:
        if node.get("type") in INVENTORY_BUILDINGS:
            inv_id = f"{node.get('id', 'node')}_inventory"
            node.setdefault("children", []).append(
                {"type": "InventoryNode", "id": inv_id, "config": {"items": {}}}
            )
    children.extend(SYSTEM_NODES)
    with open(output, "w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Wrote farm scenario to {output}")

if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "custom_map.json"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "farm_scenario.json"
    build(in_file, out_file)
