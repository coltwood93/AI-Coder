"""
HDF5 storage module for the A-Life simulation.
Provides efficient storage and retrieval of simulation states.
"""

import h5py
import numpy as np
import os

class HDF5Storage:
    def __init__(self, filename="simulation_data.hdf5"):
        self.filename = filename
        
        # Create the file if it doesn't exist
        if not os.path.exists(filename):
            try:
                with h5py.File(filename, 'w'):
                    pass  # Just create the file
            except Exception as e:
                print(f"Warning: Failed to create HDF5 file: {e}")
    
    def save_state(self, timestep, environment, **organisms_groups):
        """
        Save the simulation state for a specific timestep.
        
        Parameters:
        - timestep: The current simulation time step
        - environment: The nutrient environment grid
        - **organisms_groups: Dictionary of organism types and their lists
                            (e.g., producers=producer_list, herbivores=herbivore_list)
        """
        try:
            with h5py.File(self.filename, 'a') as f:
                # Create a group for this timestep if it doesn't exist
                timestep_str = f"timestep_{timestep}"
                if timestep_str in f:
                    del f[timestep_str]  # Replace if exists
                
                timestep_group = f.create_group(timestep_str)
                
                # Save environment
                timestep_group.create_dataset("environment", data=environment)
                
                # Save organisms
                for group_name, organisms in organisms_groups.items():
                    # Skip if empty
                    if not organisms:
                        continue
                        
                    # Create a group for this type
                    organism_group = timestep_group.create_group(group_name)
                    
                    # Get all attributes from the first organism to determine structure
                    if not hasattr(organisms[0], "__dict__"):
                        continue  # Skip if not proper objects
                    
                    sample_dict = organisms[0].__dict__.copy()
                    
                    # Create datasets for each attribute
                    for attr_name, attr_value in sample_dict.items():
                        # Skip complex objects we can't easily store
                        if isinstance(attr_value, (list, dict, set, tuple)) or callable(attr_value):
                            continue
                        
                        # Collect all values for this attribute
                        try:
                            values = [getattr(org, attr_name) for org in organisms]
                            organism_group.create_dataset(attr_name, data=values)
                        except (TypeError, ValueError) as e:
                            print(f"Couldn't save attribute {attr_name}: {e}")
                            continue
        except Exception as e:
            print(f"Error saving state to HDF5 file: {e}")
    
    def load_state(self, timestep=None):
        """
        Load the state data for a specific timestep.
        
        Returns a tuple of (environment, organism_groups) where organism_groups
        is a dictionary of organism types and their attribute arrays.
        """
        try:
            with h5py.File(self.filename, 'r') as f:
                timestep_str = f"timestep_{timestep}"
                
                if timestep_str not in f:
                    return None, {}
                    
                timestep_group = f[timestep_str]
                
                # Load environment
                environment = np.array(timestep_group["environment"])
                
                # Load organisms
                organism_groups = {}
                for group_name in timestep_group.keys():
                    if group_name == "environment":
                        continue
                        
                    organism_group = timestep_group[group_name]
                    attributes = {}
                    
                    for attr_name in organism_group.keys():
                        attributes[attr_name] = np.array(organism_group[attr_name])
                        
                    organism_groups[group_name] = attributes
                    
                return environment, organism_groups
        except Exception as e:
            print(f"Error loading state from HDF5 file: {e}")
            return None, {}

    def reset(self):
        """Reset the storage by creating a new empty file."""
        try:
            # Create the file, overwriting any existing file
            with h5py.File(self.filename, 'w'):
                pass  # Just create an empty file
            print(f"HDF5 storage reset: {self.filename}")
        except Exception as e:
            print(f"Error resetting HDF5 file: {e}")

    def create_empty_file(self):
        """Create an empty HDF5 file - compatibility method for tests."""
        self.reset()
