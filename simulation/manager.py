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
    PRODUCER_INIT_ENERGY_RANGE,
    HERBIVORE_INIT_ENERGY_RANGE,
    CARNIVORE_INIT_ENERGY_RANGE,
    OMNIVORE_INIT_ENERGY_RANGE,
    DISEASE_CHANCE_PER_TURN, BASE_SPAWN_CHANCE_PER_TURN,
    WINTER_SPAWN_MULT, SUMMER_SPAWN_MULT, MAX_TIMESTEPS, CONSUMER_NUTRIENT_RELEASE
)
from simulation.environment import (
    current_season, update_environment, spawn_random_organism_on_border, disease_outbreak
)
from simulation.history import store_state, load_state_into_sim
from simulation.stats import log_and_print_stats, calc_traits_avg

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
        
        # Add a population history tracker
        self.population_history = []
        
        # Add skip counter
        self.step_counter = 0
        
        # Initialize organisms
        self._initialize_organisms()
        
        # Store initial state and population data
        self._store_current_state()
        self._store_population_stats()
        
        # Log initial stats
        log_and_print_stats(0, self.producers, self.herbivores, self.carnivores, self.omnivores, self.csv_writer)
    
    def _initialize_organisms(self):
        """Initialize all organisms in the simulation."""
        # Get the current config values for organism counts
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        
        # Get grid dimensions
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        # Get organism counts from config
        producer_count = config.get_initial_count("producers")
        herbivore_count = config.get_initial_count("herbivores")
        carnivore_count = config.get_initial_count("carnivores")
        omnivore_count = config.get_initial_count("omnivores")
        
        print(f"Initializing organisms: {producer_count} producers, {herbivore_count} herbivores, "
              f"{carnivore_count} carnivores, {omnivore_count} omnivores")
        
        # Initialize producers
        for _ in range(producer_count):
            px = random.randint(0, grid_width - 1)
            py = random.randint(0, grid_height - 1)
            pen = random.randint(*PRODUCER_INIT_ENERGY_RANGE)
            self.producers.append(Producer(px, py, pen))
        
        # Initialize herbivores
        for _ in range(herbivore_count):
            hx = random.randint(0, grid_width - 1)
            hy = random.randint(0, grid_height - 1)
            hen = random.randint(*HERBIVORE_INIT_ENERGY_RANGE)
            self.herbivores.append(Herbivore(hx, hy, hen))
        
        # Initialize carnivores
        for _ in range(carnivore_count):
            cx = random.randint(0, grid_width - 1)
            cy = random.randint(0, grid_height - 1)
            cen = random.randint(*CARNIVORE_INIT_ENERGY_RANGE)
            self.carnivores.append(Carnivore(cx, cy, cen))
        
        # Initialize omnivores
        for _ in range(omnivore_count):
            ox = random.randint(0, grid_width - 1)
            oy = random.randint(0, grid_height - 1)
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
    
    def _store_population_stats(self):
        """Store current population statistics for historical tracking."""
        p_count = len(self.producers)
        h_count = len(self.herbivores)
        (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(self.herbivores)
        c_count = len(self.carnivores)
        (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(self.carnivores)
        o_count = len(self.omnivores)
        (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(self.omnivores)
        
        # Store in history
        self.population_history.append({
            'step': self.current_step,
            'producers': p_count,
            'herbivores': h_count,
            'carnivores': c_count,
            'omnivores': o_count,
            'stats': {
                'producers': {'count': p_count},
                'herbivores': {'count': h_count, 'speed': h_sp, 'generation': h_gen, 'metabolism': h_met, 'vision': h_vis},
                'carnivores': {'count': c_count, 'speed': c_sp, 'generation': c_gen, 'metabolism': c_met, 'vision': c_vis},
                'omnivores': {'count': o_count, 'speed': o_sp, 'generation': o_gen, 'metabolism': o_met, 'vision': o_vis}
            }
        })
    
    def step_simulation(self):
        """Execute one step of the simulation."""
        # Don't step if we've reached the maximum timesteps
        if self.current_step >= MAX_TIMESTEPS:
            return False
        
        # Get current step skip value from config
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        step_skip = config.get_step_skip()
        
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
        self.step_counter += 1
        
        # Calculate if this is a step we should display based on the skip setting
        should_display = (self.step_counter >= step_skip)
        
        # Always store the state in history for proper step-by-step navigation
        self._store_current_state()
        self._store_population_stats()
        
        # Reset step counter if we should display this frame
        if should_display:
            self.step_counter = 0
        
        # Always log stats to CSV to maintain continuity
        log_and_print_stats(
            self.current_step, 
            self.producers, self.herbivores, self.carnivores, self.omnivores, 
            self.csv_writer
        )
        
        return should_display  # Return whether we should display this step
    
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
                # Add nutrients using [y, x] coordinate order for NumPy arrays
                self.environment[oldy, oldx] += CONSUMER_NUTRIENT_RELEASE
        self.herbivores[:] = [h for h in self.herbivores if not h.is_dead()]
    
    def _update_carnivores(self):
        """Update all carnivores."""
        for c in self.carnivores:
            oldx, oldy = c.x, c.y
            c.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
            if c.is_dead():
                # Add nutrients using [y, x] coordinate order for NumPy arrays
                self.environment[oldy, oldx] += CONSUMER_NUTRIENT_RELEASE
        self.carnivores[:] = [c for c in self.carnivores if not c.is_dead()]
    
    def _update_omnivores(self):
        """Update all omnivores."""
        for o in self.omnivores:
            oldx, oldy = o.x, o.y
            o.update(self.producers, self.herbivores, self.carnivores, self.omnivores, self.environment)
            if o.is_dead():
                # Add nutrients using [y, x] coordinate order for NumPy arrays
                self.environment[oldy, oldx] += CONSUMER_NUTRIENT_RELEASE
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
        # Get current grid dimensions from config manager
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        grid_width = config.get_grid_width()
        grid_height = config.get_grid_height()
        
        # Reset the organism ID counters
        Producer.reset_id_counter()
        Herbivore.reset_id_counter()
        Carnivore.reset_id_counter()
        Omnivore.reset_id_counter()
        
        # Initialize environment with proper dimensions
        # Note: Create as height x width (rows x columns) to match NumPy convention
        self.environment = np.full((grid_height, grid_width), INITIAL_NUTRIENT_LEVEL)
        
        # Print grid dimensions for debugging
        print(f"Created new environment with shape: {self.environment.shape}")
        
        # Clear data structures
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
        self.population_history = []  # Also reset population history
        
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
        
        # Instead of gc.get_objects(), do something like:
        for org in (self.producers + self.herbivores + self.carnivores + self.omnivores):
            if hasattr(org, 'frame_counter'):
                org.frame_counter = 0
        
        # Reset the ID counters in all organism classes
        self._reset_organism_id_counters()
        
        # Initialize organisms using the helper method that gets values from config
        self._initialize_organisms()
        
        # Store initial state
        self._store_current_state()
        self._store_population_stats()  # Store initial population stats
        
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

    def get_current_stats(self):
        """Get the current simulation statistics for display."""
        if self.population_history:
            return self.population_history[-1]['stats']
        return {}
