import os
import sys
import tempfile
import unittest
import numpy as np

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

# Helper function to convert a list of objects to list of dicts.
def dictify(obj_list):
    if obj_list is None:
        return None
    new_list = []
    for obj in obj_list:
        if hasattr(obj, "__dict__"):
            new_list.append(obj.__dict__)
        else:
            # Assume it's already a dict.
            new_list.append(obj)
    return new_list

class TestMemoryResidentSimulationStore(unittest.TestCase):
    # --- Tests 1–21: Existing Tests (Updated to new design) ---
    def setUp(self):
        self.temp_hdf5 = tempfile.mktemp(suffix=".h5")
        self.hdf5_storage = HDF5Storage(self.temp_hdf5)
        self.mem_store = MemoryResidentSimulationStore(mode="live")
    
    def tearDown(self):
        if os.path.exists(self.temp_hdf5):
            os.remove(self.temp_hdf5)
    
    # 1.
    def test_update_state_and_get_current_state(self):
        timestep = 0
        board = [[0, 1], [1, 0]]
        # For this test, assume no producers and consumers are provided as lists.
        producers = []
        consumers = [DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001"),
                     DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")]
        debug_logs = ["start", "update"]
        self.mem_store.update_state(timestep, board, producers, consumers, debug_logs)
        current = self.mem_store.get_current_state()
        self.assertEqual(current["board"], board)
        self.assertEqual(current["producers"], producers)
        np.testing.assert_array_equal(
            np.array(dictify(current["consumers"])),
            np.array(dictify(consumers))
        )
        self.assertEqual(current["debug_logs"], debug_logs)
        self.assertEqual(self.mem_store.current_timestep, timestep)
    
    # 2.
    def test_piecewise_update_board(self):
        timestep = 5
        board_initial = [[0, 0], [0, 0]]
        board_updated = [[1, 1], [1, 1]]
        self.mem_store.update_state(timestep, board_initial, [], [], [])
        self.mem_store.update_board(timestep, board_updated)
        self.assertEqual(self.mem_store.get_board(timestep), board_updated)
    
    # 3.
    def test_piecewise_update_consumers(self):
        timestep = 2
        consumers = [DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")]
        self.mem_store.update_consumers(timestep, consumers)
        ret = self.mem_store.get_consumers(timestep)
        np.testing.assert_array_equal(np.array(dictify(ret)), np.array(dictify(consumers)))
    
    # 4.
    def test_piecewise_update_debug_logs(self):
        timestep = 4
        logs = ["log1", "log2"]
        self.mem_store.update_debug_logs(timestep, logs)
        self.assertEqual(self.mem_store.get_debug_logs(timestep), logs)
    
    # 5.
    def test_update_consumer_position(self):
        timestep = 6
        board = [[0, 0], [0, 0]]
        consumer1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        consumer2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        self.mem_store.update_state(timestep, board, [], [consumer1, consumer2], ["initial"])
        new_pos = [5, 5]
        # Use update_consumer_position (new method)
        self.mem_store.update_consumer_position(timestep, 0, new_pos)
        ret = self.mem_store.get_consumers(timestep)
        self.assertEqual(ret[0].__dict__["x"], new_pos[0])
        self.assertEqual(ret[0].__dict__["y"], new_pos[1])
    
    # 6.
    def test_add_and_remove_consumer(self):
        timestep = 7
        board = [[0, 0], [0, 0]]
        self.mem_store.update_state(timestep, board, [], [], ["init"])
        consumer1 = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        consumer2 = DummyOrganism(2, 2, 8, 1.2, 0, "B", "org0002", "org0001")
        self.mem_store.add_consumer(timestep, consumer1)
        self.mem_store.add_consumer(timestep, consumer2)
        cons = self.mem_store.get_consumers(timestep)
        np.testing.assert_array_equal(np.array(dictify(cons)), np.array(dictify([consumer1, consumer2])))
        self.mem_store.remove_consumer(timestep, 0)
        cons_after = self.mem_store.get_consumers(timestep)
        np.testing.assert_array_equal(np.array(dictify(cons_after)), np.array(dictify([consumer2])))
    
    # 7.
    def test_flush_to_longterm(self):
        for t in range(3):
            board = [[t, t], [t, t]]
            consumers = [DummyOrganism(t, t, 10+t, 1.0, t, "A", f"org{t:04d}")]
            self.mem_store.update_state(t, board, [], consumers, [f"log{t}"])
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        states = self.hdf5_storage.load_simulation_state()
        self.assertEqual(len(states), 3)
        for t_val, state_tuple in states:
            board_loaded, producers, consumers, logs = state_tuple
            expected_board = np.array([[t_val, t_val], [t_val, t_val]], dtype=np.int8)
            np.testing.assert_array_equal(board_loaded, expected_board)
            self.assertEqual(producers, [])
            expected_consumer = [c.__dict__ for c in [DummyOrganism(t_val, t_val, 10+t_val, 1.0, t_val, "A", f"org{t_val:04d}")]]
            np.testing.assert_array_equal(np.array(consumers), np.array(expected_consumer))
            self.assertEqual(logs[0].decode("utf-8"), f"log{t_val}")
    
    # 8.
    def test_load_from_longterm(self):
        board = [[3, 3], [3, 3]]
        consumer = DummyOrganism(3, 3, 15, 1.2, 1, "B", "org0005")
        self.hdf5_storage.save_simulation_state(5, board, [], [consumer], ["test log"])
        self.mem_store = MemoryResidentSimulationStore(mode="replay")
        state = self.mem_store.load_from_longterm(self.hdf5_storage, 5)
        self.assertIsNotNone(state)
        self.assertEqual(self.mem_store.current_timestep, 5)
        np.testing.assert_array_equal(np.array(state["board"], dtype=np.int8), np.array(board, dtype=np.int8))
        np.testing.assert_array_equal(np.array(dictify(state["consumers"])), np.array(dictify([consumer])))
        self.assertEqual(state["debug_logs"][0].decode("utf-8"), "test log")
    
    # 9.
    def test_mode_switching(self):
        cons0 = DummyOrganism(0, 0, 10, 1, 0, "A", "org0001")
        cons1 = DummyOrganism(1, 1, 9, 1, 0, "B", "org0002", "org0001")
        cons2 = DummyOrganism(2, 2, 8, 1, 0, "C", "org0003", "org0002")
        self.mem_store.update_state(0, [[0]], [], [cons0], ["t0"])
        self.mem_store.update_state(1, [[1]], [], [cons1], ["t1"])
        self.mem_store.update_state(2, [[2]], [], [cons2], ["t2"])
        self.assertTrue(self.mem_store.is_last_stored_step())
        self.assertEqual(self.mem_store.mode, "live")
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        self.mem_store.load_from_longterm(self.hdf5_storage, 1)  # note: check variable name below!
        self.assertFalse(self.mem_store.is_last_stored_step())
        self.assertEqual(self.mem_store.mode, "replay")
    
    # 10.
    def test_piecewise_consumer_update(self):
        timestep = 8
        board = [[0, 0], [0, 0]]
        consumer = DummyOrganism(1, 1, 10, 1.0, 0, "A", "org0001")
        self.mem_store.update_state(timestep, board, [], [consumer], ["initial"])
        new_position = [5, 5]
        self.mem_store.update_consumer_position(timestep, 0, new_position)
        cons = self.mem_store.get_consumers(timestep)
        self.assertEqual(cons[0].__dict__["x"], new_position[0])
        self.assertEqual(cons[0].__dict__["y"], new_position[1])
    
    # 11.
    def test_partial_updates_vs_full_update(self):
        timestep = 10
        board = [[1, 0], [0, 1]]
        consumer = DummyOrganism(3, 3, 12, 1.5, 1, "A", "org0003", None)
        debug_logs = ["start", "end"]
        self.mem_store.update_state(timestep, board, [], [consumer], debug_logs)
        full_state = self.mem_store.get_current_state()
        self.mem_store.update_board(timestep, board)
        cons_data = [consumer]  # no change
        self.mem_store.update_consumers(timestep, cons_data)
        self.mem_store.update_debug_logs(timestep, debug_logs)
        piecewise_state = self.mem_store.get_current_state()
        self.assertEqual(piecewise_state["board"], full_state["board"])
        np.testing.assert_array_equal(np.array(dictify(piecewise_state["consumers"])),
                                      np.array(dictify(full_state["consumers"])))
        self.assertEqual(piecewise_state["debug_logs"], full_state["debug_logs"])
    
    # 12.
    def test_update_state_with_empty_consumers(self):
        timestep = 20
        board = [[1, 2], [3, 4]]
        debug_logs = ["empty consumers"]
        self.mem_store.update_state(timestep, board, [], [], debug_logs)
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board)
        self.assertEqual(state["producers"], [])
        self.assertEqual(state["consumers"], [])
        self.assertEqual(state["debug_logs"], debug_logs)
    
    # 13.
    def test_update_state_with_empty_debug_logs(self):
        timestep = 21
        board = [[5, 5], [5, 5]]
        consumer = DummyOrganism(5, 5, 20, 1.0, 1, "X", "org0021")
        self.mem_store.update_state(timestep, board, [], [consumer], [])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["debug_logs"], [])
    
    # 14.
    def test_update_board_does_not_affect_consumers(self):
        timestep = 22
        board1 = [[0, 0], [0, 0]]
        consumer = DummyOrganism(2, 2, 15, 1.0, 1, "Y", "org0022")
        self.mem_store.update_state(timestep, board1, [], [consumer], ["log"])
        board2 = [[9, 9], [9, 9]]
        self.mem_store.update_board(timestep, board2)
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board2)
        np.testing.assert_array_equal(np.array(dictify(state["consumers"])), np.array(dictify([consumer])))
    
    # 15.
    def test_update_consumers_with_empty_list(self):
        timestep = 23
        board = [[7, 8], [9, 10]]
        consumer = DummyOrganism(1, 1, 10, 1.0, 0, "Z", "org0023")
        self.mem_store.update_state(timestep, board, [], [consumer], ["initial"])
        self.mem_store.update_consumers(timestep, [])
        cons = self.mem_store.get_consumers(timestep)
        self.assertEqual(cons, [])
    
    # 16.
    def test_multiple_updates_same_timestep_order(self):
        timestep = 24
        board_initial = [[0, 0]]
        consumer = DummyOrganism(1, 1, 10, 1.0, 0, "M", "org0024")
        self.mem_store.update_state(timestep, board_initial, [], [consumer], ["init"])
        self.mem_store.update_board(timestep, [[2,2]])
        cons_data = [consumer]
        self.mem_store.update_consumers(timestep, cons_data)
        self.mem_store.update_board(timestep, [[3,3]])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], [[3,3]])
        np.testing.assert_array_equal(np.array(dictify(state["consumers"])), np.array(dictify([consumer])))
    
    # 17.
    def test_load_all_debug_logs_aggregated(self):
        for t in range(26, 29):
            self.mem_store.update_state(t, [[t]], [], [DummyOrganism(t, t, 10, 1, 0, "D", f"org{t:04d}")], [f"debug{t}"])
        all_logs = self.mem_store.load_all_debug_logs()
        self.assertEqual(len(all_logs), 3)
        expected_timesteps = [26, 27, 28]
        for i, (t_val, logs) in enumerate(all_logs):
            self.assertEqual(t_val, expected_timesteps[i])
            self.assertEqual(logs, [f"debug{t_val}"])
    
    # 18.
    def test_update_with_empty_board(self):
        timestep = 29
        board = []
        self.mem_store.update_state(timestep, board, [], [], ["empty board"])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board)
    
    # 19.
    def test_load_all_consumers_aggregated(self):
        for t in range(30, 32):
            consumers = [DummyOrganism(t, t, t+10, 1.0, t, "S", f"org{t:04d}")]
            self.mem_store.update_consumers(t, consumers)
        all_cons = self.mem_store.load_all_consumers()
        self.assertEqual(len(all_cons), 2)
        expected = [[30, 30], [31, 31]]
        for i, (t_val, cons) in enumerate(all_cons):
            np.testing.assert_array_equal(np.array(dictify(cons)), np.array([{"x": expected[i][0],
                                                                               "y": expected[i][1],
                                                                               "energy": t_val+10,
                                                                               "speed": 1.0,
                                                                               "generation": t_val,
                                                                               "species": "S",
                                                                               "id": f"org{t_val:04d}",
                                                                               "parent_id": None}]))
    
    # 20.
    def test_independent_board_and_consumers_updates(self):
        timestep = 32
        board1 = [[0,0],[0,0]]
        consumers1 = [DummyOrganism(1,1,10,1.0,0,"X","org0032")]
        self.mem_store.update_state(timestep, board1, [], consumers1, ["init"])
        self.mem_store.update_board(timestep, [[5,5],[5,5]])
        consumers2 = [DummyOrganism(2,2,20,1.5,1,"Y","org0032_2")]
        self.mem_store.update_consumers(timestep, consumers2)
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], [[5,5],[5,5]])
        np.testing.assert_array_equal(np.array(dictify(state["consumers"])), np.array(dictify(consumers2)))
    
    # 21.
    def test_update_lineage_by_consumers_indirectly(self):
        # In the new design, lineage is assumed to be inside each consumer object.
        # This test checks that if you update consumers, the lineage information comes along.
        timestep = 33
        board = [[1,1],[1,1]]
        consumer = DummyOrganism(1,1,10,1.0,0,"A","org0033", "parentA")
        self.mem_store.update_state(timestep, board, [], [consumer], ["lineage init"])
        # Now update consumers with a new list, the lineage should update accordingly.
        new_consumer = DummyOrganism(2,2,15,1.2,1,"B","org0033_2", "parentB")
        self.mem_store.update_consumers(timestep, [new_consumer])
        state = self.mem_store.get_current_state()
        # We expect the consumer list to reflect the new consumer.
        np.testing.assert_array_equal(np.array(dictify(state["consumers"])), np.array(dictify([new_consumer])))
    
    # 22.
    def test_update_debug_logs_independent(self):
        timestep = 34
        board = [[4,4],[4,4]]
        self.mem_store.update_state(timestep, board, [], [], ["old log"])
        self.mem_store.update_debug_logs(timestep, ["new log"])
        self.assertEqual(self.mem_store.get_debug_logs(timestep), ["new log"])
        self.assertEqual(self.mem_store.get_board(timestep), board)
    
    # 23.
    def test_update_consumers_without_debug_logs_key(self):
        # In this new design, update_consumers simply stores the list provided.
        timestep = 35
        consumers = [DummyOrganism(1,1,10,1.0,0,"P","org0035")]
        self.mem_store.update_consumers(timestep, consumers)
        ret = self.mem_store.get_consumers(timestep)
        np.testing.assert_array_equal(np.array(dictify(ret)), np.array(dictify(consumers)))
    
    # 24.
    def test_clear_producers_by_updating_with_empty_list(self):
        timestep = 36
        board = [[1,1],[1,1]]
        producers_initial = [DummyOrganism(1,1,10,1.0,0,"A","prod0036")]
        self.mem_store.update_state(timestep, board, producers_initial, [], ["log"])
        self.mem_store.update_producers(timestep, [])
        prods = self.mem_store.get_producers(timestep)
        self.assertEqual(prods, [])
    
    # 25.
    def test_getters_return_none_when_state_missing(self):
        timestep = 37
        self.mem_store.states[timestep] = {"board": [[0,0],[0,0]]}
        self.assertIsNone(self.mem_store.get_producers(timestep))
        self.assertIsNone(self.mem_store.get_consumers(timestep))
        self.assertIsNone(self.mem_store.get_debug_logs(timestep))
    
    # 26.
    def test_flush_empty_memory(self):
        try:
            self.mem_store.flush_to_longterm(self.hdf5_storage)
        except Exception as e:
            self.fail(f"flush_to_longterm() raised an exception on empty memory store: {e}")
        states = self.hdf5_storage.load_simulation_state()
        self.assertEqual(len(states), 0)
    
    # 27.
    def test_multiple_flush_and_load(self):
        for t in range(38, 40):
            board = [[t, t], [t, t]]
            consumers = [DummyOrganism(t, t, 10+t, 1.0, t, "Z", f"org{t:04d}")]
            self.mem_store.update_state(t, board, [], consumers, [f"log{t}"])
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        highest = max(self.mem_store.states.keys())
        loaded_state = self.mem_store.load_from_longterm(self.hdf5_storage, highest)
        self.assertEqual(self.mem_store.current_timestep, highest)
        self.assertEqual(loaded_state, self.mem_store.states[highest])
    
    # 28.
    def test_update_in_replay_mode_raises_error(self):
        replay_store = MemoryResidentSimulationStore(mode="replay")
        with self.assertRaises(RuntimeError):
            replay_store.update_state(0, [[0,0]], [], [], ["log"])
    
    # 29.
    def test_update_state_with_empty_board(self):
        timestep = 39
        board = []
        self.mem_store.update_state(timestep, board, [], [], ["empty board"])
        state = self.mem_store.get_current_state()
        self.assertEqual(state["board"], board)
    
    # 30.
    def test_flush_and_load(self):
        self.mem_store.flush_to_longterm(self.hdf5_storage)
        highest = max(self.mem_store.states.keys())
        self.mem_store.load_from_longterm(self.hdf5_storage, highest)
        self.assertEqual(self.mem_store.current_timestep, highest)
    
if __name__ == '__main__':
    unittest.main()
