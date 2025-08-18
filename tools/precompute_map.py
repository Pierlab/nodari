"""Generate and cache terrain for the war simulation."""
from __future__ import annotations

import os
import pickle
import sys

# Allow running as a script from the repository root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from simulation.war.war_loader import load_plugins_for_war, setup_world, sim_params
from simulation.war.terrain_setup import terrain_regen


def main(path: str = "terrain_cache.pkl") -> None:
    """Generate terrain and store it in *path*."""

    load_plugins_for_war()
    world, terrain, _ = setup_world()
    terrain_regen(world, sim_params["terrain"])
    data = {
        "tiles": [bytes(row) for row in terrain.tiles],
        "obstacles": list(terrain.obstacles),
        "altitude_map": terrain.altitude_map,
        "speed_modifiers": terrain.speed_modifiers,
        "combat_bonuses": terrain.combat_bonuses,
        "params": sim_params["terrain"],
    }
    with open(path, "wb") as fh:
        pickle.dump(data, fh)
    print(f"Terrain cache written to {path}")


if __name__ == "__main__":  # pragma: no cover - script utility
    output = sys.argv[1] if len(sys.argv) > 1 else "terrain_cache.pkl"
    main(output)
