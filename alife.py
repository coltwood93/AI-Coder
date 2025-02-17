#!/usr/bin/env python3
"""
Multi-Species A-Life Simulation (Single File) - Extended Realism
Features from before:
 - Distinct energy gains for Herbivores vs Carnivores.
 - Stats displayed in columns on right side.
 - Maximum lifespan, reproduction cooldown for realism.
 - Occasional random spawns on the border.
 - Disease system and seasonal changes.
 - Omnivores that can eat both plants and herbivores.

**New Addition**:
 - When a carnivore and an omnivore share the same cell:
   80% chance carnivore eats omnivore,
   13% chance omnivore eats carnivore,
   7% chance they ignore each other.
"""

import sys
import random
import copy
import math
import csv
import pygame
from deap import base, creator, tools

###########################################
# GLOBAL PARAMETERS
###########################################
GRID_WIDTH, GRID_HEIGHT = 20, 20
CELL_SIZE = 20

STATS_PANEL_WIDTH = 220
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + STATS_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Producers
INITIAL_PRODUCERS = 15
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.18
PRODUCER_INIT_ENERGY_RANGE = (5, 15)

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
# We'll do simple toggling: Winter -> Summer -> Winter -> ...
# e.g., in Winter, spawn chance might be lower, or movement cost might be higher.

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
random.seed()

# Random border spawn
BASE_SPAWN_CHANCE_PER_TURN = 0.15  # nominal spawn chance
WINTER_SPAWN_MULT = 0.5            # e.g., in winter 1/2 spawn chance
SUMMER_SPAWN_MULT = 1.2            # e.g., in summer 20% more than base

# Pygame keys
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT


###########################################
# DEAP SETUP
###########################################
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

###########################################
# ORGANISM CLASSES
###########################################
class Producer:
    next_id = 0
    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers, herbivores, carnivores, omnivores, environment):
        self.energy += PRODUCER_ENERGY_GAIN
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


class Carnivore:
    next_id = 0
    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        self.age = 0
        self.max_lifespan = MAX_LIFESPAN_CARNIVORE
        self.repro_cooldown_timer = 0
        self.disease_timer = 0

        self.id = Carnivore.next_id
        Carnivore.next_id += 1

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
            self.energy = -1
            return

        # find nearest herbivore
        h_dir = self.find_nearest_herbivore(herbivores)
        if h_dir:
            for _ in range(self.speed):
                self.move_towards(h_dir, carnivores)
                move_cost = MOVE_COST_FACTOR * self.metabolism
                if self.is_infected():
                    move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                self.energy -= move_cost
                if self.energy <= 0:
                    return
                if self.check_and_eat_herbivore(herbivores):
                    break
        else:
            # no herb in sight
            if self.energy < CRITICAL_ENERGY:
                forced_steps = max(1, self.speed)
                for _ in range(forced_steps):
                    self.move_random(carnivores)
                    move_cost = MOVE_COST_FACTOR * self.metabolism
                    if self.is_infected():
                        move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                    self.energy -= move_cost
                    if self.energy <= 0:
                        return
                    if self.check_and_eat_herbivore(herbivores):
                        break
            else:
                self.move_random(carnivores)
                move_cost = MOVE_COST_FACTOR * self.metabolism
                if self.is_infected():
                    move_cost *= DISEASE_ENERGY_DRAIN_MULTIPLIER
                self.energy -= move_cost
                if self.energy <= 0:
                    return
                self.check_and_eat_herbivore(herbivores)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # reproduce
        if self.energy >= CARNIVORE_REPRO_THRESHOLD and self.repro_cooldown_timer == 0:
            self.reproduce(carnivores)

    def find_nearest_herbivore(self, herbivores):
        best_dist = self.vision + 1
        found = False
        best_dx, best_dy = 0, 0
        for h in herbivores:
            dx = h.x - self.x
            dy = h.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        return (best_dx, best_dy) if found else None

    def move_towards(self, direction, carnivores):
        dx, dy = direction
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % GRID_WIDTH
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % GRID_HEIGHT
        if not self.cell_occupied(nx, ny, carnivores):
            self.x, self.y = nx, ny
        else:
            self.move_random(carnivores)

    def move_random(self, carnivores):
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
            if not self.cell_occupied(nx, ny, carnivores):
                self.x, self.y = nx, ny
                return

    def cell_occupied(self, tx, ty, carnivores):
        for c in carnivores:
            if c is not self and c.x == tx and c.y == ty:
                return True
        return False

    def check_and_eat_herbivore(self, herbivores):
        for i in range(len(herbivores)):
            h = herbivores[i]
            if h.x == self.x and h.y == self.y:
                self.energy += EAT_GAIN_CARNIVORE
                herbivores.pop(i)
                return True
        return False

    def reproduce(self, carnivores):
        child_energy = self.energy // 2
        self.energy -= child_energy
        cloned = copy.deepcopy(self.genes)
        cloned = creator.Individual(cloned)
        (cloned,) = toolbox.mutate(cloned)
        new_genome = list(cloned)
        baby = Carnivore(self.x, self.y, child_energy, new_genome, self.generation+1)
        baby.repro_cooldown_timer = REPRODUCTION_COOLDOWN
        carnivores.append(baby)
        self.repro_cooldown_timer = REPRODUCTION_COOLDOWN

    def is_dead(self):
        return self.energy <= 0


class Omnivore:
    """
    NEW SPECIES: can eat both producers AND herbivores.
    Gains EAT_GAIN_OMNIVORE_PLANT from producers, EAT_GAIN_OMNIVORE_ANIMAL from herbivores.
    Also can clash with carnivores:
      60% carnivore kills omnivore,
      15% omnivore kills carnivore,
      25% pass peacefully.
    """
    next_id = 0
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
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % GRID_WIDTH
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % GRID_HEIGHT
        if not self.cell_occupied(nx, ny, omnivores):
            self.x, self.y = nx, ny
        else:
            self.move_random(omnivores)

    def move_random(self, omnivores):
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


###########################################
# ENVIRONMENT / SEASONS / DISEASE
###########################################
def current_season(timestep):
    # Simple 2-season cycle: Winter/Summer each SEASON_LENGTH steps
    cycle = (timestep // SEASON_LENGTH) % 2
    return "WINTER" if cycle == 0 else "SUMMER"

def random_border_cell():
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
    # Adjust spawn chance by season
    x, y = random_border_cell()
    # Weighted random: 20% Producer, 25% Herb, 25% Carn, 30% Omni (change if you like)
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

###########################################
# HELPER FUNCS: STATS, HISTORY, ETC.
###########################################
class SimulationState:
    def __init__(self, t, producers, herbivores, carnivores, omnivores):
        self.t = t
        self.producers = copy.deepcopy(producers)
        self.herbivores = copy.deepcopy(herbivores)
        self.carnivores = copy.deepcopy(carnivores)
        self.omnivores = copy.deepcopy(omnivores)

def store_state(history, t, producers, herbivores, carnivores, omnivores):
    st = SimulationState(t, producers, herbivores, carnivores, omnivores)
    history.append(st)

def load_state_into_sim(state, producers, herbivores, carnivores, omnivores):
    producers.clear()
    herbivores.clear()
    carnivores.clear()
    omnivores.clear()
    producers.extend(copy.deepcopy(state.producers))
    herbivores.extend(copy.deepcopy(state.herbivores))
    carnivores.extend(copy.deepcopy(state.carnivores))
    omnivores.extend(copy.deepcopy(state.omnivores))

def calc_traits_avg(org_list):
    if not org_list:
        return (0, 0, 0, 0)
    sp = sum(o.speed for o in org_list) / len(org_list)
    gn = sum(o.generation for o in org_list) / len(org_list)
    mt = sum(o.metabolism for o in org_list) / len(org_list)
    vs = sum(o.vision for o in org_list) / len(org_list)
    return (sp, gn, mt, vs)

def log_and_print_stats(t, producers, herbivores, carnivores, omnivores, csv_writer):
    p_count = len(producers)

    h_count = len(herbivores)
    (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)

    c_count = len(carnivores)
    (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)

    o_count = len(omnivores)
    (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(omnivores)

    csv_writer.writerow([
        t, p_count, h_count, c_count, o_count,
        h_sp, h_gen, h_met, h_vis,
        c_sp, c_gen, c_met, c_vis,
        o_sp, o_gen, o_met, o_vis
    ])

    print(
        f"Timestep {t}: "
        f"P={p_count}, H={h_count}, C={c_count}, O={o_count}, "
        f"Hsp={h_sp:.2f},Hgen={h_gen:.2f},Hmet={h_met:.2f},Hvis={h_vis:.2f}, "
        f"Csp={c_sp:.2f},Cgen={c_gen:.2f},Cmet={c_met:.2f},Cvis={c_vis:.2f}, "
        f"Osp={o_sp:.2f},Ogen={o_gen:.2f},Omet={o_met:.2f},Ovis={o_vis:.2f}"
    )

###########################################
# MAIN SIMULATION LOOP
###########################################
def run_simulation_interactive():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Single-File Extended A-Life: Seasons, Disease, Omnivores")
    clock = pygame.time.Clock()

    main_font = pygame.font.SysFont(None, 24)
    label_font = pygame.font.SysFont(None, 16)

    csvfilename = "results_interactive.csv"
    csvfile = open(csvfilename, "w", newline="")
    writer = csv.writer(csvfile)
    # CSV columns
    writer.writerow([
        "Timestep","Producers","Herbivores","Carnivores","Omnivores",
        "HavgSp","HavgGen","HavgMet","HavgVis",
        "CavgSp","CavgGen","CavgMet","CavgVis",
        "OavgSp","OavgGen","OavgMet","OavgVis"
    ])

    environment = {}

    # init producers
    producers = []
    for _ in range(INITIAL_PRODUCERS):
        px = random.randint(0, GRID_WIDTH - 1)
        py = random.randint(0, GRID_HEIGHT - 1)
        pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        producers.append(Producer(px, py, pen))

    # init herbivores
    herbivores = []
    for _ in range(INITIAL_HERBIVORES):
        hx = random.randint(0, GRID_WIDTH - 1)
        hy = random.randint(0, GRID_HEIGHT - 1)
        hen = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
        herbivores.append(Herbivore(hx, hy, hen))

    # init carnivores
    carnivores = []
    for _ in range(INITIAL_CARNIVORES):
        cx = random.randint(0, GRID_WIDTH - 1)
        cy = random.randint(0, GRID_HEIGHT - 1)
        cen = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
        carnivores.append(Carnivore(cx, cy, cen))

    # init omnivores
    omnivores = []
    for _ in range(INITIAL_OMNIVORES):
        ox = random.randint(0, GRID_WIDTH - 1)
        oy = random.randint(0, GRID_HEIGHT - 1)
        oen = random.randint(*OMNIVORE_INIT_ENERGY_RANGE)
        omnivores.append(Omnivore(ox, oy, oen))

    history = []
    current_step = 0
    is_paused = False

    store_state(history, current_step, producers, herbivores, carnivores, omnivores)

    def do_simulation_step(step):
        # figure out season
        season = current_season(step)
        # adapt spawn chance
        if season == "WINTER":
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * WINTER_SPAWN_MULT
        else:
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * SUMMER_SPAWN_MULT

        # 1) update producers
        for p in producers:
            p.update(producers, herbivores, carnivores, omnivores, environment)
        producers[:] = [p for p in producers if not p.is_dead()]

        # 2) update herbivores
        for h in herbivores:
            h.update(producers, herbivores, carnivores, omnivores, environment)
        herbivores[:] = [h for h in herbivores if not h.is_dead()]

        # 3) update carnivores
        for c in carnivores:
            c.update(producers, herbivores, carnivores, omnivores, environment)
        carnivores[:] = [c for c in carnivores if not c.is_dead()]

        # 4) update omnivores
        for o in omnivores:
            o.update(producers, herbivores, carnivores, omnivores, environment)
        omnivores[:] = [o for o in omnivores if not o.is_dead()]

        # disease chance
        if random.random() < DISEASE_CHANCE_PER_TURN:
            disease_outbreak(herbivores, carnivores, omnivores)

        # border spawn
        if random.random() < spawn_chance:
            spawn_random_organism_on_border(producers, herbivores, carnivores, omnivores, season)

        step += 1
        store_state(history, step, producers, herbivores, carnivores, omnivores)
        log_and_print_stats(step, producers, herbivores, carnivores, omnivores, writer)
        return step

    # Log initial
    log_and_print_stats(0, producers, herbivores, carnivores, omnivores, writer)

    while True:
        # auto-run if not paused & we’re at newest state
        if not is_paused and current_step == len(history) - 1:
            if current_step < MAX_TIMESTEPS:
                current_step = do_simulation_step(current_step)
            else:
                is_paused = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                csvfile.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == PAUSE_KEY:
                    is_paused = not is_paused
                elif event.key == STEP_BACK_KEY:
                    if is_paused and current_step > 0:
                        current_step -= 1
                        load_state_into_sim(history[current_step], producers, herbivores, carnivores, omnivores)
                elif event.key == STEP_FORWARD_KEY:
                    if is_paused:
                        if current_step < len(history) - 1:
                            current_step += 1
                            load_state_into_sim(history[current_step], producers, herbivores, carnivores, omnivores)
                        else:
                            if current_step < MAX_TIMESTEPS:
                                current_step = do_simulation_step(current_step)

        # draw
        st = history[current_step]
        load_state_into_sim(st, producers, herbivores, carnivores, omnivores)

        screen.fill((0, 0, 0))

        # draw grid area
        for p in producers:
            px = p.x * CELL_SIZE
            py = p.y * CELL_SIZE
            pygame.draw.rect(screen, (0, 200, 0), (px, py, CELL_SIZE, CELL_SIZE))

        for h in herbivores:
            hx = h.x * CELL_SIZE
            hy = h.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 255, 255), (hx + CELL_SIZE//2, hy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"H{h.id}", True, (0,0,0))
            screen.blit(lbl, (hx+2, hy+2))

        for c in carnivores:
            cx = c.x * CELL_SIZE
            cy = c.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 0, 0), (cx + CELL_SIZE//2, cy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"C{c.id}", True, (0,0,0))
            screen.blit(lbl, (cx+2, cy+2))

        for o in omnivores:
            ox = o.x * CELL_SIZE
            oy = o.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 165, 0), (ox + CELL_SIZE//2, oy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"O{o.id}", True, (0,0,0))
            screen.blit(lbl, (ox+2, oy+2))

        # stats panel
        panel_x = GRID_WIDTH * CELL_SIZE
        pygame.draw.rect(screen, (30, 30, 30), (panel_x, 0, STATS_PANEL_WIDTH, WINDOW_HEIGHT))

        p_count = len(producers)
        (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)
        h_count = len(herbivores)
        (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)
        c_count = len(carnivores)
        (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(omnivores)
        o_count = len(omnivores)

        row_y = 20
        # Titles
        surf_p = main_font.render("Producers", True, (200, 200, 0))
        screen.blit(surf_p, (panel_x + 10, row_y))
        surf_h = main_font.render("Herbivores", True, (200, 200, 200))
        screen.blit(surf_h, (panel_x + 80, row_y))
        surf_c = main_font.render("Carnivores", True, (255, 100, 100))
        screen.blit(surf_c, (panel_x + 150, row_y))

        row_y += 25
        # Producer count
        lbl_p = main_font.render(f"# {p_count}", True, (200, 200, 0))
        screen.blit(lbl_p, (panel_x + 20, row_y))

        # Herb column
        lbl_hc = main_font.render(f"# {h_count}", True, (200, 200, 200))
        screen.blit(lbl_hc, (panel_x + 90, row_y))
        lbl_hsp = main_font.render(f"Sp {h_sp:.1f}", True, (200, 200, 200))
        screen.blit(lbl_hsp, (panel_x + 90, row_y+20))
        lbl_hgen = main_font.render(f"Gn {h_gen:.1f}", True, (200, 200, 200))
        screen.blit(lbl_hgen, (panel_x + 90, row_y+40))
        lbl_hmet = main_font.render(f"Mt {h_met:.1f}", True, (200, 200, 200))
        screen.blit(lbl_hmet, (panel_x + 90, row_y+60))
        lbl_hvis = main_font.render(f"Vs {h_vis:.1f}", True, (200, 200, 200))
        screen.blit(lbl_hvis, (panel_x + 90, row_y+80))

        # Carn column
        lbl_cc = main_font.render(f"# {c_count}", True, (255, 100, 100))
        screen.blit(lbl_cc, (panel_x + 160, row_y))
        lbl_csp = main_font.render(f"Sp {c_sp:.1f}", True, (255, 100, 100))
        screen.blit(lbl_csp, (panel_x + 160, row_y+20))
        lbl_cgen = main_font.render(f"Gn {c_gen:.1f}", True, (255, 100, 100))
        screen.blit(lbl_cgen, (panel_x + 160, row_y+40))
        lbl_cmet = main_font.render(f"Mt {c_met:.1f}", True, (255, 100, 100))
        screen.blit(lbl_cmet, (panel_x + 160, row_y+60))
        lbl_cvis = main_font.render(f"Vs {c_vis:.1f}", True, (255, 100, 100))
        screen.blit(lbl_cvis, (panel_x + 160, row_y+80))

        # Omnivores column
        row_y2 = row_y + 120
        surf_o = main_font.render("Omnivores", True, (255, 165, 0))
        screen.blit(surf_o, (panel_x + 80, row_y2))

        row_y2 += 25
        lbl_oc = main_font.render(f"# {o_count}", True, (255, 165, 0))
        screen.blit(lbl_oc, (panel_x + 90, row_y2))
        lbl_osp = main_font.render(f"Sp {o_sp:.1f}", True, (255, 165, 0))
        screen.blit(lbl_osp, (panel_x + 90, row_y2+20))
        lbl_ogen = main_font.render(f"Gn {o_gen:.1f}", True, (255, 165, 0))
        screen.blit(lbl_ogen, (panel_x + 90, row_y2+40))
        lbl_omet = main_font.render(f"Mt {o_met:.1f}", True, (255, 165, 0))
        screen.blit(lbl_omet, (panel_x + 90, row_y2+60))
        lbl_ovis = main_font.render(f"Vs {o_vis:.1f}", True, (255, 165, 0))
        screen.blit(lbl_ovis, (panel_x + 90, row_y2+80))

        # Show season and step at bottom
        season_now = current_season(current_step)
        status_str = "PAUSED" if is_paused else "RUN"
        info_str = f"Timestep: {current_step}, Season: {season_now}, [{status_str}]"
        text_surf = main_font.render(info_str, True, (255, 255, 255))
        screen.blit(text_surf, (panel_x + 10, WINDOW_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation_interactive()
