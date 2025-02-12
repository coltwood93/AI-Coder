import os
import h5py
import numpy as np
import json

class HDF5Storage:
    def __init__(self, filename):
        self.filename = filename
        # Clear any existing file.
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f"Existing file '{self.filename}' removed.")
    
    def create_empty_file(self):
        with h5py.File(self.filename, "w") as f:
            pass
    
    # --- Saving Functions ---
    def save_board(self, timestep, board, dataset_name="board"):
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            if dataset_name in group:
                del group[dataset_name]
            board_array = np.array(board, dtype=np.int8)
            group.create_dataset(dataset_name, data=board_array, compression="gzip", chunks=True)
    
    def save_producers(self, timestep, producers):
        """
        Save producers as JSON strings.
        """
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            data = [json.dumps(p.__dict__) for p in producers]
            dt = h5py.string_dtype(encoding="utf-8")
            if "producers" in group:
                del group["producers"]
            group.create_dataset("producers", data=np.array(data, dtype=dt), dtype=dt, chunks=True)
    
    def save_consumers(self, timestep, consumers):
        """
        Save consumers as JSON strings.
        """
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            data = [json.dumps(c.__dict__) for c in consumers]
            dt = h5py.string_dtype(encoding="utf-8")
            if "consumers" in group:
                del group["consumers"]
            group.create_dataset("consumers", data=np.array(data, dtype=dt), dtype=dt, chunks=True)
    
    def save_debug_logs(self, timestep, debug_logs):
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            dt = h5py.string_dtype(encoding="utf-8")
            if "debug_logs" in group:
                del group["debug_logs"]
            group.create_dataset("debug_logs", data=np.array(debug_logs, dtype=dt), dtype=dt, chunks=True)
    
    def save_simulation_state(self, timestep, board, producers, consumers, debug_logs):
        self.save_board(timestep, board)
        self.save_producers(timestep, producers)
        self.save_consumers(timestep, consumers)
        self.save_debug_logs(timestep, debug_logs)
    
    # --- Loading Functions ---
    def _extract_state(self, group):
        board = group["board"][:] if "board" in group else None
        producers = group["producers"][:] if "producers" in group else np.array([])
        consumers = group["consumers"][:] if "consumers" in group else np.array([])
        debug_logs = group["debug_logs"][:] if "debug_logs" in group else None
        
        producers_list = [json.loads(s.decode("utf-8") if isinstance(s, bytes) else s) for s in producers]
        consumers_list = [json.loads(s.decode("utf-8") if isinstance(s, bytes) else s) for s in consumers]
        return (board, producers_list, consumers_list, debug_logs)
    
    def load_simulation_state(self, timestep=None):
        states = []
        with h5py.File(self.filename, "r") as f:
            if timestep is not None:
                group_name = f"timestep_{timestep}"
                if group_name in f:
                    group = f[group_name]
                    state = self._extract_state(group)
                    states.append((timestep, state))
            else:
                for key in f.keys():
                    if key.startswith("timestep_"):
                        try:
                            t = int(key.split("_")[1])
                        except ValueError:
                            continue
                        group = f[key]
                        state = self._extract_state(group)
                        states.append((t, state))
        states.sort(key=lambda x: x[0])
        return states
    
    def load_all_producers(self, timestep=None):
        result = []
        for t, state in self.load_simulation_state():
            if state[1] is not None:
                result.append((t, state[1]))
        return result
    
    def load_all_consumers(self, timestep=None):
        result = []
        for t, state in self.load_simulation_state():
            if state[2] is not None:
                result.append((t, state[2]))
        return result
    
    def load_all_debug_logs(self, timestep=None):
        result = []
        for t, state in self.load_simulation_state():
            if state[3] is not None:
                result.append((t, state[3]))
        return result
