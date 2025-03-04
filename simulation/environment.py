"""
Environment module for the A-Life simulation.

This module handles the environment's state and behavior, including
nutrient distribution, seasons, and climate effects.
"""

import random
import numpy as np
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, SEASON_LENGTH,
    NUTRIENT_DECAY_RATE, NUTRIENT_DIFFUSION_RATE, DISEASE_DURATION,
    BASE_SPAWN_CHANCE_PER_TURN, SUMMER_SPAWN_MULT, WINTER_SPAWN_MULT
)

def current_season(timestep):
    """
    Determine the current season based on the timestep.
    
    Args:
        timestep (int): Current simulation time step
        
    Returns:
        str: "SUMMER" or "WINTER"
    """
    phase = (timestep // SEASON_LENGTH) % 2
    return "WINTER" if phase == 0 else "SUMMER"

def random_border_cell():
    """
    Generate a random cell on the border of the grid.
    
    Returns:
        tuple: (x, y) coordinates on the border
    """
    # Choose which border: top, right, bottom, or left
    border = random.randint(0, 3)
    
    if border == 0:  # Top border
        return (random.randint(0, GRID_WIDTH - 1), 0)
    elif border == 1:  # Right border
        return (GRID_WIDTH - 1, random.randint(0, GRID_HEIGHT - 1))
    elif border == 2:  # Bottom border
        return (random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1)
    else:  # Left border
        return (0, random.randint(0, GRID_HEIGHT - 1))

def spawn_random_organism_on_border(producers, herbivores, carnivores, omnivores, season):
    """
    Randomly spawn a new organism on the border based on chance.
    
    Args:
        producers (list): List of Producer organisms
        herbivores (list): List of Herbivore organisms
        carnivores (list): List of Carnivore organisms
        omnivores (list): List of Omnivore organisms
        season (str): Current season ("SUMMER" or "WINTER")
    """
    from organisms.producer import Producer
    from organisms.herbivore import Herbivore
    from organisms.carnivore import Carnivore
    from organisms.omnivore import Omnivore
    
    # Get spawn chance based on season
    if season == "SUMMER":
        spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * SUMMER_SPAWN_MULT
    else:  # WINTER
        spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * WINTER_SPAWN_MULT
        
    # Check if we should spawn an organism
    if random.random() > spawn_chance:
        return
        
    # Generate coordinates on the border
    x, y = random_border_cell()
    
    # Randomly select which type of organism to spawn
    organism_type = random.choice(["producer", "herbivore", "carnivore", "omnivore"])
    
    # Create the appropriate organism type
    if organism_type == "producer":
        organism = Producer(x, y, 10)
        producers.append(organism)
    elif organism_type == "herbivore":
        organism = Herbivore(x, y, 15)
        herbivores.append(organism)
    elif organism_type == "carnivore":
        organism = Carnivore(x, y, 20)
        carnivores.append(organism)
    else:  # "omnivore"
        organism = Omnivore(x, y, 15)
        omnivores.append(organism)

def disease_outbreak(herbivores, carnivores, omnivores):
    """
    Randomly infect organisms with a disease.
    
    Args:
        herbivores (list): List of Herbivore organisms
        carnivores (list): List of Carnivore organisms
        omnivores (list): List of Omnivore organisms
    """
    # Combine all animals
    all_animals = herbivores + carnivores + omnivores
    if not all_animals:
        return
        
    # Randomly infect some animals (up to 20% of population)
    max_infections = min(5, len(all_animals) // 5 + 1)
    
    # Try to infect random organisms
    for _ in range(max_infections):
        if not all_animals:
            break
            
        # Select a random animal
        idx = random.randint(0, len(all_animals) - 1)
        
        # Only infect if not already infected
        if all_animals[idx].disease_timer == 0 and random.random() < 0.7:
            all_animals[idx].disease_timer = DISEASE_DURATION
            
        # Remove from pool to avoid re-infection
        all_animals.pop(idx)

def update_environment(environment):
    """
    Update the nutrient environment grid.
    
    Args:
        environment (ndarray): The current nutrient environment grid
        
    Returns:
        ndarray: Updated grid after diffusion and decay
    """
    # Create a copy of the environment to avoid modifying during calculation
    new_env = environment.copy()
    
    # Apply nutrient diffusion
    height, width = environment.shape
    
    for y in range(height):
        for x in range(width):
            # For each neighbor direction (N, E, S, W)
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                # Calculate neighbor position with wrapping
                nx = (x + dx) % width
                ny = (y + dy) % height
                
                # Calculate diffusion amount (proportional to concentration difference)
                diff = (environment[y, x] - environment[ny, nx]) * NUTRIENT_DIFFUSION_RATE
                
                # Transfer nutrients
                new_env[y, x] -= diff
                new_env[ny, nx] += diff
    
    # Apply nutrient decay
    new_env *= (1.0 - NUTRIENT_DECAY_RATE)
    
    # Ensure no negative values
    new_env = np.maximum(new_env, 0.0)
    
    return new_env
