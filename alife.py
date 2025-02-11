#!/usr/bin/env python3

"""
Two-Species A-Life Simulation with immediate producer removal when eaten:
 - Producer is popped from producers_list as soon as consumer lands on it.
 - One occupant per cell for consumers (no stacking).
 - Force movement if consumer is low on energy and no food in sight.
 - Consumer labeling for easier debugging.
 - Interactive time-travel (pause, step) + CSV logging.
 - Uses DEAP for behind-the-scenes gene creation/mutation.
 - **Now ensures one cell cannot hold multiple producers!**
"""

import sys
import random
import copy
import math
import csv
import pygame

# === DEAP IMPORTS ===
from deap import base, creator, tools

# =====================
# GLOBAL PARAMETERS
# =====================
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20
DISPLAY_WIDTH = GRID_WIDTH * CELL_SIZE
DISPLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Producer
INITIAL_PRODUCERS = 15
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.2
PRODUCER_INIT_ENERGY_RANGE = (5, 15)
NO_SEED_UNDER_CONSUMER = True  # If True, won't seed under a consumer

# Consumer
INITIAL_CONSUMERS = 15
CONSUMER_INIT_ENERGY_RANGE = (5, 25)
BASE_LIFE_COST = 1.5
MOVE_COST_FACTOR = 0.15
EAT_GAIN = 5
CONSUMER_REPRO_THRESHOLD = 20

# Genes: [speed, metabolism, vision]
MUTATION_RATE = 0.1
SPEED_RANGE = (0, 5)
METABOLISM_RANGE = (0.5, 2.0)
VISION_RANGE = (1, 3)

# Force random movement if low energy + no plant
CRITICAL_ENERGY = 8

# Optional discovery bonus
DISCOVERY_BONUS = 0.2
TRACK_CELL_HISTORY_LEN = 20

MAX_TIMESTEPS = 200
FPS = 6
random.seed()

# Pygame keys
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT


# =====================
# DEAP SETUP
# =====================

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
    Matches the existing mutate_genes logic:
     - Each gene has a chance < MUTATION_RATE> to mutate (gauss).
     - Then clamp.
    """
    # speed gene
    if random.random() < MUTATION_RATE:
        ind[0] += random.gauss(0, 1)
    # metabolism gene
    if random.random() < MUTATION_RATE:
        ind[1] += random.gauss(0, 0.1)
    # vision gene
    if random.random() < MUTATION_RATE:
        ind[2] += random.gauss(0, 1)

    # clamp
    ind[0] = max(SPEED_RANGE[0], min(SPEED_RANGE[1], ind[0]))
    ind[1] = max(METABOLISM_RANGE[0], min(METABOLISM_RANGE[1], ind[1]))
    ind[2] = max(VISION_RANGE[0], min(VISION_RANGE[1], ind[2]))
    return (ind,)


# Register creation + mutation
toolbox.register("individual", tools.initIterate, creator.Individual, create_random_genome)
toolbox.register("mutate", custom_mutate)


# =====================
# PRODUCER
# =====================
class Producer:
    """
    Gains energy passively, can seed, immediately removed if eaten.
    Ensures a single producer per cell (no duplicates).
    """
    next_id = 0

    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers_list, consumers_list):
        # Gains some energy
        self.energy += PRODUCER_ENERGY_GAIN
        if self.energy > PRODUCER_MAX_ENERGY:
            self.energy = PRODUCER_MAX_ENERGY

        # Possibly seed
        if self.energy > PRODUCER_SEED_COST and random.random() < PRODUCER_SEED_PROB:
            self.energy -= PRODUCER_SEED_COST
            nx, ny = self.random_adjacent()

            # Check if the target cell is occupied by a consumer
            if NO_SEED_UNDER_CONSUMER:
                occupant_consumer = any(c.x == nx and c.y == ny for c in consumers_list)
                if occupant_consumer:
                    return

            # NEW: Check if there's already a producer in (nx, ny)
            occupant_producer = any(p.x == nx and p.y == ny for p in producers_list)
            if occupant_producer:
                return

            # If cell is free of producers, create a new producer
            baby_en = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
            baby = Producer(nx, ny, baby_en)
            producers_list.append(baby)

    def random_adjacent(self):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (1, 1), (-1, 1), (1, -1)]
        dx, dy = random.choice(dirs)
        nx = (self.x + dx) % GRID_WIDTH
        ny = (self.y + dy) % GRID_HEIGHT
        return nx, ny

    def is_dead(self):
        return self.energy <= 0


# =====================
# CONSUMER
# =====================
class Consumer:
    """
    Genes: [speed, metabolism, vision].
    - Immediate removal of producer when eaten.
    - One occupant per cell for consumers (no stacking).
    - If no plant in sight & energy<CRITICAL_ENERGY => forced random moves.
    - Labels in black text => self.id
    """
    next_id = 0

    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation

        self.id = Consumer.next_id
        Consumer.next_id += 1

        if genes is None:
            # Use DEAP for consistent gene creation
            self.genes = toolbox.individual()
        else:
            self.genes = genes

        # for optional discovery bonus
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

    def update(self, producers_list, consumers_list):
        # baseline cost
        self.energy -= BASE_LIFE_COST
        if self.energy <= 0:
            return

        direction = self.find_nearest_producer(producers_list)
        if direction:
            steps = self.speed
            for _ in range(steps):
                self.move_towards(direction, consumers_list)
                self.energy -= (MOVE_COST_FACTOR * self.metabolism)
                if self.energy <= 0:
                    return
                if self.check_and_eat_immediate(producers_list):
                    break
        else:
            # no plant in sight
            if self.energy < CRITICAL_ENERGY:
                forced_steps = self.speed if self.speed > 0 else 1
                for _ in range(forced_steps):
                    self.move_random(consumers_list)
                    self.energy -= (MOVE_COST_FACTOR * self.metabolism)
                    if self.energy <= 0:
                        return
                    if self.check_and_eat_immediate(producers_list):
                        break
            else:
                # minimal random move
                self.move_random(consumers_list)
                self.energy -= (MOVE_COST_FACTOR * self.metabolism)
                if self.energy <= 0:
                    return
                self.check_and_eat_immediate(producers_list)

        # discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # reproduce if able
        if self.energy >= CONSUMER_REPRO_THRESHOLD:
            self.reproduce(consumers_list)

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
                best_dx = dx
                best_dy = dy
                found = True
        if found:
            return (best_dx, best_dy)
        return None

    def move_towards(self, direction, consumers_list):
        dx, dy = direction
        nx = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        ny = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)
        nx %= GRID_WIDTH
        ny %= GRID_HEIGHT

        if self.cell_occupied(nx, ny, consumers_list):
            self.move_random(consumers_list)
        else:
            self.x = nx
            self.y = ny

    def move_random(self, consumers_list):
        tries = 5
        for _ in range(tries):
            d = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            nx, ny = self.x, self.y
            if d == "UP":
                ny = (ny - 1) % GRID_HEIGHT
            elif d == "DOWN":
                ny = (ny + 1) % GRID_HEIGHT
            elif d == "LEFT":
                nx = (nx - 1) % GRID_WIDTH
            elif d == "RIGHT":
                nx = (nx + 1) % GRID_WIDTH

            if not self.cell_occupied(nx, ny, consumers_list):
                self.x, self.y = nx, ny
                return
        # if no free cell found, do nothing

    def cell_occupied(self, tx, ty, consumers_list):
        for c in consumers_list:
            if c is not self and c.x == tx and c.y == ty:
                return True
        return False

    def check_and_eat_immediate(self, producers_list):
        """
        If there's a producer in the same cell, remove it from the list immediately
        and gain EAT_GAIN.
        Return True if we ate a producer, else False
        """
        for i in range(len(producers_list)):
            p = producers_list[i]
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN
                producers_list.pop(i)  # immediate removal
                return True
        return False

    def reproduce(self, consumers_list):
        child_en = self.energy // 2
        self.energy -= child_en
        baby_genes = copy.deepcopy(self.genes)

        # Use DEAP's mutation operator
        baby_genes = creator.Individual(baby_genes)
        (baby_genes,) = toolbox.mutate(baby_genes)
        baby_genes = list(baby_genes)  # revert to plain list

        new_gen = self.generation + 1
        baby = Consumer(self.x, self.y, child_en, baby_genes, new_gen)
        consumers_list.append(baby)

    def is_dead(self):
        return self.energy <= 0


# ============= HISTORY/SNAPSHOT =============
class SimulationState:
    def __init__(self, t, producers, consumers):
        self.t = t
        # deep copy
        self.producers = copy.deepcopy(producers)
        self.consumers = copy.deepcopy(consumers)


def store_state(history, t, producers, consumers):
    st = SimulationState(t, producers, consumers)
    history.append(st)


def load_state_into_sim(state, producers, consumers):
    producers.clear()
    consumers.clear()
    producers.extend(copy.deepcopy(state.producers))
    consumers.extend(copy.deepcopy(state.consumers))


# ============= STATS =============
def average_speed(cons):
    if not cons:
        return 0
    return sum(c.speed for c in cons) / len(cons)

def average_generation(cons):
    if not cons:
        return 0
    return sum(c.generation for c in cons) / len(cons)

def average_metabolism(cons):
    if not cons:
        return 0
    return sum(c.metabolism for c in cons) / len(cons)

def average_vision(cons):
    if not cons:
        return 0
    return sum(c.vision for c in cons) / len(cons)


# ============= MAIN LOOP =============
def run_simulation_interactive():
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Immediate removal of eaten producers + occupant limit")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    label_font = pygame.font.SysFont(None, 16)

    csvfilename = "results_interactive.csv"
    csvfile = open(csvfilename, "w", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(["Timestep", "Producers", "Consumers", "AvgSpeed", "AvgGen", "AvgMetab", "AvgVision"])

    # init producers
    producers = []
    for _ in range(INITIAL_PRODUCERS):
        px = random.randint(0, GRID_WIDTH - 1)
        py = random.randint(0, GRID_HEIGHT - 1)
        pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)

        # Also avoid placing multiple producers in the same cell at start if desired.
        # For large spawns, you might want a more robust approach, but here's a simple check:
        if any(p.x == px and p.y == py for p in producers):
            continue  # skip to next
        producers.append(Producer(px, py, pen))

    # init consumers
    consumers = []
    for _ in range(INITIAL_CONSUMERS):
        cx = random.randint(0, GRID_WIDTH - 1)
        cy = random.randint(0, GRID_HEIGHT - 1)
        cen = random.randint(*CONSUMER_INIT_ENERGY_RANGE)
        c = Consumer(cx, cy, cen)
        consumers.append(c)

    history = []
    current_step = 0
    is_paused = False

    store_state(history, current_step, producers, consumers)

    def log_stats(t):
        np = len(producers)
        nc = len(consumers)
        sp = average_speed(consumers)
        gn = average_generation(consumers)
        mb = average_metabolism(consumers)
        vs = average_vision(consumers)
        writer.writerow([t, np, nc, sp, gn, mb, vs])
        print(f"Timestep {t}: P={np}, C={nc}, Sp={sp:.2f}, Gen={gn:.2f}, Met={mb:.2f}, Vis={vs:.2f}")

    def do_simulation_step(t):
        # 1) Update producers
        for p in producers:
            p.update(producers, consumers)

        # 2) Update consumers
        for c in consumers:
            c.update(producers, consumers)

        # remove dead consumers
        alive_cons = [c for c in consumers if not c.is_dead()]
        consumers.clear()
        consumers.extend(alive_cons)

        t += 1
        store_state(history, t, producers, consumers)
        log_stats(t)
        return t

    # Log initial
    log_stats(0)

    while True:
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
                        load_state_into_sim(history[current_step], producers, consumers)
                elif event.key == STEP_FORWARD_KEY:
                    if is_paused:
                        if current_step < len(history) - 1:
                            current_step += 1
                            load_state_into_sim(history[current_step], producers, consumers)
                        else:
                            if current_step < MAX_TIMESTEPS:
                                current_step = do_simulation_step(current_step)

        # Re-draw the current state
        st = history[current_step]
        load_state_into_sim(st, producers, consumers)

        screen.fill((0, 0, 0))

        # draw producers
        for p in producers:
            px = p.x * CELL_SIZE
            py = p.y * CELL_SIZE
            pygame.draw.circle(
                screen, (0, 255, 0),
                (px + CELL_SIZE // 2, py + CELL_SIZE // 2),
                CELL_SIZE // 2
            )

        # draw consumers
        for c in consumers:
            cx = c.x * CELL_SIZE
            cy = c.y * CELL_SIZE
            pygame.draw.circle(
                screen, (255, 255, 255),
                (cx + CELL_SIZE // 2, cy + CELL_SIZE // 2),
                CELL_SIZE // 2
            )

            label_str = str(c.id)
            label_surf = label_font.render(label_str, True, (0, 0, 0))
            r = label_surf.get_rect(center=(cx + CELL_SIZE // 2, cy + CELL_SIZE // 2))
            screen.blit(label_surf, r)

        # overhead stats
        np = len(producers)
        nc = len(consumers)
        sp = average_speed(consumers)
        gn = average_generation(consumers)
        mb = average_metabolism(consumers)
        vs = average_vision(consumers)
        status = "PAUSED" if is_paused else "RUN"
        info_str = (
            f"t={current_step} | P={np} | C={nc} | "
            f"Sp={sp:.2f} | G={gn:.2f} | Met={mb:.2f} | Vis={vs:.2f} | {status}"
        )
        text_surf = font.render(info_str, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    run_simulation_interactive()
