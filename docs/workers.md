# Worker Nodes

`WorkerNode` extends `UnitNode` to represent civilian workers capable of gathering resources or participating in building construction.

## States
- **idle** – no task assigned; the worker is removed from the scheduler.
- **gathering** – actively collecting resources.
- **building** – working on construction projects.

## Scheduling
Workers are updated by the `SchedulerSystem` at fixed intervals instead of every simulation tick. The interval is configured via the `update_interval` parameter (in seconds).

```python
from nodes.worker import WorkerNode
from systems.scheduler import SchedulerSystem
from nodes.world import WorldNode

world = WorldNode(name="world")
scheduler = SchedulerSystem(parent=world)
worker = WorkerNode(parent=world, update_interval=2.0)

# assign a gathering task
worker.emit("task_assigned", {"task": "gathering"})

# later, when finished
worker.emit("task_complete")
```

When a task is assigned, the worker schedules itself with the scheduler. Upon task completion, it switches back to the `idle` state, emits `unit_idle` and unregisters from the scheduler.
