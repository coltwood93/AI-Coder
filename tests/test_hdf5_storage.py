import os
import sys
import tempfile
import unittest
import numpy as np
import h5py

# Ensure that the parent directory is in the path so we can import hdf5_storage.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdf5_storage import (
    HDF5Storage,
)  # Import the HDF5Storage class from the parent module.


# Define the DummyOrganism class directly in this test file.
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


class TestHDF5Storage(unittest.TestCase):

    def setUp(self):
        # Create a temporary file name for testing.
        self.temp_filename = tempfile.mktemp(suffix=".h5")
        self.storage = HDF5Storage(self.temp_filename)

    def tearDown(self):
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def test_save_and_load_gameboard(self):
        # Create a simple 2x2 board.
        board = np.array([[0, 1], [1, 0]], dtype=np.int8)
        timestep = 0
        self.storage.save_gameboard(timestep, board.tolist())
        # Load state for that timestep.
        states = self.storage.load_simulation_state(timestep)
        self.assertEqual(len(states), 1)
        t, state = states[0]
        loaded_board = state[0]
        np.testing.assert_array_equal(loaded_board, board)

    def test_save_and_load_population(self):
        # Create two dummy organisms.
        org1 = DummyOrganism(1, 2, 10, 1.0, 0, "A", "org0001", None)
        org2 = DummyOrganism(3, 4, 8, 1.2, 0, "B", "org0002", "org0001")
        debug_logs = ["log1", "log2"]
        timestep = 1
        self.storage.save_population(timestep, [org1, org2], debug_logs)
        states = self.storage.load_simulation_state(timestep)
        self.assertEqual(len(states), 1)
        t, state = states[0]
        population_data = state[1]
        # Check positions.
        np.testing.assert_array_equal(
            population_data["positions"], np.array([[1, 2], [3, 4]])
        )
        np.testing.assert_array_equal(population_data["energy"], np.array([10, 8]))
        # Check species names.
        species_names = state[2]
        self.assertEqual(len(species_names), 2)
        self.assertEqual(species_names[0].decode("utf-8"), "A")
        self.assertEqual(species_names[1].decode("utf-8"), "B")
        # Check debug logs.
        logs = population_data["debug_logs"]
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0].decode("utf-8"), "log1")
        self.assertEqual(logs[1].decode("utf-8"), "log2")

    def test_save_and_load_lineage(self):
        org1 = DummyOrganism(1, 2, 10, 1.0, 0, "A", "org0001", None)
        org2 = DummyOrganism(3, 4, 8, 1.2, 0, "B", "org0002", "org0001")
        timestep = 2
        self.storage.save_lineage(timestep, [org1, org2])
        states = self.storage.load_simulation_state(timestep)
        self.assertEqual(len(states), 1)
        t, state = states[0]
        lineage = state[3]
        self.assertIsNotNone(lineage)
        org_ids = lineage["organism_ids"]
        parent_ids = lineage["parent_ids"]
        self.assertEqual(len(org_ids), 2)
        self.assertEqual(org_ids[0].decode("utf-8"), "org0001")
        self.assertEqual(org_ids[1].decode("utf-8"), "org0002")
        self.assertEqual(parent_ids[0].decode("utf-8"), "None")
        self.assertEqual(parent_ids[1].decode("utf-8"), "org0001")

    def test_save_and_load_simulation_state(self):
        board = np.array([[1, 0], [0, 1]], dtype=np.int8)
        org1 = DummyOrganism(5, 6, 12, 1.5, 1, "A", "org0003", None)
        debug_logs = ["start", "end"]
        timestep = 3
        self.storage.save_simulation_state(timestep, board.tolist(), [org1], debug_logs)
        states = self.storage.load_simulation_state(timestep)
        self.assertEqual(len(states), 1)
        t, state = states[0]
        loaded_board, population_data, species_names, lineage, logs = state
        np.testing.assert_array_equal(loaded_board, board)
        np.testing.assert_array_equal(population_data["positions"], np.array([[5, 6]]))
        self.assertEqual(species_names[0].decode("utf-8"), "A")
        self.assertEqual(lineage["parent_ids"][0].decode("utf-8"), "None")
        self.assertEqual(len(logs), 2)

    def test_load_aggregated_functions(self):
        # Save two timesteps.
        board0 = [[0, 1], [1, 0]]
        board1 = [[1, 1], [0, 0]]
        org = DummyOrganism(0, 0, 10, 1.0, 0, "A", "org0004", None)
        self.storage.save_simulation_state(0, board0, [org], ["log0"])
        self.storage.save_simulation_state(1, board1, [org], ["log1"])
        boards = self.storage.load_all_gameboards()
        self.assertEqual(len(boards), 2)
        pop_data = self.storage.load_all_population_data()
        self.assertEqual(len(pop_data), 2)
        lineage_data = self.storage.load_all_lineage_data()
        self.assertEqual(len(lineage_data), 2)
        logs = self.storage.load_all_debug_logs()
        self.assertEqual(len(logs), 2)

    def test_load_specific_timestep(self):
        board = [[1, 0, 1], [0, 1, 0]]
        org = DummyOrganism(2, 2, 9, 1.0, 0, "B", "org0005", None)
        self.storage.save_simulation_state(5, board, [org], ["specific log"])
        # Load state with a specific timestep.
        state_list = self.storage.load_simulation_state(timestep=5)
        self.assertEqual(len(state_list), 1)
        t, state = state_list[0]
        self.assertEqual(t, 5)
        # Similarly for gameboards.
        boards = self.storage.load_all_gameboards(timestep=5)
        self.assertEqual(len(boards), 1)
        self.assertEqual(boards[0][0], 5)
        # For population data.
        pop_data = self.storage.load_all_population_data(timestep=5)
        self.assertEqual(len(pop_data), 1)
        self.assertEqual(pop_data[0][0], 5)
        # For lineage.
        lineage = self.storage.load_all_lineage_data(timestep=5)
        self.assertEqual(len(lineage), 1)
        self.assertEqual(lineage[0][0], 5)
        # For debug logs.
        logs = self.storage.load_all_debug_logs(timestep=5)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], 5)


if __name__ == "__main__":
    unittest.main()
