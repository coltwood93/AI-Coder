import os
import h5py
import numpy as np


class HDF5Storage:
    def __init__(self, filename):
        self.filename = filename
        # Clear any existing file.
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f"Existing file '{self.filename}' removed.")
        # Define extraction functions for population fields.
        self.population_fields = {
            "positions": lambda org: [org.x, org.y],
            "energy": lambda org: org.energy,
            "speed": lambda org: org.speed,
            "generation": lambda org: org.generation,
        }
        # Define extraction functions for lineage fields.
        self.lineage_fields = {
            "organism_id": lambda org: org.id,
            "parent_id": lambda org: (
                org.parent_id if org.parent_id is not None else "None"
            ),
        }

    # ---------------------------
    # Saving Functions (unchanged)
    # ---------------------------
    def save_gameboard(self, timestep, board, dataset_name="gameboard"):
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            if dataset_name in group:
                del group[dataset_name]
            board_array = np.array(board, dtype=np.int8)
            group.create_dataset(
                dataset_name, data=board_array, compression="gzip", chunks=True
            )

    def save_population(self, timestep, organisms, debug_logs):
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            for field_name, extractor in self.population_fields.items():
                data = np.array([extractor(org) for org in organisms])
                if field_name in group:
                    del group[field_name]
                group.create_dataset(
                    field_name, data=data, compression="gzip", chunks=True
                )
            # Save species names.
            species_ds_name = "species_names"
            if species_ds_name in group:
                del group[species_ds_name]
            dt = h5py.string_dtype(encoding="utf-8")
            species_names = np.array([org.species for org in organisms], dtype=dt)
            group.create_dataset(
                species_ds_name, data=species_names, dtype=dt, chunks=True
            )
            # Save debug logs.
            debug_ds_name = "debug_logs"
            if debug_ds_name in group:
                del group[debug_ds_name]
            log_dt = h5py.string_dtype(encoding="utf-8")
            logs = np.array(debug_logs, dtype=log_dt)
            group.create_dataset(debug_ds_name, data=logs, dtype=log_dt, chunks=True)

    def save_lineage(self, timestep, organisms):
        with h5py.File(self.filename, "a") as f:
            group = f.require_group(f"timestep_{timestep}")
            lineage_group = group.require_group("lineage")
            dt = h5py.string_dtype(encoding="utf-8")
            organism_ids = np.array(
                [self.lineage_fields["organism_id"](org) for org in organisms], dtype=dt
            )
            parent_ids = np.array(
                [self.lineage_fields["parent_id"](org) for org in organisms], dtype=dt
            )
            if "organism_ids" in lineage_group:
                del lineage_group["organism_ids"]
            if "parent_ids" in lineage_group:
                del lineage_group["parent_ids"]
            lineage_group.create_dataset(
                "organism_ids", data=organism_ids, dtype=dt, chunks=True
            )
            lineage_group.create_dataset(
                "parent_ids", data=parent_ids, dtype=dt, chunks=True
            )

    def save_simulation_state(self, timestep, board, organisms, debug_logs):
        self.save_gameboard(timestep, board)
        self.save_population(timestep, organisms, debug_logs)
        self.save_lineage(timestep, organisms)

    # ---------------------------
    # Helper to extract a simulation state from an HDF5 group.
    # Returns a tuple: (board, population_data, species_names, lineage, debug_logs)
    # ---------------------------
    def _extract_state(self, group):
        board = group["gameboard"][:] if "gameboard" in group else None
        population_data = {}
        for field_name in self.population_fields:
            population_data[field_name] = (
                group[field_name][:] if field_name in group else None
            )
        # Load species names separately.
        species_names = group["species_names"][:] if "species_names" in group else None
        if "lineage" in group:
            lg = group["lineage"]
            lineage = {
                "organism_ids": lg["organism_ids"][:] if "organism_ids" in lg else None,
                "parent_ids": lg["parent_ids"][:] if "parent_ids" in lg else None,
            }
        else:
            lineage = None
        debug_logs = group["debug_logs"][:] if "debug_logs" in group else None
        # Include debug logs in population_data for consistency with aggregated functions.
        population_data["debug_logs"] = debug_logs
        return (board, population_data, species_names, lineage, debug_logs)

    # ---------------------------
    # Loading Functions (optional timestep parameter)
    # Each function returns a list of tuples (timestep, data)
    # If a specific timestep is provided, a list with one tuple is returned.
    # ---------------------------
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

    def load_all_gameboards(self, timestep=None):
        boards = []
        with h5py.File(self.filename, "r") as f:
            if timestep is not None:
                group_name = f"timestep_{timestep}"
                if group_name in f:
                    group = f[group_name]
                    if "gameboard" in group:
                        boards.append((timestep, group["gameboard"][:]))
            else:
                for key in f.keys():
                    if key.startswith("timestep_"):
                        try:
                            t = int(key.split("_")[1])
                        except ValueError:
                            continue
                        group = f[key]
                        if "gameboard" in group:
                            boards.append((t, group["gameboard"][:]))
        boards.sort(key=lambda x: x[0])
        return boards

    def load_all_population_data(self, timestep=None):
        pop_data = []
        with h5py.File(self.filename, "r") as f:
            if timestep is not None:
                group_name = f"timestep_{timestep}"
                if group_name in f:
                    group = f[group_name]
                    data = {}
                    for field in self.population_fields:
                        data[field] = group[field][:] if field in group else None
                    data["species_names"] = (
                        group["species_names"][:] if "species_names" in group else None
                    )
                    data["debug_logs"] = (
                        group["debug_logs"][:] if "debug_logs" in group else None
                    )
                    pop_data.append((timestep, data))
            else:
                for key in f.keys():
                    if key.startswith("timestep_"):
                        try:
                            t = int(key.split("_")[1])
                        except ValueError:
                            continue
                        group = f[key]
                        data = {}
                        for field in self.population_fields:
                            data[field] = group[field][:] if field in group else None
                        data["species_names"] = (
                            group["species_names"][:]
                            if "species_names" in group
                            else None
                        )
                        data["debug_logs"] = (
                            group["debug_logs"][:] if "debug_logs" in group else None
                        )
                        pop_data.append((t, data))
        pop_data.sort(key=lambda x: x[0])
        return pop_data

    def load_all_lineage_data(self, timestep=None):
        lineage_data = []
        with h5py.File(self.filename, "r") as f:
            if timestep is not None:
                group_name = f"timestep_{timestep}"
                if group_name in f:
                    group = f[group_name]
                    if "lineage" in group:
                        lg = group["lineage"]
                        lineage = {
                            "organism_ids": (
                                lg["organism_ids"][:] if "organism_ids" in lg else None
                            ),
                            "parent_ids": (
                                lg["parent_ids"][:] if "parent_ids" in lg else None
                            ),
                        }
                        lineage_data.append((timestep, lineage))
            else:
                for key in f.keys():
                    if key.startswith("timestep_"):
                        try:
                            t = int(key.split("_")[1])
                        except ValueError:
                            continue
                        group = f[key]
                        if "lineage" in group:
                            lg = group["lineage"]
                            lineage = {
                                "organism_ids": (
                                    lg["organism_ids"][:]
                                    if "organism_ids" in lg
                                    else None
                                ),
                                "parent_ids": (
                                    lg["parent_ids"][:] if "parent_ids" in lg else None
                                ),
                            }
                        else:
                            lineage = None
                        lineage_data.append((t, lineage))
        lineage_data.sort(key=lambda x: x[0])
        return lineage_data

    def load_all_debug_logs(self, timestep=None):
        logs = []
        with h5py.File(self.filename, "r") as f:
            if timestep is not None:
                group_name = f"timestep_{timestep}"
                if group_name in f:
                    group = f[group_name]
                    if "debug_logs" in group:
                        logs.append((timestep, group["debug_logs"][:]))
            else:
                for key in f.keys():
                    if key.startswith("timestep_"):
                        try:
                            t = int(key.split("_")[1])
                        except ValueError:
                            continue
                        group = f[key]
                        if "debug_logs" in group:
                            logs.append((t, group["debug_logs"][:]))
        logs.sort(key=lambda x: x[0])
        return logs
