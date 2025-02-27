import pytest
import numpy as np
from alife import (
    current_season, random_border_cell, spawn_random_organism_on_border,
    disease_outbreak, update_environment, SimulationState, calc_traits_avg,
    GRID_WIDTH, GRID_HEIGHT, SEASON_LENGTH, DISEASE_DURATION,
    INITIAL_NUTRIENT_LEVEL
)
from organisms.producer import Producer
from organisms.herbivore import Herbivore
from organisms.carnivore import Carnivore
from organisms.omnivore import Omnivore

@pytest.fixture
def environment():
    """Create a test environment grid"""
    return np.full((GRID_WIDTH, GRID_HEIGHT), INITIAL_NUTRIENT_LEVEL)

@pytest.fixture
def basic_organisms():
    """Create a basic set of test organisms"""
    producers = [Producer(1, 1, 100)]
    herbivores = [Herbivore(2, 2, 100)]
    carnivores = [Carnivore(3, 3, 100)]
    omnivores = [Omnivore(4, 4, 100)]
    return producers, herbivores, carnivores, omnivores

def test_current_season():
    """Test season calculation"""
    assert current_season(0) == "WINTER"
    assert current_season(SEASON_LENGTH - 1) == "WINTER"
    assert current_season(SEASON_LENGTH) == "SUMMER"
    assert current_season(SEASON_LENGTH * 2 - 1) == "SUMMER"
    assert current_season(SEASON_LENGTH * 2) == "WINTER"

def test_random_border_cell():
    """Test border cell generation"""
    for _ in range(100):  # Test multiple times due to randomness
        x, y = random_border_cell()
        # Check if cell is actually on the border
        assert (x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1)
        # Check if coordinates are within bounds
        assert 0 <= x < GRID_WIDTH
        assert 0 <= y < GRID_HEIGHT

def test_spawn_random_organism_on_border():
    """Test organism spawning on border"""
    # Start with empty lists
    producers = []
    herbivores = []
    carnivores = []
    omnivores = []
    
    # Spawn a new organism
    spawn_random_organism_on_border(
        producers, herbivores, carnivores, omnivores, "SUMMER"
    )
    
    # Verify that exactly one organism was added
    total_organisms = len(producers) + len(herbivores) + len(carnivores) + len(omnivores)
    assert total_organisms == 1
    
    # Find which list has the organism
    organisms_list = producers if producers else (
        herbivores if herbivores else (
            carnivores if carnivores else omnivores
        )
    )
    
    # Verify the organism is on the border
    org = organisms_list[0]
    assert (org.x == 0 or org.x == GRID_WIDTH - 1 or 
            org.y == 0 or org.y == GRID_HEIGHT - 1)

def test_disease_outbreak(basic_organisms):
    """Test disease system"""
    _, herbivores, carnivores, omnivores = basic_organisms
    
    # Initial state - no diseases
    for animal in herbivores + carnivores + omnivores:
        assert not hasattr(animal, 'disease_timer') or animal.disease_timer == 0
    
    # Trigger disease outbreak
    disease_outbreak(herbivores, carnivores, omnivores)
    
    # Check that some animals are infected
    infected = [animal for animal in herbivores + carnivores + omnivores 
               if hasattr(animal, 'disease_timer') and animal.disease_timer == DISEASE_DURATION]
    assert len(infected) > 0
    assert len(infected) <= 5  # Max number of infections per outbreak

def test_update_environment(environment):
    """Test environment updates"""
    initial_env = environment.copy()
    
    # Test nutrient decay
    updated_env = update_environment(environment)
    assert np.all(updated_env <= initial_env)  # Values should decrease or stay same
    assert np.all(updated_env >= 0)  # No negative values
    
    # Test nutrient diffusion
    high_nutrient_env = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    high_nutrient_env[0, 0] = 1.0  # Set one cell to high nutrient
    
    diffused_env = update_environment(high_nutrient_env)
    # Check if neighbors received some nutrients
    assert diffused_env[0, 1] > 0
    assert diffused_env[1, 0] > 0

def test_simulation_state(environment, basic_organisms):
    """Test simulation state management"""
    producers, herbivores, carnivores, omnivores = basic_organisms
    
    # Create state
    state = SimulationState(0, producers, herbivores, carnivores, omnivores, environment)
    
    # Test that state contains correct data
    assert state.t == 0
    assert len(state.producers) == len(producers)
    assert len(state.herbivores) == len(herbivores)
    assert len(state.carnivores) == len(carnivores)
    assert len(state.omnivores) == len(omnivores)
    assert np.array_equal(state.environment, environment)

def test_calc_traits_avg():
    """Test trait averaging calculation"""
    # Create herbivores with known trait values
    # genes array contains [speed, metabolism, vision]
    herbivore1 = Herbivore(0, 0, 100, genes=[2.0, 0.5, 3.0], generation=1)
    herbivore2 = Herbivore(0, 0, 100, genes=[2.0, 0.5, 3.0], generation=1)
    herbivores = [herbivore1, herbivore2]
    
    speed, gen, met, vis = calc_traits_avg(herbivores)
    assert speed == 2.0
    assert gen == 1.0
    assert met == 0.5
    assert vis == 3.0
    
    # Test empty list
    speed, gen, met, vis = calc_traits_avg([])
    assert speed == 0
    assert gen == 0
    assert met == 0
    assert vis == 0