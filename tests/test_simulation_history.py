import unittest
import os
import sys
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.history import SimulationState

class MockOrganism:
    def __init__(self, x, y, energy=100, id=None):
        self.x = x
        self.y = y
        self.energy = energy
        self.id = id if id is not None else id

class TestSimulationHistory(unittest.TestCase):
    def setUp(self):
        # Create some test data
        self.timestep = 10
        self.environment = np.ones((5, 5)) * 0.5
        
        # Create sample organisms
        self.producers = [MockOrganism(1, 1, 100, "p1")]
        self.herbivores = [MockOrganism(2, 2, 100, "h1"), MockOrganism(2, 3, 100, "h2")]
        self.carnivores = [MockOrganism(3, 3, 100, "c1")]
        self.omnivores = [MockOrganism(4, 4, 100, "o1")]
        
        # Create a simulation state
        self.state = SimulationState(
            self.timestep,
            self.producers,
            self.herbivores,
            self.carnivores,
            self.omnivores,
            self.environment
        )

    def test_simulation_state_creation(self):
        """Test that a simulation state is created correctly."""
        self.assertEqual(self.state.t, self.timestep)
        self.assertEqual(len(self.state.producers), len(self.producers))
        self.assertEqual(len(self.state.herbivores), len(self.herbivores))
        self.assertEqual(len(self.state.carnivores), len(self.carnivores))
        self.assertEqual(len(self.state.omnivores), len(self.omnivores))
        self.assertTrue(np.array_equal(self.state.environment, self.environment))

if __name__ == '__main__':
    unittest.main()
