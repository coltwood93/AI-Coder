#!/usr/bin/env python3
"""
Multi-Species A-Life Simulation (Producers, Herbivores, Carnivores)
Improvements:
 1) Herbivores and Carnivores get different energy gains from eating.
 2) Stats displayed in columns on the right side of the window (one column per species).
 3) Added realism via:
    - Maximum lifespan for herbivores and carnivores.
    - Reproduction cooldown (time steps between successful reproductions).
    
CONTROLS:
 - 'P': Pause/Unpause
 - Left Arrow: Rewind one timestep (when paused)
 - Right Arrow: Step forward one timestep (when paused)
 - Close Window or ESC: Quit
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

# We'll add a stats panel on the right
STATS_PANEL_WIDTH = 220
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + STATS_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Producers
INITIAL_PRODUCERS = 15
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.2
PRODUCER_INIT_ENERGY_RANGE = (5, 15)

# Herbivores
INITIAL_HERBIVORES = 10
HERBIVORE_INIT_ENERGY_RANGE = (5, 25)
HERBIVORE_REPRO_THRESHOLD = 15
EAT_GAIN_HERBIVORE = 4  # Distinct from carnivores

# Carnivores
INITIAL_CARNIVORES = 5
CARNIVORE_INIT_ENERGY_RANGE = (5, 25)
CARNIVORE_REPRO_THRESHOLD = 18
EAT_GAIN_CARNIVORE = 7  # Distinct from herbivores

# Additional Realism
MAX_LIFESPAN_HERBIVORE = 300
MAX_LIFESPAN_CARNIVORE = 250
REPRODUCTION_COOLDOWN = 10

# Energy & Movement
BASE_LIFE_COST = 1.5
MOVE_COST_FACTOR = 0.3

# Genes & Mutation
MUTATION_RATE = 0.1
SPEED_RANGE = (0, 5)
METABOLISM_RANGE = (0.5, 2.0)
VISION_RANGE = (1, 3)

# Misc
CRITICAL_ENERGY = 8     # Force random movement below this energy
DISCOVERY_BONUS = 0.2
TRACK_CELL_HISTORY_LEN = 20
MAX_TIMESTEPS = 200
FPS = 6
random.seed()

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
    """
    Create a genome [speed, metabolism, vision].
    """
    sp = random.randint(SPEED_RANGE[0], SPEED_RANGE[1])
    met = random.uniform(METABOLISM_RANGE[0], METABOLISM_RANGE[1])
    vs = random.randint(VISION_RANGE[0], VISION_RANGE[1])
    return [sp, met, vs]

def custom_mutate(ind):
    """
    Mutation: each gene has MUTATION_RATE chance to shift by a Gaussian draw.
    Then clamp into valid range.
    """
    # speed
    if random.random() < MUTATION_RATE:
        ind[0] += random.gauss(0, 1)
    # metabolism
    if random.random() < MUTATION_RATE:
        ind[1] += random.gauss(0, 0.1)
    # vision
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
# CLASSES
###########################################

class Producer:
    """
    Gains energy passively, can seed new producers, 
    removed if eaten by a herbivore (not by a carnivore).
    """
    next_id = 0

    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers_list, herbivores_list, carnivores_list, environment):
        self.energy += PRODUCER_ENERGY_GAIN
        if self.energy > PRODUCER_MAX_ENERGY:
            self.energy = PRODUCER_MAX_ENERGY

        # Possibly seed
        if self.energy > PRODUCER_SEED_COST and random.random() < PRODUCER_SEED_PROB:
            self.energy -= PRODUCER_SEED_COST
            nx, ny = self.random_adjacent()
            # Avoid placing a new producer if that cell already has one
            if not any(p.x == nx and p.y == ny for p in producers_list):
                baby_en = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
                baby = Producer(nx, ny, baby_en)
                producers_list.append(baby)

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
    """
    Genome-based: [speed, metabolism, vision].
    Eats producers for EAT_GAIN_HERBIVORE.
    Avoids carnivores if in vision range.
    Single occupant rule among herbivores.
    Additional realism:
      - max_lifespan
      - reproduction_cooldown
    """
    next_id = 0

    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        # Additional realism
        self.age = 0
        self.max_lifespan = MAX_LIFESPAN_HERBIVORE
        self.repro_cooldown_timer = 0  # how many steps left before can reproduce

        self.id = Herbivore.next_id
        Herbivore.next_id += 1

        if genes is None:
            self.genes = toolbox.individual()
        else:
            self.genes = genes
        self.recent_cells = [(x,y)]

    @property
    def speed(self):
        return int(self.genes[0])

    @property
    def metabolism(self):
        return float(self.genes[1])

    @property
    def vision(self):
        return int(self.genes[2])

    def update(self, producers_list, herbivores_list, carnivores_list, environment):
        # baseline cost
        self.energy -= BASE_LIFE_COST
        self.age += 1
        if self.repro_cooldown_timer > 0:
            self.repro_cooldown_timer -= 1

        if self.energy <= 0:
            return
        if self.age > self.max_lifespan:
            self.energy = -1  # effectively dead
            return

        # Check for carnivores in vision & run away if found
        c_dir = self.find_nearest_carnivore(carnivores_list)
        if c_dir:
            self.run_away_from(c_dir, herbivores_list)
        else:
            # chase producers if any in sight
            p_dir = self.find_nearest_producer(producers_list)
            if p_dir:
                for _ in range(self.speed):
                    self.move_towards(p_dir, herbivores_list)
                    self.energy -= MOVE_COST_FACTOR * self.metabolism
                    if self.energy <= 0:
                        return
                    if self.check_and_eat_producer(producers_list):
                        break
            else:
                # no producer in sight
                if self.energy < CRITICAL_ENERGY:
                    forced_steps = self.speed if self.speed > 0 else 1
                    for _ in range(forced_steps):
                        self.move_random(herbivores_list)
                        self.energy -= MOVE_COST_FACTOR * self.metabolism
                        if self.energy <= 0:
                            return
                        if self.check_and_eat_producer(producers_list):
                            break
                else:
                    self.move_random(herbivores_list)
                    self.energy -= MOVE_COST_FACTOR * self.metabolism
                    if self.energy <= 0:
                        return
                    self.check_and_eat_producer(producers_list)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # reproduce if able and off cooldown
        if self.energy >= HERBIVORE_REPRO_THRESHOLD and self.repro_cooldown_timer == 0:
            self.reproduce(herbivores_list)

    def find_nearest_carnivore(self, carnivores_list):
        best_dist = self.vision + 1
        best_dx, best_dy = 0, 0
        found = False
        for carn in carnivores_list:
            dx = carn.x - self.x
            dy = carn.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        if not found:
            return None
        return (best_dx, best_dy)

    def run_away_from(self, c_dir, herbivores_list):
        dx, dy = c_dir
        opp_dir = (-dx, -dy)
        for _ in range(self.speed):
            self.move_towards(opp_dir, herbivores_list)
            self.energy -= MOVE_COST_FACTOR * self.metabolism
            if self.energy <= 0:
                return

    def find_nearest_producer(self, producers_list):
        best_dist = self.vision + 1
        best_dx, best_dy = 0, 0
        found = False
        for p in producers_list:
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

    def move_towards(self, direction, herbivores_list):
        dx, dy = direction
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % GRID_WIDTH
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % GRID_HEIGHT

        if not self.cell_occupied(nx, ny, herbivores_list):
            self.x, self.y = nx, ny
        else:
            self.move_random(herbivores_list)

    def move_random(self, herbivores_list):
        tries = 5
        for _ in range(tries):
            d = random.choice(["UP","DOWN","LEFT","RIGHT"])
            nx, ny = self.x, self.y
            if d == "UP":
                ny = (ny - 1) % GRID_HEIGHT
            elif d == "DOWN":
                ny = (ny + 1) % GRID_HEIGHT
            elif d == "LEFT":
                nx = (nx - 1) % GRID_WIDTH
            elif d == "RIGHT":
                nx = (nx + 1) % GRID_WIDTH
            if not self.cell_occupied(nx, ny, herbivores_list):
                self.x, self.y = nx, ny
                return

    def cell_occupied(self, tx, ty, herbivores_list):
        for h in herbivores_list:
            if h is not self and h.x == tx and h.y == ty:
                return True
        return False

    def check_and_eat_producer(self, producers_list):
        for i in range(len(producers_list)):
            p = producers_list[i]
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN_HERBIVORE
                producers_list.pop(i)
                return True
        return False

    def reproduce(self, herbivores_list):
        child_energy = self.energy // 2
        self.energy -= child_energy

        cloned_genome = copy.deepcopy(self.genes)
        cloned_genome = creator.Individual(cloned_genome)
        (cloned_genome,) = toolbox.mutate(cloned_genome)
        new_genome = list(cloned_genome)

        baby = Herbivore(self.x, self.y, child_energy, new_genome, self.generation+1)
        baby.repro_cooldown_timer = REPRODUCTION_COOLDOWN  # Baby can't reproduce immediately
        herbivores_list.append(baby)

        # The parent should also go on cooldown
        self.repro_cooldown_timer = REPRODUCTION_COOLDOWN

    def is_dead(self):
        return self.energy <= 0


class Carnivore:
    """
    Genome-based: [speed, metabolism, vision].
    Eats herbivores for EAT_GAIN_CARNIVORE.
    Single occupant rule among carnivores only.
    Additional realism:
      - max_lifespan
      - reproduction_cooldown
    """
    next_id = 0

    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        # Additional realism
        self.age = 0
        self.max_lifespan = MAX_LIFESPAN_CARNIVORE
        self.repro_cooldown_timer = 0

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

    def update(self, producers_list, herbivores_list, carnivores_list, environment):
        self.energy -= BASE_LIFE_COST
        self.age += 1
        if self.repro_cooldown_timer > 0:
            self.repro_cooldown_timer -= 1

        if self.energy <= 0:
            return
        if self.age > self.max_lifespan:
            self.energy = -1  # effectively dead
            return

        # attempt to find nearest herbivore
        direction = self.find_nearest_herbivore(herbivores_list)
        if direction:
            for _ in range(self.speed):
                self.move_towards(direction, carnivores_list)
                self.energy -= MOVE_COST_FACTOR * self.metabolism
                if self.energy <= 0:
                    return
                if self.check_and_eat_herbivore(herbivores_list):
                    break
        else:
            if self.energy < CRITICAL_ENERGY:
                # forced random moves
                forced_steps = self.speed if self.speed > 0 else 1
                for _ in range(forced_steps):
                    self.move_random(carnivores_list)
                    self.energy -= MOVE_COST_FACTOR * self.metabolism
                    if self.energy <= 0:
                        return
                    if self.check_and_eat_herbivore(herbivores_list):
                        break
            else:
                # minimal random move
                self.move_random(carnivores_list)
                self.energy -= MOVE_COST_FACTOR * self.metabolism
                if self.energy <= 0:
                    return
                self.check_and_eat_herbivore(herbivores_list)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # reproduce if able and off cooldown
        if self.energy >= CARNIVORE_REPRO_THRESHOLD and self.repro_cooldown_timer == 0:
            self.reproduce(carnivores_list)

    def find_nearest_herbivore(self, herbivores_list):
        best_dist = self.vision + 1
        best_dx, best_dy = 0, 0
        found = False
        for h in herbivores_list:
            dx = h.x - self.x
            dy = h.y - self.y
            dist = abs(dx) + abs(dy)
            if dist <= self.vision and dist < best_dist:
                best_dist = dist
                best_dx, best_dy = dx, dy
                found = True
        return (best_dx, best_dy) if found else None

    def move_towards(self, direction, carnivores_list):
        dx, dy = direction
        nx = (self.x + (1 if dx>0 else -1 if dx<0 else 0)) % GRID_WIDTH
        ny = (self.y + (1 if dy>0 else -1 if dy<0 else 0)) % GRID_HEIGHT

        if not self.cell_occupied(nx, ny, carnivores_list):
            self.x, self.y = nx, ny
        else:
            self.move_random(carnivores_list)

    def move_random(self, carnivores_list):
        tries = 5
        for _ in range(tries):
            d = random.choice(["UP","DOWN","LEFT","RIGHT"])
            nx, ny = self.x, self.y
            if d == "UP":
                ny = (ny - 1) % GRID_HEIGHT
            elif d == "DOWN":
                ny = (ny + 1) % GRID_HEIGHT
            elif d == "LEFT":
                nx = (nx - 1) % GRID_WIDTH
            elif d == "RIGHT":
                nx = (nx + 1) % GRID_WIDTH
            if not self.cell_occupied(nx, ny, carnivores_list):
                self.x, self.y = nx, ny
                return

    def cell_occupied(self, tx, ty, carnivores_list):
        for c in carnivores_list:
            if c is not self and c.x == tx and c.y == ty:
                return True
        return False

    def check_and_eat_herbivore(self, herbivores_list):
        for i in range(len(herbivores_list)):
            h = herbivores_list[i]
            if h.x == self.x and h.y == self.y:
                self.energy += EAT_GAIN_CARNIVORE
                herbivores_list.pop(i)
                return True
        return False

    def reproduce(self, carnivores_list):
        child_energy = self.energy // 2
        self.energy -= child_energy

        cloned_genome = copy.deepcopy(self.genes)
        cloned_genome = creator.Individual(cloned_genome)
        (cloned_genome,) = toolbox.mutate(cloned_genome)
        new_genome = list(cloned_genome)

        baby = Carnivore(self.x, self.y, child_energy, new_genome, self.generation+1)
        baby.repro_cooldown_timer = REPRODUCTION_COOLDOWN
        carnivores_list.append(baby)

        # Parent on cooldown
        self.repro_cooldown_timer = REPRODUCTION_COOLDOWN

    def is_dead(self):
        return self.energy <= 0

###########################################
# HISTORY / SNAPSHOT
###########################################
class SimulationState:
    def __init__(self, t, producers, herbivores, carnivores):
        self.t = t
        self.producers = copy.deepcopy(producers)
        self.herbivores = copy.deepcopy(herbivores)
        self.carnivores = copy.deepcopy(carnivores)

def store_state(history, t, producers, herbivores, carnivores):
    st = SimulationState(t, producers, herbivores, carnivores)
    history.append(st)

def load_state_into_sim(state, producers, herbivores, carnivores):
    producers.clear()
    herbivores.clear()
    carnivores.clear()
    producers.extend(copy.deepcopy(state.producers))
    herbivores.extend(copy.deepcopy(state.herbivores))
    carnivores.extend(copy.deepcopy(state.carnivores))

###########################################
# STAT HELPERS
###########################################
def calc_traits_avg(org_list):
    """
    Returns (avg_speed, avg_generation, avg_metabolism, avg_vision).
    """
    if not org_list:
        return (0, 0, 0, 0)
    sp = sum(o.speed for o in org_list) / len(org_list)
    gn = sum(o.generation for o in org_list) / len(org_list)
    mt = sum(o.metabolism for o in org_list) / len(org_list)
    vs = sum(o.vision for o in org_list) / len(org_list)
    return (sp, gn, mt, vs)

def log_and_print_stats(t, producers, herbivores, carnivores, csv_writer):
    """
    Log to CSV + print to console for producers, herbivores, carnivores.
    """
    p_count = len(producers)

    h_count = len(herbivores)
    (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)

    c_count = len(carnivores)
    (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)

    # CSV
    csv_writer.writerow([
        t, p_count, h_count, c_count,
        h_sp, h_gen, h_met, h_vis,
        c_sp, c_gen, c_met, c_vis
    ])

    # Console
    print(
        f"Timestep {t}: "
        f"P={p_count}, H={h_count}, C={c_count}, "
        f"Hsp={h_sp:.2f}, Hgen={h_gen:.2f}, Hmet={h_met:.2f}, Hvis={h_vis:.2f}, "
        f"Csp={c_sp:.2f}, Cgen={c_gen:.2f}, Cmet={c_met:.2f}, Cvis={c_vis:.2f}"
    )

###########################################
# MAIN SIMULATION LOOP
###########################################
def run_simulation_interactive():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Producers, Herbivores, Carnivores A-Life")
    clock = pygame.time.Clock()

    # Fonts
    main_font = pygame.font.SysFont(None, 24)
    label_font = pygame.font.SysFont(None, 16)

    csvfilename = "results_interactive.csv"
    csvfile = open(csvfilename, "w", newline="")
    writer = csv.writer(csvfile)
    # CSV columns
    writer.writerow([
        "Timestep","Producers","Herbivores","Carnivores",
        "HavgSp","HavgGen","HavgMet","HavgVis",
        "CavgSp","CavgGen","CavgMet","CavgVis"
    ])

    environment = {}

    # Init producers
    producers = []
    for _ in range(INITIAL_PRODUCERS):
        px = random.randint(0, GRID_WIDTH - 1)
        py = random.randint(0, GRID_HEIGHT - 1)
        pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        producers.append(Producer(px, py, pen))

    # Init herbivores
    herbivores = []
    for _ in range(INITIAL_HERBIVORES):
        hx = random.randint(0, GRID_WIDTH - 1)
        hy = random.randint(0, GRID_HEIGHT - 1)
        hen = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
        h = Herbivore(hx, hy, hen)
        herbivores.append(h)

    # Init carnivores
    carnivores = []
    for _ in range(INITIAL_CARNIVORES):
        cx = random.randint(0, GRID_WIDTH - 1)
        cy = random.randint(0, GRID_HEIGHT - 1)
        cen = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
        c = Carnivore(cx, cy, cen)
        carnivores.append(c)

    history = []
    current_step = 0
    is_paused = False

    # Store initial
    store_state(history, current_step, producers, herbivores, carnivores)

    def do_simulation_step(step):
        # 1) Update producers
        for p in producers:
            p.update(producers, herbivores, carnivores, environment)
        producers[:] = [p for p in producers if not p.is_dead()]

        # 2) Update herbivores
        for h in herbivores:
            h.update(producers, herbivores, carnivores, environment)
        herbivores[:] = [h for h in herbivores if not h.is_dead()]

        # 3) Update carnivores
        for c in carnivores:
            c.update(producers, herbivores, carnivores, environment)
        carnivores[:] = [c for c in carnivores if not c.is_dead()]

        step += 1
        store_state(history, step, producers, herbivores, carnivores)
        log_and_print_stats(step, producers, herbivores, carnivores, writer)
        return step

    # Log initial
    log_and_print_stats(0, producers, herbivores, carnivores, writer)

    while True:
        # Auto-run if not paused & at newest state
        if not is_paused and current_step == len(history) - 1:
            if current_step < MAX_TIMESTEPS:
                current_step = do_simulation_step(current_step)
            else:
                is_paused = True  # or break if you want to auto-exit

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
                        load_state_into_sim(history[current_step], producers, herbivores, carnivores)
                elif event.key == STEP_FORWARD_KEY:
                    if is_paused:
                        if current_step < len(history) - 1:
                            current_step += 1
                            load_state_into_sim(history[current_step], producers, herbivores, carnivores)
                        else:
                            if current_step < MAX_TIMESTEPS:
                                current_step = do_simulation_step(current_step)

        # Drawing
        st = history[current_step]
        load_state_into_sim(st, producers, herbivores, carnivores)

        screen.fill((0, 0, 0))

        # Draw the grid area
        for p in producers:
            px = p.x * CELL_SIZE
            py = p.y * CELL_SIZE
            pygame.draw.rect(screen, (0, 200, 0), (px, py, CELL_SIZE, CELL_SIZE))

        for h in herbivores:
            hx = h.x * CELL_SIZE
            hy = h.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 255, 255), (hx + CELL_SIZE//2, hy + CELL_SIZE//2), CELL_SIZE//2)
            # label them if desired
            lbl_surf = label_font.render(f"H{h.id}", True, (0,0,0))
            screen.blit(lbl_surf, (hx+2, hy+2))

        for c in carnivores:
            cx = c.x * CELL_SIZE
            cy = c.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 0, 0), (cx + CELL_SIZE//2, cy + CELL_SIZE//2), CELL_SIZE//2)
            lbl_surf = label_font.render(f"C{c.id}", True, (0,0,0))
            screen.blit(lbl_surf, (cx+2, cy+2))

        # Side Stats Panel (columns for Producers, Herbivores, Carnivores)
        panel_x = GRID_WIDTH * CELL_SIZE
        pygame.draw.rect(screen, (30, 30, 30), (panel_x, 0, STATS_PANEL_WIDTH, WINDOW_HEIGHT))

        # Calculate stats
        p_count = len(producers)

        (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)
        h_count = len(herbivores)

        (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)
        c_count = len(carnivores)

        # We'll arrange them in columns:
        # Producer column at panel_x + 10
        # Herbivore column at panel_x + 70
        # Carnivore column at panel_x + 130
        # Each row about 20 px vertical spacing
        row_y = 20

        # Titles
        title_surf_p = main_font.render("Producers", True, (200, 200, 0))
        screen.blit(title_surf_p, (panel_x + 10, row_y))

        title_surf_h = main_font.render("Herbivores", True, (200, 200, 200))
        screen.blit(title_surf_h, (panel_x + 80, row_y))

        title_surf_c = main_font.render("Carnivores", True, (255, 100, 100))
        screen.blit(title_surf_c, (panel_x + 150, row_y))

        row_y += 25

        # Producer stats (just count here)
        p_label_count = main_font.render(f"# {p_count}", True, (200, 200, 0))
        screen.blit(p_label_count, (panel_x + 20, row_y))

        # Herbivores stats
        h_label_count = main_font.render(f"# {h_count}", True, (200, 200, 200))
        screen.blit(h_label_count, (panel_x + 90, row_y))

        h_label_sp = main_font.render(f"Sp {h_sp:.1f}", True, (200, 200, 200))
        screen.blit(h_label_sp, (panel_x + 90, row_y+20))

        h_label_gen = main_font.render(f"Gn {h_gen:.1f}", True, (200, 200, 200))
        screen.blit(h_label_gen, (panel_x + 90, row_y+40))

        h_label_met = main_font.render(f"Mt {h_met:.1f}", True, (200, 200, 200))
        screen.blit(h_label_met, (panel_x + 90, row_y+60))

        h_label_vis = main_font.render(f"Vs {h_vis:.1f}", True, (200, 200, 200))
        screen.blit(h_label_vis, (panel_x + 90, row_y+80))

        # Carnivores stats
        c_label_count = main_font.render(f"# {c_count}", True, (255, 100, 100))
        screen.blit(c_label_count, (panel_x + 160, row_y))

        c_label_sp = main_font.render(f"Sp {c_sp:.1f}", True, (255, 100, 100))
        screen.blit(c_label_sp, (panel_x + 160, row_y+20))

        c_label_gen = main_font.render(f"Gn {c_gen:.1f}", True, (255, 100, 100))
        screen.blit(c_label_gen, (panel_x + 160, row_y+40))

        c_label_met = main_font.render(f"Mt {c_met:.1f}", True, (255, 100, 100))
        screen.blit(c_label_met, (panel_x + 160, row_y+60))

        c_label_vis = main_font.render(f"Vs {c_vis:.1f}", True, (255, 100, 100))
        screen.blit(c_label_vis, (panel_x + 160, row_y+80))

        # Timestep or status at bottom
        status_str = "PAUSED" if is_paused else "RUN"
        info_str = f"Timestep: {current_step}  [{status_str}]"
        text_surf = main_font.render(info_str, True, (255, 255, 255))
        screen.blit(text_surf, (panel_x + 10, WINDOW_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation_interactive()
