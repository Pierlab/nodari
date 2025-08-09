# Animal Nodes

Introducing animals into the simulation requires a dedicated `AnimalNode` type that composes existing building blocks:

- **Needs** – animals often require hunger or fatigue tracking. These can reuse `NeedNode` instances attached as children.
- **Resource production** – livestock like cows or chickens may produce milk or eggs through a `ResourceProducerNode`.
- **Events** – actions such as feeding or harvesting emit events (`animal_fed`, `resource_produced`) for systems to react.
- **Hierarchy** – animals live within the node tree like any other entity. They can be attached to a `FarmNode` or directly to the world root.
- **Reproduction** – reproduction logic can be added later via additional nodes or systems.

The new `AnimalNode` class establishes a foundation for these behaviours, enabling future expansion without altering existing nodes.
