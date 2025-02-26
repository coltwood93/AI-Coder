import random
import copy
from deap import creator
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, BASE_LIFE_COST, DISEASE_ENERGY_DRAIN_MULTIPLIER,
    MOVE_COST_FACTOR, CRITICAL_ENERGY, DISCOVERY_BONUS, TRACK_CELL_HISTORY_LEN,
    HERBIVORE_REPRO_THRESHOLD, EAT_GAIN_HERBIVORE, MAX_LIFESPAN_HERBIVORE,
    REPRODUCTION_COOLDOWN, SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE,
    CONSUMER_NUTRIENT_RELEASE
)
from utils.toolbox import toolbox

class Herbivore:
    next_id = 0
    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        self.age = 0
        self.max_lifespan = MAX_LIFESPAN_HERBIVORE
        self.repro_cooldown_timer = 0
        self.disease_timer = 0  # If >0, we are infected

        self.id = Herbivore.next_id
        Herbivore.next_id += 1

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
        # baseline cost
        life_cost = BASE_LIFE_COST
        if self.is_infected():
            life_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
            self.disease_timer -= 1  # reduce infection timer

        self.energy -= life_cost
        self.age += 1
        if self.repro_cooldown_timer > 0:
            self.repro_cooldown_timer -= 1

        if self.energy <= 0:
            return
        if self.age > self.max_lifespan:
            environment[self.x, self.y] += CONSUMER_NUTRIENT_RELEASE
            self.energy = -1
            return

        # run away from carnivores or omnivores if in range
        c_dir = self.find_nearest_predator(carnivores, omnivores)
        if c_dir:
            self.run_away(c_dir, herbivores)
        else:
            # chase producers
            p_dir = self.find_nearest_producer(producers)
            if p_dir:
                for _ in range(self.speed):
                    self.move_towards(p_dir, herbivores)
                    move_cost = MOVE_COST_FACTOR * self.metabolism
                    if self.is_infected():
                        move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                    self.energy -= move_cost
                    if self.energy <= 0:
                        environment[self.x, self.y] += CONSUMER_NUTRIENT_RELEASE
                        return
                    if self.check_and_eat_producer(producers):
                        break
            else:
                if self.energy < CRITICAL_ENERGY:
                    forced_steps = max(1, self.speed)
                    for _ in range(forced_steps):
                        self.move_random(herbivores)
                        move_cost = MOVE_COST_FACTOR * self.metabolism
                        if self.is_infected():
                            move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                        self.energy -= move_cost
                        if self.energy <= 0:
                            environment[self.x, self.y] += CONSUMER_NUTRIENT_RELEASE
                            return
                        if self.check_and_eat_producer(producers):
                            break
                else:
                    self.move_random(herbivores)
                    move_cost = MOVE_COST_FACTOR * self.metabolism
                    if self.is_infected():
                        move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                    self.energy -= move_cost
                    if self.energy <= 0:
                        environment[self.x, self.y] += CONSUMER_NUTRIENT_RELEASE
                        return
                    self.check_and_eat_producer(producers)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # reproduce
        if self.energy >= HERBIVORE_REPRO_THRESHOLD and self.repro_cooldown_timer == 0:
            self.reproduce(herbivores)

    def find_nearest_predator(self, carnivores, omnivores):
        best_dist = self.vision + 1
        best_dx, best_dy = 0, 0
        found = False
        # check carnivores
        for c in carnivores:
            dx = c.x - self.x
            dy = c.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        # check omnivores
        for o in omnivores:
            dx = o.x - self.x
            dy = o.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        return (best_dx, best_dy) if found else None

    def run_away(self, c_dir, herbivores):
        dx, dy = c_dir
        opp_dir = (-dx, -dy)
        for _ in range(self.speed):
            self.move_towards(opp_dir, herbivores)
            move_cost = MOVE_COST_FACTOR * self.metabolism
            if self.is_infected():
                move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
            self.energy -= move_cost
            if self.energy <= 0:
                return

    def find_nearest_producer(self, producers):
        best_dist = self.vision + 1
        found = False
        best_dx, best_dy = 0, 0
        for p in producers:
            dx = p.x - self.x
            dy = p.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        if not found:
            return None
        return (best_dx, best_dy)

    def move_towards(self, direction, herbivores):
        dx, dy = direction
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % GRID_WIDTH
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % GRID_HEIGHT
        if not self.cell_occupied(nx, ny, herbivores):
            self.x, self.y = nx, ny
        else:
            self.move_random(herbivores)

    def move_random(self, herbivores):
        tries = 5
        for _ in range(tries):
            d = random.choice(["UP","DOWN","LEFT","RIGHT"])
            nx, ny = self.x, self.y
            if d=="UP":
                ny = (ny - 1) % GRID_HEIGHT
            elif d=="DOWN":
                ny = (ny + 1) % GRID_HEIGHT
            elif d=="LEFT":
                nx = (nx - 1) % GRID_WIDTH
            elif d=="RIGHT":
                nx = (nx + 1) % GRID_WIDTH
            if not self.cell_occupied(nx, ny, herbivores):
                self.x, self.y = nx, ny
                return

    def cell_occupied(self, tx, ty, herbivores):
        for h in herbivores:
            if h is not self and h.x == tx and h.y == ty:
                return True
        return False

    def check_and_eat_producer(self, producers):
        for i in range(len(producers)):
            p = producers[i]
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN_HERBIVORE
                producers.pop(i)
                return True
        return False

    def reproduce(self, herbivores):
        child_energy = self.energy // 2
        self.energy -= child_energy
        cloned = copy.deepcopy(self.genes)
        cloned = creator.Individual(cloned)
        (cloned,) = toolbox.mutate(cloned)
        new_genome = list(cloned)
        baby = Herbivore(self.x, self.y, child_energy, new_genome, self.generation+1)
        baby.repro_cooldown_timer = REPRODUCTION_COOLDOWN
        herbivores.append(baby)
        self.repro_cooldown_timer = REPRODUCTION_COOLDOWN

    def is_dead(self):
        return self.energy <= 0
