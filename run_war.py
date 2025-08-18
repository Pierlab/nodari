"""Run the war simulation with a visual Pygame window."""

from __future__ import annotations

import os
import sys
import random
import math
import time
import logging
import json

import pygame

import config

from core.loader import load_simulation_from_file
from core.plugins import load_plugins
from nodes.army import ArmyNode
from nodes.general import GeneralNode
from nodes.nation import NationNode
from nodes.transform import TransformNode
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from nodes.strategist import StrategistNode
from nodes.officer import OfficerNode
from nodes.bodyguard import BodyguardUnitNode
from tools.terrain_generators import (
    carve_river,
    generate_base,
    place_forest,
    place_lake,
    place_mountains,
    place_swamp_desert,
)
from systems.movement import MovementSystem
from systems.logger import LoggingSystem
from systems.pygame_viewer import PygameViewerSystem
from systems.time import TimeSystem
from systems.command import CommandSystem
from systems.visibility import VisibilitySystem
from systems.pathfinding import PathfindingSystem


DEFAULT_SIM_PARAMS = {
    "dispersion": 200.0,
    "unit_size": 5,
    "soldiers_per_dot": 5,
    "bodyguard_size": 5,
    "vision_radius_m": 100.0,
    "visibility": True,
    "command_delay": 0.0,
    "movement_blocking": True,
}


def load_sim_params(path: str) -> dict:
    """Load simulation parameters from *path*.

    The file is expected to contain a top-level ``parameters`` mapping. Values
    are merged with :data:`DEFAULT_SIM_PARAMS` so missing entries fall back to
    sensible defaults.
    """

    params = dict(DEFAULT_SIM_PARAMS)
    try:
        with open(path, "r", encoding="utf8") as fh:
            data = json.load(fh)
        params.update(data.get("parameters", {}))
    except FileNotFoundError:
        pass
    return params


RUN_WAR_IMPORT_ONLY = os.environ.get("RUN_WAR_IMPORT_ONLY") == "1"

if not RUN_WAR_IMPORT_ONLY:
    # Ensure pygame can be used even when no display is available
    if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    try:
        pygame.init()
    except pygame.error as exc:  # pragma: no cover - environment-specific
        print(f"Unable to initialize pygame: {exc}")
        sys.exit(1)

    # Load all plugins required for the war simulation
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
            "systems.time",
            "systems.movement",
            "systems.combat",
            "systems.moral",
            "systems.victory",
            "systems.logger",
            "systems.pygame_viewer",
        ]
    )

    # Disable all logging to keep the console quiet
    logging.basicConfig(level=logging.CRITICAL)
    logging.disable(logging.CRITICAL)
    logger = logging.getLogger(__name__)

    # Load the simulation from a JSON/YAML file
    config_file = sys.argv[1] if len(sys.argv) > 1 else "example/war_simulation_config.json"
    world = load_simulation_from_file(config_file)

    terrain_node = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain_node is not None:
        terrain_params = dict(getattr(terrain_node, "params", {}))
    else:
        terrain_params = {}

    terrain_params.setdefault("forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5})
    terrain_params.pop("rivers", None)
    terrain_params.pop("lakes", None)
    terrain_params.setdefault("mountains", {"total_area_pct": 5, "perlin_scale": 0.01, "peak_density": 0.2})
    terrain_params.setdefault("swamp_desert", {"swamp_pct": 3, "desert_pct": 5, "clumpiness": 0.5})

    # Remove any logging systems defined in the configuration
    for child in list(world.children):
        if isinstance(child, LoggingSystem):
            world.remove_child(child)

    if not any(isinstance(c, PygameViewerSystem) for c in world.children):
        PygameViewerSystem(parent=world)

    pathfinder = next((c for c in world.children if isinstance(c, PathfindingSystem)), None)
    if pathfinder is None:
        pathfinder = PathfindingSystem(parent=world, terrain=terrain_node)

    time_system = next((c for c in world.children if isinstance(c, TimeSystem)), None)
    if time_system is not None:
        time_system.current_time = config.START_TIME

    FPS = config.FPS
    TIME_SCALE = config.TIME_SCALE
    settings_file = sys.argv[2] if len(sys.argv) > 2 else "example/war_settings.json"
    sim_params = load_sim_params(settings_file)
    sim_params["terrain"] = terrain_params
else:
    logger = logging.getLogger(__name__)
    world = None
    terrain_node = None
    terrain_params: dict = {}
    pathfinder = None
    time_system = None
    FPS = config.FPS
    TIME_SCALE = config.TIME_SCALE
    sim_params = dict(DEFAULT_SIM_PARAMS)
    sim_params["terrain"] = terrain_params

river_width_presets = [(2, 5), (4, 8), (8, 14)]
river_width_index = 0
mountain_presets = [
    {"total_area_pct": 5, "threshold": 0.75},
    {"total_area_pct": 10, "threshold": 0.65},
    {"total_area_pct": 20, "threshold": 0.55},
]
mountain_preset_index = 0
forest_layouts = [
    {"total_area_pct": 10, "clusters": 6, "cluster_spread": 0.6},
    {"total_area_pct": 30, "clusters": 2, "cluster_spread": 0.2},
]
forest_layout_index = 0
reliability_presets = [1.0, 0.8, 0.5]
reliability_index = 0
viewer: PygameViewerSystem | None = None
movement_system: MovementSystem | None = None
command_system: CommandSystem | None = None
visibility_system: VisibilitySystem | None = None
pathfinder: PathfindingSystem | None = None


def terrain_regen(world, params: dict) -> None:
    """Regenerate terrain tiles according to *params*."""

    terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain is None:
        return

    width, height = int(world.width), int(world.height)
    start_time = time.perf_counter()

    tiles = generate_base(width, height, fill="plain")
    logger.info("Base terrain generated in %.2fs", time.perf_counter() - start_time)

    obstacles: set[tuple[int, int]] = set()
    altitude_map: list[list[float]] | None = None

    step_start = time.perf_counter()
    for river in params.get("rivers", []):
        tiles, obstacles = carve_river(
            tiles,
            start=river.get("start", (0, 0)),
            end=river.get("end", (width - 1, height - 1)),
            width_min=river.get("width_min", 2),
            width_max=river.get("width_max", 5),
            meander=river.get("meander", 0.3),
            obstacles_set=obstacles,
        )
    logger.info("Rivers carved in %.2fs", time.perf_counter() - step_start)

    step_start = time.perf_counter()
    for lake in params.get("lakes", []):
        tiles, obstacles = place_lake(
            tiles,
            center=lake.get("center", (width // 2, height // 2)),
            radius=lake.get("radius", 20),
            irregularity=lake.get("irregularity", 0.4),
            obstacles_set=obstacles,
        )
    logger.info("Lakes placed in %.2fs", time.perf_counter() - step_start)

    forests = params.get("forests", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_forest(
        tiles,
        total_area_pct=forests.get("total_area_pct", 10),
        clusters=forests.get("clusters", 5),
        cluster_spread=forests.get("cluster_spread", 0.5),
        obstacles_set=obstacles,
    )
    logger.info("Forests placed in %.2fs", time.perf_counter() - step_start)

    mountains = params.get("mountains", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_mountains(
        tiles,
        total_area_pct=mountains.get("total_area_pct", 5),
        perlin_scale=mountains.get("perlin_scale", 0.01),
        peak_density=mountains.get("peak_density", 0.2),
        altitude_map_out=None,
        obstacles_set=obstacles,
        obstacle_threshold=params.get("obstacle_altitude_threshold", 0.75),
    )
    logger.info("Mountains generated in %.2fs", time.perf_counter() - step_start)

    swamp_desert = params.get("swamp_desert", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_swamp_desert(
        tiles,
        swamp_pct=swamp_desert.get("swamp_pct", 3),
        desert_pct=swamp_desert.get("desert_pct", 5),
        clumpiness=swamp_desert.get("clumpiness", 0.5),
        obstacles_set=obstacles,
    )
    logger.info("Swamps and deserts placed in %.2fs", time.perf_counter() - step_start)
    logger.info("Terrain regeneration finished in %.2fs", time.perf_counter() - start_time)

    terrain.tiles = tiles
    terrain.obstacles = obstacles
    terrain.altitude_map = altitude_map
    terrain.speed_modifiers.update(
        {
            "water": 0.4,
            "mountain": 0.6,
            "swamp": 0.5,
            "desert": 0.8,
        }
    )
    terrain.combat_bonuses.update(
        {
            "water": -2,
            "mountain": 3,
            "swamp": -1,
            "desert": 0,
        }
    )


def _spawn_armies(
    world,
    dispersion_radius: float,
    soldiers_per_dot: int,
    bodyguard_size: int,
    pathfinder: PathfindingSystem | None = None,
) -> None:
    """Spawn hierarchical armies for each nation.

    Each nation receives a general already present in the configuration.
    This helper populates the general with a strategist, bodyguards and a
    single army composed of officers commanding small units. Positions are
    dispersed around the nation's capital within ``dispersion_radius``.
    ``UnitNode`` sizes are rounded to multiples of ``soldiers_per_dot`` so
    the viewer can scale unit dots accordingly. When a ``pathfinder`` is
    supplied only the first officer's units receive movement orders toward the
    enemy capital and their path is precomputed for step-by-step exploration.
    """

    def _pos_around(cx: float, cy: float) -> list[float]:
        if dispersion_radius <= 0:
            return [cx, cy]
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, dispersion_radius)
        return [cx + math.cos(angle) * r, cy + math.sin(angle) * r]

    def _round_size(size: int) -> int:
        mul = max(1, soldiers_per_dot)
        return max(mul, int(math.ceil(size / mul)) * mul)

    nations = [n for n in world.children if isinstance(n, NationNode)]
    width, height = world.width, world.height
    for nation in nations:
        general = next((c for c in nation.children if isinstance(c, GeneralNode)), None)
        if general is None:
            continue

        # keep transform, remove other subordinates before respawning
        transform = next((c for c in general.children if isinstance(c, TransformNode)), None)
        for child in list(general.children):
            if child is not transform:
                general.remove_child(child)
        if transform is None:
            cap = getattr(nation, "capital_position", [width / 2, height / 2])
            transform = TransformNode(position=list(cap))
            general.add_child(transform)
        center = transform.position

        # strategist assisting the general
        strategist = StrategistNode(name=f"{nation.name}_strategist")
        general.add_child(strategist)

        # bodyguards directly protecting the general
        for i in range(5):
            size = _round_size(bodyguard_size)
            bg = BodyguardUnitNode(
                name=f"{nation.name}_bodyguard_{i+1}",
                size=size,
                state="idle",
                speed=1.0,
                morale=100,
                vision_radius_m=sim_params.get("vision_radius_m", 100.0),
            )
            bg.add_child(TransformNode(position=_pos_around(*center)))
            general.add_child(bg)

        # main army with officers and units
        army = ArmyNode(name=f"{nation.name}_army", goal="advance", size=0)
        army.add_child(TransformNode(position=list(center)))
        total_units = 0
        enemies = [n for n in nations if n is not nation]
        target_cap = enemies[0].capital_position if enemies else [width / 2, height / 2]
        unit_size = _round_size(sim_params.get("unit_size", 5))
        for i in range(5):
            officer = OfficerNode(name=f"{nation.name}_officer_{i+1}")
            officer.add_child(TransformNode(position=_pos_around(*center)))
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
                pos = _pos_around(*center)
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


def apply_sim_params() -> None:
    """Propagate *sim_params* values to systems."""

    if viewer:
        viewer.set_render_params(soldiers_per_dot=sim_params["soldiers_per_dot"])
    if movement_system:
        movement_system.set_blocking(sim_params.get("movement_blocking", True))
    if visibility_system:
        visibility_system.set_enabled(sim_params["visibility"])
    if command_system:
        command_system.set_delay(sim_params["command_delay"])


def _reset() -> None:
    terrain_regen(world, sim_params["terrain"])
    _spawn_armies(
        world,
        sim_params["dispersion"],
        sim_params["soldiers_per_dot"],
        sim_params["bodyguard_size"],
        pathfinder,
    )
    if time_system is not None:
        time_system.current_time = config.START_TIME
    apply_sim_params()


if __name__ == "__main__":
    # initial world setup
    _reset()

    movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
    if movement_system:
        movement_system.direction_noise = 0.2
        movement_system.avoid_obstacles = True
        movement_system.pathfinder = pathfinder

    command_system = next((c for c in world.children if isinstance(c, CommandSystem)), None)
    visibility_system = next((c for c in world.children if isinstance(c, VisibilitySystem)), None)
    if command_system:
        sim_params["command_delay"] = command_system.base_delay_s
    if visibility_system:
        sim_params["visibility"] = visibility_system.enabled

    def _forest_minus() -> None:
        forests = sim_params["terrain"].setdefault(
            "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
        )
        forests["total_area_pct"] = max(0.0, forests.get("total_area_pct", 0) - 1)
        terrain_regen(world, sim_params["terrain"])

    def _forest_plus() -> None:
        forests = sim_params["terrain"].setdefault(
            "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
        )
        forests["total_area_pct"] = min(100.0, forests.get("total_area_pct", 0) + 1)
        terrain_regen(world, sim_params["terrain"])

    def _dispersion_minus() -> None:
        sim_params["dispersion"] = max(0.0, sim_params["dispersion"] - 10.0)
        _reset()

    def _dispersion_plus() -> None:
        sim_params["dispersion"] += 10.0
        _reset()

    def _cmd_delay_minus() -> None:
        if command_system:
            sim_params["command_delay"] = max(
                0.0, sim_params["command_delay"] - 0.5
            )
            apply_sim_params()

    def _cmd_delay_plus() -> None:
        if command_system:
            sim_params["command_delay"] += 0.5
            apply_sim_params()

    clock = pygame.time.Clock()
    viewer = next((c for c in world.children if isinstance(c, PygameViewerSystem)), None)
    # Center the view on the world by default
    if viewer:
        # Scale the viewer so the whole world fits within the window.
        scale_x = viewer.view_width / world.width
        scale_y = viewer.view_height / world.height
        viewer.scale = min(scale_x, scale_y)
        viewer.unit_radius = 10
        viewer.draw_capital = True
        viewer.offset_x = world.width / 2 - viewer.view_width / (2 * viewer.scale)
        viewer.offset_y = world.height / 2 - viewer.view_height / (2 * viewer.scale)

    apply_sim_params()
    paused = False
    running = True
    while running and pygame.get_init():
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    _reset()
                elif event.key == pygame.K_s:
                    TIME_SCALE = max(0.01, TIME_SCALE / 2)
                elif event.key == pygame.K_x:
                    TIME_SCALE = min(100, TIME_SCALE * 2)
                elif viewer and event.key == pygame.K_LEFTBRACKET:
                    prev = viewer.scale
                    viewer.scale = max(0.1, viewer.scale * 0.9)
                    cx = viewer.offset_x + viewer.view_width / (2 * prev)
                    cy = viewer.offset_y + viewer.view_height / (2 * prev)
                    viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                    viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
                elif viewer and event.key == pygame.K_RIGHTBRACKET:
                    prev = viewer.scale
                    viewer.scale = viewer.scale * 1.1
                    cx = viewer.offset_x + viewer.view_width / (2 * prev)
                    cy = viewer.offset_y + viewer.view_height / (2 * prev)
                    viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                    viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
                elif viewer and event.key == pygame.K_h:
                    viewer.offset_x -= viewer.view_width * 0.1 / viewer.scale
                elif viewer and event.key == pygame.K_l:
                    viewer.offset_x += viewer.view_width * 0.1 / viewer.scale
                elif viewer and event.key == pygame.K_j:
                    viewer.offset_y += viewer.view_height * 0.1 / viewer.scale
                elif viewer and event.key == pygame.K_k:
                    viewer.offset_y -= viewer.view_height * 0.1 / viewer.scale
                elif viewer and event.key == pygame.K_b:
                    viewer.set_render_params(show_role_rings=not viewer.show_role_rings)
                elif event.key == pygame.K_i and visibility_system:
                    sim_params["visibility"] = not sim_params["visibility"]
                    apply_sim_params()
                elif viewer and event.key == pygame.K_SEMICOLON:
                    viewer.set_render_params(show_intel_overlay=not viewer.show_intel_overlay)
                elif event.key == pygame.K_COMMA and command_system:
                    _cmd_delay_minus()
                elif event.key == pygame.K_PERIOD and command_system:
                    _cmd_delay_plus()
                elif event.key == pygame.K_n and command_system:
                    reliability_index = (reliability_index + 1) % len(reliability_presets)
                    command_system.reliability = reliability_presets[reliability_index]
                elif paused:
                    if event.key == pygame.K_f:
                        _forest_minus()
                    elif event.key == pygame.K_g:
                        _forest_plus()
                    elif event.key == pygame.K_w and sim_params["terrain"].get("rivers"):
                        river_width_index = (river_width_index + 1) % len(river_width_presets)
                        wmin, wmax = river_width_presets[river_width_index]
                        for river in sim_params["terrain"].get("rivers", []):
                            river["width_min"], river["width_max"] = wmin, wmax
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_m:
                        mountain_preset_index = (mountain_preset_index + 1) % len(mountain_presets)
                        preset = mountain_presets[mountain_preset_index]
                        mountains = sim_params["terrain"].setdefault("mountains", {})
                        mountains["total_area_pct"] = preset["total_area_pct"]
                        sim_params["terrain"]["obstacle_altitude_threshold"] = preset["threshold"]
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_v:
                        forest_layout_index = (forest_layout_index + 1) % len(forest_layouts)
                        sim_params["terrain"]["forests"] = dict(forest_layouts[forest_layout_index])
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_d:
                        sim_params["dispersion"] = 0.0 if sim_params["dispersion"] > 0 else 200.0
                        _reset()
                    elif event.key == pygame.K_p:
                        _dispersion_minus()
                    elif event.key == pygame.K_o:
                        _dispersion_plus()
                    elif event.key == pygame.K_c:
                        cycle = [1, 2, 5, 10]
                        idx = cycle.index(sim_params["soldiers_per_dot"])
                        sim_params["soldiers_per_dot"] = cycle[(idx + 1) % len(cycle)]
                        _reset()
        if viewer:
            if paused:
                forest_pct = sim_params["terrain"].get("forests", {}).get(
                    "total_area_pct", 0
                )
                menu_items = [
                    {
                        "label": f"Dispersion R: {sim_params['dispersion']:.0f} m",
                        "minus": _dispersion_minus,
                        "plus": _dispersion_plus,
                    },
                    {
                        "label": f"Forest %: {forest_pct:.0f}",
                        "minus": _forest_minus,
                        "plus": _forest_plus,
                    },
                ]
                if command_system:
                    menu_items.insert(
                        1,
                        {
                            "label": f"Cmd delay: {command_system.base_delay_s:.1f}s",
                            "minus": _cmd_delay_minus,
                            "plus": _cmd_delay_plus,
                        },
                    )
                viewer.set_menu_items(menu_items)
                info = [
                    f"Soldiers/dot: {sim_params['soldiers_per_dot']}",
                    f"FoW: {'ON' if sim_params['visibility'] else 'OFF'}",
                    f"Intel overlay: {'ON' if viewer.show_intel_overlay else 'OFF'}",
                    "F/G or buttons: -/+ forest, W: river width, M: mountains, V: forest layout",
                    "P/O or buttons: -/+ dispersion, D: cluster toggle, C: cycle dot scale",
                    ",/. or buttons: cmd delay, B: rings, I: fog, ;: intel, N: reliability, R: reset",
                ]
                if command_system:
                    info.insert(0, f"Reliability: {command_system.reliability:.2f}")
                viewer.extra_info = info
            else:
                viewer.set_menu_items([])
                viewer.extra_info = []
            viewer.process_events(events)
        dt = clock.tick(FPS) / 1000.0
        world.update(0 if paused else dt * TIME_SCALE)

    pygame.quit()
