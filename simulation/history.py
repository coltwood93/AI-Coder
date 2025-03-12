"""
Manages the history of simulation states for replay and analysis.
"""

import numpy as np
import copy

class SimulationState:
    """
    Represents a snapshot of the simulation state at a point in time.
    """
    def __init__(self, t, producers, herbivores, carnivores, omnivores, environment):
        """
        Initialize a simulation state.
        
        Args:
            t: Current time step
            producers: List of producer organisms
            herbivores: List of herbivore organisms
            carnivores: List of carnivore organisms 
            omnivores: List of omnivore organisms
            environment: Nutrient grid (as 2D numpy array)
        """
        self.t = t
        # Make deep copies to prevent modification
        self.producers = copy.deepcopy(producers) if producers else []
        self.herbivores = copy.deepcopy(herbivores) if herbivores else []
        self.carnivores = copy.deepcopy(carnivores) if carnivores else []
        self.omnivores = copy.deepcopy(omnivores) if omnivores else []
        self.environment = environment.copy() if environment is not None else None
    
    def get_organism_counts(self):
        """Return a dictionary with counts of each organism type."""
        return {
            "producers": len(self.producers),
            "herbivores": len(self.herbivores),
            "carnivores": len(self.carnivores),
            "omnivores": len(self.omnivores)
        }

def store_state(history, t, producers, herbivores, carnivores, omnivores, environment):
    """
    Create a simulation state and append it to the history.
    """
    st = SimulationState(t, producers, herbivores, carnivores, omnivores, environment)
    history.append(st)

def load_state_into_sim(state, producers, herbivores, carnivores, omnivores, environment):
    """
    Load the given state back into the simulation.
    This modifies the given data structures to match the stored state.
    """
    producers.clear()
    herbivores.clear()
    carnivores.clear()
    omnivores.clear()
    producers.extend(copy.deepcopy(state.producers))
    herbivores.extend(copy.deepcopy(state.herbivores))
    carnivores.extend(copy.deepcopy(state.carnivores))
    omnivores.extend(copy.deepcopy(state.omnivores))
    np.copyto(environment, state.environment)
