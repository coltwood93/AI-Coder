# For testing, we keep DummyOrganism here.
# In your simulation, you would import your actual Consumer class.
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
                      or "replay" for a replay (read-only).
        """
        if mode not in ("live", "replay"):
            raise ValueError("mode must be either 'live' or 'replay'")
        self.mode = mode
        self.states = {}  # Dictionary keyed by timestep.
        self.current_timestep = None

    def update_state(self, timestep, environment, **organism_groups):
        """
        Stores the environment and any number of organism groups (producers, herbivores, etc.)
        in an in-memory dictionary for quick retrieval.
        """
        if self.mode != "live":
            raise RuntimeError("Cannot update state in replay mode.")
        
        state = {
            "environment": environment.copy(),
            "organisms": {}
        }
        for group_name, organisms in organism_groups.items():
            state["organisms"][group_name] = [o for o in organisms]
        self.states[timestep] = state
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    # --- Piecewise Update Methods ---
    def update_board(self, timestep, board):
        """Update only the board for the given timestep."""
        self.states.setdefault(timestep, {})["board"] = board
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_producers(self, timestep, producers):
        """Update only the producers list for the given timestep."""
        self.states.setdefault(timestep, {})["producers"] = producers
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_consumers(self, timestep, consumers):
        """Update only the consumers list for the given timestep."""
        self.states.setdefault(timestep, {})["consumers"] = consumers
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def update_debug_logs(self, timestep, debug_logs):
        """Update only the debug logs for the given timestep."""
        self.states.setdefault(timestep, {})["debug_logs"] = debug_logs
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    # --- Getters ---
    def get_board(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("board", None)

    def get_producers(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("producers", None)

    def get_consumers(self, timestep=None):
        ts = timestep if timestep is not None else self.current_timestep
        return self.states.get(ts, {}).get("consumers", None)

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
        If timestep is provided, returns one tuple if exists, else empty list.
        """
        if timestep is not None:
            if timestep in self.states:
                return [(timestep, self.states[timestep])]
            return []
        return sorted(self.states.items(), key=lambda x: x[0])
    
    def load_all_producers(self, timestep=None):
        result = []
        for t, state in self.states.items():
            if "producers" in state:
                result.append((t, state["producers"]))
        return sorted(result, key=lambda x: x[0])
    
    def load_all_consumers(self, timestep=None):
        result = []
        for t, state in self.states.items():
            if "consumers" in state:
                result.append((t, state["consumers"]))
        return sorted(result, key=lambda x: x[0])
    
    def load_all_debug_logs(self, timestep=None):
        result = []
        for t, state in self.states.items():
            if "debug_logs" in state:
                result.append((t, state["debug_logs"]))
        return sorted(result, key=lambda x: x[0])
    
    # --- Persistence Functions ---
    def flush_to_longterm(self, storage):
        """
        Write all in‑memory simulation states to long‑term storage.
        If no states are stored, delegate empty file creation to the storage.
        """
        if not self.states:
            storage.create_empty_file()
            return
        for t, state in self.states.items():
            board = state.get("board")
            producers = state.get("producers", [])
            consumers = state.get("consumers", [])
            debug_logs = state.get("debug_logs")
            if debug_logs is None:
                debug_logs = []
            storage.save_simulation_state(t, board, producers, consumers, debug_logs)
    
    def load_from_longterm(self, storage, timestep):
        """
        Load the simulation state for a given timestep from long‑term storage into memory.
        Returns the loaded state as a dict, or None if not found.
        """
        state_list = storage.load_simulation_state(timestep)
        if state_list:
            t, state_tuple = state_list[0]
            # Expect state_tuple to be (board, producers, consumers, debug_logs)
            state = {
                "board": state_tuple[0],
                "producers": state_tuple[1],
                "consumers": state_tuple[2],
                "debug_logs": state_tuple[3]
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

    def add_consumer(self, timestep, consumer):
        state = self.states.setdefault(timestep, {})
        consumers = state.setdefault("consumers", [])
        consumers.append(consumer)
        self.current_timestep = timestep
        self.update_mode_based_on_state()

    def remove_consumer(self, timestep, index):
        state = self.states.get(timestep)
        if state is None or "consumers" not in state:
            raise ValueError("No state or consumers data found for timestep %s" % timestep)
        state["consumers"].pop(index)

    def update_consumer_position(self, timestep, index, new_position):
        state = self.states.get(timestep)
        if state is None or "consumers" not in state:
            raise ValueError("No state or consumers data found for timestep %s" % timestep)
        consumer = state["consumers"][index]
        if hasattr(consumer, "x"):
            consumer.x = new_position[0]
            consumer.y = new_position[1]
        else:
            consumer["x"] = new_position[0]
            consumer["y"] = new_position[1]
    
    def reset(self):
        """Reset the memory store to initial state."""
        self.mode = "live"
        self.states = {}
        self.current_timestep = None
        print("Memory store reset complete")