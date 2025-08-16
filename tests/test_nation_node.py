from core.simnode import SimNode
from nodes.nation import NationNode


def test_morale_change_emits_event():
    nation = NationNode(morale=100, capital_position=[0, 0])
    events: list[dict] = []
    nation.on_event("moral_changed", lambda _o, _e, payload: events.append(payload))

    nation.change_morale(-10)

    assert nation.morale == 90
    assert events[0]["previous"] == 100
    assert events[0]["morale"] == 90
    assert events[0]["delta"] == -10


def test_capital_capture_emits_event():
    nation = NationNode(morale=50, capital_position=[5, 5])
    events: list[dict] = []
    nation.on_event("capital_captured", lambda _o, _e, payload: events.append(payload))

    nation.capture_capital()

    assert events[0]["position"] == [5, 5]


def test_references_generals_and_armies():
    class GeneralNode(SimNode):
        pass

    class ArmyNode(SimNode):
        pass

    army = ArmyNode(name="army")
    general = GeneralNode(name="general")
    general.add_child(army)

    nation = NationNode(morale=100, capital_position=[0, 0])
    nation.add_child(general)

    assert nation.get_generals() == [general]
    assert nation.get_armies() == [army]

