# Map editor

The map editor in `tools/map_editor.py` is a lightweight layout tool. It lets you
place buildings and characters on a grid and export the result as JSON. The
exported file only describes spatial information; behavioural logic and systems
are added separately.

## Usage

```
python tools/map_editor.py [output.json] [keymap.json] [existing_map.json]
```

* **Left click** – place current item or select when in *select* mode.
* **Right click** – delete item under cursor.
* **1-6** – choose building type.
* **M/F** – male/female character.
* **S** – enter select/resize mode.
* **Arrow keys** – resize selected building.
* **Z** – undo last placement.
* **E** – export map.

Passing a previous map as `existing_map.json` loads its contents for further
editing.

To transform the exported layout into a runnable farm scenario use
`tools/build_farm_scenario.py`:

```
python tools/build_farm_scenario.py custom_map.json scenario.json
```

This adds basic inventories and core systems (time, economy, viewer…) to the
map file.
