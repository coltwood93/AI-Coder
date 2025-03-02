#!/usr/bin/env python3
"""
Test runner script for the A-Life project.
Discovers and runs all tests, handling both unittest and pytest styles.
"""

import unittest
import sys
import os

def run_tests():
    """
    Discover and run all tests in the tests/ directory.
    """
    # Ensure the project root is in the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    print("====================================")
    print("Running all tests for A-Life Project")
    print("====================================")
    
    # Use the test discovery mechanism
    test_loader = unittest.defaultTestLoader
    test_loader.testMethodPrefix = "test"  # Default prefix for test methods
    
    # Discover tests in the tests directory
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print("\n====================================")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Skipped: {len(result.skipped)}")
    print("====================================")
    
    # Return appropriate exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
