import random
from deap import base, creator, tools
from .constants import SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE, MUTATION_RATE

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

def create_random_genome():
    sp = random.randint(SPEED_RANGE[0], SPEED_RANGE[1])
    met = random.uniform(METABOLISM_RANGE[0], METABOLISM_RANGE[1])
    vs = random.randint(VISION_RANGE[0], VISION_RANGE[1])
    return [sp, met, vs]

def custom_mutate(ind):
    if random.random() < MUTATION_RATE:
        ind[0] += random.gauss(0, 1)
    if random.random() < MUTATION_RATE:
        ind[1] += random.gauss(0, 0.1)
    if random.random() < MUTATION_RATE:
        ind[2] += random.gauss(0, 1)

    # clamp
    ind[0] = max(SPEED_RANGE[0], min(SPEED_RANGE[1], ind[0]))
    ind[1] = max(METABOLISM_RANGE[0], min(METABOLISM_RANGE[1], ind[1]))
    ind[2] = max(VISION_RANGE[0], min(VISION_RANGE[1], ind[2]))
    return (ind,)

toolbox.register("individual", tools.initIterate, creator.Individual, create_random_genome)
toolbox.register("mutate", custom_mutate)
