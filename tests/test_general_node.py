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


def test_general_attempts_flank_with_probability():
    general = GeneralNode(style="balanced", flank_success_chance=1.0)
    army = ArmyNode(parent=general, goal="advance", size=1)

    # Guaranteed success
    assert general.attempt_flank(army) is True
    assert army.goal == "flank"

    # Guaranteed failure
    other_army = ArmyNode(parent=general, goal="advance", size=1)
    general.flank_success_chance = 0.0
    assert general.attempt_flank(other_army) is False
    assert other_army.goal == "advance"
