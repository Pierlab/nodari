from nodes.terrain import TerrainNode


def test_tile_lookup_and_modifiers():
    tiles = [["plain", "forest"], ["hill", "plain"]]
    terrain = TerrainNode(tiles=tiles)

    assert terrain.get_tile(0, 0) == "plain"
    assert terrain.get_tile(1, 0) == "forest"
    assert terrain.get_speed_modifier(1, 0) == 0.7
    assert terrain.get_combat_bonus(0, 1) == 2


def test_custom_modifiers():
    tiles = [["forest"]]
    terrain = TerrainNode(
        tiles=tiles,
        speed_modifiers={"forest": 0.5},
        combat_bonuses={"forest": 3},
    )

    assert terrain.get_speed_modifier(0, 0) == 0.5
    assert terrain.get_combat_bonus(0, 0) == 3
