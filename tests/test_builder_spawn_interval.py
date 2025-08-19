from nodes.world import WorldNode
from nodes.nation import NationNode
from systems.ai import AISystem
from systems.scheduler import SchedulerSystem
from nodes.builder import BuilderNode
from nodes.transform import TransformNode


def test_ai_spawns_builder_and_scheduler_handles_it():
    world = WorldNode(width=100, height=100)
    nation = NationNode(parent=world, morale=100, capital_position=[0, 0])
    scheduler = SchedulerSystem(parent=world)
    AISystem(parent=world, builder_spawn_interval=1.0)

    # No builders initially
    assert not [c for c in nation.children if isinstance(c, BuilderNode)]

    # After one second a builder should spawn at the capital
    world.update(1.0)
    builders = [c for c in nation.children if isinstance(c, BuilderNode)]
    assert len(builders) == 1
    builder = builders[0]
    tr = next(c for c in builder.children if isinstance(c, TransformNode))
    assert tr.position == [0, 0]

    # Scheduler should register the builder once a task is assigned
    assert scheduler._tasks == []
    builder.emit("task_assigned", {"task": "build"})
    assert any(t.node is builder for t in scheduler._tasks)
