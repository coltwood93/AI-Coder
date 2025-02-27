import os
import h5py
import numpy as np
import json

class HDF5Storage:
    def __init__(self, filepath):
        self.filepath = filepath
        # Clear any existing file.
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            print(f"Existing file '{self.filepath}' removed.")
    
    def create_empty_file(self):
        with h5py.File(self.filepath, "w"):
            pass
    
    def _to_python_scalars(self, obj_dict):
        """
        Convert any NumPy scalars in obj_dict to native Python types.
        """
        py_dict = {}
        for k, v in obj_dict.items():
            if isinstance(v, np.integer):
                py_dict[k] = int(v)
            elif isinstance(v, np.floating):
                py_dict[k] = float(v)
            else:
                py_dict[k] = v
        return py_dict

    # --- Saving Functions ---
    def save_board(self, timestep, board, dataset_name="board"):
        with h5py.File(self.filepath, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            if dataset_name in group:
                del group[dataset_name]
            board_array = np.array(board, dtype=np.float32)
            group.create_dataset(dataset_name, data=board_array, compression="gzip", chunks=True)
    
    def save_producers(self, timestep, producers):
        with h5py.File(self.filepath, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            # Convert each Producer's __dict__ to only have Python-native types
            data_dicts = []
            for p in producers:
                # Convert NumPy floats/ints to Python float/int
                p_dict = self._to_python_scalars(p.__dict__)
                data_dicts.append(json.dumps(p_dict))
            dt = h5py.string_dtype(encoding="utf-8")
            if "producers" in group:
                del group["producers"]
            group.create_dataset("producers",
                                data=np.array(data_dicts, dtype=dt),
                                dtype=dt, chunks=True)
            
    def save_consumers(self, timestep, consumers):
        """
        Save consumers as JSON strings.
        """
        with h5py.File(self.filepath, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            data = [json.dumps(c.__dict__) for c in consumers]
            dt = h5py.string_dtype(encoding="utf-8")
            if "consumers" in group:
                del group["consumers"]
            group.create_dataset("consumers", data=np.array(data, dtype=dt), dtype=dt, chunks=True)
    
    def save_debug_logs(self, timestep, debug_logs):
        with h5py.File(self.filepath, "a") as f:
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
    
    def save_state(self, step, environment, **organism_groups):
        """
        Saves environment and organism groups in HDF5 format. 
        """
        with h5py.File(self.filepath, "a") as f:
            group = f.require_group(f"step_{step}")
            # Save environment
            env_array = np.array(environment, dtype=np.float32)
            if "environment" in group:
                del group["environment"]
            group.create_dataset("environment", data=env_array, compression="gzip", chunks=True)
            # Save organism groups
            for group_name, organisms in organism_groups.items():
                data_dicts = [json.dumps(self._to_python_scalars(o.__dict__)) for o in organisms]
                dt = h5py.string_dtype(encoding="utf-8")
                if group_name in group:
                    del group[group_name]
                group.create_dataset(group_name, data=np.array(data_dicts, dtype=dt), dtype=dt, chunks=True)
    
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
        with h5py.File(self.filepath, "r") as f:
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
