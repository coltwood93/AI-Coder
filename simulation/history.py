"""
State history management for the A-Life simulation.
"""

import copy
import numpy as np

class SimulationState:
    """
    Class to store a complete state of the simulation, 
    including all organisms and environment.
    """
    def __init__(self, t, producers, herbivores, carnivores, omnivores, environment):
        self.t = t
        self.producers = copy.deepcopy(producers)
        self.herbivores = copy.deepcopy(herbivores)
        self.carnivores = copy.deepcopy(carnivores)
        self.omnivores = copy.deepcopy(omnivores)
        self.environment = np.copy(environment)

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
