from nodes.inventory import InventoryNode
from systems.time import TimeSystem
from systems.economy import EconomySystem


def test_time_system_emits_events():
    sys = TimeSystem(phase_length=2)
    phases = []
    sys.on_event("phase_changed", lambda e, n, p: phases.append(p["phase"]))
    sys.update(1)
    sys.update(1)  # phase change after 2 ticks
    assert phases == [1]


def test_time_system_time_scale_accelerates():
    sys = TimeSystem(tick_duration=1.0, time_scale=2.0)
    ticks = []
    sys.on_event("tick", lambda e, n, p: ticks.append(p["tick"]))
    sys.update(0.5)  # scaled to 1.0, triggers a tick
    assert ticks == [1]


def test_economy_buy_success():
    econ = EconomySystem()
    buyer = InventoryNode(items={"money": 10})
    seller = InventoryNode(items={"wheat": 5})
    events = []
    econ.on_event("buy_success", lambda e, n, p: events.append("ok"))
    econ.emit(
        "buy_request",
        {
            "buyer": buyer,
            "seller": seller,
            "item": "wheat",
            "quantity": 2,
            "price": 1,
        },
        direction="up",
    )
    assert buyer.items["wheat"] == 2
    assert seller.items["wheat"] == 3
    assert buyer.items["money"] == 8
    assert events == ["ok"]
