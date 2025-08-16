from core.simnode import SimNode
from nodes.general import GeneralNode


def test_general_records_style_and_reports():
    general = GeneralNode(style="aggressive")

    class ArmyNode(SimNode):
        pass

    army = ArmyNode(name="army")
    general.add_child(army)

    army.emit("battlefield_event", {"sector": 1})

    assert general.style == "aggressive"
    assert general.reports[0]["sector"] == 1
    assert general.get_armies() == [army]
