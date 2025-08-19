"""Loading utilities for the war simulation."""
from __future__ import annotations

import json
import logging
import os
import pickle
import sys

import config
from core.loader import load_simulation_from_file
from core.plugins import load_plugins

from simulation.war.nodes import (
    GeneralNode,
    NationNode,
    StrategistNode,
    TerrainNode,
    TransformNode,
)
from nodes.builder import BuilderNode
from systems.ai import AISystem
from systems.scheduler import SchedulerSystem
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
            "nodes.building",
            "nodes.resource",
            "nodes.builder",
            "nodes.worker",
            "systems.movement",
            "systems.combat",
            "systems.moral",
            "systems.pathfinding",
            "systems.victory",
            "systems.time",
            "systems.logger",
            "systems.scheduler",
            "systems.ai",
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

    config_file = config_file or "example/flat_1km_config.json"
    world = load_simulation_from_file(config_file)

    ai = AISystem(
        parent=world,
        capital_min_radius=sim_params.get("capital_min_radius", 0),
        city_influence_radius=sim_params.get("city_influence_radius", 0),
        build_duration=sim_params.get("build_duration", 0.0),
        unit_speed=sim_params.get("unit_speed", 1.0),
    )

    # Ensure a SchedulerSystem is present so that newly spawned workers can be
    # registered for periodic updates. If one is already defined in the config
    # file it is reused, otherwise we create it here.
    if not any(isinstance(c, SchedulerSystem) for c in world.children):
        SchedulerSystem(parent=world)


    terrain_node = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    terrain_params = dict(getattr(terrain_node, "params", {})) if terrain_node else {}
    terrain_params.setdefault("forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5})
    terrain_params.setdefault("mountains", {"total_area_pct": 5, "perlin_scale": 0.01, "peak_density": 0.2})
    terrain_params.setdefault("swamp_desert", {"swamp_pct": 3, "desert_pct": 5, "clumpiness": 0.5})

    movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
    pathfinder = next((c for c in world.children if isinstance(c, PathfindingSystem)), None)
    if pathfinder is None:
        pathfinder = PathfindingSystem(parent=world, terrain=terrain_node)

    settings_file = settings_file or (
        sys.argv[2] if len(sys.argv) > 2 else "example/war_settings.json"
    )
    sim_params.update(load_sim_params(settings_file))
    sim_params["terrain"] = terrain_params

    world.width = sim_params.get("map_width", world.width)
    world.height = sim_params.get("map_height", world.height)
    terrain_regen(world, terrain_params)

    ai.city_influence_radius = sim_params.get("city_influence_radius", 0)
    ai.builder_spawn_interval = sim_params.get("builder_spawn_interval", 0.0)
    ai.build_duration = sim_params.get("build_duration", 0.0)
    ai.unit_speed = sim_params.get("unit_speed", ai.unit_speed)

    if movement_system:
        movement_system.set_blocking(sim_params.get("movement_blocking", True))
        movement_system.wander_drift = sim_params.get(
            "wander_drift", movement_system.wander_drift
        )
        movement_system.wander_speed = sim_params.get(
            "unit_speed", movement_system.wander_speed
        )

    for nation in [n for n in world.children if isinstance(n, NationNode)]:
        nation.city_influence_radius = sim_params.get("city_influence_radius", 0)


    return world, terrain_node, pathfinder


def spawn_builder(world) -> BuilderNode | None:
    """Spawn a :class:`BuilderNode` at the capital of the main nation."""

    nation = next((c for c in world.children if isinstance(c, NationNode)), None)
    if nation is None:
        return None

    capital = getattr(nation, "capital_position", [world.width / 2, world.height / 2])
    count = sum(1 for c in nation.children if isinstance(c, BuilderNode))
    builder = BuilderNode(
        name=f"{nation.name}_builder_{count + 1}",
        state="exploring",
        speed=sim_params.get("unit_speed", 1.0),
        morale=100,
        build_duration=sim_params.get("build_duration", 0.0),
    )
    builder.add_child(TransformNode(position=list(capital)))
    nation.add_child(builder)
    builder.emit("unit_idle", {}, direction="up")
    return builder


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

        for child in list(nation.children):
            if isinstance(child, BuilderNode):
                nation.remove_child(child)

        for i in range(3):
            builder = BuilderNode(
                name=f"{nation.name}_builder_{i+1}",
                state="exploring",
                speed=sim_params.get("unit_speed", 1.0),
                morale=100,
                build_duration=sim_params.get("build_duration", 0.0),
            )
            builder.add_child(TransformNode(position=list(center)))
            nation.add_child(builder)
            builder.emit("unit_idle", {}, direction="up")



def reset_world(world, pathfinder: PathfindingSystem | None = None) -> MovementSystem | None:
    """Reset terrain using current ``sim_params`` without spawning armies."""

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
    # Armies are no longer spawned automatically to start with an empty world
    movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
    if movement_system:
        movement_system.set_blocking(sim_params.get("movement_blocking", True))
        movement_system.wander_drift = sim_params.get("wander_drift", movement_system.wander_drift)
        movement_system.wander_speed = sim_params.get(
            "unit_speed", sim_params.get("wander_speed", movement_system.wander_speed)
        )
    return movement_system
