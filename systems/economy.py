"""Simple economy system handling buy requests."""
from __future__ import annotations

from core.simnode import SystemNode
from core.plugins import register_node_type
from nodes.inventory import InventoryNode


class EconomySystem(SystemNode):
    def __init__(self, base_prices: dict[str, float] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.prices: dict[str, float] = base_prices or {}
        self.on_event("buy_request", self._on_buy)

    def _price_for(self, item: str) -> float:
        return self.prices.setdefault(item, 1.0)

    def _on_buy(self, emitter, event_name, payload):
        buyer: InventoryNode = payload["buyer"]
        seller: InventoryNode = payload["seller"]
        item = payload["item"]
        qty = payload["quantity"]
        price = payload.get("price", self._price_for(item))
        if seller.items.get(item, 0) >= qty and buyer.items.get("money", 0) >= price * qty:
            seller.transfer_to(buyer, item, qty)
            if price:
                buyer.remove_item("money", price * qty)
                seller.add_item("money", price * qty)
            self.emit("buy_success", payload)
            stock = seller.items.get(item, 0)
            if stock < 5:
                self.prices[item] = price + 1
            elif stock > 10 and price > 1:
                self.prices[item] = price - 1
        else:
            self.prices[item] = price + 1
            self.emit("buy_failed", payload)


register_node_type("EconomySystem", EconomySystem)
