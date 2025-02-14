#!/usr/bin/env python3

import sys
import random
import copy
import csv
import pygame
import numpy as np

from deap import base, creator, tools

from memory_storage import MemoryResidentSimulationStore
from hdf5_storage import HDF5Storage

GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20
STATS_PANEL_WIDTH = 200
DISPLAY_WIDTH = GRID_WIDTH * CELL_SIZE + STATS_PANEL_WIDTH
DISPLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE

INITIAL_PRODUCERS = 25
PRODUCER_ENERGY_GAIN = 0.6
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 2
PRODUCER_SEED_PROB = 0.25
PRODUCER_INIT_ENERGY_RANGE = (8, 15)
NO_SEED_UNDER_CONSUMER = True

INITIAL_CONSUMERS = 8
CONSUMER_INIT_ENERGY_RANGE = (15, 25)
BASE_LIFE_COST = 1.5
MOVE_COST_FACTOR = 0.15
EAT_GAIN = 4
CONSUMER_REPRO_THRESHOLD = 45
CRITICAL_ENERGY = 6

MUTATION_RATE = 0.1
SPEED_RANGE = (1, 4)
METABOLISM_RANGE = (0.8, 1.2)
VISION_RANGE = (1, 4)

DISCOVERY_BONUS = 0.3
TRACK_CELL_HISTORY_LEN = 20

MAX_TIMESTEPS = 200
FPS = 6
random.seed()

# Pygame Keys
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT

# Nutrient environment
INITIAL_NUTRIENT_LEVEL = 0.5
NUTRIENT_DIFFUSION_RATE = 0.1
NUTRIENT_DECAY_RATE = 0.01
PRODUCER_NUTRIENT_CONSUMPTION = 0.1
CONSUMER_NUTRIENT_RELEASE = 0.05

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

class Producer:
    next_id = 0
    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def random_adjacent(self):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (1, 1), (-1, 1), (1, -1)]
        dx, dy = random.choice(dirs)
        nx = (self.x + dx) % GRID_WIDTH
        ny = (self.y + dy) % GRID_HEIGHT
        return nx, ny

    def is_dead(self):
        return self.energy <= 0

    def update(self, producers, consumers, environment):
        nutrient_taken = min(environment[self.x, self.y], PRODUCER_NUTRIENT_CONSUMPTION)
        self.energy += nutrient_taken * PRODUCER_ENERGY_GAIN
        environment[self.x, self.y] -= nutrient_taken

        if self.energy > PRODUCER_MAX_ENERGY:
            self.energy = PRODUCER_MAX_ENERGY

        if self.energy > PRODUCER_SEED_COST and random.random() < PRODUCER_SEED_PROB:
            self.energy -= PRODUCER_SEED_COST
            nx, ny = self.random_adjacent()
            if NO_SEED_UNDER_CONSUMER:
                occupant_consumer = any(c.x == nx and c.y == ny for c in consumers)
                if occupant_consumer:
                    return
            occupant_producer = any(p.x == nx and p.y == ny for p in producers)
            if occupant_producer:
                return
            baby_en = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
            baby = Producer(nx, ny, baby_en)
            producers.append(baby)

class Consumer:
    next_id = 0
    def __init__(self, x, y, energy=10, genes=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation
        self.id = Consumer.next_id
        Consumer.next_id += 1
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

    def count_nearby_consumers(self, consumers_list, radius=2):
        count = 0
        for c in consumers_list:
            if c is not self:
                dx = abs(c.x - self.x)
                dy = abs(c.y - self.y)
                if dx <= radius and dy <= radius:
                    count += 1
        return count

    def release_nutrients(self, environment):
        environment[self.x, self.y] += CONSUMER_NUTRIENT_RELEASE

    def check_and_eat_immediate(self, producers):
        for i in range(len(producers)):
            p = producers[i]
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN
                producers.pop(i)
                return True
        return False

    def cell_occupied(self, tx, ty, consumers_list):
        for c in consumers_list:
            if c is not self and c.x == tx and c.y == ty:
                return True
        return False

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
        return (best_dx, best_dy) if found else None

    def reproduce(self, consumers_list):
        child_en = self.energy / 2
        self.energy /= 2
        baby_genes = copy.deepcopy(self.genes)
        baby_genes = creator.Individual(baby_genes)
        (baby_genes,) = toolbox.mutate(baby_genes)
        baby_genes = list(baby_genes)
        new_gen = self.generation + 1
        baby = Consumer(self.x, self.y, child_en, baby_genes, new_gen)
        consumers_list.append(baby)

    def is_dead(self):
        return self.energy <= 0

    def update(self, producers_list, consumers_list, environment):
        nearby = self.count_nearby_consumers(consumers_list)
        competition_cost = nearby * 0.1
        self.energy -= BASE_LIFE_COST + (self.speed * 0.2) + competition_cost
        if self.energy <= 0:
            self.release_nutrients(environment)
            return
        direction = self.find_nearest_producer(producers_list)
        if direction:
            steps = self.speed
            for _ in range(steps):
                self.move_towards(direction, consumers_list)
                self.energy -= (MOVE_COST_FACTOR * self.metabolism * (1 + self.speed * 0.1))
                if self.energy <= 0:
                    self.release_nutrients(environment)
                    return
                if self.check_and_eat_immediate(producers_list):
                    break
        else:
            if self.energy < CRITICAL_ENERGY:
                forced_steps = self.speed if self.speed > 0 else 1
                for _ in range(forced_steps):
                    self.move_random(consumers_list)
                    self.energy -= MOVE_COST_FACTOR * self.metabolism
                    if self.energy <= 0:
                        self.release_nutrients(environment)
                        return
                    if self.check_and_eat_immediate(producers_list):
                        break
            else:
                self.move_random(consumers_list)
                self.energy -= MOVE_COST_FACTOR * self.metabolism
                if self.energy <= 0:
                    self.release_nutrients(environment)
                    return
                self.check_and_eat_immediate(producers_list)

        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        if self.energy >= CONSUMER_REPRO_THRESHOLD:
            self.reproduce(consumers_list)

def update_environment(environment):
    new_env = environment.copy()
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            up = (x, (y - 1) % GRID_HEIGHT)
            down = (x, (y + 1) % GRID_HEIGHT)
            left = ((x - 1) % GRID_WIDTH, y)
            right = ((x + 1) % GRID_WIDTH, y)
            neighbors_avg = (environment[up] + environment[down]
                             + environment[left] + environment[right]) / 4
            diff = (neighbors_avg - environment[x, y]) * NUTRIENT_DIFFUSION_RATE
            new_env[x, y] += diff
    new_env *= (1 - NUTRIENT_DECAY_RATE)
    environment[:] = new_env

def average_speed(cons):
    return sum(c.speed for c in cons)/len(cons) if cons else 0

def average_generation(cons):
    return sum(c.generation for c in cons)/len(cons) if cons else 0

def average_metabolism(cons):
    return sum(c.metabolism for c in cons)/len(cons) if cons else 0

def average_vision(cons):
    return sum(c.vision for c in cons)/len(cons) if cons else 0

def run_simulation_interactive():
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("A-Life with Auto Replay -> Live Mode")
    clock = pygame.time.Clock()
    stats_font = pygame.font.SysFont(None, 20)
    label_font = pygame.font.SysFont(None, 16)

    csvfilename = "results_interactive.csv"
    csvfile = open(csvfilename, "w", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(["Timestep","Producers","Consumers","AvgSpeed","AvgGen","AvgMetab","AvgVision"])

    environment = np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL, dtype=np.float32)

    # init producers
    producers = []
    for _ in range(INITIAL_PRODUCERS):
        px = random.randint(0, GRID_WIDTH - 1)
        py = random.randint(0, GRID_HEIGHT - 1)
        pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        if any(p.x == px and p.y == py for p in producers):
            continue
        producers.append(Producer(px, py, pen))

    # init consumers
    consumers = []
    for _ in range(INITIAL_CONSUMERS):
        cx = random.randint(0, GRID_WIDTH - 1)
        cy = random.randint(0, GRID_HEIGHT - 1)
        cen = random.randint(*CONSUMER_INIT_ENERGY_RANGE)
        consumers.append(Consumer(cx, cy, cen))

    # Storage
    mem_store = MemoryResidentSimulationStore(mode="live")
    hdf5_storage = HDF5Storage("simulation_data.h5")

    current_step = 0
    live_step = 0
    is_paused = False

    # Single-step storing in memory store
    def store_live_state(t):
        mem_store.update_state(
            t,
            environment.copy(),
            producers,
            consumers,
            debug_logs=[f"Step {t}"]
        )
        mem_store.flush_to_longterm(hdf5_storage)
        # remove older timesteps, keep only t
        for oldt in list(mem_store.states.keys()):
            if oldt != t:
                del mem_store.states[oldt]

    def log_stats(t):
        np_ = len(producers)
        nc_ = len(consumers)
        sp = average_speed(consumers)
        gn = average_generation(consumers)
        mb = average_metabolism(consumers)
        vs = average_vision(consumers)
        writer.writerow([t, np_, nc_, sp, gn, mb, vs])
        print(f"Timestep {t}: P={np_}, C={nc_}, Sp={sp:.2f}, Gen={gn:.2f}, Met={mb:.2f}, Vis={vs:.2f}")

    def do_simulation_step(t):
        if not producers and not consumers:
            return t
        # 1) update producers
        for p in producers:
            p.update(producers, consumers, environment)
        # 2) update consumers
        for c in consumers:
            c.update(producers, consumers, environment)
        alive_cons = [c for c in consumers if not c.is_dead()]
        consumers.clear()
        consumers.extend(alive_cons)
        # 3) environment
        update_environment(environment)
        t += 1
        store_live_state(t)
        log_stats(t)
        return t

    # store initial
    store_live_state(current_step)
    log_stats(0)

    #
    # Functions to rebuild from HDF5
    #
    def dict_to_producer(d):
        p = Producer(int(d["x"]), int(d["y"]), float(d["energy"]))
        p.id = int(d["id"])
        return p

    def dict_to_consumer(d):
        x = int(d["x"])
        y = int(d["y"])
        en = float(d["energy"])
        gen = int(d["generation"])
        genes = d.get("genes")
        if genes is None:
            c = Consumer(x, y, en, None, gen)
        else:
            # ensure each gene is float
            g_sp = float(genes[0])
            g_met = float(genes[1])
            g_vis = float(genes[2])
            c = Consumer(x, y, en, [g_sp, g_met, g_vis], gen)
        c.id = int(d["id"])
        return c

    while True:
        # AUTO-STEP if we are unpaused
        if not is_paused:
            if mem_store.mode == "replay":
                # if we haven't caught up to the live step, keep stepping forward from HDF5
                if current_step < live_step:
                    current_step += 1
                    loaded = hdf5_storage.load_simulation_state(current_step)
                    if loaded:
                        _, (board, prods, cons, _) = loaded[0]
                        environment[:] = board
                        producers.clear()
                        producers.extend(dict_to_producer(d) for d in prods)
                        consumers.clear()
                        consumers.extend(dict_to_consumer(d) for d in cons)
                    if current_step == live_step:
                        mem_store.mode = "live"
                else:
                    # We are at the live step now, switch to live
                    mem_store.mode = "live"

            else:
                # we are in LIVE mode
                if current_step < MAX_TIMESTEPS:
                    if producers or consumers:
                        current_step = do_simulation_step(current_step)
                        live_step = current_step
                    else:
                        print("Populations extinct. Pausing.")
                        is_paused = True
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
                    # step back if possible
                    if mem_store.is_live() and current_step > 0:
                        mem_store.mode = "replay"
                    if current_step > 0:
                        current_step -= 1
                        loaded = hdf5_storage.load_simulation_state(current_step)
                        if loaded:
                            _, (board, prods, cons, _) = loaded[0]
                            environment[:] = board
                            producers.clear()
                            producers.extend(dict_to_producer(d) for d in prods)
                            consumers.clear()
                            consumers.extend(dict_to_consumer(d) for d in cons)
                elif event.key == STEP_FORWARD_KEY:
                    # step forward if paused, or forcibly in replay
                    if mem_store.mode == "replay":
                        if current_step < live_step:
                            current_step += 1
                            loaded = hdf5_storage.load_simulation_state(current_step)
                            if loaded:
                                _, (board, prods, cons, _) = loaded[0]
                                environment[:] = board
                                producers.clear()
                                producers.extend(dict_to_producer(d) for d in prods)
                                consumers.clear()
                                consumers.extend(dict_to_consumer(d) for d in cons)
                            if current_step == live_step:
                                mem_store.mode = "live"
                        else:
                            # already at live step
                            mem_store.mode = "live"
                    else:
                        # live mode
                        if current_step < MAX_TIMESTEPS:
                            current_step = do_simulation_step(current_step)
                            live_step = current_step

        # drawing
        screen.fill((0,0,0))
        # environment heatmap
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                val = environment[x, y]
                blue_intensity = int(max(0, min(255, val * 255)))
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (0,0,blue_intensity), rect)

        stats_panel = pygame.Surface((STATS_PANEL_WIDTH, DISPLAY_HEIGHT))
        stats_panel.fill((30,30,30))
        screen.blit(stats_panel, (GRID_WIDTH*CELL_SIZE, 0))

        for p in producers:
            px = p.x*CELL_SIZE
            py = p.y*CELL_SIZE
            pygame.draw.circle(
                screen, (0,255,0),
                (px + CELL_SIZE//2, py + CELL_SIZE//2),
                CELL_SIZE//2
            )
        for c in consumers:
            cx = c.x*CELL_SIZE
            cy = c.y*CELL_SIZE
            pygame.draw.circle(
                screen, (255,255,255),
                (cx + CELL_SIZE//2, cy + CELL_SIZE//2),
                CELL_SIZE//2
            )
            label_str = str(c.id)
            label_surf = label_font.render(label_str, True, (0, 0, 0))
            r = label_surf.get_rect(center=(cx + CELL_SIZE//2, cy + CELL_SIZE//2))
            screen.blit(label_surf, r)

        num_p = len(producers)
        num_c = len(consumers)
        sp = average_speed(consumers)
        gn = average_generation(consumers)
        mb = average_metabolism(consumers)
        vs = average_vision(consumers)

        if not producers and not consumers:
            status = "EXTINCT"
            color = (255,0,0)
        elif mem_store.mode == "replay":
            status = "REPLAY"
            color = (255,255,0)
        else:
            status = "LIVE"
            color = (0,255,0)

        stats_x = GRID_WIDTH*CELL_SIZE + 10
        stats_y = 10
        line_h = 25

        def draw_stat(label, value, y_pos, c=(200,200,200)):
            text = f"{label}: {value}"
            surf = stats_font.render(text, True, c)
            screen.blit(surf, (stats_x, y_pos))
            return y_pos + line_h

        y_pos = stats_y
        y_pos = draw_stat("Timestep", current_step, y_pos)
        y_pos = draw_stat("Status", status, y_pos, color)
        y_pos += line_h/2
        y_pos = draw_stat("Producers", num_p, y_pos, (0,255,0))
        y_pos = draw_stat("Consumers", num_c, y_pos, (255,255,255))
        y_pos += line_h/2
        y_pos = draw_stat("Avg Gen", f"{gn:.1f}", y_pos)
        y_pos = draw_stat("Avg Spd", f"{sp:.1f}", y_pos)
        y_pos = draw_stat("Avg Met", f"{mb:.2f}", y_pos)
        y_pos = draw_stat("Avg Vis", f"{vs:.1f}", y_pos)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    run_simulation_interactive()
