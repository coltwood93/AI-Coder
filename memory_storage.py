import os
import numpy as np

# DummyOrganism must be available in the global namespace.
# (Replace this with your actual organism class if needed.)
class DummyOrganism:
    def __init__(self, x, y, energy, speed, generation, species, id, parent_id=None):
        self.x = x
        self.y = y
        self.energy = energy
        self.speed = speed
        self.generation = generation
        self.species = species
        self.id = id
        self.parent_id = parent_id

class MemoryResidentSimulationStore:
    def __init__(self, mode="live"):
        """
        Initialize the in‑memory simulation store.
        
        Parameters:
          mode (str): "live" for a running simulation (updates allowed)
                      or "replay" for a replay (only loading allowed).
        """
        if mode not in ("live", "replay"):
            raise ValueError("mode must be either 'live' or 'replay'")
        self.mode = mode
        self.states = {}  # Dictionary keyed by timestep.
        self.current_timestep = None

    def update_state(self, timestep, board, organisms, debug_logs):
        """
        Update the entire state for a given timestep.
        This method extracts all fields from the provided data and stores them.
        
        Parameters:
          - timestep (int): the current simulation timestep.
          - board: a 2D list (or array) representing the gameboard.
          - organisms: list of organism objects.
          - debug_logs: list of log messages (strings) for this timestep.
        """
        if self.mode != "live":
            raise RuntimeError("Cannot update state in replay mode.")
        
        population_data = {
            "positions": [[org.x, org.y] for org in organisms],
            "energy": [org.energy for org in organisms],
            "speed": [org.speed for org in organisms],
            "generation": [org.generation for org in organisms],
            "debug_logs": debug_logs  # Stored here for convenience.
        }
        species_names = [org.species for org in organisms]
        lineage = {
            "organism_ids": [org.id for org in organisms],
            "parent_ids": [org.parent_id if org.parent_id is not None else "None" for org in organisms]
        }
        state = {
            "board": board,
            "population": population_data,
            "species_names": species_names,
            "lineage": lineage,
            "debug_logs": debug_logs
        }
        self.states[timestep] = state
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    # --- Piecewise Update Methods ---
    def update_board(self, timestep, board):
        """Update only the gameboard for the given timestep."""
        self.states.setdefault(timestep, {})["board"] = board
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_population(self, timestep, population_data, species_names):
        """
        Update only the population data for the given timestep.
        
        Parameters:
        - population_data: dict with keys "positions", "energy", "speed", "generation".
        - species_names: list of species strings.
        """
        state = self.states.setdefault(timestep, {})
        # Ensure the population dictionary always has the "debug_logs" key.
        if "debug_logs" not in population_data:
            population_data["debug_logs"] = None
        state["population"] = population_data
        state["species_names"] = species_names
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_lineage(self, timestep, lineage):
        """Update only the lineage data for the given timestep."""
        self.states.setdefault(timestep, {})["lineage"] = lineage
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_debug_logs(self, timestep, debug_logs):
        """Update only the debug logs for the given timestep."""
        self.states.setdefault(timestep, {})["debug_logs"] = debug_logs
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    # --- Methods for Individual Organism Updates ---
    def update_organism_position(self, timestep, organism_index, new_position):
        """
        Update the position of a specific organism in the population.
        
        Parameters:
          - timestep (int): the timestep in which to update.
          - organism_index (int): index of the organism in the population list.
          - new_position (list or tuple): the new [x, y] coordinates.
        """
        state = self.states.get(timestep)
        if state is None or "population" not in state:
            raise ValueError("No state or population data found for timestep %s" % timestep)
        state["population"]["positions"][organism_index] = list(new_position)
    
    def add_organism(self, timestep, organism):
        """
        Add a new organism to the population at the given timestep.
        
        Updates the population lists, species names, and lineage.
        """
        state = self.states.setdefault(timestep, {})
        pop = state.setdefault("population", {
            "positions": [],
            "energy": [],
            "speed": [],
            "generation": [],
            "debug_logs": state.get("debug_logs", [])
        })
        pop["positions"].append([organism.x, organism.y])
        pop["energy"].append(organism.energy)
        pop["speed"].append(organism.speed)
        pop["generation"].append(organism.generation)
        state.setdefault("species_names", []).append(organism.species)
        lin = state.setdefault("lineage", {"organism_ids": [], "parent_ids": []})
        lin["organism_ids"].append(organism.id)
        lin["parent_ids"].append(organism.parent_id if organism.parent_id is not None else "None")
    
    def remove_organism(self, timestep, organism_index):
        """
        Remove an organism from the population at the given timestep.
        
        Removes entries from population, species names, and lineage.
        """
        state = self.states.get(timestep)
        if state is None or "population" not in state:
            raise ValueError("No state or population data found for timestep %s" % timestep)
        pop = state["population"]
        for key in ["positions", "energy", "speed", "generation"]:
            pop[key].pop(organism_index)
        state["species_names"].pop(organism_index)
        state["lineage"]["organism_ids"].pop(organism_index)
        state["lineage"]["parent_ids"].pop(organism_index)

    # --- Getters for Individual Pieces ---
    def get_board(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("board", None)

    def get_population(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("population", None)

    def get_species_names(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("species_names", None)

    def get_lineage(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("lineage", None)

    def get_debug_logs(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("debug_logs", None)

    def get_current_state(self):
        if self.current_timestep is not None:
            return self.states.get(self.current_timestep, None)
        return None

    # --- Aggregated Loading Functions ---
    def load_simulation_state(self, timestep=None):
        """
        Return a list of tuples (timestep, state).
        If a specific timestep is provided, return a list with one tuple if exists, else empty list.
        """
        if timestep is not None:
            if timestep in self.states:
                return [(timestep, self.states[timestep])]
            else:
                return []
        else:
            return sorted(self.states.items(), key=lambda x: x[0])
    
    def load_all_population_data(self, timestep=None):
        if timestep is not None:
            if timestep in self.states and "population" in self.states[timestep]:
                return [(timestep, self.states[timestep]["population"])]
            else:
                return []
        else:
            result = []
            for t, state in self.states.items():
                if "population" in state:
                    result.append((t, state["population"]))
            return sorted(result, key=lambda x: x[0])
    
    def load_all_lineage_data(self, timestep=None):
        if timestep is not None:
            if timestep in self.states and "lineage" in self.states[timestep]:
                return [(timestep, self.states[timestep]["lineage"])]
            else:
                return []
        else:
            result = []
            for t, state in self.states.items():
                if "lineage" in state:
                    result.append((t, state["lineage"]))
            return sorted(result, key=lambda x: x[0])
    
    def load_all_debug_logs(self, timestep=None):
        if timestep is not None:
            if timestep in self.states and "debug_logs" in self.states[timestep]:
                return [(timestep, self.states[timestep]["debug_logs"])]
            else:
                return []
        else:
            result = []
            for t, state in self.states.items():
                if "debug_logs" in state:
                    result.append((t, state["debug_logs"]))
            return sorted(result, key=lambda x: x[0])
    
    # --- Persistence Functions ---
    def flush_to_longterm(self, storage):
        """
        Write all in‑memory simulation states to long‑term storage.
        If no states are stored, create an empty file.
        """
        if not self.states:
            storage.create_empty_file()
            return
        for t, state in self.states.items():
            board = state.get("board")
            population_data = state.get("population")
            species_names = state.get("species_names")
            lineage = state.get("lineage")
            debug_logs = state.get("debug_logs")
            # Ensure debug_logs (and optionally others) are not None.
            if debug_logs is None:
                debug_logs = []
            organisms = self._reconstruct_organisms(population_data, species_names, lineage)
            storage.save_simulation_state(t, board, organisms, debug_logs)        # Optionally, clear the in-memory store:
        # self.states.clear()
    
    def _reconstruct_organisms(self, population_data, species_names, lineage):
        organisms = []
        if population_data is None or species_names is None or lineage is None:
            return organisms
        positions = population_data.get("positions", [])
        energies = population_data.get("energy", [])
        speeds = population_data.get("speed", [])
        generations = population_data.get("generation", [])
        org_ids = lineage.get("organism_ids", [])
        parent_ids = lineage.get("parent_ids", [])
        for i in range(len(positions)):
            org = DummyOrganism(
                x=positions[i][0],
                y=positions[i][1],
                energy=energies[i],
                speed=speeds[i],
                generation=generations[i],
                species=species_names[i],
                id=org_ids[i],
                parent_id=parent_ids[i] if parent_ids[i] != "None" else None
            )
            organisms.append(org)
        return organisms
    
    def load_from_longterm(self, storage, timestep):
        """
        Load a simulation state for a given timestep from long‑term storage into memory.
        Returns the loaded state as a dict, or None if not found.
        """
        state_list = storage.load_simulation_state(timestep)
        if state_list:
            t, state_tuple = state_list[0]
            state = {
                "board": state_tuple[0],
                "population": state_tuple[1],
                "species_names": state_tuple[2],
                "lineage": state_tuple[3],
                "debug_logs": state_tuple[4]
            }
            self.states[t] = state
            self.current_timestep = t
            self.update_mode_based_on_state()
            return state
        return None
    
    # --- Mode and Timestep Helpers ---
    def is_last_stored_step(self):
        if not self.states:
            return False
        return self.current_timestep == max(self.states.keys())
    
    def update_mode_based_on_state(self):
        if self.is_last_stored_step():
            self.mode = "live"
        else:
            self.mode = "replay"
    
    def is_live(self):
        return self.mode == "live"
