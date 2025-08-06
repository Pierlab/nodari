from nodes.need import NeedNode


def test_need_threshold_and_satisfy():
    events = []

    def handler(emitter, event, payload):
        events.append(event)

    need = NeedNode(need_name="hunger", threshold=10, increase_rate=5)
    need.on_event("need_threshold_reached", handler)
    need.update(1)  # value=5
    assert events == []
    need.update(1)  # value=10 -> threshold reached
    assert events == ["need_threshold_reached"]
    need.on_event("need_satisfied", handler)
    need.satisfy(10)
    assert "need_satisfied" in events
