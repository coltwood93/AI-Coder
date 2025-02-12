import os
import sys
import tempfile
import unittest
import numpy as np
import h5py

# Insert the parent directory into sys.path so we can import our modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdf5_storage import HDF5Storage
from memory_storage import MemoryResidentSimulationStore

# Define a DummyOrganism for testing.
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

class TestMemoryResidentSimulationStore(unittest.TestCase):
    # --- Tests 1–21: Existing Tests ---
    def setUp(self):
        # Create a temporary file for HDF5 storage.
        self.temp_hdf5 = tempfile.mktemp(suffix=".h5")
        self.hdf5_storage = HDF5Storage(self.temp_hdf5)
        # Create a MemoryResidentSimulationStore in live mode.
        self.mem_store = MemoryResidentSimulationStore(mode="live")
    
    def tearDown(self):
        if os.path.exists(self.temp_hdf5):
            os.remove(self.temp_hdf5)
    
    # 1.
    def test_update_state_and_get_current_state(self):
        timestep = 0
        board = [[0, 1], [1, 0]]
        org1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        org2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        organisms = [org1, org2]
        debug_logs = ["start", "update"]
        self.mem_store.update_state(timestep, board, organisms, debug_logs)
        current = self.mem_store.get_current_state()
        self.assertEqual(current["board"], board)
        np.testing.assert_array_equal(np.array(current["population"]["positions"]), np.array([[1, 1], [2, 2]]))
        self.assertEqual(current["population"]["energy"], [10, 8])
        self.assertEqual(current["species_names"], ["A", "B"])
        self.assertEqual(current["lineage"]["organism_ids"], ["org0001", "org0002"])
        self.assertEqual(current["lineage"]["parent_ids"], ["None", "org0001"])
        self.assertEqual(current["debug_logs"], debug_logs)
        self.assertEqual(self.mem_store.current_timestep, timestep)
    
    # 2.
    def test_piecewise_update_board(self):
        timestep = 5
        board_initial = [[0, 0], [0, 0]]
        board_updated = [[1, 1], [1, 1]]
        self.mem_store.update_state(timestep, board_initial, [], [])
        self.mem_store.update_board(timestep, board_updated)
        self.assertEqual(self.mem_store.get_board(timestep), board_updated)
    
    # 3.
    def test_piecewise_update_population(self):
        timestep = 2
        pop_data = {"positions": [[1, 1]], "energy": [10], "speed": [1.0], "generation": [0], "debug_logs": ["init"]}
        species_names = ["A"]
        self.mem_store.update_population(timestep, pop_data, species_names)
        pop = self.mem_store.get_population(timestep)
        np.testing.assert_array_equal(np.array(pop["positions"]), np.array([[1, 1]]))
        self.assertEqual(pop["energy"], [10])
        self.assertEqual(self.mem_store.get_species_names(timestep), species_names)
    
    # 4.
    def test_piecewise_update_lineage(self):
        timestep = 3
        lineage = {"organism_ids": ["org0001"], "parent_ids": ["None"]}
        self.mem_store.update_lineage(timestep, lineage)
        self.assertEqual(self.mem_store.get_lineage(timestep), lineage)
    
    # 5.
    def test_piecewise_update_debug_logs(self):
        timestep = 4
        logs = ["log1", "log2"]
        self.mem_store.update_debug_logs(timestep, logs)
        self.assertEqual(self.mem_store.get_debug_logs(timestep), logs)
    
    # 6.
    def test_update_organism_position(self):
        timestep = 6
        board = [[0, 0], [0, 0]]
        org1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        org2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        self.mem_store.update_state(timestep, board, [org1, org2], ["initial"])
        new_pos = [5, 5]
        self.mem_store.update_organism_position(timestep, 0, new_pos)
        pop = self.mem_store.get_population(timestep)
        self.assertEqual(pop["positions"][0], new_pos)
    
    # 7.
    def test_add_and_remove_organism(self):
        timestep = 7
        board = [[0, 0], [0, 0]]
        self.mem_store.update_state(timestep, board, [], ["init"])
        org1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        org2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        self.mem_store.add_organism(timestep, org1)
        self.mem_store.add_organism(timestep, org2)
        pop = self.mem_store.get_population(timestep)
        np.testing.assert_array_equal(np.array(pop["positions"]), np.array([[1, 1], [2, 2]]))
        self.assertEqual(self.mem_store.get_species_names(timestep), ["A", "B"])
        lineage = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage["organism_ids"], ["org0001", "org0002"])
        self.mem_store.remove_organism(timestep, 0)
        pop = self.mem_store.get_population(timestep)
        np.testing.assert_array_equal(np.array(pop["positions"]), np.array([[2, 2]]))
        self.assertEqual(self.mem_store.get_species_names(timestep), ["B"])
        lineage = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage["organism_ids"], ["org0002"])
    
    # 8.
    def test_flush_to_longterm(self):
        for t in range(3):
            board = [[t, t], [t, t]]
            org = DummyOrganism(t, t, 10+t, 1.0, t, "A", f"org{t:04d}")
            self.mem_store.update_state(t, board, [org], [f"log{t}"])
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        states = self.hdf5_storage.load_simulation_state()
        self.assertEqual(len(states), 3)
        for t_val, state_tuple in states:
            board_loaded, pop_data, species_names, lineage, logs = state_tuple
            expected_board = np.array([[t_val, t_val], [t_val, t_val]], dtype=np.int8)
            np.testing.assert_array_equal(board_loaded, expected_board)
            np.testing.assert_array_equal(np.array(pop_data["positions"]), np.array([[t_val, t_val]]))
            self.assertEqual(species_names[0].decode("utf-8"), "A")
            self.assertEqual(logs[0].decode("utf-8"), f"log{t_val}")
    
    # 9.
    def test_load_from_longterm(self):
        board = [[3, 3], [3, 3]]
        org = DummyOrganism(3, 3, 15, 1.2, 1, "B", "org0005")
        self.hdf5_storage.save_simulation_state(5, board, [org], ["test log"])
        self.mem_store = MemoryResidentSimulationStore(mode="replay")
        state = self.mem_store.load_from_longterm(self.hdf5_storage, 5)
        self.assertIsNotNone(state)
        self.assertEqual(self.mem_store.current_timestep, 5)
        np.testing.assert_array_equal(np.array(state["board"], dtype=np.int8), np.array(board, dtype=np.int8))
        pop_data = state["population"]
        np.testing.assert_array_equal(np.array(pop_data["positions"]), np.array([[3, 3]]))
        species_names = state["species_names"]
        self.assertEqual(species_names[0].decode("utf-8"), "B")
        self.assertEqual(state["debug_logs"][0].decode("utf-8"), "test log")
    
    # 10.
    def test_mode_switching(self):
        self.mem_store.update_state(0, [[0]], [DummyOrganism(0, 0, 10, 1, 0, "A", "org0001")], ["t0"])
        self.mem_store.update_state(1, [[1]], [DummyOrganism(1, 1, 9, 1, 0, "B", "org0002", "org0001")], ["t1"])
        self.mem_store.update_state(2, [[2]], [DummyOrganism(2, 2, 8, 1, 0, "C", "org0003", "org0002")], ["t2"])
        self.assertTrue(self.mem_store.is_last_stored_step())
        self.assertEqual(self.mem_store.mode, "live")
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        self.mem_store.load_from_longterm(self.hdf5_storage, 1)
        self.assertFalse(self.mem_store.is_last_stored_step())
        self.assertEqual(self.mem_store.mode, "replay")
    
    # 11.
    def test_piecewise_organism_update(self):
        timestep = 8
        board = [[0, 0], [0, 0]]
        org = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        self.mem_store.update_state(timestep, board, [org], ["initial"])
        new_position = [5, 5]
        self.mem_store.update_organism_position(timestep, 0, new_position)
        pop = self.mem_store.get_population(timestep)
        self.assertEqual(pop["positions"][0], new_position)
    
    # 12.
    def test_add_remove_individual_organism(self):
        timestep = 9
        board = [[0, 0], [0, 0]]
        self.mem_store.update_state(timestep, board, [], ["init"])
        org1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        org2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        self.mem_store.add_organism(timestep, org1)
        self.mem_store.add_organism(timestep, org2)
        pop = self.mem_store.get_population(timestep)
        np.testing.assert_array_equal(np.array(pop["positions"]), np.array([[1, 1], [2, 2]]))
        self.assertEqual(self.mem_store.get_species_names(timestep), ["A", "B"])
        lineage = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage["organism_ids"], ["org0001", "org0002"])
        self.mem_store.remove_organism(timestep, 0)
        pop = self.mem_store.get_population(timestep)
        np.testing.assert_array_equal(np.array(pop["positions"]), np.array([[2, 2]]))
        self.assertEqual(self.mem_store.get_species_names(timestep), ["B"])
        lineage = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage["organism_ids"], ["org0002"])
    
    # 13.
    def test_partial_updates_vs_full_update(self):
        timestep = 10
        board = [[1, 0], [0, 1]]
        org1 = DummyOrganism(3, 3, 12, 1.5, 1, "A", "org0003", None)
        debug_logs = ["start", "end"]
        self.mem_store.update_state(timestep, board, [org1], debug_logs)
        full_state = self.mem_store.get_current_state()
        self.mem_store.update_board(timestep, board)
        pop_data = {"positions": [[3, 3]], "energy": [12], "speed": [1.5], "generation": [1], "debug_logs": debug_logs}
        self.mem_store.update_population(timestep, pop_data, ["A"])
        self.mem_store.update_lineage(timestep, {"organism_ids": ["org0003"], "parent_ids": ["None"]})
        self.mem_store.update_debug_logs(timestep, debug_logs)
        piecewise_state = self.mem_store.get_current_state()
        self.assertEqual(piecewise_state["board"], full_state["board"])
        self.assertEqual(piecewise_state["population"], full_state["population"])
        self.assertEqual(piecewise_state["species_names"], full_state["species_names"])
        self.assertEqual(piecewise_state["lineage"], full_state["lineage"])
        self.assertEqual(piecewise_state["debug_logs"], full_state["debug_logs"])
    
    # --- Additional Edge-Case Tests (Total tests: 30) ---
    # 14.
    def test_update_state_with_empty_population(self):
        timestep = 20
        board = [[1, 2], [3, 4]]
        debug_logs = ["empty population"]
        # Expect lineage to be an empty structure.
        self.mem_store.update_state(timestep, board, [], debug_logs)
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board)
        self.assertEqual(state["population"]["positions"], [])
        self.assertEqual(state["species_names"], [])
        # Accept either {} or {"organism_ids": [], "parent_ids": []}
        expected_lineage = {"organism_ids": [], "parent_ids": []}
        self.assertEqual(state.get("lineage", {}), expected_lineage)
        self.assertEqual(state["debug_logs"], debug_logs)
    
    # 15.
    def test_update_state_with_empty_debug_logs(self):
        timestep = 21
        board = [[5, 5], [5, 5]]
        org = DummyOrganism(5, 5, 20, 1.0, 1, "X", "org0021")
        self.mem_store.update_state(timestep, board, [org], [])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["debug_logs"], [])
    
    # 16.
    def test_update_board_does_not_affect_population(self):
        timestep = 22
        board1 = [[0, 0], [0, 0]]
        org = DummyOrganism(2, 2, 15, 1.0, 1, "Y", "org0022")
        self.mem_store.update_state(timestep, board1, [org], ["log"])
        board2 = [[9, 9], [9, 9]]
        self.mem_store.update_board(timestep, board2)
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board2)
        np.testing.assert_array_equal(np.array(state["population"]["positions"]), np.array([[2, 2]]))
        self.assertEqual(state["species_names"], ["Y"])
        self.assertEqual(state["lineage"]["organism_ids"], ["org0022"])
    
    # 17.
    def test_update_population_with_empty_list(self):
        timestep = 23
        board = [[7, 8], [9, 10]]
        org = DummyOrganism(1, 1, 10, 1.0, 0, "Z", "org0023")
        self.mem_store.update_state(timestep, board, [org], ["initial"])
        empty_pop = {"positions": [], "energy": [], "speed": [], "generation": [], "debug_logs": []}
        self.mem_store.update_population(timestep, empty_pop, [])
        pop = self.mem_store.get_population(timestep)
        self.assertEqual(pop["positions"], [])
        self.assertEqual(pop["energy"], [])
        self.assertEqual(self.mem_store.get_species_names(timestep), [])
    
    # 18.
    def test_multiple_updates_same_timestep_order(self):
        timestep = 24
        board_initial = [[0, 0]]
        org = DummyOrganism(1, 1, 10, 1.0, 0, "M", "org0024")
        self.mem_store.update_state(timestep, board_initial, [org], ["init"])
        self.mem_store.update_board(timestep, [[2, 2]])
        pop_data = {"positions": [[1, 1]], "energy": [10], "speed": [1.0], "generation": [0], "debug_logs": ["pop"]}
        self.mem_store.update_population(timestep, pop_data, ["M"])
        self.mem_store.update_board(timestep, [[3, 3]])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], [[3, 3]])
        np.testing.assert_array_equal(np.array(state["population"]["positions"]), np.array([[1, 1]]))
    
    # 19.
    def test_load_all_debug_logs_aggregated(self):
        for t in range(26, 29):
            self.mem_store.update_state(t, [[t]], [DummyOrganism(t, t, 10, 1, 0, "D", f"org{t:04d}")], [f"debug{t}"])
        all_logs = self.mem_store.load_all_debug_logs()
        self.assertEqual(len(all_logs), 3)
        expected_timesteps = [26, 27, 28]
        for i, (t_val, logs) in enumerate(all_logs):
            self.assertEqual(t_val, expected_timesteps[i])
            self.assertEqual(logs, [f"debug{t_val}"])
    
    # 20.
    def test_update_with_empty_board(self):
        timestep = 29
        board = []
        self.mem_store.update_state(timestep, board, [], ["empty board"])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board)
    
    # 21.
    def test_load_all_population_data_aggregated(self):
        for t in range(30, 32):
            pop_data = {"positions": [[t, t]], "energy": [t+10], "speed": [1.0], "generation": [t], "debug_logs": [f"log{t}"]}
            self.mem_store.update_population(t, pop_data, [f"S{t}"])
        all_pop = self.mem_store.load_all_population_data()
        self.assertEqual(len(all_pop), 2)
        expected = [[30, 30], [31, 31]]
        for i, (t_val, data) in enumerate(all_pop):
            np.testing.assert_array_equal(np.array(data["positions"]), np.array([expected[i]]))
    
    # 22.
    def test_independent_board_and_population_updates(self):
        timestep = 32
        board1 = [[0,0],[0,0]]
        pop_data1 = {"positions": [[1,1]], "energy": [10], "speed": [1.0], "generation": [0], "debug_logs": ["pop1"]}
        self.mem_store.update_state(timestep, board1, [DummyOrganism(1,1,10,1.0,0,"X","org0032")], ["init"])
        self.mem_store.update_board(timestep, [[5,5],[5,5]])
        pop_data2 = {"positions": [[2,2]], "energy": [20], "speed": [1.5], "generation": [1], "debug_logs": ["pop2"]}
        self.mem_store.update_population(timestep, pop_data2, ["Y"])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], [[5,5],[5,5]])
        np.testing.assert_array_equal(np.array(state["population"]["positions"]), np.array([[2,2]]))
        self.assertEqual(state["species_names"], ["Y"])
    
    # 23.
    def test_update_lineage_independently(self):
        timestep = 33
        board = [[1,1],[1,1]]
        self.mem_store.update_state(timestep, board, [], ["lineage init"])
        lineage_initial = {"organism_ids": ["org_initial"], "parent_ids": ["None"]}
        self.mem_store.update_lineage(timestep, lineage_initial)
        lineage_before = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage_before, lineage_initial)
        pop_data = {"positions": [[1,1]], "energy": [10], "speed": [1.0], "generation": [0], "debug_logs": ["pop"]}
        self.mem_store.update_population(timestep, pop_data, ["L"])
        lineage_after = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage_after, lineage_initial)
    
    # 24.
    def test_update_debug_logs_independent(self):
        timestep = 34
        board = [[4,4],[4,4]]
        self.mem_store.update_state(timestep, board, [], ["old log"])
        self.mem_store.update_debug_logs(timestep, ["new log"])
        self.assertEqual(self.mem_store.get_debug_logs(timestep), ["new log"])
        self.assertEqual(self.mem_store.get_board(timestep), board)
    
    # 25.
    def test_update_population_without_debug_logs_key(self):
        # Provide a population dictionary missing the "debug_logs" key.
        timestep = 35
        board = [[3, 4],[5, 6]]
        pop_data = {"positions": [[1,2]], "energy": [10], "speed": [1.0], "generation": [0]}  # no debug_logs
        self.mem_store.update_population(timestep, pop_data, ["P"])
        pop = self.mem_store.get_population(timestep)
        # The implementation should leave debug_logs as None (or not set)
        self.assertTrue("debug_logs" in pop)
        self.assertEqual(pop["debug_logs"], None)
    
    # 26.
    def test_clear_lineage_by_updating_with_empty_dict(self):
        timestep = 36
        board = [[1,1],[1,1]]
        org = DummyOrganism(1,1,10,1.0,0,"A","org0036")
        self.mem_store.update_state(timestep, board, [org], ["log"])
        # Now update lineage with an empty dictionary.
        self.mem_store.update_lineage(timestep, {})
        lineage = self.mem_store.get_lineage(timestep)
        self.assertEqual(lineage, {})
    
    # 27.
    def test_getters_return_none_when_state_missing(self):
        # If a state was only partially updated, getters for missing keys should return None.
        timestep = 37
        self.mem_store.states[timestep] = {"board": [[0,0],[0,0]]}
        self.assertEqual(self.mem_store.get_population(timestep), None)
        self.assertEqual(self.mem_store.get_species_names(timestep), None)
        self.assertEqual(self.mem_store.get_lineage(timestep), None)
        self.assertEqual(self.mem_store.get_debug_logs(timestep), None)
    
    # 28.
    def test_flush_empty_memory(self):
        # If the memory store is empty, flush_to_longterm should not raise an exception and file remains empty.
        try:
            self.mem_store.flush_to_longterm(self.hdf5_storage)
        except Exception as e:
            self.fail(f"flush_to_longterm() raised an exception on empty memory store: {e}")
        states = self.hdf5_storage.load_simulation_state()
        self.assertEqual(len(states), 0)
    
    # 29.
    def test_multiple_flush_and_load(self):
        # Update multiple timesteps, flush, then load the highest timestep.
        for t in range(38, 40):
            board = [[t, t], [t, t]]
            org = DummyOrganism(t, t, 10+t, 1.0, t, "Z", f"org{t:04d}")
            self.mem_store.update_state(t, board, [org], [f"log{t}"])
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        highest = max(self.mem_store.states.keys())
        loaded_state = self.mem_store.load_from_longterm(self.hdf5_storage, highest)
        self.assertEqual(self.mem_store.current_timestep, highest)
    
    # 30.
    def test_update_in_replay_mode_raises_error(self):
        replay_store = MemoryResidentSimulationStore(mode="replay")
        with self.assertRaises(RuntimeError):
            replay_store.update_state(0, [[0,0]], [], ["log"])
    
if __name__ == '__main__':
    unittest.main()
