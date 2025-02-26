import random
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, PRODUCER_ENERGY_GAIN, PRODUCER_MAX_ENERGY,
    PRODUCER_SEED_COST, PRODUCER_SEED_PROB, PRODUCER_INIT_ENERGY_RANGE,
    PRODUCER_NUTRIENT_CONSUMPTION
)

class Producer:
    next_id = 0
    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers, herbivores, carnivores, omnivores, environment):
        nutrient_taken = min(environment[self.x, self.y], PRODUCER_NUTRIENT_CONSUMPTION)
        self.energy += nutrient_taken * PRODUCER_ENERGY_GAIN
        environment[self.x, self.y] -= nutrient_taken

        if self.energy > PRODUCER_MAX_ENERGY:
            self.energy = PRODUCER_MAX_ENERGY

        # Possibly seed
        if self.energy > PRODUCER_SEED_COST and random.random() < PRODUCER_SEED_PROB:
            self.energy -= PRODUCER_SEED_COST
            nx, ny = self.random_adjacent()
            if not any(p.x == nx and p.y == ny for p in producers):
                en = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
                baby = Producer(nx, ny, en)
                producers.append(baby)

    def random_adjacent(self):
        dirs = [(-1,0),(1,0),(0,-1),(0,1),
                (-1,-1),(1,1),(-1,1),(1,-1)]
        dx, dy = random.choice(dirs)
        nx = (self.x + dx) % GRID_WIDTH
        ny = (self.y + dy) % GRID_HEIGHT
        return nx, ny

    def is_dead(self):
        return self.energy <= 0
