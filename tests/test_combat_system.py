from nodes.world import WorldNode
from nodes.terrain import TerrainNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from systems.combat import CombatSystem


def test_combat_routes_losing_unit_and_reduces_morale():
    world = WorldNode(seed=1)
    terrain = TerrainNode(tiles=[["plain"]])
    CombatSystem(parent=world, terrain=terrain)

    north = NationNode(parent=world, morale=100, capital_position=[0, 0])
    south = NationNode(parent=world, morale=100, capital_position=[1, 0])

    n_gen = GeneralNode(parent=north, style="balanced")
    n_army = ArmyNode(parent=n_gen, goal="defend", size=1)
    n_unit = UnitNode(parent=n_army, size=50)
    TransformNode(parent=n_unit, position=[0, 0])

    s_gen = GeneralNode(parent=south, style="balanced")
    s_army = ArmyNode(parent=s_gen, goal="advance", size=1)
    s_unit = UnitNode(parent=s_army, size=100)
    TransformNode(parent=s_unit, position=[0, 0])

    world.update(1.0)

    assert n_unit.state == "fleeing"
    assert s_unit.state == "fighting"
    assert north.morale < 100
