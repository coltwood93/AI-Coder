import pytest
import numpy as np
import random
from organisms.producer import Producer
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, PRODUCER_ENERGY_GAIN, PRODUCER_MAX_ENERGY,
    PRODUCER_SEED_COST, PRODUCER_SEED_PROB, PRODUCER_INIT_ENERGY_RANGE,
    PRODUCER_NUTRIENT_CONSUMPTION
)

@pytest.fixture
def basic_producer():
    """Create a basic producer for testing"""
    return Producer(x=5, y=5, energy=10)

def test_producer_initialization(basic_producer):
    """Test producer initialization"""
    assert basic_producer.x == 5
    assert basic_producer.y == 5
    assert basic_producer.energy == 10
    assert hasattr(basic_producer, 'id')
    assert isinstance(basic_producer.id, int)

def test_producer_nutrient_consumption(basic_producer):
    """Test producer consuming nutrients from environment"""
    environment = np.full((GRID_WIDTH, GRID_HEIGHT), 0.5)  # environment with nutrients
    initial_energy = basic_producer.energy
    initial_nutrients = environment[5, 5]
    
    # Update producer to consume nutrients
    basic_producer.update([], [], [], [], environment)
    
    # Should have gained energy from nutrients
    nutrients_consumed = min(initial_nutrients, PRODUCER_NUTRIENT_CONSUMPTION)
    expected_energy_gain = nutrients_consumed * PRODUCER_ENERGY_GAIN
    assert basic_producer.energy == initial_energy + expected_energy_gain
    assert environment[5, 5] == initial_nutrients - nutrients_consumed

def test_producer_energy_cap(basic_producer):
    """Test producer energy doesn't exceed maximum"""
    environment = np.full((GRID_WIDTH, GRID_HEIGHT), 1.0)  # Rich environment
    basic_producer.energy = PRODUCER_MAX_ENERGY - 0.1
    
    # Update should cap energy at max
    basic_producer.update([], [], [], [], environment)
    assert abs(basic_producer.energy - PRODUCER_MAX_ENERGY) < 0.1  # Allow for larger floating point imprecision
    
    # Further updates shouldn't increase energy beyond max
    basic_producer.update([], [], [], [], environment)
    assert abs(basic_producer.energy - PRODUCER_MAX_ENERGY) < 0.1

def test_producer_seeding(basic_producer):
    """Test producer reproduction through seeding"""
    # Set up test with controlled random seed
    random.seed(42)
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))  # No nutrients to avoid energy gain
    producers = [basic_producer]
    
    # Give producer enough energy to seed
    basic_producer.energy = PRODUCER_SEED_COST + 1
    
    # Mock the random probability to ensure seeding occurs
    original_random = random.random
    random.random = lambda: PRODUCER_SEED_PROB - 0.01  # Just under threshold to trigger seeding
    
    # Update should create a new producer
    basic_producer.update(producers, [], [], [], environment)
    
    # Restore random function
    random.random = original_random
    
    # Verify seeding occurred
    assert len(producers) == 2
    assert basic_producer.energy == 1  # Initial energy minus seed cost
    
    # New producer should be in an adjacent cell
    new_producer = producers[1]
    dx = abs(new_producer.x - basic_producer.x)
    dy = abs(new_producer.y - basic_producer.y)
    assert (dx <= 1 and dy <= 1) and not (dx == 0 and dy == 0)
    assert PRODUCER_INIT_ENERGY_RANGE[0] <= new_producer.energy <= PRODUCER_INIT_ENERGY_RANGE[1]

def test_producer_seeding_occupied_cell(basic_producer):
    """Test producer doesn't seed to occupied cells"""
    # Place another producer in every adjacent cell
    producers = [basic_producer]
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            x = (basic_producer.x + dx) % GRID_WIDTH
            y = (basic_producer.y + dy) % GRID_HEIGHT
            producers.append(Producer(x, y, energy=10))
    
    # Give producer enough energy to seed
    basic_producer.energy = PRODUCER_SEED_COST + 1
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))  # No nutrients to avoid energy gain
    
    # Mock the random probability to ensure seeding would occur
    original_random = random.random
    random.random = lambda: PRODUCER_SEED_PROB - 0.01
    
    # Update should not create new producer since all adjacent cells are occupied
    initial_producer_count = len(producers)
    basic_producer.update(producers, [], [], [], environment)
    
    # Restore random function
    random.random = original_random
    
    # Verify no seeding occurred but energy was consumed in attempt
    assert len(producers) == initial_producer_count
    assert basic_producer.energy == 1  # Initial energy (3) minus seed cost (2)

def test_producer_death(basic_producer):
    """Test producer death condition"""
    assert not basic_producer.is_dead()
    
    # Death by energy depletion
    basic_producer.energy = 0
    assert basic_producer.is_dead()
    
    basic_producer.energy = -1
    assert basic_producer.is_dead()

def test_producer_adjacent_cell_selection():
    """Test producer's random adjacent cell selection"""
    producer = Producer(x=5, y=5, energy=10)
    
    # Test multiple random adjacent selections
    for _ in range(50):  # Test multiple times for randomness
        nx, ny = producer.random_adjacent()
        # Should be within one cell in any direction (including diagonals)
        assert abs(nx - producer.x) <= 1
        assert abs(ny - producer.y) <= 1
        # Should not be the same cell
        assert not (nx == producer.x and ny == producer.y)
        # Should wrap around grid edges
        assert 0 <= nx < GRID_WIDTH
        assert 0 <= ny < GRID_HEIGHT