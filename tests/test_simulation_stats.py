import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.stats import calc_traits_avg

class MockOrganism:
    def __init__(self, speed, metabolism, vision, generation=1, energy=100):
        self.genes = [speed, metabolism, vision]
        self.generation = generation
        self.energy = energy
        self.disease_timer = 0
    
    @property
    def speed(self):
        return self.genes[0]
        
    @property
    def metabolism(self):
        return self.genes[1]
        
    @property
    def vision(self):
        return self.genes[2]
    
    def is_infected(self):
        return self.disease_timer > 0

class TestSimulationStats(unittest.TestCase):
    def setUp(self):
        # Create sample organisms for testing
        self.herbivores = [
            MockOrganism(2, 0.5, 2, 1),
            MockOrganism(3, 0.6, 1, 2)
        ]
        self.carnivores = [
            MockOrganism(4, 0.7, 3, 1),
            MockOrganism(5, 0.8, 4, 3)
        ]
        self.omnivores = [
            MockOrganism(3, 0.6, 2, 2),
            MockOrganism(4, 0.5, 3, 4)
        ]
        
        # Create an infected organism for testing
        self.infected_herbivore = MockOrganism(2, 0.5, 2)
        self.infected_herbivore.disease_timer = 10

    def test_calc_traits_avg(self):
        """Test calculation of average traits."""
        # Test with herbivores
        avg_speed, avg_gen, avg_met, avg_vis = calc_traits_avg(self.herbivores)
        self.assertEqual(avg_speed, 2.5)
        self.assertEqual(avg_gen, 1.5)
        self.assertEqual(avg_met, 0.55)
        self.assertEqual(avg_vis, 1.5)
        
        # Test with carnivores
        avg_speed, avg_gen, avg_met, avg_vis = calc_traits_avg(self.carnivores)
        self.assertEqual(avg_speed, 4.5)
        self.assertEqual(avg_gen, 2.0)
        self.assertEqual(avg_met, 0.75)
        self.assertEqual(avg_vis, 3.5)
        
        # Test with omnivores
        avg_speed, avg_gen, avg_met, avg_vis = calc_traits_avg(self.omnivores)
        self.assertEqual(avg_speed, 3.5)
        self.assertEqual(avg_gen, 3.0)
        self.assertEqual(avg_met, 0.55)
        self.assertEqual(avg_vis, 2.5)
    
    def test_calc_traits_avg_empty_list(self):
        """Test calculation of average traits with an empty list."""
        avg_speed, avg_gen, avg_met, avg_vis = calc_traits_avg([])
        self.assertEqual(avg_speed, 0.0)
        self.assertEqual(avg_gen, 0.0)
        self.assertEqual(avg_met, 0.0)
        self.assertEqual(avg_vis, 0.0)

if __name__ == '__main__':
    unittest.main()
