from core.simnode import SimNode
from nodes.unit import UnitNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.transform import TransformNode
from nodes.strategist import StrategistNode
from systems.visibility import VisibilitySystem


def test_visibility_spots_enemy_and_updates_tiles():
    root = SimNode("root")
    vis = VisibilitySystem(parent=root)

    nation_a = NationNode(morale=100, capital_position=[0, 0], parent=root)
    gen_a = GeneralNode(style="balanced", parent=nation_a)
    strat = StrategistNode(parent=gen_a)
    army_a = ArmyNode(goal="hold", size=0, parent=gen_a)
    unit_a = UnitNode(parent=army_a, vision_radius_m=10.0)
    TransformNode(position=[0.0, 0.0], parent=unit_a)

    nation_b = NationNode(morale=100, capital_position=[10, 10], parent=root)
    unit_b = UnitNode(parent=nation_b)
    TransformNode(position=[5.0, 0.0], parent=unit_b)

    vis.update(1.0)

    intel = strat.get_enemy_estimates()
    assert intel and intel[0]["enemy"] == unit_b.name
    tiles = vis.visible_tiles[id(nation_a)]
    assert (5, 0) in tiles
