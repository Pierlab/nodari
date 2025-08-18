from nodes.world import WorldNode
from nodes.nation import NationNode
from systems.moral import MoralSystem


def test_nation_collapses_when_morale_depleted():
    world = WorldNode()
    MoralSystem(parent=world)
    nation = NationNode(parent=world, morale=5, capital_position=[0, 0])

    collapsed = []

    def on_collapsed(origin, event, payload):
        collapsed.append(payload)

    nation.on_event("nation_collapsed", on_collapsed)
    nation.change_morale(-5)
    world.update(1.0)
    assert collapsed and collapsed[0]["morale"] <= 0


def test_collapse_emitted_only_once():
    world = WorldNode()
    MoralSystem(parent=world)
    nation = NationNode(parent=world, morale=2, capital_position=[0, 0])
    collapsed: list[dict] = []
    nation.on_event("nation_collapsed", lambda _o, _e, p: collapsed.append(p))

    nation.change_morale(-2)
    world.update(1.0)
    nation.change_morale(-1)
    world.update(1.0)

    assert len(collapsed) == 1
