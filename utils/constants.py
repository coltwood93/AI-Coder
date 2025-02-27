import pygame

# Desired minimum window dimensions
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Grid dimensions (number of cells)
GRID_WIDTH, GRID_HEIGHT = 20, 20

# Calculate cell size to fit at least the minimum window dimensions
# but maintain proportionality
BASE_CELL_SIZE = 20  # Default size if no stretching needed

# Calculate what cell size would be needed to reach minimum dimensions
width_cell_size = MIN_WINDOW_WIDTH / GRID_WIDTH
height_cell_size = MIN_WINDOW_HEIGHT / GRID_HEIGHT

# Use the larger of the two to ensure we meet or exceed both minimum dimensions
CELL_SIZE = max(BASE_CELL_SIZE, width_cell_size, height_cell_size)

STATS_PANEL_WIDTH = 220
WINDOW_WIDTH = int(GRID_WIDTH * CELL_SIZE + STATS_PANEL_WIDTH)
WINDOW_HEIGHT = int(GRID_HEIGHT * CELL_SIZE)

# Producers
INITIAL_PRODUCERS = 15
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.18
PRODUCER_INIT_ENERGY_RANGE = (5, 15)
PRODUCER_NUTRIENT_CONSUMPTION = 0.1

# Herbivores
INITIAL_HERBIVORES = 10
HERBIVORE_INIT_ENERGY_RANGE = (5, 25)
HERBIVORE_REPRO_THRESHOLD = 26
EAT_GAIN_HERBIVORE = 6  # Gains when eating producers

# Carnivores
INITIAL_CARNIVORES = 10
CARNIVORE_INIT_ENERGY_RANGE = (15, 35)
CARNIVORE_REPRO_THRESHOLD = 27
EAT_GAIN_CARNIVORE = 10  # Gains when eating herbivores

# Omnivores
INITIAL_OMNIVORES = 3
OMNIVORE_INIT_ENERGY_RANGE = (5, 25)
OMNIVORE_REPRO_THRESHOLD = 28
EAT_GAIN_OMNIVORE_PLANT = 3  # Gains when eating producers
EAT_GAIN_OMNIVORE_ANIMAL = 5 # Gains when eating herbivores

# Additional Realism
MAX_LIFESPAN_HERBIVORE = 300
MAX_LIFESPAN_CARNIVORE = 250
MAX_LIFESPAN_OMNIVORE = 280
REPRODUCTION_COOLDOWN = 10

# Energy & Movement
BASE_LIFE_COST = 1.5
MOVE_COST_FACTOR = 0.3

# Genes & Mutation
MUTATION_RATE = 0.1
SPEED_RANGE = (0, 5)
METABOLISM_RANGE = (0.5, 2.0)
VISION_RANGE = (1, 3)

# Seasons
SEASON_LENGTH = 50   # Switch every 50 timesteps

# Disease System
DISEASE_CHANCE_PER_TURN = 0.01  # 1% chance each turn for disease event
DISEASE_ENERGY_DRAIN_MULTIPLIER = 1.3  # If infected, life cost goes up 30%
DISEASE_DURATION = 40  # Ticks an infected animal remains infected

# Misc
CRITICAL_ENERGY = 8     # Force random movement if below this
DISCOVERY_BONUS = 0.2
TRACK_CELL_HISTORY_LEN = 20
MAX_TIMESTEPS = 400
FPS = 6

# Random border spawn
BASE_SPAWN_CHANCE_PER_TURN = 0.15  # nominal spawn chance
WINTER_SPAWN_MULT = 0.5            # e.g., in winter 1/2 spawn chance
SUMMER_SPAWN_MULT = 1.2            # e.g., in summer 20% more than base

# Nutrient environment
INITIAL_NUTRIENT_LEVEL = 0.5
NUTRIENT_DIFFUSION_RATE = 0.1
NUTRIENT_DECAY_RATE = 0.01
CONSUMER_NUTRIENT_RELEASE = 0.5  # Increased nutrient release

# Pygame keys
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT
