# Getting Started Tutorial

This guide walks through creating and running a minimal farm simulation.

## 1. Create the world

```python
from core.simnode import SimNode
from systems.time import TimeSystem

root = SimNode("world")
TimeSystem(parent=root)
```

## 2. Add a character

```python
from nodes.character import CharacterNode
from nodes.ai_behavior import AIBehaviorNode

char = CharacterNode(name="farmer", parent=root)
# by default the AI uses ``FarmerRoutine`` but any routine class can be
# provided via the ``routine`` argument
AIBehaviorNode(parent=char)
```

## 3. Run the simulation

```python
from core.simnode import SimNode

def run(root: SimNode, steps: int = 10):
    for _ in range(steps):
        root.update(1.0)

run(root)
```

This simple script sets up the minimal components and advances the world
for a few ticks. Modify or extend the node tree to experiment with new
behaviours.
