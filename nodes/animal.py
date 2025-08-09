"""Node representing an animal with basic hunger handling."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type
from .need import NeedNode
from .resource_producer import ResourceProducerNode


class AnimalNode(SimNode):
    """Represents an animal with optional needs and resource production."""

    def __init__(
        self,
        species: str,
        hunger: NeedNode | None = None,
        producer: ResourceProducerNode | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.species = species
        if hunger:
            hunger.parent = self
        if producer:
            producer.parent = self

    def feed(self, amount: float) -> None:
        """Satisfy the hunger need if present."""
        for child in self.children:
            if isinstance(child, NeedNode) and child.need_name == "hunger":
                child.satisfy(amount)
                self.emit("animal_fed", {"species": self.species, "amount": amount})
                break


register_node_type("AnimalNode", AnimalNode)
