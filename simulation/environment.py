"""
Environment-related functions for the A-Life simulation.
Handles seasons, disease, nutrient diffusion, and random organism spawning.
"""

import random
import numpy as np
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, SEASON_LENGTH, DISEASE_DURATION,
    PRODUCER_INIT_ENERGY_RANGE, HERBIVORE_INIT_ENERGY_RANGE,
    CARNIVORE_INIT_ENERGY_RANGE, OMNIVORE_INIT_ENERGY_RANGE,
    NUTRIENT_DECAY_RATE, NUTRIENT_DIFFUSION_RATE,
    BASE_SPAWN_CHANCE_PER_TURN, WINTER_SPAWN_MULT, SUMMER_SPAWN_MULT  # Add these imports
)
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from organisms.omnivore import Omnivore

def current_season(timestep):
    """
    Determine the current season based on timestep.
    Simple 2-season cycle: Winter/Summer each SEASON_LENGTH steps
    """
    cycle = (timestep // SEASON_LENGTH) % 2
    return "WINTER" if cycle == 0 else "SUMMER"

def random_border_cell():
    """
    Generate coordinates for a random cell on the edge of the grid.
    """
    side = random.choice(["TOP", "BOTTOM", "LEFT", "RIGHT"])
    if side == "TOP":
        return (random.randint(0, GRID_WIDTH - 1), 0)
    elif side == "BOTTOM":
        return (random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1)
    elif side == "LEFT":
        return (0, random.randint(0, GRID_HEIGHT - 1))
    else:
        return (GRID_WIDTH - 1, random.randint(0, GRID_HEIGHT - 1))

def spawn_random_organism_on_border(producers, herbivores, carnivores, omnivores, season):
    """
    Spawn a random organism on the grid border based on season.
    
    Args:
        producers (list): List of producer organisms
        herbivores (list): List of herbivore organisms
        carnivores (list): List of carnivore organisms
        omnivores (list): List of omnivore organisms
        season (str): Current season ("SUMMER" or "WINTER")
    """
    # Update grid width and height dynamically
    from utils.config_manager import ConfigManager
    config = ConfigManager()
    grid_width = config.get_grid_width()
    grid_height = config.get_grid_height()
    
    # Adjust spawn chance based on season
    if season == "SUMMER":
        spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * SUMMER_SPAWN_MULT
    else:  # WINTER
        spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * WINTER_SPAWN_MULT
    
    # Check if spawning should happen
    if random.random() > spawn_chance:
        return
    
    # Generate random border position using correct grid dimensions
    border = random.randint(0, 3)
    if border == 0:  # Top
        x, y = random.randint(0, grid_width - 1), 0
    elif border == 1:  # Right
        x, y = grid_width - 1, random.randint(0, grid_height - 1)
    elif border == 2:  # Bottom
        x, y = random.randint(0, grid_width - 1), grid_height - 1
    else:  # Left
        x, y = 0, random.randint(0, grid_height - 1)
    
    # Randomly choose organism type with weighted probabilities
    organism_type = random.choices(
        ["producer", "herbivore", "carnivore", "omnivore"],
        weights=[0.5, 0.25, 0.15, 0.1],
        k=1
    )[0]
    
    # Create organism based on type
    if organism_type == "producer":
        energy = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        producers.append(Producer(x, y, energy))
    elif organism_type == "herbivore":
        energy = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
        herbivores.append(Herbivore(x, y, energy))
    elif organism_type == "carnivore":
        energy = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
        carnivores.append(Carnivore(x, y, energy))
    else:  # omnivore
        energy = random.randint(*OMNIVORE_INIT_ENERGY_RANGE)
        omnivores.append(Omnivore(x, y, energy))

def disease_outbreak(herbivores, carnivores, omnivores):
    """
    Infect a small subset of animals for DISEASE_DURATION.
    We'll pick e.g., 5 random animals total to infect (if that many exist).
    """
    all_animals = herbivores + carnivores + omnivores
    if len(all_animals) == 0:
        return
    k = min(5, len(all_animals))
    infected = random.sample(all_animals, k)
    for a in infected:
        a.disease_timer = DISEASE_DURATION

def update_environment(environment):
    """
    Update the nutrient environment:
    - Decay nutrients naturally
    - Diffuse nutrients between cells
    """
    environment -= NUTRIENT_DECAY_RATE
    environment = np.maximum(environment, 0)  # Ensure we don't go below zero
    
    # Get current grid dimensions directly from the environment array
    grid_height, grid_width = environment.shape
    
    # Diffusion - copy to avoid changing the environment during diffusion
    temp_env = environment.copy()
    
    for y in range(grid_height):
        for x in range(grid_width):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = (x+dx) % grid_width, (y+dy) % grid_height
                diff_amt = NUTRIENT_DIFFUSION_RATE * (temp_env[y,x] - temp_env[ny,nx])
                environment[y,x] -= diff_amt
                environment[ny,nx] += diff_amt
    
    return environment
