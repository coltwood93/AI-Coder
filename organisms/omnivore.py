import copy
import random  # Add import for random
from deap import creator
from utils.constants import (
    BASE_LIFE_COST, DISEASE_ENERGY_DRAIN_MULTIPLIER,
    MOVE_COST_FACTOR, CRITICAL_ENERGY, DISCOVERY_BONUS, TRACK_CELL_HISTORY_LEN,
    OMNIVORE_REPRO_THRESHOLD, EAT_GAIN_OMNIVORE_PLANT, EAT_GAIN_OMNIVORE_ANIMAL,
    MAX_LIFESPAN_OMNIVORE, REPRODUCTION_COOLDOWN, EAT_GAIN_CARNIVORE, CONSUMER_NUTRIENT_RELEASE
)
from utils.toolbox import toolbox

class Omnivore:
    # Class variable to track organism IDs
    next_id = 0
    
    @classmethod
    def reset_id_counter(cls):
        """Reset the ID counter to 0."""
        cls.next_id = 0

    """
    NEW SPECIES: can eat both producers AND herbivores.
    Gains EAT_GAIN_OMNIVORE_PLANT from producers, EAT_GAIN_OMNIVORE_ANIMAL from herbivores.
    Also can clash with carnivores:
      60% carnivore kills omnivore,
      15% omnivore kills carnivore,
      25% pass peacefully.
    """
    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        self.age = 0
        self.max_lifespan = MAX_LIFESPAN_OMNIVORE
        self.repro_cooldown_timer = 0
        self.disease_timer = 0

        self.id = Omnivore.next_id
        Omnivore.next_id += 1

        if genes is None:
            self.genes = toolbox.individual()
        else:
            self.genes = genes
        self.recent_cells = [(x, y)]

    @property
    def speed(self):
        return int(self.genes[0])

    @property
    def metabolism(self):
        return float(self.genes[1])

    @property
    def vision(self):
        return int(self.genes[2])

    def is_infected(self):
        return self.disease_timer > 0

    def update(self, producers, herbivores, carnivores, omnivores, environment):
        # Get current grid dimensions to ensure we don't go out of bounds
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        # Ensure coordinates are within bounds (in case grid was resized)
        self.x = self.x % grid_width
        self.y = self.y % grid_height
        
        # baseline cost
        life_cost = BASE_LIFE_COST
        if self.is_infected():
            life_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
            self.disease_timer -= 1
        self.energy -= life_cost

        self.age += 1
        if self.repro_cooldown_timer > 0:
            self.repro_cooldown_timer -= 1

        if self.energy <= 0:
            return
        if self.age > self.max_lifespan:
            # Add nutrients back to environment when dying of old age - use [y, x] order
            environment[self.y, self.x] += CONSUMER_NUTRIENT_RELEASE
            self.energy = -1
            return

        # Omnivore tries to find whichever is closer: a herbivore or a producer
        h_dir, h_dist = self.find_nearest_herbivore(herbivores)
        p_dir, p_dist = self.find_nearest_producer(producers)
        target_dir = None
        target_type = None

        if h_dir and p_dir:
            if h_dist < p_dist:
                target_dir = h_dir
                target_type = "HERB"
            else:
                target_dir = p_dir
                target_type = "PLANT"
        elif h_dir:
            target_dir = h_dir
            target_type = "HERB"
        elif p_dir:
            target_dir = p_dir
            target_type = "PLANT"

        if target_dir:
            # Move up to speed steps
            for _ in range(self.speed):
                self.move_towards(target_dir, omnivores)
                move_cost = MOVE_COST_FACTOR * self.metabolism
                if self.is_infected():
                    move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                self.energy -= move_cost
                if self.energy <= 0:
                    # Add nutrients back to environment when dying of starvation during movement
                    environment[self.y, self.x] += CONSUMER_NUTRIENT_RELEASE
                    return

                if target_type == "HERB":
                    if self.check_and_eat_herb(herbivores):
                        break
                else:
                    if self.check_and_eat_plant(producers):
                        break
        else:
            # No target in sight
            if self.energy < CRITICAL_ENERGY:
                forced_steps = max(1, self.speed)
                for _ in range(forced_steps):
                    self.move_random(omnivores)
                    move_cost = MOVE_COST_FACTOR * self.metabolism
                    if self.is_infected():
                        move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                    self.energy -= move_cost
                    if self.energy <= 0:
                        # Add nutrients back to environment when dying of starvation during movement
                        environment[self.y, self.x] += CONSUMER_NUTRIENT_RELEASE
                        return
                    # possibly ate something
                    if self.check_and_eat_herb(herbivores):
                        return
                    if self.check_and_eat_plant(producers):
                        return
            else:
                self.move_random(omnivores)
                move_cost = MOVE_COST_FACTOR * self.metabolism
                if self.is_infected():
                    move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                self.energy -= move_cost
                if self.energy <= 0:
                    # Add nutrients back to environment when dying of starvation during movement
                    environment[self.y, self.x] += CONSUMER_NUTRIENT_RELEASE
                    return
                self.check_and_eat_herb(herbivores)
                self.check_and_eat_plant(producers)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # after normal movement/eating, see if we share a cell with a carnivore
        # handle the 60/15/25 logic
        if self.energy > 0:  # still alive
            self.check_carnivore_encounter(carnivores)

        # reproduce
        if self.energy >= OMNIVORE_REPRO_THRESHOLD and self.repro_cooldown_timer == 0:
            self.reproduce(omnivores)

    def check_carnivore_encounter(self, carnivores):
        """
        If an omnivore and a carnivore share the same cell,
         60% carnivore kills omnivore,
         15% omnivore kills carnivore,
         25% pass peacefully.
        We handle only the FIRST carnivore found in this cell.
        """
        for i, c in enumerate(carnivores):
            if c.x == self.x and c.y == self.y and not c.is_dead() and not self.is_dead():
                r = random.random()
                if r < 0.80:
                    # carnivore kills omnivore
                    c.energy += EAT_GAIN_CARNIVORE
                    self.energy = -1  # effectively kills the omnivore
                elif r < 0.93:
                    # omnivore kills carnivore
                    self.energy += EAT_GAIN_OMNIVORE_ANIMAL
                    carnivores.pop(i)
                # else pass peacefully, do nothing
                return  # only handle one carnivore at a time

    def find_nearest_herbivore(self, herbivores):
        best_dist = self.vision + 1
        found = False
        best_dx, best_dy = 0,0
        for h in herbivores:
            dx = h.x - self.x
            dy = h.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        return ((best_dx, best_dy), best_dist) if found else (None, None)

    def find_nearest_producer(self, producers):
        best_dist = self.vision + 1
        found = False
        best_dx, best_dy = 0,0
        for p in producers:
            dx = p.x - self.x
            dy = p.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        return ((best_dx, best_dy), best_dist) if found else (None, None)

    def move_towards(self, direction, omnivores):
        dx, dy = direction
        
        # Use dynamic grid dimensions
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % grid_width
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % grid_height
        if not self.cell_occupied(nx, ny, omnivores):
            self.x, self.y = nx, ny
        else:
            self.move_random(omnivores)

    def move_random(self, omnivores):
        tries = 5
        
        # Use dynamic grid dimensions
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        for _ in range(tries):
            d = random.choice(["UP","DOWN","LEFT","RIGHT"])
            nx, ny = self.x, self.y
            if d=="UP":
                ny = (ny - 1) % grid_height
            elif d=="DOWN":
                ny = (ny + 1) % grid_height
            elif d=="LEFT":
                nx = (nx - 1) % grid_width
            elif d=="RIGHT":
                nx = (nx + 1) % grid_width
            if not self.cell_occupied(nx, ny, omnivores):
                self.x, self.y = nx, ny
                return

    def cell_occupied(self, tx, ty, omnivores):
        for o in omnivores:
            if o is not self and o.x == tx and o.y == ty:
                return True
        return False

    def check_and_eat_herb(self, herbivores):
        for i in range(len(herbivores)):
            h = herbivores[i]
            if h.x == self.x and h.y == self.y:
                self.energy += EAT_GAIN_OMNIVORE_ANIMAL
                herbivores.pop(i)
                return True
        return False

    def check_and_eat_plant(self, producers):
        for i in range(len(producers)):
            p = producers[i]
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN_OMNIVORE_PLANT
                producers.pop(i)
                return True
        return False

    def reproduce(self, omnivores):
        child_energy = self.energy // 2
        self.energy -= child_energy
        cloned = copy.deepcopy(self.genes)
        cloned = creator.Individual(cloned)
        (cloned,) = toolbox.mutate(cloned)
        new_genome = list(cloned)
        baby = Omnivore(self.x, self.y, child_energy, new_genome, self.generation+1)
        baby.repro_cooldown_timer = REPRODUCTION_COOLDOWN
        omnivores.append(baby)
        self.repro_cooldown_timer = REPRODUCTION_COOLDOWN

    def is_dead(self):
        return self.energy <= 0
