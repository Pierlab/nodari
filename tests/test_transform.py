from nodes.transform import TransformNode


def test_velocity_updates_position():
    t = TransformNode(position=[0.0, 0.0], velocity=[1.0, 0.5])
    t.update(2.0)
    assert t.position == [2.0, 1.0]
