import unittest
import numpy as np
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import (
    current_season, random_border_cell, spawn_random_organism_on_border,
    disease_outbreak, update_environment
)
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, SEASON_LENGTH, 
    DISEASE_DURATION, INITIAL_NUTRIENT_LEVEL,
    NUTRIENT_DECAY_RATE, NUTRIENT_DIFFUSION_RATE
)

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        # Create a simple test environment
        self.environment = np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL)
        
        # Reset organism counters to ensure clean test state
        from organisms.producer import Producer
        from organisms.herbivore import Herbivore
        from organisms.carnivore import Carnivore
        from organisms.omnivore import Omnivore
        
        Producer.reset_id_counter()
        Herbivore.reset_id_counter()
        Carnivore.reset_id_counter()
        Omnivore.reset_id_counter()
    
    def test_current_season(self):
        """Test that current_season returns correct values."""
        # Updated to match the actual implementation
        self.assertEqual(current_season(0), "WINTER")
        self.assertEqual(current_season(SEASON_LENGTH - 1), "WINTER")
        self.assertEqual(current_season(SEASON_LENGTH), "SUMMER")
        self.assertEqual(current_season(SEASON_LENGTH * 2 - 1), "SUMMER")
        self.assertEqual(current_season(SEASON_LENGTH * 2), "WINTER")
    
    def test_random_border_cell(self):
        """Test that random_border_cell returns valid border coordinates."""
        for _ in range(50):
            x, y = random_border_cell()
            
            # Check coordinates are within grid bounds
            self.assertTrue(0 <= x < GRID_WIDTH)
            self.assertTrue(0 <= y < GRID_HEIGHT)
            
            # Check that at least one coordinate is on the border
            self.assertTrue(
                x == 0 or x == GRID_WIDTH - 1 or 
                y == 0 or y == GRID_HEIGHT - 1
            )
    
    def test_spawn_random_organism_on_border(self):
        """Test spawning an organism on the border."""
        producers = []
        herbivores = []
        carnivores = []
        omnivores = []
        
        # Test for both seasons
        for season in ["SUMMER", "WINTER"]:
            spawn_random_organism_on_border(
                producers, herbivores, carnivores, omnivores, season
            )
            
            # Check that at least one organism was created
            total_count = len(producers) + len(herbivores) + len(carnivores) + len(omnivores)
            self.assertGreater(total_count, 0)
            
            # Check that the most recently created organism is on a border
            latest_organism = None
            if producers:
                latest_organism = producers[-1]
            elif herbivores:
                latest_organism = herbivores[-1]
            elif carnivores:
                latest_organism = carnivores[-1]
            elif omnivores:
                latest_organism = omnivores[-1]
                
            self.assertIsNotNone(latest_organism)
            self.assertTrue(
                latest_organism.x == 0 or 
                latest_organism.x == GRID_WIDTH - 1 or
                latest_organism.y == 0 or 
                latest_organism.y == GRID_HEIGHT - 1
            )
    
    def test_disease_outbreak(self):
        """Test that disease outbreak infects organisms."""
        # Create some test organisms
        from organisms.herbivore import Herbivore
        from organisms.carnivore import Carnivore
        from organisms.omnivore import Omnivore
        
        herbivores = [Herbivore(1, 1, 100) for _ in range(5)]
        carnivores = [Carnivore(2, 2, 100) for _ in range(5)]
        omnivores = [Omnivore(3, 3, 100) for _ in range(5)]
        
        # Check that no organisms are infected initially
        for org in herbivores + carnivores + omnivores:
            self.assertEqual(org.disease_timer, 0)
        
        # Trigger disease outbreak
        disease_outbreak(herbivores, carnivores, omnivores)
        
        # Check that at least one organism was infected
        infected_count = sum(org.disease_timer > 0 for org in herbivores + carnivores + omnivores)
        self.assertGreater(infected_count, 0)
        
        # Check that infected organisms have the right disease duration
        for org in herbivores + carnivores + omnivores:
            if org.disease_timer > 0:
                self.assertEqual(org.disease_timer, DISEASE_DURATION)
    
    def test_update_environment(self):
        """Test environment update with nutrient diffusion and decay."""
        # Create a test environment with varied nutrient levels
        test_env = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        test_env[5, 5] = 1.0  # High concentration at center
        
        # Make a copy of the original environment
        original_env = test_env.copy()
        
        # Update environment and check results
        updated_env = update_environment(test_env)
        
        # Check overall nutrient conservation (minus decay)
        original_total = np.sum(original_env)
        updated_total = np.sum(updated_env)
        self.assertLessEqual(updated_total, original_total)  # Total shouldn't increase
        
        # Check diffusion - neighbors should have received some nutrients
        self.assertGreater(updated_env[4, 5], 0)  # Left
        self.assertGreater(updated_env[6, 5], 0)  # Right
        self.assertGreater(updated_env[5, 4], 0)  # Up
        self.assertGreater(updated_env[5, 6], 0)  # Down
        
        # High concentration cell should have decreased
        self.assertLess(updated_env[5, 5], original_env[5, 5])
        
        # No cell should have negative nutrients
        self.assertTrue(np.all(updated_env >= 0))

if __name__ == '__main__':
    unittest.main()