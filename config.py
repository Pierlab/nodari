"""Central configuration for the farm simulation."""

# Display settings
VIEW_WIDTH = 1200
VIEW_HEIGHT = 720
PANEL_WIDTH = 320
FONT_SIZE = 14

# Map editor defaults
SCALE = 5
WORLD_WIDTH = 240
WORLD_HEIGHT = 144
BUILDING_SIZE = 10  # in world units

# Simulation timing
FPS = 24
TIME_SCALE = 600  # one simulated minute per real second
START_TIME = 8 * 3600 + 0 * 60  # 07:30 in seconds

# Character movement speeds in kilometres per hour
CHARACTER_SPEED = 1.0
CHARACTER_RANDOM_SPEED = 2.0
