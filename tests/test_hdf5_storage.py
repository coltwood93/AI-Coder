import os
import sys
import tempfile
import unittest
import numpy as np
import h5py

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdf5_storage import HDF5Storage

class DummyOrganism:
    def __init__(self, x, y, energy, speed, age, type_id, id):
        self.x = x
        self.y = y
        self.energy = energy
        self.speed = speed
        self.age = age
        self.type_id = type_id
        self.id = id

class TestHDF5Storage(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.mktemp(suffix=".h5")
        self.storage = HDF5Storage(self.temp_file)
        self.storage.create_empty_file()  # Create the empty HDF5 file
    
    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_initialization(self):
        """Test that the storage is properly initialized"""
        self.assertTrue(os.path.exists(self.temp_file))
        with h5py.File(self.temp_file, 'r') as f:
            self.assertEqual(len(f.keys()), 0)

    def test_save_and_load_board(self):
        """Test saving and loading board state"""
        test_board = [[1, 2], [3, 4]]
        self.storage.save_board(timestep=1, board=test_board)
        states = self.storage.load_simulation_state(timestep=1)
        self.assertEqual(len(states), 1)
        timestep, (board, _, _, _) = states[0]
        np.testing.assert_array_equal(board, np.array(test_board))

    def test_save_and_load_organisms(self):
        """Test saving and loading organisms"""
        producer = DummyOrganism(1, 1, 10, 1.0, 0, "P", "prod001")
        consumer = DummyOrganism(2, 2, 20, 2.0, 1, "C", "cons001")
        
        self.storage.save_simulation_state(
            timestep=1,
            board=[[1, 1], [1, 1]],
            producers=[producer],
            consumers=[consumer],
            debug_logs=["Test log"]
        )
        
        states = self.storage.load_simulation_state(timestep=1)
        self.assertEqual(len(states), 1)
        _, (_, producers, consumers, logs) = states[0]
        
        self.assertEqual(len(producers), 1)
        self.assertEqual(producers[0]["id"], "prod001")
        self.assertEqual(producers[0]["energy"], 10)
        
        self.assertEqual(len(consumers), 1)
        self.assertEqual(consumers[0]["id"], "cons001")
        self.assertEqual(consumers[0]["energy"], 20)
        
        self.assertEqual(logs[0].decode('utf-8'), "Test log")

    def test_load_all_functions(self):
        """Test the load_all_* functions"""
        self.storage.save_simulation_state(
            timestep=1,
            board=[[1, 1], [1, 1]],
            producers=[DummyOrganism(1, 1, 10, 1.0, 0, "P", "prod001")],
            consumers=[DummyOrganism(2, 2, 20, 2.0, 1, "C", "cons001")],
            debug_logs=["Log 1"]
        )
        
        producers = self.storage.load_all_producers()
        consumers = self.storage.load_all_consumers()
        logs = self.storage.load_all_debug_logs()
        
        self.assertEqual(len(producers), 1)
        self.assertEqual(len(consumers), 1)
        self.assertEqual(len(logs), 1)
        
        _, producer_list = producers[0]
        self.assertEqual(producer_list[0]["id"], "prod001")
        
        _, consumer_list = consumers[0]
        self.assertEqual(consumer_list[0]["id"], "cons001")
        
        _, log_list = logs[0]
        self.assertEqual(log_list[0].decode('utf-8'), "Log 1")

    def test_multiple_timesteps(self):
        """Test saving and loading multiple timesteps"""
        for t in range(3):
            self.storage.save_simulation_state(
                timestep=t,
                board=[[t, t], [t, t]],
                producers=[],
                consumers=[DummyOrganism(t, t, 10+t, 1.0, t, "C", f"org{t:04d}")],
                debug_logs=[f"Log {t}"]
            )
        
        states = self.storage.load_simulation_state()
        self.assertEqual(len(states), 3)
        for i, (timestep, state) in enumerate(states):
            self.assertEqual(timestep, i)
            board, _, consumers, logs = state
            np.testing.assert_array_equal(board, np.array([[i, i], [i, i]]))
            self.assertEqual(consumers[0]["id"], f"org{i:04d}")
            self.assertEqual(logs[0].decode('utf-8'), f"Log {i}")

if __name__ == '__main__':
    unittest.main()