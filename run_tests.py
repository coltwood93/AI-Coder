#!/usr/bin/env python3
"""
Run all tests for the A-Life project.
"""
import sys
import os
import unittest
import importlib

def run_all_tests():
    """Run all tests in the tests directory."""
    print("=" * 36)
    print("Running all tests for A-Life Project")
    print("=" * 36)
    
    # Add the project root to the Python path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root_dir)
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=1).run(test_suite)
    
    # Return success if all tests passed
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # Initialize pygame first to avoid issues
    try:
        import pygame
        pygame.init()
        print(f"{pygame.version.ver} (SDL {pygame.version.SDL})")
        print(f"Hello from the pygame community. https://www.pygame.org/contribute.html")
    except ImportError:
        print("Pygame not found - some tests might fail.")
    
    sys.exit(run_all_tests())
