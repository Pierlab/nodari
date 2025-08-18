"""Loading utilities for the war simulation."""
from __future__ import annotations

import json
import logging
import math
import os
import random
import pickle
import sys

import config
from core.loader import load_simulation_from_file
from core.plugins import load_plugins

from simulation.war.nodes import (
    ArmyNode,
    BodyguardUnitNode,
    GeneralNode,
    NationNode,
    OfficerNode,
    StrategistNode,
    TerrainNode,
    TransformNode,
    UnitNode,
)
from simulation.war.presets import DEFAULT_SIM_PARAMS
from simulation.war.systems import MovementSystem, PathfindingSystem
from simulation.war.terrain_setup import terrain_regen

logger = logging.getLogger(__name__)

sim_params = dict(DEFAULT_SIM_PARAMS)
sim_params["terrain"] = {}


def load_plugins_for_war() -> None:
    """Load node and system plugins required for the war simulation."""

    load_plugins(
        [
            "nodes.world",
            "nodes.nation",
            "nodes.general",
            "nodes.army",
            "nodes.unit",
            "nodes.terrain",
            "nodes.transform",
            "nodes.strategist",
            "nodes.officer",
            "nodes.bodyguard",
            "systems.movement",
            "systems.combat",
            "systems.moral",
            "systems.pathfinding",
            "systems.victory",
            "systems.time",
            "systems.logger",
        ]
    )


def load_sim_params(path: str) -> dict:
    """Load simulation parameters from *path*."""

    params = dict(DEFAULT_SIM_PARAMS)
    try:
        with open(path, "r", encoding="utf8") as fh:
            data = json.load(fh)
        params.update(data.get("parameters", {}))
    except FileNotFoundError:
        pass
    return params


def setup_world(config_file: str | None = None, settings_file: str | None = None):
    """Load the world and simulation parameters."""

    config_file = config_file or (sys.argv[1] if len(sys.argv) > 1 else "example/war_simulation_config.json")
    world = load_simulation_from_file(config_file)

    terrain_node = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    terrain_params = dict(getattr(terrain_node, "params", {})) if terrain_node else {}
    terrain_params.setdefault("forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5})
    terrain_params.setdefault("mountains", {"total_area_pct": 5, "perlin_scale": 0.01, "peak_density": 0.2})
    terrain_params.setdefault("swamp_desert", {"swamp_pct": 3, "desert_pct": 5, "clumpiness": 0.5})

    pathfinder = next((c for c in world.children if isinstance(c, PathfindingSystem)), None)
    if pathfinder is None:
        pathfinder = PathfindingSystem(parent=world, terrain=terrain_node)

    settings_file = settings_file or (sys.argv[2] if len(sys.argv) > 2 else "example/war_settings.json")
    sim_params.update(load_sim_params(settings_file))
    sim_params["terrain"] = terrain_params
    return world, terrain_node, pathfinder


def _pos_around(cx: float, cy: float, dispersion_radius: float) -> list[float]:
    if dispersion_radius <= 0:
        return [cx, cy]
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, dispersion_radius)
    return [cx + math.cos(angle) * r, cy + math.sin(angle) * r]


def _round_size(size: int, soldiers_per_dot: int) -> int:
    mul = max(1, soldiers_per_dot)
    return max(mul, int(math.ceil(size / mul)) * mul)


def _spawn_armies(
    world,
    dispersion_radius: float,
    soldiers_per_dot: int,
    bodyguard_size: int,
    pathfinder: PathfindingSystem | None = None,
) -> None:
    """Spawn hierarchical armies for each nation."""

    nations = [n for n in world.children if isinstance(n, NationNode)]
    width, height = world.width, world.height
    for nation in nations:
        general = next((c for c in nation.children if isinstance(c, GeneralNode)), None)
        if general is None:
            continue

        transform = next((c for c in general.children if isinstance(c, TransformNode)), None)
        for child in list(general.children):
            if child is not transform:
                general.remove_child(child)
        if transform is None:
            cap = getattr(nation, "capital_position", [width / 2, height / 2])
            transform = TransformNode(position=list(cap))
            general.add_child(transform)
        center = transform.position

        strategist = StrategistNode(name=f"{nation.name}_strategist")
        general.add_child(strategist)

        for i in range(5):
            size = _round_size(bodyguard_size, soldiers_per_dot)
            bg = BodyguardUnitNode(
                name=f"{nation.name}_bodyguard_{i+1}",
                size=size,
                state="idle",
                speed=1.0,
                morale=100,
                vision_radius_m=sim_params.get("vision_radius_m", 100.0),
            )
            bg.add_child(TransformNode(position=_pos_around(*center, dispersion_radius)))
            general.add_child(bg)

        army = ArmyNode(name=f"{nation.name}_army", goal="advance", size=0)
        army.add_child(TransformNode(position=list(center)))
        total_units = 0
        enemies = [n for n in nations if n is not nation]
        target_cap = enemies[0].capital_position if enemies else [width / 2, height / 2]
        unit_size = _round_size(sim_params.get("unit_size", 5), soldiers_per_dot)
        for i in range(5):
            officer = OfficerNode(name=f"{nation.name}_officer_{i+1}")
            officer.add_child(TransformNode(position=_pos_around(*center, dispersion_radius)))
            for j in range(4):
                unit_target = list(target_cap) if i == 0 else None
                unit = UnitNode(
                    name=f"{nation.name}_unit_{i+1}_{j+1}",
                    size=unit_size,
                    state="idle",
                    speed=1.0,
                    morale=100,
                    target=unit_target,
                    vision_radius_m=sim_params.get("vision_radius_m", 100.0),
                )
                pos = _pos_around(*center, dispersion_radius)
                unit.add_child(TransformNode(position=pos))
                if i == 0 and unit_target is not None and pathfinder is not None:
                    start = (int(round(pos[0])), int(round(pos[1])))
                    goal = (int(round(unit_target[0])), int(round(unit_target[1])))
                    path = pathfinder.find_path(start, goal)
                    if len(path) > 1:
                        unit._path = path[1:]
                officer.add_child(unit)
                total_units += 1
            army.add_child(officer)
        army.size = total_units
        general.add_child(army)



def reset_world(world, pathfinder: PathfindingSystem | None = None) -> MovementSystem | None:
    """Reset terrain and spawn armies using current ``sim_params``."""

    cache_path = os.environ.get("WAR_TERRAIN_CACHE")
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as fh:
            data = pickle.load(fh)
        terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
        if terrain is not None:
            terrain.tiles = [bytearray(row) for row in data.get("tiles", [])]
            terrain.obstacles = {tuple(o) for o in data.get("obstacles", [])}
            terrain.altitude_map = data.get("altitude_map")
            terrain.speed_modifiers.update(data.get("speed_modifiers", {}))
            terrain.combat_bonuses.update(data.get("combat_bonuses", {}))
            sim_params["terrain"] = data.get("params", {})
    else:
        terrain_regen(world, sim_params["terrain"])
    _spawn_armies(
        world,
        sim_params["dispersion"],
        sim_params["soldiers_per_dot"],
        sim_params["bodyguard_size"],
        pathfinder,
    )
    movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
    if movement_system:
        movement_system.set_blocking(sim_params.get("movement_blocking", True))
    return movement_system
