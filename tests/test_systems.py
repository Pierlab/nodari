from systems.time import TimeSystem


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
