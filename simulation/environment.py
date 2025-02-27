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
    NUTRIENT_DECAY_RATE, NUTRIENT_DIFFUSION_RATE
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
    Create and add a random organism on the border of the grid.
    Weighted random selection between different organism types.
    """
    x, y = random_border_cell()
    # Weighted random: 20% Producer, 25% Herb, 25% Carn, 30% Omni
    r = random.random()
    if r < 0.20:
        en = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        producers.append(Producer(x, y, en))
    elif r < 0.45:
        en = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
        herbivores.append(Herbivore(x, y, en))
    elif r < 0.70:
        en = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
        carnivores.append(Carnivore(x, y, en))
    else:
        en = random.randint(*OMNIVORE_INIT_ENERGY_RANGE)
        omnivores.append(Omnivore(x, y, en))

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
    
    # Diffusion - copy to avoid changing the environment during diffusion
    temp_env = environment.copy()
    
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = (x+dx) % GRID_WIDTH, (y+dy) % GRID_HEIGHT
                diff_amt = NUTRIENT_DIFFUSION_RATE * (temp_env[x,y] - temp_env[nx,ny])
                environment[x,y] -= diff_amt
                environment[nx,ny] += diff_amt
    
    return environment
