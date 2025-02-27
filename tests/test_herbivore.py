import pytest
import numpy as np
from organisms.herbivore import Herbivore
from organisms.producer import Producer
from organisms.carnivore import Carnivore
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, MAX_LIFESPAN_HERBIVORE, EAT_GAIN_HERBIVORE,
    DISEASE_ENERGY_DRAIN_MULTIPLIER, HERBIVORE_REPRO_THRESHOLD,
    REPRODUCTION_COOLDOWN, BASE_LIFE_COST, MOVE_COST_FACTOR,
    CRITICAL_ENERGY, DISCOVERY_BONUS
)

@pytest.fixture
def basic_herbivore():
    """Create a basic herbivore for testing"""
    return Herbivore(x=5, y=5, energy=100, genes=[2.0, 1.0, 3.0], generation=0)

@pytest.fixture
def basic_producer():
    """Create a basic producer for testing"""
    return Producer(x=6, y=6, energy=50)

@pytest.fixture
def basic_predator():
    """Create a basic carnivore predator for testing"""
    return Carnivore(x=7, y=7, energy=100)

def test_herbivore_initialization(basic_herbivore):
    """Test herbivore initialization"""
    assert basic_herbivore.x == 5
    assert basic_herbivore.y == 5
    assert basic_herbivore.energy == 100
    assert basic_herbivore.generation == 0
    assert basic_herbivore.age == 0
    assert basic_herbivore.max_lifespan == MAX_LIFESPAN_HERBIVORE
    assert basic_herbivore.repro_cooldown_timer == 0
    assert basic_herbivore.disease_timer == 0
    assert basic_herbivore.speed == 2
    assert basic_herbivore.metabolism == 1.0
    assert basic_herbivore.vision == 3
    assert len(basic_herbivore.recent_cells) == 1
    assert basic_herbivore.recent_cells[0] == (5, 5)

def test_herbivore_movement(basic_herbivore):
    """Test herbivore movement"""
    original_x = basic_herbivore.x
    original_y = basic_herbivore.y
    
    # Test move_random
    basic_herbivore.move_random([])
    assert (basic_herbivore.x != original_x or basic_herbivore.y != original_y)
    assert 0 <= basic_herbivore.x < GRID_WIDTH
    assert 0 <= basic_herbivore.y < GRID_HEIGHT

    # Test move_towards
    basic_herbivore.x = 5
    basic_herbivore.y = 5
    basic_herbivore.move_towards((1, 1), [])
    assert basic_herbivore.x == 6 or basic_herbivore.y == 6

def test_herbivore_eating(basic_herbivore, basic_producer):
    """Test herbivore eating behavior"""
    # Place herbivore and producer in same location
    basic_herbivore.x = basic_producer.x
    basic_herbivore.y = basic_producer.y
    
    producers = [basic_producer]
    initial_energy = basic_herbivore.energy
    
    # Test eating
    assert basic_herbivore.check_and_eat_producer(producers)
    assert basic_herbivore.energy == initial_energy + EAT_GAIN_HERBIVORE
    assert len(producers) == 0

def test_herbivore_disease(basic_herbivore):
    """Test herbivore disease mechanics"""
    assert not basic_herbivore.is_infected()
    
    # Infect herbivore
    basic_herbivore.disease_timer = 5
    assert basic_herbivore.is_infected()
    
    # Test energy cost is higher when infected
    initial_energy = basic_herbivore.energy
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_herbivore.update([], [], [], [], environment)
    
    expected_cost = BASE_LIFE_COST * DISEASE_ENERGY_DRAIN_MULTIPLIER
    assert basic_herbivore.energy < initial_energy - expected_cost
    assert basic_herbivore.disease_timer == 4

def test_herbivore_reproduction(basic_herbivore):
    """Test herbivore reproduction"""
    herbivores = [basic_herbivore]
    basic_herbivore.energy = HERBIVORE_REPRO_THRESHOLD
    
    # Test reproduction
    basic_herbivore.reproduce(herbivores)
    assert len(herbivores) == 2
    assert herbivores[1].generation == basic_herbivore.generation + 1
    assert herbivores[1].energy == HERBIVORE_REPRO_THRESHOLD // 2
    assert basic_herbivore.repro_cooldown_timer == REPRODUCTION_COOLDOWN

def test_herbivore_death(basic_herbivore):
    """Test herbivore death conditions"""
    assert not basic_herbivore.is_dead()
    
    # Death by energy depletion
    basic_herbivore.energy = 0
    assert basic_herbivore.is_dead()
    
    # Death by old age
    basic_herbivore.energy = 100
    basic_herbivore.age = MAX_LIFESPAN_HERBIVORE + 1
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_herbivore.update([], [], [], [], environment)
    assert basic_herbivore.is_dead()

def test_herbivore_vision_and_detection(basic_herbivore, basic_producer, basic_predator):
    """Test herbivore vision and detection of food/threats"""
    producers = [basic_producer]
    carnivores = [basic_predator]
    
    # Test producer within vision range
    basic_herbivore.x = 5
    basic_herbivore.y = 5
    basic_producer.x = 6
    basic_producer.y = 7
    direction = basic_herbivore.find_nearest_producer(producers)
    assert direction is not None
    assert direction == (1, 2)
    
    # Test predator detection and running away
    basic_predator.x = 6
    basic_predator.y = 7
    pred_dir = basic_herbivore.find_nearest_predator(carnivores, [])
    assert pred_dir is not None
    assert pred_dir == (1, 2)
    
    # Test running away behavior
    initial_x, initial_y = basic_herbivore.x, basic_herbivore.y
    basic_herbivore.run_away(pred_dir, [])
    # Should move in opposite direction of predator
    assert (basic_herbivore.x != initial_x or basic_herbivore.y != initial_y)

def test_herbivore_critical_behavior(basic_herbivore, basic_producer):
    """Test herbivore behavior when energy is critical"""
    basic_herbivore.energy = CRITICAL_ENERGY - 1
    producers = [basic_producer]
    initial_energy = basic_herbivore.energy
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    
    # Should move randomly when no food in sight and energy is critical
    basic_producer.x = 20  # Put producer out of vision range
    basic_producer.y = 20
    basic_herbivore.update(producers, [], [], [], environment)
    
    # Should have moved and lost energy from movement
    assert basic_herbivore.energy < initial_energy
    
    # Test discovery bonus
    if DISCOVERY_BONUS > 0:
        # Clear recent cells to ensure discovery bonus
        basic_herbivore.recent_cells = []
        old_energy = basic_herbivore.energy
        start_x, start_y = basic_herbivore.x, basic_herbivore.y
        
        # Just check that update adds current position to recent cells
        basic_herbivore.update(producers, [], [], [], environment)
        assert len(basic_herbivore.recent_cells) > 0
        # The cell should be either the starting position or where it moved to
        current_pos = (basic_herbivore.x, basic_herbivore.y)
        assert current_pos in basic_herbivore.recent_cells or (start_x, start_y) in basic_herbivore.recent_cells
        
        # Calculate expected energy after update:
        # - BASE_LIFE_COST is always applied
        # - Movement costs are applied for critical energy behavior
        # - DISCOVERY_BONUS is added for visiting new cell
        movement_cost = MOVE_COST_FACTOR * basic_herbivore.metabolism
        expected_energy = old_energy - BASE_LIFE_COST - (movement_cost * basic_herbivore.speed) + DISCOVERY_BONUS
        assert abs(expected_energy - basic_herbivore.energy) < 0.001  # Allow for floating point imprecision