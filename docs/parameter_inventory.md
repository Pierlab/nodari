# Parameter inventory

## Nodes

### AIBehaviorNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target_inventory | Optional[InventoryNode] | None |  |
| speed | float | 1.0 |  |
| random_speed | float | 2.0 |  |
| home | Optional[str | SimNode] | None |  |
| work | Optional[str | SimNode] | None |  |
| home_inventory | Optional[str | InventoryNode] | None |  |
| work_inventory | Optional[str | InventoryNode] | None |  |
| well_inventory | Optional[str | InventoryNode] | None |  |
| warehouse_inventory | Optional[str | InventoryNode] | None |  |
| field | Optional[str | SimNode] | None |  |
| field_inventory | Optional[str | InventoryNode] | None |  |
| lunch_position | Optional[List[float]] | None |  |
| wage | float | 1.0 |  |
| idle_chance | float | 0.1 |  |
| wake_hour | float | 6.0 |  |
| work_start_hour | float | 8.0 |  |
| lunch_hour | float | 12.0 |  |
| lunch_end_hour | float | 14.0 |  |
| work_end_hour | float | 18.0 |  |
| sleep_hour | float | 22.0 |  |
| idle_jitter_distance | float | 0.5 |  |
| water_per_fetch | int | 5 |  |
| wheat_threshold | int | 20 |  |
| update_interval | float | None | None |  |
| routine | str | Type[BaseRoutine] | None | None |  |
| kwargs | _empty |  |  |

### AnimalNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| species | str |  |  |
| hunger | NeedNode | None | None |  |
| producer | ResourceProducerNode | None | None |  |
| kwargs | _empty |  |  |

### ArmyNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| goal | str |  |  Current objective of the army: ``"advance"``, ``"defend"`` or ``"retreat"``. |
| size | int | 0 |  Number of unit groups in the army. |
| kwargs | _empty |  |  |

### BarnNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### CharacterNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| gender | str | 'male' |  |
| kwargs | _empty |  |  |

### FarmNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### GeneralNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| style | str |  |  Tactical approach of the general: ``"aggressive"``, ``"defensive"`` or ``"balanced"``. |
| kwargs | _empty |  |  |

### HouseNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### InventoryNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| items | Optional[Dict[str, int]] | None |  |
| kwargs | _empty |  |  |

### NationNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| morale | int |  |  Initial morale value. |
| capital_position | List[int] |  |  ``[x, y]`` coordinates of the nation's capital. |
| kwargs | _empty |  |  |

### NeedNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| need_name | str |  |  |
| threshold | float |  |  |
| increase_rate | float |  |  |
| decrease_rate | float | 0.0 |  |
| value | float | 0.0 |  |
| update_interval | float | None | None |  |
| kwargs | _empty |  |  |

### PastureNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### ResourceProducerNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resource | str |  |  Name of the produced resource. |
| rate_per_tick | int |  |  Quantity produced each time :meth:`work` is called or per tick when ``auto`` is ``True``. |
| inputs | Optional[Dict[str, int]] | None |  Resources consumed from the output inventory before producing. |
| output_inventory | Optional[InventoryNode] | None |  Inventory receiving the produced resource. |
| auto | bool | True |  If ``True`` (default) production happens automatically every update. |
| kwargs | _empty |  |  |

### SiloNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| capacity | int | None | None |  |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### TerrainNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tiles | List[List[str]] |  |  Two-dimensional list describing the terrain type at each map position. |
| speed_modifiers | Optional[Dict[str, float]] | None | None |  Optional mapping of terrain type to movement speed modifier. |
| combat_bonuses | Optional[Dict[str, int]] | None | None |  Optional mapping of terrain type to combat bonus value. |
| obstacles | Optional[List[List[int]]] | None | None |  Optional list of impassable ``[x, y]`` coordinates. |
| kwargs | _empty |  |  |

### TransformNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position | List[float] | None | None |  Initial position in meters. Defaults to ``[0.0, 0.0]``. |
| velocity | List[float] | None | None |  Initial velocity in meters per second. Defaults to ``[0.0, 0.0]``. |
| kwargs | _empty |  |  |

### UnitNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| size | int | 100 |  Number of soldiers in this unit. |
| state | str | 'idle' |  Current state of the unit: ``"idle"``, ``"moving"``, ``"fighting"`` or ``"fleeing"``. |
| speed | float | 1.0 |  Movement speed of the unit. |
| morale | int | 100 |  Morale value of the unit. |
| target | list[int] | None | None |  Optional ``[x, y]`` coordinates the unit is moving toward. |
| kwargs | _empty |  |  |

### WarehouseNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | None | None |  |
| height | int | None | None |  |
| kwargs | _empty |  |  |

### WellNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | 10 |  |
| height | int | 10 |  |
| kwargs | _empty |  |  |

### WorldNode

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | 100 |  Width of the world map in meters. |
| height | int | 100 |  Height of the world map in meters. |
| seed | int | None | None |  Optional seed for global random number generation to make simulations deterministic. |
| kwargs | _empty |  |  |

## Systems

### CombatSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| terrain | TerrainNode | str | None | None |  Reference to the :class:`TerrainNode` providing combat bonuses. If a string is supplied the node with this id is looked up on first update. |
| kwargs | _empty |  |  |

### DistanceSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| kwargs | _empty |  |  |

### EconomySystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| base_prices | dict[str, float] | None | None |  |
| kwargs | _empty |  |  |

### LoggingSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| events | Optional[Iterable[str]] | None |  Iterable of event names to log. If ``None``, a default set of common events is used. |
| logger | Optional[logging.Logger] | None |  Optional :class:`logging.Logger` instance. Defaults to one named after the system. |
| kwargs | _empty |  |  |

### MoralSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collapse_threshold | int | 0 |  Morale value at or below which a nation collapses. |
| kwargs | _empty |  |  |

### MovementSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| terrain | TerrainNode | str | None | None |  Reference to the :class:`TerrainNode` providing tile modifiers. If a string is supplied the node with this id is looked up on first update. |
| obstacles | Optional[List[List[int]]] | None | None |  Additional impassable ``[x, y]`` coordinates merged with terrain obstacles. |
| kwargs | _empty |  |  |

### PygameViewerSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width | int | 1200 |  |
| height | int | 720 |  |
| scale | float | 5.0 |  Scale applied to positions stored in :class:`TransformNode`s. |
| panel_width | int | 320 |  Width of the information panel appended to the right of the view. |
| font_size | int | 14 |  Font size used to render the panel text. |
| kwargs | _empty |  |  |

### SchedulerSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| kwargs | _empty |  |  |

### TimeSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tick_duration | float | 1.0 |  |
| phase_length | int | 10 |  |
| start_time | float | 0.0 |  |
| time_scale | float | 1.0 |  |
| kwargs | _empty |  |  |

### WeatherSystem

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| states | List[str] | None | None |  |
| change_interval | float | 3600.0 |  |
| kwargs | _empty |  |  |
