#!/usr/bin/env python3
"""
Multi-Species A-Life Simulation (Single File) - Extended Realism
Features:
 - Distinct energy gains for Herbivores vs Carnivores.
 - Stats displayed in columns on right side.
 - Maximum lifespan, reproduction cooldown for realism.
 - Occasional random spawns on the border.
 - Disease system and seasonal changes.
 - Omnivores that can eat both plants and herbivores.
 - Nutrient environment and nutrient cycling.
"""

import sys
import random
import copy
import math
import csv
import pygame
import numpy as np
from utils.constants import *
from utils.toolbox import toolbox
from memory_storage import MemoryResidentSimulationStore
from hdf5_storage import HDF5Storage
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from organisms.omnivore import Omnivore

# Set random seed for reproducibility
random.seed()

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

def update_environment(environment):
    """
    Update the nutrient environment:
    - Decay nutrients naturally
    - Diffuse nutrients between cells
    """
    environment -= NUTRIENT_DECAY_RATE
    environment = np.maximum(environment, 0)  # Ensure we don't go below zero
    
    # Diffusion - copy to avoid changing the environment during diffusion
    temp_env = environment.copy()
    
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = (x+dx) % GRID_WIDTH, (y+dy) % GRID_HEIGHT
                diff_amt = NUTRIENT_DIFFUSION_RATE * (temp_env[x,y] - temp_env[nx,ny])
                environment[x,y] -= diff_amt
                environment[nx,ny] += diff_amt
    
    return environment

###########################################
# HELPER FUNCS: STATS, HISTORY, ETC.
###########################################
class SimulationState:
    def __init__(self, t, producers, herbivores, carnivores, omnivores, environment):
        self.t = t
        self.producers = copy.deepcopy(producers)
        self.herbivores = copy.deepcopy(herbivores)
        self.carnivores = copy.deepcopy(carnivores)
        self.omnivores = copy.deepcopy(omnivores)
        self.environment = np.copy(environment)

def store_state(history, t, producers, herbivores, carnivores, omnivores, environment):
    st = SimulationState(t, producers, herbivores, carnivores, omnivores, environment)
    history.append(st)

def load_state_into_sim(state, producers, herbivores, carnivores, omnivores, environment):
    producers.clear()
    herbivores.clear()
    carnivores.clear()
    omnivores.clear()
    producers.extend(copy.deepcopy(state.producers))
    herbivores.extend(copy.deepcopy(state.herbivores))
    carnivores.extend(copy.deepcopy(state.carnivores))
    omnivores.extend(copy.deepcopy(state.omnivores))
    np.copyto(environment, state.environment)

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
    pygame.display.set_caption("A-Life: Seasons, Disease, Omnivores, Nutrient Environment")
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

    # Initialize environment with nutrients
    environment = np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL)

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

    store_state(history, current_step, producers, herbivores, carnivores, omnivores, environment)

    def do_simulation_step(step):
        # figure out season
        season = current_season(step)
        # adapt spawn chance
        if season == "WINTER":
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * WINTER_SPAWN_MULT
        else:
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * SUMMER_SPAWN_MULT

        # 1) update producers - consume nutrients from environment
        for p in producers:
            p.update(producers, herbivores, carnivores, omnivores, environment)
        producers[:] = [p for p in producers if not p.is_dead()]

        # 2) update herbivores
        for h in herbivores:
            oldx, oldy = h.x, h.y
            h.update(producers, herbivores, carnivores, omnivores, environment)
            if h.is_dead():
                environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        herbivores[:] = [h for h in herbivores if not h.is_dead()]

        # 3) update carnivores
        for c in carnivores:
            oldx, oldy = c.x, c.y
            c.update(producers, herbivores, carnivores, omnivores, environment)
            if c.is_dead():
                environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        carnivores[:] = [c for c in carnivores if not c.is_dead()]

        # 4) update omnivores
        for o in omnivores:
            oldx, oldy = o.x, o.y
            o.update(producers, herbivores, carnivores, omnivores, environment)
            if o.is_dead():
                environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        omnivores[:] = [o for o in omnivores if not o.is_dead()]

        # disease chance
        if random.random() < DISEASE_CHANCE_PER_TURN:
            disease_outbreak(herbivores, carnivores, omnivores)

        # border spawn
        if random.random() < spawn_chance:
            spawn_random_organism_on_border(producers, herbivores, carnivores, omnivores, season)

        # update environment - diffusion and decay
        environment[:] = update_environment(environment)

        step += 1
        store_state(history, step, producers, herbivores, carnivores, omnivores, environment)
        log_and_print_stats(step, producers, herbivores, carnivores, omnivores, writer)
        return step

    # Log initial
    log_and_print_stats(0, producers, herbivores, carnivores, omnivores, writer)

    while True:
        # auto-run if not paused & we're at newest state
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
                        load_state_into_sim(history[current_step], producers, herbivores, carnivores, omnivores, environment)
                elif event.key == STEP_FORWARD_KEY:
                    if is_paused:
                        if current_step < len(history) - 1:
                            current_step += 1
                            load_state_into_sim(history[current_step], producers, herbivores, carnivores, omnivores, environment)
                        else:
                            if current_step < MAX_TIMESTEPS:
                                current_step = do_simulation_step(current_step)

        # draw
        screen.fill((0, 0, 0))

        # Draw nutrient environment - blue gradient (darker blue = more nutrients)
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                val = environment[x, y]  # nutrient level (0 to 1)
                r = int(0 * val)
                g = int(0 * val)
                b = int(255 * val)
                pygame.draw.rect(screen, (r, g, b), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw organisms
        # Producers as green squares
        for p in producers:
            px = p.x * CELL_SIZE
            py = p.y * CELL_SIZE
            pygame.draw.rect(screen, (0, 200, 0), (px, py, CELL_SIZE, CELL_SIZE))

        # Herbivores as white circles
        for h in herbivores:
            hx = h.x * CELL_SIZE
            hy = h.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 255, 255), (hx + CELL_SIZE//2, hy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"H{h.id}", True, (0,0,0))
            screen.blit(lbl, (hx+2, hy+2))

        # Carnivores as red circles
        for c in carnivores:
            cx = c.x * CELL_SIZE
            cy = c.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 0, 0), (cx + CELL_SIZE//2, cy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"C{c.id}", True, (0,0,0))
            screen.blit(lbl, (cx+2, cy+2))

        # Omnivores as orange circles
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
