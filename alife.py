#!/usr/bin/env python3

"""
Two-Species A-Life (Producers & Consumers) with:
- Speed-Vision synergy
- Discovery bonus
- Baseline costs
- Removal of eaten producers
- **Consumer labeling** so you can see if they are truly speed=0 or just not moving

Press 'P' to pause/unpause, Left/Right arrows to step back/forward while paused.
"""

import sys
import random
import copy
import math
import csv
import pygame

# =====================
# GLOBAL PARAMS
# =====================
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20
DISPLAY_WIDTH = GRID_WIDTH * CELL_SIZE
DISPLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Producer
INITIAL_PRODUCERS = 8
PRODUCER_ENERGY_GAIN = 0.3
PRODUCER_MAX_ENERGY = 30
PRODUCER_SEED_COST = 5
PRODUCER_SEED_PROB = 0.05
PRODUCER_INIT_ENERGY_RANGE = (5,15)

# Consumer
INITIAL_CONSUMERS = 8
CONSUMER_INIT_ENERGY_RANGE = (5,15)
BASE_LIFE_COST = 3.0     # baseline cost each turn
MOVE_COST_FACTOR = 0.01  # cost per step = this * metabolism
EAT_GAIN = 3
CONSUMER_REPRO_THRESHOLD = 20

# Genes: [base_speed, metabolism, base_vision]
MUTATION_RATE = 0.1
SPEED_RANGE = (0,5)
METABOLISM_RANGE = (0.5,2.5)
VISION_RANGE = (0,10)

VISION_BASE = 1
VISION_SPEED_FACTOR = 3.0

DISCOVERY_BONUS = 0.5
TRACK_CELL_HISTORY_LEN = 20

NO_SEED_UNDER_CONSUMER = True
MAX_TIMESTEPS = 200
FPS = 6

random.seed()

# Pygame keys
PAUSE_KEY = pygame.K_p
STEP_BACK_KEY = pygame.K_LEFT
STEP_FORWARD_KEY = pygame.K_RIGHT

# =====================
# PRODUCER
# =====================
class Producer:
    """Plant-like species. Gains energy, seeds new producers, no movement."""
    next_id = 0
    def __init__(self, x, y, energy=10):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = Producer.next_id
        Producer.next_id += 1

    def update(self, producers_list, consumers_list):
        self.energy += PRODUCER_ENERGY_GAIN
        if self.energy > PRODUCER_MAX_ENERGY:
            self.energy = PRODUCER_MAX_ENERGY

        # Possibly seed
        if self.energy > PRODUCER_SEED_COST and random.random() < PRODUCER_SEED_PROB:
            self.energy -= PRODUCER_SEED_COST
            nx, ny = self.random_adjacent()
            if NO_SEED_UNDER_CONSUMER:
                # no seed if consumer is on that cell
                any_consumer = any((c.x == nx and c.y == ny) for c in consumers_list)
                if any_consumer:
                    return
            baby_energy = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
            baby = Producer(nx, ny, baby_energy)
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


# =====================
# CONSUMER
# =====================
class Consumer:
    """
    Genes: [base_speed, metabolism, base_vision].
    Actual speed = int(base_speed).
    Actual vision = VISION_BASE + base_vision + speed*VISION_SPEED_FACTOR.
    Each consumer has a unique ID, displayed in black text on the circle.
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
            base_speed = random.randint(SPEED_RANGE[0], SPEED_RANGE[1])
            metabolism = random.uniform(METABOLISM_RANGE[0], METABOLISM_RANGE[1])
            base_vision = random.randint(VISION_RANGE[0], VISION_RANGE[1])
            self.genes = [base_speed, metabolism, base_vision]
        else:
            self.genes = genes

        self.recent_cells = [(x, y)]  # track visited cells to apply discovery bonus

    @property
    def speed(self):
        return int(self.genes[0])

    @property
    def metabolism(self):
        return float(self.genes[1])

    @property
    def base_vision(self):
        return float(self.genes[2])

    @property
    def vision(self):
        return int(VISION_BASE + self.base_vision + (self.speed * VISION_SPEED_FACTOR))

    def update(self, producers_list, consumers_list):
        # Baseline cost
        self.energy -= BASE_LIFE_COST
        if self.energy <= 0:
            return

        # Movement
        steps = self.speed
        for _ in range(steps):
            direction = self.find_nearest_producer(producers_list)
            if direction:
                self.move_towards(direction)
            else:
                self.move_random()
            self.energy -= (MOVE_COST_FACTOR * self.metabolism)
            if self.energy <= 0:
                return

        # Discovery bonus
        if DISCOVERY_BONUS > 0:
            if (self.x, self.y) not in self.recent_cells:
                self.energy += DISCOVERY_BONUS
                self.recent_cells.append((self.x, self.y))
                if len(self.recent_cells) > TRACK_CELL_HISTORY_LEN:
                    self.recent_cells.pop(0)

        # Eat
        self.check_and_eat(producers_list)

        # Reproduce
        if self.energy >= CONSUMER_REPRO_THRESHOLD:
            self.reproduce(consumers_list)

    def find_nearest_producer(self, producers_list):
        best_dist = self.vision + 1
        best_dx, best_dy = 0,0
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

    def move_towards(self, direction):
        dx, dy = direction
        if dx > 0:
            self.x = (self.x + 1) % GRID_WIDTH
        elif dx < 0:
            self.x = (self.x - 1) % GRID_WIDTH
        if dy > 0:
            self.y = (self.y + 1) % GRID_HEIGHT
        elif dy < 0:
            self.y = (self.y - 1) % GRID_HEIGHT

    def move_random(self):
        d = random.choice(["UP","DOWN","LEFT","RIGHT"])
        if d == "UP":
            self.y = (self.y - 1) % GRID_HEIGHT
        elif d == "DOWN":
            self.y = (self.y + 1) % GRID_HEIGHT
        elif d == "LEFT":
            self.x = (self.x - 1) % GRID_WIDTH
        elif d == "RIGHT":
            self.x = (self.x + 1) % GRID_WIDTH

    def check_and_eat(self, producers_list):
        for p in producers_list:
            if p.x == self.x and p.y == self.y:
                self.energy += EAT_GAIN
                p.energy = 0  # mark eaten
                break

    def reproduce(self, consumers_list):
        child_energy = self.energy // 2
        self.energy -= child_energy
        new_gen = self.generation + 1
        child_genes = copy.deepcopy(self.genes)
        child_genes = self.mutate_genes(child_genes)

        baby = Consumer(
            x=self.x, y=self.y,
            energy=child_energy,
            genes=child_genes,
            generation=new_gen
        )
        consumers_list.append(baby)

    def mutate_genes(self, genes):
        # [base_speed, metabolism, base_vision]
        if random.random() < MUTATION_RATE:
            genes[0] += random.gauss(0, 1)
        if random.random() < MUTATION_RATE:
            genes[1] += random.gauss(0, 0.1)
        if random.random() < MUTATION_RATE:
            genes[2] += random.gauss(0, 1)
        # clamp
        genes[0] = max(SPEED_RANGE[0], min(SPEED_RANGE[1], genes[0]))
        genes[1] = max(METABOLISM_RANGE[0], min(METABOLISM_RANGE[1], genes[1]))
        genes[2] = max(VISION_RANGE[0], min(VISION_RANGE[1], genes[2]))
        return genes

    def is_dead(self):
        return self.energy <= 0

# =====================
# SNAPSHOT/HISTORY
# =====================
class SimulationState:
    def __init__(self, t, producers, consumers):
        self.t = t
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

# =====================
# STATS
# =====================
def average_speed(cons):
    if not cons: return 0.0
    return sum(c.speed for c in cons) / len(cons)

def average_generation(cons):
    if not cons: return 0.0
    return sum(c.generation for c in cons) / len(cons)

def average_metabolism(cons):
    if not cons: return 0.0
    return sum(c.metabolism for c in cons) / len(cons)

def average_vision(cons):
    if not cons: return 0.0
    return sum(c.vision for c in cons)/len(cons)

# =====================
# MAIN INTERACTIVE
# =====================
def run_simulation_interactive():
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Two-Species: Eaten producer removal + labeling")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    label_font = pygame.font.SysFont(None, 16)

    csv_filename = "results_interactive.csv"
    csvfile = open(csv_filename, "w", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(["Timestep","Producers","Consumers","AvgSpeed","AvgGen","AvgMetab","AvgVision"])

    # init producers
    producers = []
    for _ in range(INITIAL_PRODUCERS):
        px = random.randint(0, GRID_WIDTH-1)
        py = random.randint(0, GRID_HEIGHT-1)
        pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
        producers.append(Producer(px, py, pen))

    # init consumers
    consumers = []
    for _ in range(INITIAL_CONSUMERS):
        cx = random.randint(0, GRID_WIDTH-1)
        cy = random.randint(0, GRID_HEIGHT-1)
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

        # remove eaten producers => energy=0
        alive_prods = [p for p in producers if p.energy>0 and not p.is_dead()]
        producers.clear()
        producers.extend(alive_prods)

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
        # auto-run if not paused & at last step
        if not is_paused and current_step == len(history)-1:
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
                    if is_paused and current_step>0:
                        current_step -= 1
                        load_state_into_sim(history[current_step], producers, consumers)
                elif event.key == STEP_FORWARD_KEY:
                    if is_paused:
                        if current_step < len(history)-1:
                            current_step += 1
                            load_state_into_sim(history[current_step], producers, consumers)
                        else:
                            if current_step < MAX_TIMESTEPS:
                                current_step = do_simulation_step(current_step)

        st = history[current_step]
        load_state_into_sim(st, producers, consumers)

        screen.fill((0,0,0))
        # draw producers (green)
        for p in producers:
            px = p.x*CELL_SIZE
            py = p.y*CELL_SIZE
            pygame.draw.circle(screen, (0,255,0), (px+CELL_SIZE//2, py+CELL_SIZE//2), CELL_SIZE//2)

        # draw consumers (white) + label
        for c in consumers:
            cx = c.x*CELL_SIZE
            cy = c.y*CELL_SIZE
            pygame.draw.circle(screen, (255,255,255), (cx+CELL_SIZE//2, cy+CELL_SIZE//2), CELL_SIZE//2)

            # label each consumer ID
            label_str = str(c.id)
            label_surf = label_font.render(label_str, True, (0,0,0))
            label_rect = label_surf.get_rect(center=(cx + CELL_SIZE//2, cy + CELL_SIZE//2))
            screen.blit(label_surf, label_rect)

        np = len(producers)
        nc = len(consumers)
        sp = average_speed(consumers)
        gn = average_generation(consumers)
        mb = average_metabolism(consumers)
        vs = average_vision(consumers)
        status = "PAUSED" if is_paused else "RUN"
        info_str = f"t={current_step} | P={np} | C={nc} | sp={sp:.2f} | gen={gn:.2f} | met={mb:.2f} | vis={vs:.2f} | {status}"
        text_surf = font.render(info_str, True, (255,255,255))
        screen.blit(text_surf, (10,10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation_interactive()
