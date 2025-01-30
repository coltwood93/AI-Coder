import h5py
import numpy as np
import time
import os


def generate_debug_log(timestep, event_message):
    """Creates a timestamped debug log entry."""
    timestamp = int(time.time())  # Epoch timestamp
    return f"[{timestamp}] Timestep {timestep}: {event_message}"


class HDF5Storage:
    def __init__(self, filename=f"simulation_data.{int(time.time())}.h5"):
        self.filename = filename

        # Check if the file already exists
        if os.path.exists(self.filename):
            response = input(
                f"File '{self.filename}' already exists. Overwrite? (y/n): "
            )
            if response.lower() not in ("y", "yes"):
                print("Operation cancelled by user.")
                raise SystemExit(0)  # or sys.exit(), whichever you prefer
        self.fields = {
            "positions": lambda org: [org.x, org.y],
            "energy": lambda org: org.energy,
            "speed": lambda org: org.speed,
            "generation": lambda org: org.generation,
        }

    def save_population(self, timestep, organisms, debug_logs):
        """Stores organisms' structured data and debug logs in HDF5, using species names directly."""
        with h5py.File(self.filename, "a") as f:
            # Require the group (create if doesn't exist)
            group = f.require_group(f"timestep_{timestep}")

            # Dynamically store all defined organism fields
            for field_name, extractor in self.fields.items():
                data = np.array([extractor(org) for org in organisms])

                # If the dataset already exists, delete it before recreating
                if field_name in group:
                    del group[field_name]

                group.create_dataset(
                    field_name,
                    data=data,
                    compression="gzip",
                    chunks=True,  # Let h5py pick a chunk layout
                )

            # Store species names as variable-length strings
            species_ds_name = "species_names"
            if species_ds_name in group:
                del group[species_ds_name]
            dt = h5py.string_dtype(encoding="utf-8")
            species_names = np.array([org.species for org in organisms], dtype=dt)
            group.create_dataset(
                species_ds_name, data=species_names, dtype=dt, chunks=True
            )

            # Store debug logs (timestamped messages)
            debug_ds_name = "debug_logs"
            if debug_ds_name in group:
                del group[debug_ds_name]
            log_dt = h5py.string_dtype(encoding="utf-8")
            logs = np.array(debug_logs, dtype=log_dt)
            group.create_dataset(debug_ds_name, data=logs, dtype=log_dt, chunks=True)

    def load_population_and_logs(self, timestep):
        """Loads organisms' data and debug logs from HDF5."""
        with h5py.File(self.filename, "r") as f:
            group_name = f"timestep_{timestep}"
            # Check if the group exists
            if group_name not in f:
                # Return None or raise an exception; here we return empty results
                return [], []

            group = f[group_name]

            # Load all dynamically defined organism fields
            loaded_data = {}
            for field_name in self.fields:
                if field_name in group:
                    loaded_data[field_name] = group[field_name][:]
                else:
                    # This dataset is missing; decide how to handle it
                    loaded_data[field_name] = None

            # Load species names if available
            if "species_names" in group:
                species_names = group["species_names"][:]
            else:
                species_names = []

            # Load debug logs if available
            if "debug_logs" in group:
                debug_logs = list(group["debug_logs"])
            else:
                debug_logs = []

        # Reconstruct organism dictionaries
        organisms = []
        for i in range(len(species_names)):
            organism_data = {}
            for field_name, _ in self.fields.items():
                # If for some reason loaded_data[field_name] is None or shorter,
                # you might need extra safeguards. For now, assume matching lengths.
                if loaded_data[field_name] is not None:
                    organism_data[field_name] = loaded_data[field_name][i]
                else:
                    organism_data[field_name] = None
            # Decode species name
            organism_data["species"] = species_names[i].decode("utf-8")
            organisms.append(organism_data)

        # Decode debug logs from bytes to strings
        decoded_logs = [log.decode("utf-8") for log in debug_logs]
        return organisms, decoded_logs

    def load_population_only(self, timestep):
        """Loads organisms' structured data and species names without retrieving logs."""
        with h5py.File(self.filename, "r") as f:
            group_name = f"timestep_{timestep}"
            if group_name not in f:
                return []

            group = f[group_name]

            loaded_data = {}
            for field_name in self.fields:
                if field_name in group:
                    loaded_data[field_name] = group[field_name][:]
                else:
                    loaded_data[field_name] = None

            # Load species names if available
            if "species_names" in group:
                species_names = group["species_names"][:]
            else:
                species_names = []

        organisms = []
        for i in range(len(species_names)):
            organism_data = {}
            for field_name, _ in self.fields.items():
                if loaded_data[field_name] is not None:
                    organism_data[field_name] = loaded_data[field_name][i]
                else:
                    organism_data[field_name] = None
            # Decode species
            organism_data["species"] = species_names[i].decode("utf-8")
            organisms.append(organism_data)

        return organisms

    def load_logs_only(self, timestep):
        """Loads only debug logs from a specific timestep."""
        with h5py.File(self.filename, "r") as f:
            group_name = f"timestep_{timestep}"
            if group_name not in f:
                return []

            group = f[group_name]

            # Retrieve logs if they exist
            if "debug_logs" in group:
                debug_logs = list(group["debug_logs"])
                return [log.decode("utf-8") for log in debug_logs]
            else:
                return []


########################################
# DEMO / TEST SCRIPT:


# A simple Organism class for demonstration
class DummyOrganism:
    def __init__(self, x, y, energy, speed, generation, species):
        self.x = x
        self.y = y
        self.energy = energy
        self.speed = speed
        self.generation = generation
        self.species = species


def main():
    # 1) Create a storage object (writes to a file named with current epoch time)
    storage = HDF5Storage(filename="test_simulation_data.h5")

    # 2) Create some dummy organisms
    organisms = [
        DummyOrganism(
            x=0, y=0, energy=100, speed=1.0, generation=1, species="speciesA"
        ),
        DummyOrganism(
            x=10, y=5, energy=90, speed=1.2, generation=1, species="speciesA"
        ),
        DummyOrganism(
            x=-5, y=15, energy=120, speed=0.8, generation=1, species="speciesB"
        ),
    ]

    # 3) Create some debug logs using generate_debug_log
    debug_logs = [
        generate_debug_log(timestep=0, event_message="Starting simulation."),
        generate_debug_log(timestep=0, event_message="Initialized population."),
    ]

    # 4) Save the population and logs for timestep=0
    print("Saving population and logs for timestep=0...")
    storage.save_population(timestep=0, organisms=organisms, debug_logs=debug_logs)

    # 5) Load the data back (population + logs) and print it
    loaded_organisms, loaded_logs = storage.load_population_and_logs(timestep=0)
    print("\nLoaded Organisms + Logs (timestep=0):")
    print("Organisms:", loaded_organisms)
    print("Logs:", loaded_logs)

    # 6) Load only population
    pop_only = storage.load_population_only(timestep=0)
    print("\nLoaded Population Only (timestep=0):")
    print(pop_only)

    # 7) Load only logs
    logs_only = storage.load_logs_only(timestep=0)
    print("\nLoaded Logs Only (timestep=0):")
    print(logs_only)

    # 8) Demonstrate overwriting the same timestep by adding a new organism
    organisms.append(
        DummyOrganism(
            x=100, y=100, energy=200, speed=2.0, generation=2, species="speciesC"
        )
    )
    debug_logs.append(
        generate_debug_log(timestep=0, event_message="Added another organism.")
    )
    print("\nOverwriting timestep=0 with new data...")
    storage.save_population(timestep=0, organisms=organisms, debug_logs=debug_logs)

    # 9) Re-load to show that the new data replaced old data for timestep=0
    loaded_organisms, loaded_logs = storage.load_population_and_logs(timestep=0)
    print("\nAfter Overwriting, Loaded Organisms + Logs (timestep=0):")
    print("Organisms:", loaded_organisms)
    print("Logs:", loaded_logs)

    # 10) Clean up the test file if desired
    # os.remove("test_simulation_data.h5")


if __name__ == "__main__":
    main()
