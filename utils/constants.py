"""
Constants for the A-Life simulation.

These are the default values that will be overridden by user configuration.
"""

import pygame

# Default display constants
DEFAULT_GRID_WIDTH = 20
DEFAULT_GRID_HEIGHT = 20

# Default organism counts
DEFAULT_INITIAL_PRODUCERS = 15
DEFAULT_INITIAL_HERBIVORES = 10
DEFAULT_INITIAL_CARNIVORES = 10
DEFAULT_INITIAL_OMNIVORES = 3

# Default simulation settings
DEFAULT_SIMULATION_SPEED = 1.0
DEFAULT_FPS = 15

# These values will be replaced at runtime with values from config_manager
# Keep them here as initial values until config is loaded
GRID_WIDTH = DEFAULT_GRID_WIDTH
GRID_HEIGHT = DEFAULT_GRID_HEIGHT

INITIAL_PRODUCERS = DEFAULT_INITIAL_PRODUCERS
INITIAL_HERBIVORES = DEFAULT_INITIAL_HERBIVORES
INITIAL_CARNIVORES = DEFAULT_INITIAL_CARNIVORES
INITIAL_OMNIVORES = DEFAULT_INITIAL_OMNIVORES

SIMULATION_SPEED = DEFAULT_SIMULATION_SPEED
FPS = DEFAULT_FPS

# Fixed window dimensions
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 720

# Stats panel width
STATS_PANEL_WIDTH = 250

# These values will be calculated dynamically when applying configuration
GRID_DISPLAY_WIDTH = WINDOW_WIDTH - STATS_PANEL_WIDTH
GRID_DISPLAY_HEIGHT = WINDOW_HEIGHT
CELL_SIZE_X = GRID_DISPLAY_WIDTH / GRID_WIDTH
CELL_SIZE_Y = GRID_DISPLAY_HEIGHT / GRID_HEIGHT
CELL_SIZE = min(CELL_SIZE_X, CELL_SIZE_Y)

# Energy ranges for initialization
PRODUCER_INIT_ENERGY_RANGE = (5, 15)
HERBIVORE_INIT_ENERGY_RANGE = (5, 25)
CARNIVORE_INIT_ENERGY_RANGE = (15, 35)
OMNIVORE_INIT_ENERGY_RANGE = (5, 25)

# Energy dynamics
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.18

EAT_GAIN_HERBIVORE = 6
EAT_GAIN_CARNIVORE = 10
EAT_GAIN_OMNIVORE_PLANT = 3
EAT_GAIN_OMNIVORE_ANIMAL = 5

HERBIVORE_REPRO_THRESHOLD = 26
CARNIVORE_REPRO_THRESHOLD = 27
OMNIVORE_REPRO_THRESHOLD = 28

MAX_LIFESPAN_HERBIVORE = 300
MAX_LIFESPAN_CARNIVORE = 250
MAX_LIFESPAN_OMNIVORE = 280

REPRODUCTION_COOLDOWN = 10

# Environment dynamics
BASE_LIFE_COST = 1.5
MOVE_COST_FACTOR = 0.3
CRITICAL_ENERGY = 8
DISCOVERY_BONUS = 0.2
TRACK_CELL_HISTORY_LEN = 20

NUTRIENT_DECAY_RATE = 0.01
NUTRIENT_DIFFUSION_RATE = 0.1
INITIAL_NUTRIENT_LEVEL = 0.5
PRODUCER_NUTRIENT_CONSUMPTION = 0.1
CONSUMER_NUTRIENT_RELEASE = 0.5

# Seasons and Disease
SEASON_LENGTH = 50
DISEASE_CHANCE_PER_TURN = 0.01
DISEASE_DURATION = 40
DISEASE_ENERGY_DRAIN_MULTIPLIER = 1.3

# Spawning
BASE_SPAWN_CHANCE_PER_TURN = 0.15
WINTER_SPAWN_MULT = 0.5
SUMMER_SPAWN_MULT = 1.2

# Game controls
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT

# Simulation limits
MAX_TIMESTEPS = 400

# Genetics & Mutation
MUTATION_RATE = 0.1
SPEED_RANGE = (0, 5)
METABOLISM_RANGE = (0.5, 2.0)
VISION_RANGE = (1, 3)

# Function to update constants from config manager
def update_from_config(config_manager):
    """Update global constants from the configuration manager."""
    global GRID_WIDTH, GRID_HEIGHT
    global INITIAL_PRODUCERS, INITIAL_HERBIVORES, INITIAL_CARNIVORES, INITIAL_OMNIVORES
    global SIMULATION_SPEED, FPS
    global CELL_SIZE, CELL_SIZE_X, CELL_SIZE_Y, GRID_DISPLAY_WIDTH, GRID_DISPLAY_HEIGHT
    
    # Update grid size
    GRID_WIDTH = config_manager.get_grid_width()
    GRID_HEIGHT = config_manager.get_grid_height()
    
    # Update initial organism counts
    INITIAL_PRODUCERS = config_manager.get_initial_count("producers")
    INITIAL_HERBIVORES = config_manager.get_initial_count("herbivores")
    INITIAL_CARNIVORES = config_manager.get_initial_count("carnivores")
    INITIAL_OMNIVORES = config_manager.get_initial_count("omnivores")
    
    # Update simulation settings
    SIMULATION_SPEED = config_manager.get_simulation_speed()
    FPS = config_manager.get_fps()
    
    # Recalculate derived values
    GRID_DISPLAY_WIDTH = WINDOW_WIDTH - STATS_PANEL_WIDTH
    GRID_DISPLAY_HEIGHT = WINDOW_HEIGHT
    CELL_SIZE_X = GRID_DISPLAY_WIDTH / GRID_WIDTH
    CELL_SIZE_Y = GRID_DISPLAY_HEIGHT / GRID_HEIGHT
    CELL_SIZE = min(CELL_SIZE_X, CELL_SIZE_Y)
    
    print(f"Updated constants: Grid {GRID_WIDTH}x{GRID_HEIGHT}, Speed {SIMULATION_SPEED}, FPS {FPS}")
