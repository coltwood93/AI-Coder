"""
Configuration manager for the A-Life simulation.
Handles saving and loading of user settings.
"""

import json
import os
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, 
    INITIAL_PRODUCERS, INITIAL_HERBIVORES, INITIAL_CARNIVORES, INITIAL_OMNIVORES,
    SIMULATION_SPEED, FPS
)

class ConfigManager:
    """Manages user configuration settings."""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {
            "grid": {
                "width": GRID_WIDTH,
                "height": GRID_HEIGHT
            },
            "initial_counts": {
                "producers": INITIAL_PRODUCERS,
                "herbivores": INITIAL_HERBIVORES,
                "carnivores": INITIAL_CARNIVORES,
                "omnivores": INITIAL_OMNIVORES
            },
            "simulation": {
                "speed": SIMULATION_SPEED,
                "fps": FPS
            }
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update config with loaded values
                    self._update_dict_recursive(self.config, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def _update_dict_recursive(self, target, source):
        """Update target dictionary with values from source, recursively."""
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._update_dict_recursive(target[key], value)
                else:
                    target[key] = value
    
    def get_grid_width(self):
        """Get the configured grid width."""
        return self.config["grid"]["width"]
    
    def get_grid_height(self):
        """Get the configured grid height."""
        return self.config["grid"]["height"]
    
    def get_initial_count(self, organism_type):
        """Get the initial count for a specific organism type."""
        return self.config["initial_counts"].get(organism_type, 0)
    
    def get_simulation_speed(self):
        """Get the simulation speed setting."""
        return self.config["simulation"]["speed"]
    
    def get_fps(self):
        """Get the frames per second setting."""
        return self.config["simulation"]["fps"]
    
    def set_grid_size(self, width, height):
        """Set the grid dimensions."""
        self.config["grid"]["width"] = max(10, min(100, width))  # Limit between 10 and 100
        self.config["grid"]["height"] = max(10, min(100, height))
        self.save_config()
    
    def set_initial_count(self, organism_type, count):
        """Set the initial count for a specific organism type."""
        if organism_type in self.config["initial_counts"]:
            self.config["initial_counts"][organism_type] = max(0, min(100, count))
            self.save_config()
    
    def set_simulation_speed(self, speed):
        """Set the simulation speed."""
        self.config["simulation"]["speed"] = max(0.1, min(2.0, speed))
        self.save_config()
    
    def set_fps(self, fps):
        """Set the frames per second."""
        self.config["simulation"]["fps"] = max(5, min(60, fps))
        self.save_config()
