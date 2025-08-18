from nodes.world import WorldNode
from nodes.nation import NationNode
from nodes.builder import BuilderNode
from nodes.transform import TransformNode
from systems.ai import AISystem
from systems.movement import MovementSystem


def test_builders_explore_from_capital():
    world = WorldNode(width=200, height=200)
    AISystem(parent=world, exploration_radius=60, capital_min_radius=50)
    MovementSystem(parent=world)
    nation = NationNode(parent=world, morale=100, capital_position=[0, 0])

    builders = []
    transforms = []
    for _ in range(3):
        builder = BuilderNode(parent=nation, state="idle")
        tr = TransformNode(parent=builder, position=[0.0, 0.0])
        # Notify AI after transform exists
        builder.emit("unit_idle", {})
        builders.append(builder)
        transforms.append(tr)

    capital = nation.capital_position
    distances = [0.0, 0.0, 0.0]

    for _ in range(5):
        world.update(1.0)
        for i, tr in enumerate(transforms):
            dx = tr.position[0] - capital[0]
            dy = tr.position[1] - capital[1]
            dist = (dx * dx + dy * dy) ** 0.5
            assert tr.position != capital
            assert dist > distances[i]
            distances[i] = dist
