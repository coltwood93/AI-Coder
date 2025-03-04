"""
DEAP toolbox configuration for the A-Life simulation.
Used for genetic algorithms and organism mutation.
"""

from deap import base, creator, tools
import random
from utils.constants import MUTATION_RATE, SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE

# Create fitness class
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Initialize toolbox
toolbox = base.Toolbox()

# Gene definitions for organisms
# 0: speed (0-5)
# 1: metabolism (0.5-2.0)
# 2: vision (1-3)

# Register gene generators
def random_speed():
    return random.randint(*SPEED_RANGE)

def random_metabolism():
    return METABOLISM_RANGE[0] + random.random() * (METABOLISM_RANGE[1] - METABOLISM_RANGE[0])

def random_vision():
    return random.randint(*VISION_RANGE)

# Register genes
toolbox.register("attr_speed", random_speed)
toolbox.register("attr_metabolism", random_metabolism)
toolbox.register("attr_vision", random_vision)

# Register individual creation
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_speed, toolbox.attr_metabolism, toolbox.attr_vision), n=1)

# Register mutation
def mutate_genes(individual):
    """
    Mutate genes with a chance based on MUTATION_RATE to change:
    - Speed: +/- 1 with bounds [SPEED_RANGE[0], SPEED_RANGE[1]]
    - Metabolism: +/- 0.2 with bounds [METABOLISM_RANGE[0], METABOLISM_RANGE[1]]
    - Vision: +/- 1 with bounds [VISION_RANGE[0], VISION_RANGE[1]]
    """
    # Speed mutation
    if random.random() < MUTATION_RATE:
        individual[0] += random.choice([-1, 1])
        individual[0] = max(SPEED_RANGE[0], min(SPEED_RANGE[1], individual[0]))
    
    # Metabolism mutation
    if random.random() < MUTATION_RATE:
        individual[1] += random.uniform(-0.2, 0.2)
        individual[1] = max(METABOLISM_RANGE[0], min(METABOLISM_RANGE[1], individual[1]))
    
    # Vision mutation
    if random.random() < MUTATION_RATE:
        individual[2] += random.choice([-1, 1])
        individual[2] = max(VISION_RANGE[0], min(VISION_RANGE[1], individual[2]))
    
    return (individual,)

toolbox.register("mutate", mutate_genes)
