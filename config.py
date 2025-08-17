"""Central configuration for the farm simulation."""

# Display settings
VIEW_WIDTH = 1200
VIEW_HEIGHT = 720
# Narrower sidebar for a less obstructed view
PANEL_WIDTH = 200
FONT_SIZE = 14

# Map editor defaults
SCALE = 5
WORLD_WIDTH = 240
WORLD_HEIGHT = 144
BUILDING_SIZE = 10  # in world units

# World scaling (meters per grid unit and default war map size)
WORLD_SCALE_M = 1.0  # meters per grid unit
DEFAULT_WORLD_W = 1000  # default world width in grid units
DEFAULT_WORLD_H = 600   # default world height in grid units

# Simulation timing
# Use a modest simulation acceleration to keep troop movement visible
FPS = 24
TIME_SCALE = 10  # ten simulated seconds per real second
START_TIME = 8 * 3600 + 0 * 60  # 07:30 in seconds

# Character movement speeds in kilometres per hour
CHARACTER_SPEED = 1.0
CHARACTER_RANDOM_SPEED = 2.0
