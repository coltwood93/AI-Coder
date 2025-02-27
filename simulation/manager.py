"""
Core simulation management for the A-Life simulation.
Handles simulation state, updates, and lifecycle.
"""

import random
import numpy as np
from memory_storage import MemoryResidentSimulationStore
from hdf5_storage import HDF5Storage
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from organisms.omnivore import Omnivore
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, INITIAL_NUTRIENT_LEVEL,
    INITIAL_PRODUCERS, PRODUCER_INIT_ENERGY_RANGE,
    INITIAL_HERBIVORES, HERBIVORE_INIT_ENERGY_RANGE,
    INITIAL_CARNIVORES, CARNIVORE_INIT_ENERGY_RANGE,
    INITIAL_OMNIVORES, OMNIVORE_INIT_ENERGY_RANGE,
    DISEASE_CHANCE_PER_TURN, BASE_SPAWN_CHANCE_PER_TURN,
    WINTER_SPAWN_MULT, SUMMER_SPAWN_MULT, MAX_TIMESTEPS, CONSUMER_NUTRIENT_RELEASE
)
from simulation.environment import (
    current_season, update_environment, spawn_random_organism_on_border, disease_outbreak
)
from simulation.history import store_state, load_state_into_sim, SimulationState
from simulation.stats import log_and_print_stats

class SimulationManager:
    """Manages the state and lifecycle of the simulation."""
    
    def __init__(self, csv_writer):
        self.environment = np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL)
        self.producers = []
        self.herbivores = []
        self.carnivores = []
        self.omnivores = []
        self.history = []
        self.current_step = 0
        self.is_paused = False
        self.is_replaying = False
        self.csv_writer = csv_writer
        
        # Initialize storage systems
        self.memory_store = MemoryResidentSimulationStore()
        self.hdf5_store = HDF5Storage("simulation_results.hdf5")
        
        # Initialize organisms
        self._initialize_organisms()
        
        # Store initial state
        self._store_current_state()
        
        # Log initial stats
        log_and_print_stats(0, self.producers, self.herbivores, self.carnivores, self.omnivores, self.csv_writer)
    
    def _initialize_organisms(self):
        """Initialize all organisms in the simulation."""
        # Initialize producers
        for _ in range(INITIAL_PRODUCERS):
            px = random.randint(0, GRID_WIDTH - 1)
            py = random.randint(0, GRID_HEIGHT - 1)
            pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
            self.producers.append(Producer(px, py, pen))
        
        # Initialize herbivores
        for _ in range(INITIAL_HERBIVORES):
            hx = random.randint(0, GRID_WIDTH - 1)
            hy = random.randint(0, GRID_HEIGHT - 1)
            hen = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
            self.herbivores.append(Herbivore(hx, hy, hen))
        
        # Initialize carnivores
        for _ in range(INITIAL_CARNIVORES):
            cx = random.randint(0, GRID_WIDTH - 1)
            cy = random.randint(0, GRID_HEIGHT - 1)
            cen = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
            self.carnivores.append(Carnivore(cx, cy, cen))
        
        # Initialize omnivores
        for _ in range(INITIAL_OMNIVORES):
            ox = random.randint(0, GRID_WIDTH - 1)
            oy = random.randint(0, GRID_HEIGHT - 1)
            oen = random.randint(*OMNIVORE_INIT_ENERGY_RANGE)
            self.omnivores.append(Omnivore(ox, oy, oen))
    
    def _store_current_state(self):
        """Store current state in history and external storage."""
        store_state(
            self.history, self.current_step, 
            self.producers, self.herbivores, self.carnivores, self.omnivores, 
            self.environment
        )
        
        # Also store in external storage systems
        if self.current_step > 0:  # Only for steps after initial
            self.memory_store.update_state(
                self.current_step, self.environment,
                producers=self.producers,
                herbivores=self.herbivores,
                carnivores=self.carnivores,
                omnivores=self.omnivores
            )
            self.hdf5_store.save_state(
                self.current_step, self.environment,
                producers=self.producers,
                herbivores=self.herbivores,
                carnivores=self.carnivores,
                omnivores=self.omnivores
            )
    
    def step_simulation(self):
        """Execute one step of the simulation."""
        # Don't step if we've reached the maximum timesteps
        if self.current_step >= MAX_TIMESTEPS:
            return False
        
        # Calculate season and spawn chance
        season = current_season(self.current_step)
        if season == "WINTER":
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * WINTER_SPAWN_MULT
        else:
            spawn_chance = BASE_SPAWN_CHANCE_PER_TURN * SUMMER_SPAWN_MULT
        
        # Update all organisms
        self._update_producers()
        self._update_herbivores()
        self._update_carnivores()
        self._update_omnivores()
        
        # Handle disease outbreak chance
        if random.random() < DISEASE_CHANCE_PER_TURN:
            disease_outbreak(self.herbivores, self.carnivores, self.omnivores)
        
        # Handle random border spawns
        if random.random() < spawn_chance:
            spawn_random_organism_on_border(
                self.producers, self.herbivores, self.carnivores, self.omnivores, season
            )
        
        # Update the environment
        self.environment[:] = update_environment(self.environment)
        
        # Increment step counter
        self.current_step += 1
        
        # Store current state
        self._store_current_state()
        
        # Log stats
        log_and_print_stats(
            self.current_step, 
            self.producers, self.herbivores, self.carnivores, self.omnivores, 
            self.csv_writer
        )
        
        return True
    
    def _update_producers(self):
        """Update all producers."""
        for p in self.producers:
            p.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
        self.producers[:] = [p for p in self.producers if not p.is_dead()]
    
    def _update_herbivores(self):
        """Update all herbivores."""
        for h in self.herbivores:
            oldx, oldy = h.x, h.y
            h.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
            if h.is_dead():
                self.environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        self.herbivores[:] = [h for h in self.herbivores if not h.is_dead()]
    
    def _update_carnivores(self):
        """Update all carnivores."""
        for c in self.carnivores:
            oldx, oldy = c.x, c.y
            c.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
            if c.is_dead():
                self.environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        self.carnivores[:] = [c for c in self.carnivores if not c.is_dead()]
    
    def _update_omnivores(self):
        """Update all omnivores."""
        for o in self.omnivores:
            oldx, oldy = o.x, o.y
            o.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
            if o.is_dead():
                self.environment[oldx, oldy] += CONSUMER_NUTRIENT_RELEASE
        self.omnivores[:] = [o for o in self.omnivores if not o.is_dead()]
    
    def step_back(self):
        """Step back one step in simulation history."""
        if self.current_step > 0:
            self.current_step -= 1
            load_state_into_sim(
                self.history[self.current_step],
                self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment
            )
            self.is_replaying = True
            return True
        return False
    
    def step_forward(self):
        """Step forward one step in simulation history."""
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            load_state_into_sim(
                self.history[self.current_step],
                self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment
            )
            self.is_replaying = True
            
            # Check if we've reached the end of history
            if self.current_step == len(self.history) - 1:
                self.is_replaying = False
            
            return True
        return False
    
    def reset(self):
        """Reset the simulation to initial state."""
        # Clear data structures
        self.environment = np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL)
        self.producers = []
        self.herbivores = []
        self.carnivores = []
        self.omnivores = []
        
        # Reset flags and counters
        self.current_step = 0
        self.is_paused = False
        self.is_replaying = False
        
        # Reset the history
        self.history = []
        
        # Reset storage systems to avoid "replay mode" errors
        try:
            self.memory_store = MemoryResidentSimulationStore(mode="live")
        except Exception as e:
            print(f"Warning: Error creating new memory store: {e}")
            # As a fallback, try to reset the existing store's mode
            if hasattr(self.memory_store, 'mode'):
                self.memory_store.mode = "live"
            if hasattr(self.memory_store, 'states'):
                self.memory_store.states = {}
        
        try:
            self.hdf5_store = HDF5Storage("simulation_results.hdf5")
        except Exception as e:
            print(f"Warning: Error creating new HDF5 store: {e}")
        
        # Reset the frame counter in the main app if it exists
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, 'frame_counter'):
                obj.frame_counter = 0
        
        # Reset the ID counters in all organism classes
        self._reset_organism_id_counters()
        
        # Reinitialize organisms
        self._initialize_organisms()
        
        # Store initial state
        self._store_current_state()
        
        # Log initial stats
        log_and_print_stats(0, self.producers, self.herbivores, self.carnivores, self.omnivores, self.csv_writer)
        
        print("Simulation reset complete")

    def _reset_organism_id_counters(self):
        """Reset the ID counters for all organism types."""
        from organisms.producer import Producer
        from organisms.herbivore import Herbivore
        from organisms.carnivore import Carnivore
        from organisms.omnivore import Omnivore
        
        # Call reset_id_counter on each organism class
        Producer.reset_id_counter()
        Herbivore.reset_id_counter()
        Carnivore.reset_id_counter()
        Omnivore.reset_id_counter()
        
        print("Reset all organism ID counters")
