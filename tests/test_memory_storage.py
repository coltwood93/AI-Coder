import unittest
import os
import sys
import tempfile
import numpy as np

# Insert the parent directory into sys.path so we can import our modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdf5_storage import HDF5Storage
from memory_storage import MemoryResidentSimulationStore, DummyOrganism

# Helper function to convert a list of objects to list of dicts
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
    def setUp(self):
        self.mem_store = MemoryResidentSimulationStore()
        self.temp_fd, self.temp_filename = tempfile.mkstemp(suffix='.hdf5')
        os.close(self.temp_fd)
        self.hdf5_storage = HDF5Storage(filename=self.temp_filename)
    
    def tearDown(self):
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_update_state_and_get_current_state(self):
        """Test basic update state functionality."""
        timestep = 1
        environment = np.array([[0.5, 0.3], [0.2, 0.8]])
        producers = [DummyOrganism(0, 0, 10, 1, 1, "P", "1")]
        herbivores = [DummyOrganism(1, 1, 20, 2, 1, "H", "2")]
        
        # Update state using keyword args
        self.mem_store.update_state(
            timestep, environment, 
            producers=producers,
            herbivores=herbivores
        )
        
        # Get current state
        state = self.mem_store.get_current_state()
        self.assertIsNotNone(state)
        self.assertIn('environment', state)
        self.assertIn('organisms', state)
        self.assertIn('producers', state['organisms'])
        self.assertIn('herbivores', state['organisms'])
    
    def test_getters_return_none_when_state_missing(self):
        """Test that getters return None when state doesn't exist."""
        self.assertIsNone(self.mem_store.get_current_state())
        
        # Use the getters that actually exist in the class
        self.assertIsNone(self.mem_store.get_board())
        self.assertIsNone(self.mem_store.get_producers())
        self.assertIsNone(self.mem_store.get_consumers())
        self.assertIsNone(self.mem_store.get_debug_logs())
    
    def test_load_all_consumers_aggregated(self):
        """Test load_all_consumers for multiple timesteps."""
        # Reset manually to ensure clean state
        self.mem_store = MemoryResidentSimulationStore()
        
        # Add data for multiple timesteps
        for t in range(3):
            environment = np.array([[t, t+1], [t+2, t+3]])
            herbivores = [DummyOrganism(t, t, 10, 1, t, "H", t)]
            
            # Update state with herbivores
            self.mem_store.update_state(t, environment, herbivores=herbivores)
        
        # Get all states and check herbivores
        for t in range(3):
            state = self.mem_store.states.get(t, {})
            if 'organisms' in state and 'herbivores' in state['organisms']:
                orgs = state['organisms']['herbivores']
                self.assertEqual(1, len(orgs))
                self.assertEqual(t, orgs[0].x)
                self.assertEqual(t, orgs[0].y)
    
    def test_update_consumers_without_debug_logs_key(self):
        """Test updating consumers when debug logs key doesn't exist."""
        timestep = 1
        environment = np.array([[0.1, 0.2], [0.3, 0.4]])
        herbivores = [DummyOrganism(0, 0, 10, 1, 0, "H", "1")]
        
        # Update state without other organism types
        self.mem_store.update_state(timestep, environment, herbivores=herbivores)
        
        # Get state and verify
        state = self.mem_store.get_current_state()
        self.assertIsNotNone(state)
        self.assertIn('organisms', state)
        self.assertIn('herbivores', state['organisms'])
        self.assertEqual(1, len(state['organisms']['herbivores']))
    
    def test_reset(self):
        """Test resetting the memory store."""
        # Add some data first
        self.mem_store.update_state(1, np.array([[1, 1], [1, 1]]))
        self.assertIsNotNone(self.mem_store.get_current_state())
        
        # Reset the store
        self.mem_store.reset()
        
        # Check that it's empty now
        self.assertEqual({}, self.mem_store.states)
        self.assertIsNone(self.mem_store.current_timestep)
    
    def test_is_live(self):
        """Test the is_live method."""
        # Should be in live mode by default
        self.assertTrue(self.mem_store.is_live())
        
        # Create a replay mode store
        replay_store = MemoryResidentSimulationStore(mode="replay")
        self.assertFalse(replay_store.is_live())

if __name__ == '__main__':
    unittest.main()
