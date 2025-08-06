"""Simple economy system handling buy requests."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type
from nodes.inventory import InventoryNode


class EconomySystem(SystemNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_event("buy_request", self._on_buy)

    def _on_buy(self, emitter, event_name, payload):
        buyer: InventoryNode = payload["buyer"]
        seller: InventoryNode = payload["seller"]
        item = payload["item"]
        qty = payload["quantity"]
        price = payload.get("price", 0)
        if seller.items.get(item, 0) >= qty and buyer.items.get("money", 0) >= price * qty:
            seller.transfer_to(buyer, item, qty)
            if price:
                buyer.remove_item("money", price * qty)
                seller.add_item("money", price * qty)
            self.emit("buy_success", payload)
        else:
            self.emit("buy_failed", payload)


register_node_type("EconomySystem", EconomySystem)
