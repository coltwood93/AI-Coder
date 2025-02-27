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
import csv
import pygame
import numpy as np
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, STATS_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    INITIAL_PRODUCERS, PRODUCER_INIT_ENERGY_RANGE,  
    INITIAL_HERBIVORES, HERBIVORE_INIT_ENERGY_RANGE,
    INITIAL_CARNIVORES, CARNIVORE_INIT_ENERGY_RANGE,
    INITIAL_OMNIVORES, OMNIVORE_INIT_ENERGY_RANGE,
    SEASON_LENGTH, DISEASE_CHANCE_PER_TURN, DISEASE_DURATION,
    NUTRIENT_DECAY_RATE, NUTRIENT_DIFFUSION_RATE, INITIAL_NUTRIENT_LEVEL,
    CONSUMER_NUTRIENT_RELEASE, MAX_TIMESTEPS, FPS,
    PAUSE_KEY, STEP_BACK_KEY, STEP_FORWARD_KEY,
    BASE_SPAWN_CHANCE_PER_TURN, WINTER_SPAWN_MULT, SUMMER_SPAWN_MULT
)
from memory_storage import MemoryResidentSimulationStore
from hdf5_storage import HDF5Storage
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from organisms.omnivore import Omnivore

# Set random seed for reproducibility
random.seed()

# Define state constants - add these at the top of the file or where constants are defined
MAIN_MENU = "main_menu"
OPTIONS_MENU = "options_menu"
SIMULATION = "simulation"
PAUSE_MENU = "pause_menu"

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

    memory_store = MemoryResidentSimulationStore()
    hdf5_store = HDF5Storage("simulation_results.hdf5")

    history = []
    current_step = 0
    is_paused = False
    is_replaying = False

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

        # Use the updated signatures
        memory_store.update_state(
            step,
            environment,
            producers=producers,
            herbivores=herbivores,
            carnivores=carnivores,
            omnivores=omnivores
        )
        hdf5_store.save_state(
            step,
            environment,
            producers=producers,
            herbivores=herbivores,
            carnivores=carnivores,
            omnivores=omnivores
        )

        log_and_print_stats(step, producers, herbivores, carnivores, omnivores, writer)
        return step

    # Log initial
    log_and_print_stats(0, producers, herbivores, carnivores, omnivores, writer)

    # MAIN GAME LOOP - This is the key part that needs attention
    current_state = MAIN_MENU  # Start in the main menu
    from_main_menu = True
    running = True
    is_paused = False  # Start unpaused when simulation begins

    # Debug print to verify initial state
    print(f"Starting in state: {current_state}")

    def render_simulation(surface):
        """Renders the simulation state to the given surface."""
        surface.fill((0, 0, 0))
        
        # Render environment (nutrient levels as blue gradient)
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                val = environment[x, y]
                r = int(0 * val)
                g = int(0 * val)
                b = int(255 * val)
                pygame.draw.rect(surface, (r, g, b), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Render producers (green squares)
        for p in producers:
            px = p.x * CELL_SIZE
            py = p.y * CELL_SIZE
            pygame.draw.rect(surface, (0, 200, 0), (px, py, CELL_SIZE, CELL_SIZE))

        # Render herbivores (white circles)
        for h in herbivores:
            hx = h.x * CELL_SIZE
            hy = h.y * CELL_SIZE
            pygame.draw.circle(surface, (255, 255, 255), (hx + CELL_SIZE//2, hy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"H{h.id}", True, (0,0,0))
            surface.blit(lbl, (hx+2, hy+2))

        # Render carnivores (red circles)
        for c in carnivores:
            cx = c.x * CELL_SIZE
            cy = c.y * CELL_SIZE
            pygame.draw.circle(surface, (255, 0, 0), (cx + CELL_SIZE//2, cy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"C{c.id}", True, (0,0,0))
            surface.blit(lbl, (cx+2, cy+2))

        # Render omnivores (orange circles)
        for o in omnivores:
            ox = o.x * CELL_SIZE
            oy = o.y * CELL_SIZE
            pygame.draw.circle(surface, (255, 165, 0), (ox + CELL_SIZE//2, oy + CELL_SIZE//2), CELL_SIZE//2)
            lbl = label_font.render(f"O{o.id}", True, (0,0,0))
            surface.blit(lbl, (ox+2, oy+2))

        # Render stats panel
        panel_x = GRID_WIDTH * CELL_SIZE
        pygame.draw.rect(surface, (30, 30, 30), (panel_x, 0, STATS_PANEL_WIDTH, WINDOW_HEIGHT))

        p_count = len(producers)
        (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)
        h_count = len(herbivores)
        (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)
        c_count = len(carnivores)
        (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(omnivores)
        o_count = len(omnivores)

        row_y = 20
        surf_p = main_font.render("Producers", True, (200, 200, 0))
        surface.blit(surf_p, (panel_x + 10, row_y))
        surf_h = main_font.render("Herbivores", True, (200, 200, 200))
        surface.blit(surf_h, (panel_x + 80, row_y))
        surf_c = main_font.render("Carnivores", True, (255, 100, 100))
        surface.blit(surf_c, (panel_x + 150, row_y))

        row_y += 25
        lbl_p = main_font.render(f"# {p_count}", True, (200, 200, 0))
        surface.blit(lbl_p, (panel_x + 20, row_y))

        lbl_hc = main_font.render(f"# {h_count}", True, (200, 200, 200))
        surface.blit(lbl_hc, (panel_x + 90, row_y))
        lbl_hsp = main_font.render(f"Sp {h_sp:.1f}", True, (200, 200, 200))
        surface.blit(lbl_hsp, (panel_x + 90, row_y+20))
        lbl_hgen = main_font.render(f"Gn {h_gen:.1f}", True, (200, 200, 200))
        surface.blit(lbl_hgen, (panel_x + 90, row_y+40))
        lbl_hmet = main_font.render(f"Mt {h_met:.1f}", True, (200, 200, 200))
        surface.blit(lbl_hmet, (panel_x + 90, row_y+60))
        lbl_hvis = main_font.render(f"Vs {h_vis:.1f}", True, (200, 200, 200))
        surface.blit(lbl_hvis, (panel_x + 90, row_y+80))

        lbl_cc = main_font.render(f"# {c_count}", True, (255, 100, 100))
        surface.blit(lbl_cc, (panel_x + 160, row_y))
        lbl_csp = main_font.render(f"Sp {c_sp:.1f}", True, (255, 100, 100))
        surface.blit(lbl_csp, (panel_x + 160, row_y+20))
        lbl_cgen = main_font.render(f"Gn {c_gen:.1f}", True, (255, 100, 100))
        surface.blit(lbl_cgen, (panel_x + 160, row_y+40))
        lbl_cmet = main_font.render(f"Mt {c_met:.1f}", True, (255, 100, 100))
        surface.blit(lbl_cmet, (panel_x + 160, row_y+60))
        lbl_cvis = main_font.render(f"Vs {c_vis:.1f}", True, (255, 100, 100))
        surface.blit(lbl_cvis, (panel_x + 160, row_y+80))

        row_y2 = row_y + 120
        surf_o = main_font.render("Omnivores", True, (255, 165, 0))
        surface.blit(surf_o, (panel_x + 80, row_y2))

        row_y2 += 25
        lbl_oc = main_font.render(f"# {o_count}", True, (255, 165, 0))
        surface.blit(lbl_oc, (panel_x + 90, row_y2))
        lbl_osp = main_font.render(f"Sp {o_sp:.1f}", True, (255, 165, 0))
        surface.blit(lbl_osp, (panel_x + 90, row_y2+20))
        lbl_ogen = main_font.render(f"Gn {o_gen:.1f}", True, (255, 165, 0))
        surface.blit(lbl_ogen, (panel_x + 90, row_y2+40))
        lbl_omet = main_font.render(f"Mt {o_met:.1f}", True, (255, 165, 0))
        surface.blit(lbl_omet, (panel_x + 90, row_y2+60))
        lbl_ovis = main_font.render(f"Vs {o_vis:.1f}", True, (255, 165, 0))
        surface.blit(lbl_ovis, (panel_x + 90, row_y2+80))

        season_now = current_season(current_step)
        status_str = "PAUSED" if is_paused else "RUN"
        info_str = f"Timestep: {current_step}, Season: {season_now}, [{status_str}]"
        text_surf = main_font.render(info_str, True, (255, 255, 255))
        surface.blit(text_surf, (panel_x + 10, WINDOW_HEIGHT - 30))

    while running:
        # Handle events based on the current state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Debug event handling
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)} in state: {current_state}")

            # State-specific event handling
            if current_state == MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        print("Starting simulation from main menu")
                        current_state = SIMULATION
                        is_paused = False  # Ensure simulation starts unpaused
                    elif event.key == pygame.K_o:
                        print("Opening options from main menu")
                        current_state = OPTIONS_MENU
                        from_main_menu = True
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        print("Quitting from main menu")
                        running = False
            
            elif current_state == OPTIONS_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print(f"Returning from options to {'main menu' if from_main_menu else 'pause menu'}")
                        current_state = MAIN_MENU if from_main_menu else PAUSE_MENU
                    elif event.key == pygame.K_q:
                        print("Quitting from options menu")
                        running = False
            
            elif current_state == SIMULATION:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        print(f"{'Pausing' if not is_paused else 'Resuming'} simulation")
                        is_paused = not is_paused
                    elif event.key == pygame.K_ESCAPE:
                        print("Opening pause menu")
                        current_state = PAUSE_MENU
                    elif event.key == STEP_BACK_KEY:
                        # Auto-pause if not already paused
                        if not is_paused:
                            print("Auto-pausing for step back")
                            is_paused = True
                            
                        # Then perform the step back operation
                        if current_step > 0:
                            print(f"Stepping back to {current_step-1}")
                            current_step -= 1
                            load_state_into_sim(history[current_step],
                                            producers, herbivores, carnivores, omnivores, environment)
                            is_replaying = True
                    elif event.key == STEP_FORWARD_KEY:
                        # Auto-pause if not already paused
                        if not is_paused:
                            print("Auto-pausing for step forward")
                            is_paused = True
                            
                        # Then perform the step forward operation
                        if current_step < len(history) - 1:
                            print(f"Stepping forward to {current_step+1}")
                            current_step += 1
                            load_state_into_sim(history[current_step],
                                            producers, herbivores, carnivores, omnivores, environment)
                            is_replaying = True
                        elif current_step < MAX_TIMESTEPS:
                            print(f"Simulating next step from {current_step}")
                            current_step = do_simulation_step(current_step)
            
            elif current_state == PAUSE_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r or event.key == pygame.K_p:
                        print("Resuming simulation from pause menu")
                        current_state = SIMULATION
                        is_paused = False
                    elif event.key == pygame.K_o:
                        print("Opening options from pause menu")
                        current_state = OPTIONS_MENU
                        from_main_menu = False
                    elif event.key == pygame.K_m:
                        print("Returning to main menu from pause menu")
                        current_state = MAIN_MENU
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        print("Quitting from pause menu")
                        running = False

        # Update simulation state if in simulation mode and not paused
        if current_state == SIMULATION and not is_paused:
            if is_replaying and current_step < len(history) - 1:
                # Replay mode - stepping through history
                print(f"Replaying step: {current_step+1}")
                current_step += 1
                load_state_into_sim(history[current_step], 
                                producers, herbivores, carnivores, omnivores, environment)
                
                # Check if we've reached the end of history
                if current_step == len(history) - 1:
                    print("Reached end of history, switching to live simulation")
                    is_replaying = False
            elif not is_replaying and current_step < MAX_TIMESTEPS:
                # Live simulation mode - calculating new steps
                current_step = do_simulation_step(current_step)

        # Clear the screen before drawing
        screen.fill((0, 0, 0))

        # Render the current screen based on state
        if current_state == MAIN_MENU:
            # Clear screen and draw the main menu
            screen.fill((0, 0, 50))
            font = pygame.font.SysFont(None, 48)
            title_surf = font.render("A-Life Simulation", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
            screen.blit(title_surf, title_rect)
            
            small_font = pygame.font.SysFont(None, 32)
            instructions = [
                "[S] Start Simulation",
                "[O] Options",
                "[Q/ESC] Quit"
            ]
            y = 200
            for line in instructions:
                text = small_font.render(line, True, (200, 200, 200))
                rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
                screen.blit(text, rect)
                y += 40
            
        elif current_state == OPTIONS_MENU:
            # Draw the options menu
            screen.fill((30, 30, 30))
            font = pygame.font.SysFont(None, 48)
            title_surf = font.render("OPTIONS", True, (200, 200, 200))
            title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
            screen.blit(title_surf, title_rect)
            
            small_font = pygame.font.SysFont(None, 32)
            return_text = "[ESC] Return to " + ("Main Menu" if from_main_menu else "Pause Menu")
            lines = [
                return_text,
                "[Q] Quit"
            ]
            y = 200
            for line in lines:
                text = small_font.render(line, True, (220, 220, 220))
                rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
                screen.blit(text, rect)
                y += 40
            
        elif current_state == SIMULATION:
            # Draw the simulation
            render_simulation(screen)
            
        elif current_state == PAUSE_MENU:
            # Draw the simulation with pause menu overlay
            render_simulation(screen)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.SysFont(None, 48)
            text_surf = font.render("PAUSED", True, (255, 255, 255))
            rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
            screen.blit(text_surf, rect)
            
            small_font = pygame.font.SysFont(None, 32)
            menu_items = [
                "[R/P] Resume",
                "[O] Options",
                "[M] Main Menu",
                "[Q/ESC] Quit"
            ]
            y = 200
            for item in menu_items:
                line_surf = small_font.render(item, True, (200, 200, 200))
                rect = line_surf.get_rect(center=(WINDOW_WIDTH // 2, y))
                screen.blit(line_surf, rect)
                y += 40

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    # Clean up resources
    csvfile.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_simulation_interactive()
