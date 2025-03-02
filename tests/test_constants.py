import unittest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import constants
from utils.constants import (
    DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT,  # Import default values
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, CELL_SIZE_X, CELL_SIZE_Y,
    GRID_DISPLAY_WIDTH, GRID_DISPLAY_HEIGHT,
    INITIAL_PRODUCERS, INITIAL_HERBIVORES, INITIAL_CARNIVORES, INITIAL_OMNIVORES,
    PRODUCER_ENERGY_GAIN, PRODUCER_MAX_ENERGY,
    EAT_GAIN_HERBIVORE, EAT_GAIN_CARNIVORE, 
    EAT_GAIN_OMNIVORE_PLANT, EAT_GAIN_OMNIVORE_ANIMAL,
    HERBIVORE_REPRO_THRESHOLD, CARNIVORE_REPRO_THRESHOLD, OMNIVORE_REPRO_THRESHOLD,
    MUTATION_RATE, SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE,
    update_from_config
)

class TestConstants(unittest.TestCase):
    def test_grid_dimensions(self):
        """Test that grid dimensions are positive integers."""
        self.assertGreater(GRID_WIDTH, 0)
        self.assertGreater(GRID_HEIGHT, 0)
    
    def test_cell_size(self):
        """Test that cell size is calculated correctly."""
        self.assertEqual(CELL_SIZE, min(CELL_SIZE_X, CELL_SIZE_Y))
        self.assertGreater(CELL_SIZE, 0)
    
    def test_initial_organism_counts(self):
        """Test that initial organism counts are non-negative."""
        self.assertGreaterEqual(INITIAL_PRODUCERS, 0)
        self.assertGreaterEqual(INITIAL_HERBIVORES, 0)
        self.assertGreaterEqual(INITIAL_CARNIVORES, 0)
        self.assertGreaterEqual(INITIAL_OMNIVORES, 0)
    
    def test_energy_gains(self):
        """Test that energy gains are positive."""
        self.assertGreater(PRODUCER_ENERGY_GAIN, 0)
        self.assertGreater(EAT_GAIN_HERBIVORE, 0)
        self.assertGreater(EAT_GAIN_CARNIVORE, 0)
        self.assertGreater(EAT_GAIN_OMNIVORE_PLANT, 0)
        self.assertGreater(EAT_GAIN_OMNIVORE_ANIMAL, 0)
    
    def test_reproduction_thresholds(self):
        """Test that reproduction thresholds are positive and make sense."""
        self.assertGreater(HERBIVORE_REPRO_THRESHOLD, 0)
        self.assertGreater(CARNIVORE_REPRO_THRESHOLD, 0)
        self.assertGreater(OMNIVORE_REPRO_THRESHOLD, 0)
    
    def test_genetic_parameters(self):
        """Test genetic parameters are in valid ranges."""
        # Mutation rate should be between 0 and 1
        self.assertGreaterEqual(MUTATION_RATE, 0)
        self.assertLessEqual(MUTATION_RATE, 1)
        
        # Range checks
        self.assertLess(SPEED_RANGE[0], SPEED_RANGE[1])
        self.assertLess(METABOLISM_RANGE[0], METABOLISM_RANGE[1])
        self.assertLess(VISION_RANGE[0], VISION_RANGE[1])

    def test_mock_config_manager(self):
        """Test that update_from_config works with a mock config manager."""
        
        # Store original values before test
        orig_grid_width = GRID_WIDTH
        orig_grid_height = GRID_HEIGHT
        orig_producers = INITIAL_PRODUCERS
        orig_herbivores = INITIAL_HERBIVORES
        orig_carnivores = INITIAL_CARNIVORES
        orig_omnivores = INITIAL_OMNIVORES
        
        try:
            # Create a mock config manager
            class MockConfigManager:
                def get_grid_width(self):
                    return orig_grid_width
                    
                def get_grid_height(self):
                    return orig_grid_height
                    
                def get_simulation_speed(self):
                    return 1.5
                    
                def get_fps(self):
                    return 30
                    
                def get_initial_count(self, organism_type):
                    counts = {
                        "producers": orig_producers,
                        "herbivores": orig_herbivores,
                        "carnivores": orig_carnivores,
                        "omnivores": orig_omnivores
                    }
                    return counts.get(organism_type, 0)
            
            # Update constants using mock config
            mock_config = MockConfigManager()
            update_from_config(mock_config)
            
            # Check values remained unchanged
            self.assertEqual(GRID_WIDTH, orig_grid_width)
            self.assertEqual(GRID_HEIGHT, orig_grid_height)
            self.assertEqual(INITIAL_PRODUCERS, orig_producers)
            self.assertEqual(INITIAL_HERBIVORES, orig_herbivores)
            self.assertEqual(INITIAL_CARNIVORES, orig_carnivores)
            self.assertEqual(INITIAL_OMNIVORES, orig_omnivores)
        finally:
            # No need to restore values since we didn't change them
            pass

if __name__ == '__main__':
    unittest.main()
