import pytest
import numpy as np
from organisms.carnivore import Carnivore
from organisms.herbivore import Herbivore
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, MAX_LIFESPAN_CARNIVORE, EAT_GAIN_CARNIVORE,
    DISEASE_ENERGY_DRAIN_MULTIPLIER, CARNIVORE_REPRO_THRESHOLD,
    REPRODUCTION_COOLDOWN, BASE_LIFE_COST
)

@pytest.fixture
def basic_carnivore():
    """Create a basic carnivore for testing"""
    return Carnivore(x=5, y=5, energy=100, genes=[2.0, 1.0, 3.0], generation=0)

@pytest.fixture
def basic_herbivore():
    """Create a basic herbivore for testing"""
    return Herbivore(x=6, y=6, energy=50)

def test_carnivore_initialization(basic_carnivore):
    """Test carnivore initialization"""
    assert basic_carnivore.x == 5
    assert basic_carnivore.y == 5
    assert basic_carnivore.energy == 100
    assert basic_carnivore.generation == 0
    assert basic_carnivore.age == 0
    assert basic_carnivore.max_lifespan == MAX_LIFESPAN_CARNIVORE
    assert basic_carnivore.repro_cooldown_timer == 0
    assert basic_carnivore.disease_timer == 0
    assert basic_carnivore.speed == 2
    assert basic_carnivore.metabolism == 1.0
    assert basic_carnivore.vision == 3
    assert len(basic_carnivore.recent_cells) == 1
    assert basic_carnivore.recent_cells[0] == (5, 5)

def test_carnivore_movement(basic_carnivore):
    """Test carnivore movement"""
    original_x = basic_carnivore.x
    original_y = basic_carnivore.y
    
    # Test move_random
    basic_carnivore.move_random([])
    assert (basic_carnivore.x != original_x or basic_carnivore.y != original_y)
    assert 0 <= basic_carnivore.x < GRID_WIDTH
    assert 0 <= basic_carnivore.y < GRID_HEIGHT

    # Test move_towards
    basic_carnivore.x = 5
    basic_carnivore.y = 5
    basic_carnivore.move_towards((1, 1), [])
    assert basic_carnivore.x == 6 or basic_carnivore.y == 6

def test_carnivore_eating(basic_carnivore, basic_herbivore):
    """Test carnivore eating behavior"""
    # Place carnivore and herbivore in same location
    basic_carnivore.x = basic_herbivore.x
    basic_carnivore.y = basic_herbivore.y
    
    herbivores = [basic_herbivore]
    initial_energy = basic_carnivore.energy
    
    # Test eating
    assert basic_carnivore.check_and_eat_herbivore(herbivores)
    assert basic_carnivore.energy == initial_energy + EAT_GAIN_CARNIVORE
    assert len(herbivores) == 0

def test_carnivore_disease(basic_carnivore):
    """Test carnivore disease mechanics"""
    assert not basic_carnivore.is_infected()
    
    # Infect carnivore
    basic_carnivore.disease_timer = 5
    assert basic_carnivore.is_infected()
    
    # Test energy cost is higher when infected
    initial_energy = basic_carnivore.energy
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_carnivore.update([], [], [], [], environment)
    
    expected_cost = BASE_LIFE_COST * DISEASE_ENERGY_DRAIN_MULTIPLIER
    assert basic_carnivore.energy < initial_energy - expected_cost
    assert basic_carnivore.disease_timer == 4

def test_carnivore_reproduction(basic_carnivore):
    """Test carnivore reproduction"""
    carnivores = [basic_carnivore]
    basic_carnivore.energy = CARNIVORE_REPRO_THRESHOLD
    
    # Test reproduction
    basic_carnivore.reproduce(carnivores)
    assert len(carnivores) == 2
    assert carnivores[1].generation == basic_carnivore.generation + 1
    assert carnivores[1].energy == CARNIVORE_REPRO_THRESHOLD // 2
    assert basic_carnivore.repro_cooldown_timer == REPRODUCTION_COOLDOWN
    
def test_carnivore_death(basic_carnivore):
    """Test carnivore death conditions"""
    assert not basic_carnivore.is_dead()
    
    # Death by energy depletion
    basic_carnivore.energy = 0
    assert basic_carnivore.is_dead()
    
    # Death by old age
    basic_carnivore.energy = 100
    basic_carnivore.age = MAX_LIFESPAN_CARNIVORE + 1
    environment = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    basic_carnivore.update([], [], [], [], environment)
    assert basic_carnivore.is_dead()

def test_carnivore_vision(basic_carnivore, basic_herbivore):
    """Test carnivore vision and prey detection"""
    herbivores = [basic_herbivore]
    
    # Test herbivore within vision range
    basic_carnivore.x = 5
    basic_carnivore.y = 5
    basic_herbivore.x = 6  # Changed from 7 to be within vision range
    basic_herbivore.y = 7
    direction = basic_carnivore.find_nearest_herbivore(herbivores)
    assert direction is not None
    assert direction == (1, 2)  # Changed expected result to match new position
    
    # Test herbivore outside vision range
    basic_herbivore.x = 10
    basic_herbivore.y = 10
    direction = basic_carnivore.find_nearest_herbivore(herbivores)
    assert direction is None