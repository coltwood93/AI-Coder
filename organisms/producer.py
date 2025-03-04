import random
from utils.constants import (
    PRODUCER_ENERGY_GAIN, PRODUCER_MAX_ENERGY,
    PRODUCER_SEED_COST, PRODUCER_SEED_PROB, PRODUCER_INIT_ENERGY_RANGE,
    PRODUCER_NUTRIENT_CONSUMPTION
)

class Producer:
    # Class variable to track organism IDs
    next_id = 0
    
    @classmethod
    def reset_id_counter(cls):
        """Reset the ID counter to 0."""
        cls.next_id = 0

    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers, herbivores, carnivores, omnivores, environment):
        # Get current grid dimensions to ensure we don't go out of bounds
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        # Ensure coordinates are within bounds (in case grid was resized)
        self.x = self.x % grid_width
        self.y = self.y % grid_height
        
        # Now safely access environment with validated coordinates
        nutrient_taken = min(environment[self.y, self.x], PRODUCER_NUTRIENT_CONSUMPTION)
        self.energy += nutrient_taken * PRODUCER_ENERGY_GAIN
        environment[self.y, self.x] -= nutrient_taken

        # Cap energy at maximum after gains
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
        
        # Use dynamic grid dimensions
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        nx = (self.x + dx) % grid_width
        ny = (self.y + dy) % grid_height
        return nx, ny

    def is_dead(self):
        return self.energy <= 0
