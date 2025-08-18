import os
import json
import random

os.environ["RUN_WAR_IMPORT_ONLY"] = "1"

from nodes.world import WorldNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.transform import TransformNode
from nodes.army import ArmyNode
from nodes.unit import UnitNode

from run_war import load_sim_params, _spawn_armies, sim_params


def test_load_sim_params(tmp_path):
    data = {"parameters": {"unit_size": 7, "vision_radius_m": 150.0}}
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(data))

    params = load_sim_params(str(path))
    assert params["unit_size"] == 7
    assert params["vision_radius_m"] == 150.0
    # ensure defaults are preserved
    assert params["dispersion"] == 200.0


def test_spawn_armies_respects_sim_params():
    random.seed(0)
    world = WorldNode(width=3, height=3)
    north = NationNode(parent=world, name="north", capital_position=[0, 0], morale=100)
    g_north = GeneralNode(parent=north, style="balanced")
    TransformNode(parent=g_north, position=[0, 0])
    south = NationNode(parent=world, name="south", capital_position=[2, 2], morale=100)
    g_south = GeneralNode(parent=south, style="balanced")
    TransformNode(parent=g_south, position=[2, 2])

    old_params = dict(sim_params)
    try:
        sim_params["unit_size"] = 20
        sim_params["vision_radius_m"] = 50.0
        _spawn_armies(world, 0, sim_params["soldiers_per_dot"], sim_params["bodyguard_size"], None)

        army = next(c for c in g_north.children if isinstance(c, ArmyNode))
        unit = next(c for c in army.get_officers()[0].children if isinstance(c, UnitNode))
        assert unit.size == 20
        assert unit.vision_radius_m == 50.0
    finally:
        sim_params.clear()
        sim_params.update(old_params)
