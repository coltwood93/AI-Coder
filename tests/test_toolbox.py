import pytest
import random
from deap import creator
from utils.toolbox import toolbox, create_random_genome, custom_mutate
from utils.constants import (
    SPEED_RANGE, METABOLISM_RANGE, VISION_RANGE, MUTATION_RATE
)

def test_create_random_genome():
    """Test random genome creation with proper ranges"""
    for _ in range(100):  # Test multiple times for randomness
        genome = create_random_genome()
        
        # Check correct number of genes
        assert len(genome) == 3
        
        # Check each gene is within its range
        speed, metabolism, vision = genome
        assert SPEED_RANGE[0] <= speed <= SPEED_RANGE[1]
        assert METABOLISM_RANGE[0] <= metabolism <= METABOLISM_RANGE[1]
        assert VISION_RANGE[0] <= vision <= VISION_RANGE[1]
        
        # Check types
        assert isinstance(speed, int)  # Speed should be integer
        assert isinstance(metabolism, float)  # Metabolism should be float
        assert isinstance(vision, int)  # Vision should be integer

def test_individual_creation():
    """Test individual creation through toolbox"""
    ind = toolbox.individual()
    
    # Check it's the right type
    assert isinstance(ind, creator.Individual)
    assert hasattr(ind, 'fitness')
    
    # Check genes are within ranges
    assert SPEED_RANGE[0] <= ind[0] <= SPEED_RANGE[1]
    assert METABOLISM_RANGE[0] <= ind[1] <= METABOLISM_RANGE[1]
    assert VISION_RANGE[0] <= ind[2] <= VISION_RANGE[1]

def test_mutation_chance():
    """Test mutation probability is correct"""
    # Use fixed seed for reproducibility
    random.seed(42)
    
    # Create many individuals and count mutations
    n_tests = 1000
    mutation_counts = [0, 0, 0]  # Count for each gene
    
    for _ in range(n_tests):
        ind = creator.Individual([2, 1.0, 2])  # Middle values
        mutated, = custom_mutate(ind)
        
        # Count when mutation occurred (value changed)
        mutation_counts[0] += (mutated[0] != 2)
        mutation_counts[1] += (mutated[1] != 1.0)
        mutation_counts[2] += (mutated[2] != 2)
    
    # Check mutation rates are roughly correct (within 30% of expected)
    expected = n_tests * MUTATION_RATE
    for count in mutation_counts:
        assert abs(count - expected) < expected * 0.3, \
            f"Mutation rate too far from expected. Got {count/n_tests:.2f}, expected {MUTATION_RATE:.2f}"

def test_mutation_clamping():
    """Test mutation stays within allowed ranges"""
    random.seed(42)
    
    # Test extreme values
    min_ind = creator.Individual([
        SPEED_RANGE[0],
        METABOLISM_RANGE[0],
        VISION_RANGE[0]
    ])
    max_ind = creator.Individual([
        SPEED_RANGE[1],
        METABOLISM_RANGE[1],
        VISION_RANGE[1]
    ])
    
    # Test many mutations from min and max
    for _ in range(100):
        # Test from minimum
        mutated_min, = custom_mutate(min_ind[:])  # Copy to not modify original
        assert SPEED_RANGE[0] <= mutated_min[0] <= SPEED_RANGE[1]
        assert METABOLISM_RANGE[0] <= mutated_min[1] <= METABOLISM_RANGE[1]
        assert VISION_RANGE[0] <= mutated_min[2] <= VISION_RANGE[1]
        
        # Test from maximum
        mutated_max, = custom_mutate(max_ind[:])  # Copy to not modify original
        assert SPEED_RANGE[0] <= mutated_max[0] <= SPEED_RANGE[1]
        assert METABOLISM_RANGE[0] <= mutated_max[1] <= METABOLISM_RANGE[1]
        assert VISION_RANGE[0] <= mutated_max[2] <= VISION_RANGE[1]

def test_mutation_changes():
    """Test that mutations can both increase and decrease values"""
    random.seed(42)
    
    # Middle-range individual
    original = creator.Individual([
        (SPEED_RANGE[0] + SPEED_RANGE[1]) // 2,
        (METABOLISM_RANGE[0] + METABOLISM_RANGE[1]) / 2,
        (VISION_RANGE[0] + VISION_RANGE[1]) // 2
    ])
    
    increases = [0, 0, 0]
    decreases = [0, 0, 0]
    
    # Test many mutations
    for _ in range(1000):
        mutated, = custom_mutate(original[:])  # Copy to not modify original
        
        # Count increases and decreases
        for i in range(3):
            if mutated[i] > original[i]:
                increases[i] += 1
            elif mutated[i] < original[i]:
                decreases[i] += 1
    
    # Should see both increases and decreases for each gene
    for inc, dec in zip(increases, decreases):
        assert inc > 0, "Mutation never increased value"
        assert dec > 0, "Mutation never decreased value"
        # Roughly equal number of increases and decreases
        ratio = inc / (inc + dec)
        assert 0.4 <= ratio <= 0.6, "Mutations are biased"