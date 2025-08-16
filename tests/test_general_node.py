from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.nation import NationNode


def test_general_records_style_and_reports():
    general = GeneralNode(style="aggressive")
    army = ArmyNode(name="army", goal="advance")
    general.add_child(army)

    army.emit("battlefield_event", {"sector": 1})

    assert general.style == "aggressive"
    assert general.reports[0]["sector"] == 1
    assert general.get_armies() == [army]


def test_general_ai_changes_army_goal_based_on_morale_and_reports():
    nation = NationNode(name="nation", morale=100, capital_position=[0, 0])
    general = GeneralNode(parent=nation, style="balanced")
    army = ArmyNode(parent=general, goal="advance", size=1)

    # High morale with no reports keeps goal
    general.update(0)
    assert army.goal == "advance"

    # Unit engaged while morale drops -> defend
    nation.morale = 50
    army.emit("battlefield_event", {"type": "unit_engaged"})
    general.update(0)
    assert army.goal == "defend"

    # Unit routed and very low morale -> retreat
    nation.morale = 20
    army.emit("battlefield_event", {"type": "unit_routed"})
    general.update(0)
    assert army.goal == "retreat"
