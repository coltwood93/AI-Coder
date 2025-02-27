import pytest
import numpy as np
import random
from organisms.omnivore import Omnivore
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, MAX_LIFESPAN_OMNIVORE, EAT_GAIN_OMNIVORE_PLANT,
    EAT_GAIN_OMNIVORE_ANIMAL, DISEASE_ENERGY_DRAIN_MULTIPLIER, OMNIVORE_REPRO_THRESHOLD,
    REPRODUCTION_COOLDOWN, BASE_LIFE_COST, MOVE_COST_FACTOR,
    CRITICAL_ENERGY, DISCOVERY_BONUS, EAT_GAIN_CARNIVORE
)

@pytest.fixture
def basic_omnivore():
    """Create a basic omnivore for testing"""
    return Omnivore(x=5, y=5, energy=100, genes=[2.0, 1.0, 3.0], generation=0)

@pytest.fixture
def basic_producer():
    """Create a basic producer for testing"""
    return Producer(x=6, y=6, energy=50)

@pytest.fixture
def basic_herbivore():
    """Create a basic herbivore for testing"""
    return Herbivore(x=6, y=6, energy=50)

@pytest.fixture
def basic_carnivore():
    """Create a basic carnivore for testing"""
    return Carnivore(x=7, y=7, energy=100)

def test_omnivore_initialization(basic_omnivore):
    """Test omnivore initialization"""
    assert basic_omnivore.x == 5
    assert basic_omnivore.y == 5
    assert basic_omnivore.energy == 100
    assert basic_omnivore.generation == 0
    assert basic_omnivore.age == 0
    assert basic_omnivore.max_lifespan == MAX_LIFESPAN_OMNIVORE
    assert basic_omnivore.repro_cooldown_timer == 0
    assert basic_omnivore.disease_timer == 0
    assert basic_omnivore.speed == 2
    assert basic_omnivore.metabolism == 1.0
    assert basic_omnivore.vision == 3
    assert len(basic_omnivore.recent_cells) == 1
    assert basic_omnivore.recent_cells[0] == (5, 5)

def test_omnivore_movement(basic_omnivore):
    """Test omnivore movement"""
    original_x = basic_omnivore.x
    original_y = basic_omnivore.y
    
    # Test move_random
    basic_omnivore.move_random([])
    assert (basic_omnivore.x != original_x or basic_omnivore.y != original_y)
    assert 0 <= basic_omnivore.x < GRID_WIDTH
    assert 0 <= basic_omnivore.y < GRID_HEIGHT

    # Test move_towards
    basic_omnivore.x = 5
    basic_omnivore.y = 5
    basic_omnivore.move_towards((1, 1), [])
    assert basic_omnivore.x == 6 or basic_omnivore.y == 6

def test_omnivore_eating_producer(basic_omnivore, basic_producer):
    """Test omnivore eating plant behavior"""
    # Place omnivore and producer in same location
    basic_omnivore.x = basic_producer.x
    basic_omnivore.y = basic_producer.y
    
    producers = [basic_producer]
    initial_energy = basic_omnivore.energy
    
    # Test eating producer
    assert basic_omnivore.check_and_eat_plant(producers)
    assert basic_omnivore.energy == initial_energy + EAT_GAIN_OMNIVORE_PLANT
    assert len(producers) == 0

def test_omnivore_eating_herbivore(basic_omnivore, basic_herbivore):
    """Test omnivore eating herbivore behavior"""
    # Place omnivore and herbivore in same location
    basic_omnivore.x = basic_herbivore.x
    basic_omnivore.y = basic_herbivore.y
    
    herbivores = [basic_herbivore]
    initial_energy = basic_omnivore.energy
    
    # Test eating herbivore
    assert basic_omnivore.check_and_eat_herb(herbivores)
    assert basic_omnivore.energy == initial_energy + EAT_GAIN_OMNIVORE_ANIMAL
    assert len(herbivores) == 0

def test_omnivore_disease(basic_omnivore):
    """Test omnivore disease mechanics"""
    assert not basic_omnivore.is_infected()
    
    # Infect omnivore
    basic_omnivore.disease_timer = 5
    assert basic_omnivore.is_infected()
    
    # Test energy cost is higher when infected
    initial_energy = basic_omnivore.energy
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_omnivore.update([], [], [], [], environment)
    
    expected_cost = BASE_LIFE_COST * DISEASE_ENERGY_DRAIN_MULTIPLIER
    assert basic_omnivore.energy < initial_energy - expected_cost
    assert basic_omnivore.disease_timer == 4

def test_omnivore_reproduction(basic_omnivore):
    """Test omnivore reproduction"""
    omnivores = [basic_omnivore]
    basic_omnivore.energy = OMNIVORE_REPRO_THRESHOLD
    
    # Test reproduction
    basic_omnivore.reproduce(omnivores)
    assert len(omnivores) == 2
    assert omnivores[1].generation == basic_omnivore.generation + 1
    assert omnivores[1].energy == OMNIVORE_REPRO_THRESHOLD // 2
    assert basic_omnivore.repro_cooldown_timer == REPRODUCTION_COOLDOWN

def test_omnivore_death(basic_omnivore):
    """Test omnivore death conditions"""
    assert not basic_omnivore.is_dead()
    
    # Death by energy depletion
    basic_omnivore.energy = 0
    assert basic_omnivore.is_dead()
    
    # Death by old age
    basic_omnivore.energy = 100
    basic_omnivore.age = MAX_LIFESPAN_OMNIVORE + 1
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_omnivore.update([], [], [], [], environment)
    assert basic_omnivore.is_dead()

def test_omnivore_vision_and_detection(basic_omnivore, basic_producer, basic_herbivore):
    """Test omnivore vision and detection of food"""
    producers = [basic_producer]
    herbivores = [basic_herbivore]
    
    # Test producer within vision range
    basic_omnivore.x = 5
    basic_omnivore.y = 5
    basic_producer.x = 6
    basic_producer.y = 7
    direction, distance = basic_omnivore.find_nearest_producer(producers)
    assert direction is not None
    assert direction == (1, 2)
    assert distance == 3
    
    # Test herbivore within vision range
    basic_herbivore.x = 6
    basic_herbivore.y = 7
    direction, distance = basic_omnivore.find_nearest_herbivore(herbivores)
    assert direction is not None
    assert direction == (1, 2)
    assert distance == 3

def test_omnivore_carnivore_encounter(basic_omnivore, basic_carnivore):
    """Test omnivore-carnivore encounter mechanics"""
    # Place omnivore and carnivore in same location
    basic_omnivore.x = basic_carnivore.x
    basic_carnivore.y = basic_carnivore.y
    carnivores = [basic_carnivore]
    
    # Test with fixed random seed for predictable outcomes
    random.seed(42)  # Choose seed that gives each outcome
    
    # Test carnivore victory (60% chance)
    initial_carnivore_energy = basic_carnivore.energy
    basic_omnivore.check_carnivore_encounter(carnivores)
    if basic_omnivore.is_dead():
        assert basic_carnivore.energy == initial_carnivore_energy + EAT_GAIN_CARNIVORE
    
    # Reset for next test
    basic_omnivore.energy = 100
    basic_carnivore.energy = initial_carnivore_energy
    
    # Test omnivore victory (15% chance) - need to try multiple times due to randomness
    max_attempts = 100
    for _ in range(max_attempts):
        if len(carnivores) == 0:  # Omnivore won
            assert basic_omnivore.energy == 100 + EAT_GAIN_OMNIVORE_ANIMAL
            break
        basic_omnivore.check_carnivore_encounter(carnivores)

def test_omnivore_target_selection(basic_omnivore, basic_producer, basic_herbivore):
    """Test omnivore choosing between producer and herbivore targets"""
    producers = [basic_producer]
    herbivores = [basic_herbivore]
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    
    # Place producer closer than herbivore
    basic_omnivore.x = 5
    basic_omnivore.y = 5
    basic_producer.x = 6  # Distance 2
    basic_producer.y = 6
    basic_herbivore.x = 7  # Distance 4
    basic_herbivore.y = 7
    
    # Should move towards and try to eat producer
    basic_omnivore.update(producers, herbivores, [], [], environment)
    assert len(producers) == 0 or (basic_omnivore.x, basic_omnivore.y) != (5, 5)
    
    # Reset positions, place herbivore closer
    basic_omnivore.x = 5
    basic_omnivore.y = 5
    basic_producer.x = 8  # Distance 6
    basic_producer.y = 8
    basic_herbivore.x = 6  # Distance 2
    basic_herbivore.y = 6
    
    # Should move towards and try to eat herbivore
    basic_omnivore.update(producers, herbivores, [], [], environment)
    assert len(herbivores) == 0 or (basic_omnivore.x, basic_omnivore.y) != (5, 5)