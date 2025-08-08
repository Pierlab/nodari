"""Utility helpers for :mod:`nodes.ai_behavior`."""
from __future__ import annotations

from typing import Iterator, List, Optional, TYPE_CHECKING
import math
import random

from core.simnode import SimNode
from core.units import kmh_to_mps
from .inventory import InventoryNode
from .need import NeedNode
from .transform import TransformNode
from systems.time import TimeSystem

if TYPE_CHECKING:  # pragma: no cover - hints only
    from .ai_behavior import AIBehaviorNode
    from .resource_producer import ResourceProducerNode


# Reference random speed used to scale idle jitter (2 km/h)
_REF_RANDOM_SPEED = kmh_to_mps(2.0)


def root(node: SimNode) -> SimNode:
    """Return the root of ``node``'s tree."""
    while node.parent is not None:
        node = node.parent
    return node


def walk(node: SimNode) -> Iterator[SimNode]:
    """Yield ``node`` and all of its descendants."""
    yield node
    for child in node.children:
        yield from walk(child)


def find_by_name(node: SimNode, name: str) -> Optional[SimNode]:
    """Find a node by ``name`` in ``node``'s subtree."""
    if node.name == name:
        return node
    for child in node.children:
        found = find_by_name(child, name)
        if found is not None:
            return found
    return None


def time_system(node: SimNode) -> Optional[TimeSystem]:
    """Return the :class:`~systems.time.TimeSystem` attached to ``node``."""
    r = root(node)
    for child in walk(r):
        if isinstance(child, TimeSystem):
            return child
    return None


def scheduler_system(node: SimNode):
    """Return the scheduler system if available."""
    from systems.scheduler import SchedulerSystem

    r = root(node)
    for child in walk(r):
        if isinstance(child, SchedulerSystem):
            return child
    return None


def get_position(node: SimNode | None) -> Optional[List[float]]:
    """Return the position of ``node`` if it has a transform."""
    if node is None:
        return None
    for child in node.children:
        if isinstance(child, TransformNode):
            return child.position
    return None


def find_inventory(node: SimNode | None) -> Optional[InventoryNode]:
    if node is None:
        return None
    for child in node.children:
        if isinstance(child, InventoryNode):
            return child
    return None


def find_need(node: SimNode | None, name: str) -> Optional[NeedNode]:
    if node is None:
        return None
    for child in node.children:
        if isinstance(child, NeedNode) and child.need_name == name:
            return child
    return None


def find_producer(node: SimNode | None) -> Optional["ResourceProducerNode"]:
    if node is None:
        return None
    from .resource_producer import ResourceProducerNode

    for child in node.children:
        if isinstance(child, ResourceProducerNode):
            return child
    return None


def find_transform(node: SimNode | None) -> Optional[TransformNode]:
    if node is None:
        return None
    for child in node.children:
        if isinstance(child, TransformNode):
            return child
    return None


def move_towards(transform: TransformNode, target: List[float], speed: float, dt: float) -> None:
    dx = target[0] - transform.position[0]
    dy = target[1] - transform.position[1]
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return
    step = speed * dt
    if step >= dist:
        transform.position[0], transform.position[1] = target[0], target[1]
    else:
        transform.position[0] += dx / dist * step
        transform.position[1] += dy / dist * step


def is_at_position(pos: List[float], target: List[float], threshold: float = 0.5) -> bool:
    dx = pos[0] - target[0]
    dy = pos[1] - target[1]
    return math.hypot(dx, dy) <= threshold


def apply_idle_jitter(
    transform: TransformNode,
    target: List[float],
    random_speed: float,
    jitter_distance: float,
    sleeping: bool,
) -> None:
    if sleeping:
        transform.position[0], transform.position[1] = target[0], target[1]
        return
    jitter = (random_speed / _REF_RANDOM_SPEED) * jitter_distance
    transform.position[0] = target[0] + random.uniform(-jitter, jitter)
    transform.position[1] = target[1] + random.uniform(-jitter, jitter)


def determine_target(ai: "AIBehaviorNode") -> Optional[List[float]]:
    """Return the next target position for ``ai``."""
    time_sys = time_system(ai)
    if time_sys is None:
        return None
    t = time_sys.current_time % 86400
    wake = ai.wake_time
    work_start = ai.work_start_time
    lunch = ai.lunch_time
    lunch_end = ai.lunch_end_time
    work_end = ai.work_end_time
    sleep = ai.sleep_time

    if t < wake or t >= sleep:
        ai._sleeping = True
        ai._idle = False
        ai._task = None
        return get_position(ai.home if isinstance(ai.home, SimNode) else None)
    ai._sleeping = False
    if wake <= t < work_start:
        ai._idle = False
        ai._task = None
        return get_position(ai.home if isinstance(ai.home, SimNode) else None)
    if work_start <= t < lunch:
        ai._idle = False
        if ai._task == "fetch_water" and isinstance(ai.well_inventory, InventoryNode):
            return get_position(ai.well_inventory.parent)
        if ai._task == "deliver_water":
            return get_position(ai.work if isinstance(ai.work, SimNode) else None)
        if ai._task == "deliver_water_to_field" and isinstance(ai.field, SimNode):
            return get_position(ai.field)
        if ai._task == "deliver_wheat_to_farm":
            return get_position(ai.work if isinstance(ai.work, SimNode) else None)
        if ai._task == "deliver_wheat" and isinstance(ai.warehouse_inventory, InventoryNode):
            return get_position(ai.warehouse_inventory.parent)
        return get_position(ai.work if isinstance(ai.work, SimNode) else None)
    if lunch <= t < lunch_end:
        if not ai._idle and random.random() < ai.idle_chance:
            ai._idle = True
        return ai.lunch_position
    if lunch_end <= t < work_end:
        ai._idle = False
        if ai._task == "fetch_water" and isinstance(ai.well_inventory, InventoryNode):
            return get_position(ai.well_inventory.parent)
        if ai._task == "deliver_water":
            return get_position(ai.work if isinstance(ai.work, SimNode) else None)
        if ai._task == "deliver_water_to_field" and isinstance(ai.field, SimNode):
            return get_position(ai.field)
        if ai._task == "deliver_wheat_to_farm":
            return get_position(ai.work if isinstance(ai.work, SimNode) else None)
        if ai._task == "deliver_wheat" and isinstance(ai.warehouse_inventory, InventoryNode):
            return get_position(ai.warehouse_inventory.parent)
        return get_position(ai.work if isinstance(ai.work, SimNode) else None)
    ai._task = None
    return get_position(ai.home if isinstance(ai.home, SimNode) else None)


def handle_work(ai: "AIBehaviorNode", transform: TransformNode, target: List[float], dt: float) -> None:
    time_sys = time_system(ai)
    if time_sys is None:
        return
    t = time_sys.current_time % 86400
    work_start = ai.work_start_time
    lunch = ai.lunch_time
    lunch_end = ai.lunch_end_time
    work_end = ai.work_end_time
    inv = find_inventory(ai.parent)
    farm_inv = ai.work_inventory if isinstance(ai.work_inventory, InventoryNode) else None
    well_inv = ai.well_inventory if isinstance(ai.well_inventory, InventoryNode) else None
    warehouse_inv = ai.warehouse_inventory if isinstance(ai.warehouse_inventory, InventoryNode) else None
    field_inv = ai.field_inventory if isinstance(ai.field_inventory, InventoryNode) else None
    producer = find_producer(ai.work if isinstance(ai.work, SimNode) else None)
    if not (work_start <= t < lunch or (lunch_end <= t < work_end and not ai._idle)):
        if inv:
            if farm_inv:
                amt = inv.items.get("water", 0)
                if amt > 0:
                    inv.transfer_to(farm_inv, "water", amt)
            if warehouse_inv:
                amt = inv.items.get("wheat", 0)
                if amt > 0:
                    inv.transfer_to(warehouse_inv, "wheat", amt)
            if (t >= work_end or t < work_start) and ai.home_inventory and isinstance(ai.home_inventory, InventoryNode):
                amt = inv.items.get("money", 0)
                if amt > 0:
                    inv.transfer_to(ai.home_inventory, "money", amt)
        return
    work_pos = get_position(ai.work if isinstance(ai.work, SimNode) else None)
    well_pos = get_position(well_inv.parent) if well_inv else None
    warehouse_pos = get_position(warehouse_inv.parent) if warehouse_inv else None
    field_pos = get_position(ai.field if isinstance(ai.field, SimNode) else None)

    if ai._task == "fetch_water" and well_inv and well_pos and is_at_position(transform.position, well_pos):
        well_producer = find_producer(well_inv.parent)
        if well_producer:
            well_producer.work(ai.water_per_fetch)
        qty = min(ai.water_per_fetch, well_inv.items.get("water", 0))
        if inv and qty > 0:
            well_inv.transfer_to(inv, "water", qty)
        ai._task = "deliver_water"
        return

    if ai._task == "deliver_water" and work_pos and is_at_position(transform.position, work_pos):
        if inv and farm_inv:
            amt = inv.items.get("water", 0)
            if amt > 0:
                inv.transfer_to(farm_inv, "water", amt)
        ai._task = None

    if ai._task == "deliver_water_to_field" and field_pos and is_at_position(transform.position, field_pos):
        if inv and field_inv:
            amt = inv.items.get("water", 0)
            if amt > 0:
                inv.transfer_to(field_inv, "water", amt)
        ai._task = None

    if ai._task == "deliver_wheat" and warehouse_pos and is_at_position(transform.position, warehouse_pos):
        if inv and warehouse_inv:
            amt = inv.items.get("wheat", 0)
            if amt > 0:
                inv.transfer_to(warehouse_inv, "wheat", amt)
        ai._task = None

    if ai._task == "deliver_wheat_to_farm" and work_pos and is_at_position(transform.position, work_pos):
        if inv and farm_inv:
            amt = inv.items.get("wheat", 0)
            if amt > 0:
                inv.transfer_to(farm_inv, "wheat", amt)
        ai._task = None

    if work_pos and is_at_position(transform.position, work_pos):
        if inv and farm_inv:
            if inv.items.get("water", 0) > 0:
                amt = inv.items.get("water", 0)
                inv.transfer_to(farm_inv, "water", amt)
            if inv.items.get("wheat", 0) > 0:
                amt = inv.items.get("wheat", 0)
                inv.transfer_to(farm_inv, "wheat", amt)
            if farm_inv.items.get("water", 0) > 0 and field_inv and field_inv.items.get("water", 0) < 1 and inv.items.get("water", 0) == 0:
                qty = farm_inv.items.get("water", 0)
                farm_inv.transfer_to(inv, "water", qty)
                ai._task = "deliver_water_to_field"
                return
            if field_inv and field_inv.items.get("wheat", 0) > 0 and inv.items.get("wheat", 0) == 0:
                qty = field_inv.items.get("wheat", 0)
                field_inv.transfer_to(inv, "wheat", qty)
                ai._task = "deliver_wheat_to_farm"
                return
            if farm_inv.items.get("wheat", 0) >= ai.wheat_threshold and inv.items.get("wheat", 0) == 0 and warehouse_inv:
                qty = farm_inv.items.get("wheat", 0)
                farm_inv.transfer_to(inv, "wheat", qty)
                ai._task = "deliver_wheat"
                return
            if farm_inv.items.get("water", 0) < 1 and well_inv and inv.items.get("water", 0) == 0:
                ai._task = "fetch_water"
                return
        if producer is not None and farm_inv:
            producer.work()

        ai._money_acc += ai.wage * dt
        if inv is not None and ai._money_acc >= 1.0:
            amount = int(ai._money_acc)
            ai._money_acc -= amount
            inv.add_item("money", amount)

    if field_pos and is_at_position(transform.position, field_pos):
        if ai._task == "deliver_water_to_field" and inv and field_inv:
            amt = inv.items.get("water", 0)
            if amt > 0:
                inv.transfer_to(field_inv, "water", amt)
            ai._task = None
            return
        if inv and field_inv and field_inv.items.get("wheat", 0) > 0 and inv.items.get("wheat", 0) == 0:
            qty = field_inv.items.get("wheat", 0)
            field_inv.transfer_to(inv, "wheat", qty)
            ai._task = "deliver_wheat_to_farm"
            return


