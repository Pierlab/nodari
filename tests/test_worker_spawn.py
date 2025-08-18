from nodes.world import WorldNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.transform import TransformNode
from nodes.builder import BuilderNode
from simulation.war.war_loader import _spawn_armies


def test_spawn_armies_adds_builders():
    world = WorldNode(width=100, height=100)
    nation = NationNode(parent=world, morale=100, capital_position=[50, 50])
    general = GeneralNode(parent=nation, style="balanced")
    TransformNode(parent=general, position=[50, 50])
    _spawn_armies(world, dispersion_radius=0, soldiers_per_dot=1, bodyguard_size=1)
    builders = [c for c in nation.children if isinstance(c, BuilderNode)]
    assert len(builders) == 3
    for b in builders:
        assert b.state == "exploring"
        tr = next(c for c in b.children if isinstance(c, TransformNode))
        assert tr.position == [50, 50]

