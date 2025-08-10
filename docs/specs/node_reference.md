# Node Reference

Detailed description of the simulation nodes. Each section outlines the
purpose of the node, notable attributes and how it interacts with other
components in the world tree.

## AnimalNode

Represents an individual animal. An animal may have child
`NeedNode` instances (e.g. hunger) and optionally a
`ResourceProducerNode` to model milk, eggs, etc. Feeding an
animal satisfies the hunger need and emits an `animal_fed` event.

## BarnNode

Simple container used to shelter animals or store equipment. The barn has
no special behaviour of its own but groups related nodes in the tree.

## CharacterNode

Composite node representing a farmer or other NPC. Characters typically
contain a `TransformNode` for position, an `AIBehaviorNode` for simple
behaviour and an `InventoryNode` for personal items.

## FarmNode

Central node representing a farm. It usually owns various buildings,
inventories and resource producers that belong to the same farmstead.

## HouseNode

Dwelling where characters live and store resources. Houses often contain
an `InventoryNode` to hold goods owned by the inhabitants.

## InventoryNode

Maintains a dictionary of item quantities. Provides `add_item`,
`remove_item` and `transfer_to` helpers and emits an `inventory_changed`
event whenever the stock is modified.

## NeedNode

Models a consumable need such as hunger or fatigue. The need value
increases over time until it crosses a threshold, at which point a
`need_threshold_reached` event is emitted. Satisfying the need lowers the
value and can trigger `need_satisfied`.

## PastureNode

Open grazing area for animals. Used primarily as a location within the
world tree.

## ResourceProducerNode

Produces a named resource either automatically every tick or when the
`work` method is called. Inputs can be configured so production consumes
other resources. Successful production emits a `resource_produced` event.

## SiloNode

Tall structure used to store harvested crops. The optional `capacity`
attribute can limit how much grain the silo may hold.

## TransformNode

Stores 2D position and velocity in metres and metres per second. During
each update the position is advanced according to the velocity.

## WarehouseNode

Generic storage building used for goods that do not belong in the silo or
house.

## WellNode

Node representing a simple well where characters can collect water.

## WorldNode

Root of the simulation tree. Tracks the overall world size and optional
random seed used to make simulations deterministic.

## AIBehaviorNode

Light‑weight behaviour controller for characters. The node delegates its
logic to a pluggable *routine* class, allowing different behaviours to be
swapped without modifying the core engine. The default
`FarmerRoutine` handles navigation, daily schedules and interactions with
inventories (fetching water, eating when hungry, delivering goods). Other
routines can be referenced in configuration files via their dotted class
path.
