#!/usr/bin/env python3
"""
Main entry point for the A-Life application.
"""

import sys
import random
import csv
import pygame
import numpy as np

# Import constants needed for the main application
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, 
    STATS_PANEL_WIDTH, FPS, SIMULATION_SPEED, update_from_config
)

# Import app states
from utils.app_states import MAIN_MENU, OPTIONS_MENU, SIMULATION, PAUSE_MENU, STATS_VIEW

# Import simulation components
from simulation.environment import current_season
from simulation.stats import calc_traits_avg
from simulation.manager import SimulationManager

# Import UI components
from ui.renderer import SimulationRenderer
from ui.input_handler import InputHandler
from ui.options_menu import OptionsMenu
from ui.main_menu_options import MainMenuOptions
from utils.config_manager import ConfigManager

# Add a new constant for main menu–only options
MAIN_MENU_OPTIONS = "main_menu_options"

# Set random seed for reproducibility
random.seed()

###########################################
# APPLICATION CONTROLLER
###########################################
class SimulationApp:
    """Main application controller that ties everything together."""
    
    def __init__(self):
        # Initialize config manager first, so constants get updated
        self.config_manager = ConfigManager()
        update_from_config(self.config_manager)
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("A-Life: Seasons, Disease, Omnivores, Nutrient Environment")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.main_font = pygame.font.SysFont(None, 24)
        self.label_font = pygame.font.SysFont(None, 16)
        
        # Initialize options menu
        self.options_menu = OptionsMenu(self.config_manager, self.main_font)
        self.main_menu_options = MainMenuOptions(self.config_manager, self.main_font)
        
        # Setup CSV logging
        self.csvfile = open("results_interactive.csv", "w", newline="")
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow([
            "Timestep","Producers","Herbivores","Carnivores","Omnivores",
            "HavgSp","HavgGen","HavgMet","HavgVis",
            "CavgSp","CavgGen","CavgMet","CavgVis",
            "OavgSp","OavgGen","OavgMet","OavgVis"
        ])
        
        # Initialize simulation components
        self.simulation = SimulationManager(self.writer)
        self.renderer = SimulationRenderer(self.screen, self.main_font, self.label_font)
        self.input_handler = InputHandler(self.simulation)
        
        # Initial UI state
        self.current_state = MAIN_MENU
        self.from_main_menu = True
        self.has_simulation_started = False  # Track if simulation has been started
    
    def run(self):
        """Run the main application loop."""
        running = True
        
        while running:
            # Always get the latest settings directly from config_manager
            current_fps = self.config_manager.get_fps()
            current_speed = self.config_manager.get_simulation_speed()
            
            # Process events
            events = pygame.event.get()
            new_state, new_from_main_menu, continue_running = self.input_handler.handle_events(
                events, self.current_state, self.from_main_menu
            )
            
            # If current_state == MAIN_MENU_OPTIONS, let main_menu_options handle events
            if self.current_state == MAIN_MENU_OPTIONS:
                # Process escape key to return to main menu
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.current_state = MAIN_MENU
                        update_from_config(self.config_manager)
                        break
                
                # Process other inputs if we're still in options
                if self.current_state == MAIN_MENU_OPTIONS:
                    self.main_menu_options.handle_input(events)
                    # Check if we should return to main menu
                    if self.main_menu_options.should_return_to_menu():
                        self.current_state = MAIN_MENU
                        # Update simulation parameters from options
                        update_from_config(self.config_manager)
            
            # Update state if changed
            if new_state is not None:
                previous_state = self.current_state
                self.current_state = new_state
                
                # If coming back from options menu, apply updated settings
                if previous_state == OPTIONS_MENU and new_state != OPTIONS_MENU:
                    self._apply_updated_settings()
                    
            if new_from_main_menu is not None:
                self.from_main_menu = new_from_main_menu
            
            # Check if we should exit
            if not continue_running:
                running = False
                break
            
            # Handle mouse wheel scrolling for stats panel
            for event in events:
                if event.type == pygame.MOUSEWHEEL and self.current_state in (SIMULATION, PAUSE_MENU):
                    mouse_x, _ = pygame.mouse.get_pos()
                    if self.renderer.handle_scroll(event, mouse_x):
                        print(f"Scrolling stats panel: {self.renderer.stats_scroll_y}/{self.renderer.max_scroll_y}")
            
            # Update simulation if needed
            self._update_simulation(current_fps, current_speed)
            
            # Render the current state
            self._render_current_state()
            
            # Update the display and use the current fps setting
            pygame.display.flip()
            self.clock.tick(current_fps)
        
        # Cleanup resources
        self._cleanup()
    
    def _apply_updated_settings(self):
        """Apply updated simulation settings."""
        # Update constants from config
        update_from_config(self.config_manager)
        
        # Reset frame counter to apply new speed immediately
        self.frame_counter = 0
        
        # Update the clock to apply new FPS setting
        self.clock = pygame.time.Clock()
        
        print(f"Applied settings: Speed={self.config_manager.get_simulation_speed()}, FPS={self.config_manager.get_fps()}")
    
    def _update_simulation(self, current_fps, current_speed):
        """Update the simulation state if appropriate."""
        if self.current_state == SIMULATION and not self.simulation.is_paused:
            # Always get latest values directly from config_manager
            current_fps = self.config_manager.get_fps()
            current_speed = self.config_manager.get_simulation_speed()
            
            # Reset frame counter if not exists
            if not hasattr(self, 'frame_counter'):
                self.frame_counter = 0
                
            # Increment frame counter
            self.frame_counter += 1
            
            # Calculate frames to wait before updating simulation
            # Lower values = more frequent updates = faster simulation 
            update_interval = max(1, int(current_fps / current_speed))
                
            # Only update when enough frames have passed
            if self.frame_counter >= update_interval:
                self.frame_counter = 0
                # Print debug info periodically
                if self.simulation.current_step % 10 == 0:
                    print(f"Speed={current_speed}, FPS={current_fps}, Update interval={update_interval}")
                
                # Update simulation
                if self.simulation.is_replaying:
                    if self.simulation.current_step < len(self.simulation.history) - 1:
                        print(f"Replaying step: {self.simulation.current_step+1}")
                        self.simulation.step_forward()
                else:
                    self.simulation.step_simulation()
    
    def _render_current_state(self):
        """Render the appropriate screen based on current state."""
        if self.current_state == MAIN_MENU:
            menu_items = ["[S] Start New Simulation", "[O] Options", "[Q/ESC] Quit"]
            
            # Add continue option only if simulation has been started
            if self.has_simulation_started:
                menu_items.insert(0, "[C] Continue Simulation") 
                
            self.renderer.render_menu(
                "main_menu",
                menu_items,
                "A-Life Simulation"
            )
        
        elif self.current_state == MAIN_MENU_OPTIONS:
            # Render the MainMenuOptions screen
            self.main_menu_options.draw(self.screen)
        
        elif self.current_state == OPTIONS_MENU:
            # Render mid-game options menu
            self.renderer.render_options_menu(self.options_menu)
        
        elif self.current_state == SIMULATION:
            self._render_simulation()
        
        elif self.current_state == PAUSE_MENU:
            self._render_simulation()  # Render simulation in background
            
            # Then overlay the pause menu
            self.renderer.render_pause_overlay([
                "[R/P/ESC] Resume", 
                "[X] Restart Simulation", 
                "[S] View Stats",
                "[O] Options", 
                "[M] Main Menu", 
                "[Q] Quit"
            ])
        
        elif self.current_state == STATS_VIEW:
            # Use the stats view renderer
            self.renderer.render_stats_view(self.simulation)
    
    def _render_simulation(self):
        """Helper to render the simulation state."""
        self.renderer.render_simulation(
            self.simulation.environment, 
            self.simulation.producers, 
            self.simulation.herbivores, 
            self.simulation.carnivores, 
            self.simulation.omnivores,
            self.simulation.current_step, 
            self.simulation.is_paused, 
            self.simulation.is_replaying
        )
    
    def _cleanup(self):
        """Clean up resources before exiting."""
        self.csvfile.close()
        pygame.quit()
        sys.exit()

###########################################
# MAIN ENTRY POINT
###########################################
def run_simulation_interactive():
    """Main function to launch the simulation."""
    app = SimulationApp()
    app.run()

if __name__ == "__main__":
    run_simulation_interactive()
