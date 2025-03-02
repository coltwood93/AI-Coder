import unittest
import numpy as np
import random
from unittest.mock import patch
from deap import base, creator, tools
from utils.toolbox import toolbox

# Get the actual ranges from constants
from utils.constants import SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE

class TestToolbox(unittest.TestCase):
    def setUp(self):
        # Make sure creator types are defined
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)
    
    def test_toolbox_creation(self):
        """Test that the toolbox is properly initialized."""
        self.assertIsInstance(toolbox, base.Toolbox)
        self.assertTrue(hasattr(toolbox, "individual"))
        self.assertTrue(hasattr(toolbox, "mutate"))
    
    def test_individual_creation(self):
        """Test creating an individual."""
        ind = toolbox.individual()
        self.assertIsInstance(ind, creator.Individual)
        self.assertEqual(3, len(ind))  # Speed, metabolism, vision
        
        # Check value ranges using constants rather than hardcoded values
        self.assertGreaterEqual(ind[0], SPEED_RANGE[0])
        self.assertLessEqual(ind[0], SPEED_RANGE[1])
        
        self.assertGreaterEqual(ind[1], METABOLISM_RANGE[0])
        self.assertLessEqual(ind[1], METABOLISM_RANGE[1])
        
        self.assertGreaterEqual(ind[2], VISION_RANGE[0])
        self.assertLessEqual(ind[2], VISION_RANGE[1])
    
    def test_mutation(self):
        """Test mutation operator."""
        # Create a dummy individual with middle-range values
        ind = creator.Individual([
            (SPEED_RANGE[0] + SPEED_RANGE[1]) // 2,
            (METABOLISM_RANGE[0] + METABOLISM_RANGE[1]) / 2,
            (VISION_RANGE[0] + VISION_RANGE[1]) // 2
        ])
        original = ind.copy()
        
        # Apply multiple mutations to increase chance of change
        changed = False
        for _ in range(10):  # Try several times
            mutated_ind, = toolbox.mutate(ind.copy())
            
            # Check that mutation produced changes
            for i in range(len(original)):
                if original[i] != mutated_ind[i]:
                    changed = True
                    break
                    
            if changed:
                break
                
        self.assertTrue(changed, "Mutation didn't change any genes after multiple attempts")

if __name__ == '__main__':
    unittest.main()