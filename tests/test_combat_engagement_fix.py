from nodes.world import WorldNode
from nodes.terrain import TerrainNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from systems.movement import MovementSystem


def test_opposing_units_stop_and_fight_on_same_tile():
    world = WorldNode()
    terrain = TerrainNode(tiles=[["plain"] * 2])
    MovementSystem(parent=world, terrain=terrain)

    north = NationNode(parent=world, morale=100, capital_position=[0, 0])
    n_gen = GeneralNode(parent=north, style="balanced")
    n_army = ArmyNode(parent=n_gen, goal="advance", size=1)
    u1 = UnitNode(parent=n_army, speed=2.0, target=[1, 0])
    TransformNode(parent=u1, position=[0.0, 0.0])

    south = NationNode(parent=world, morale=100, capital_position=[1, 0])
    s_gen = GeneralNode(parent=south, style="balanced")
    s_army = ArmyNode(parent=s_gen, goal="defend", size=1)
    u2 = UnitNode(parent=s_army, speed=2.0, target=[0, 0])
    TransformNode(parent=u2, position=[1.0, 0.0])

    world.update(1.0)

    tr1 = next(c for c in u1.children if isinstance(c, TransformNode))
    tr2 = next(c for c in u2.children if isinstance(c, TransformNode))

    assert tr1.position == [1.0, 0.0]
    assert tr2.position == [1.0, 0.0]
    assert u1.state == u2.state == "fighting"

