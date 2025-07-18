"""
Color constants and visualization parameters
"""

# Color Constants
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
PURPLE = (155, 89, 182)
GREY = (180, 180, 180)
BLUE = (52, 152, 219)
DARK_GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)
SIDEBAR_BG = (240, 240, 240)  # Light Gray for sidebar

# Target Priority Colors
TARGET_HIGH = (255, 0, 0)     # Red - High priority
TARGET_MEDIUM = (255, 165, 0) # Orange - Medium priority  
TARGET_LOW = (0, 255, 0)      # Green - Low priority

# Visualization Parameters
TRAIL_LENGTH = 15
TRAIL_ALPHA = 150
FADING_SPEED = 5
DEFAULT_SPEED = 1
TRAFFIC_LIGHT_CYCLE = 5  # seconds

# Robot Parameters
DEFAULT_BATTERY = 100
DEFAULT_SENSOR_RANGE = 5
DEFAULT_ROBOT_SPEED = 1.0
BATTERY_DRAIN_RATE = 0.1
SPEED_MULTIPLIERS = [0.5, 1.0, 1.5, 2.0]