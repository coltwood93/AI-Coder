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
    STATS_PANEL_WIDTH, FPS, SIMULATION_SPEED
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

# Set random seed for reproducibility
random.seed()

###########################################
# APPLICATION CONTROLLER
###########################################
class SimulationApp:
    """Main application controller that ties everything together."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("A-Life: Seasons, Disease, Omnivores, Nutrient Environment")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.main_font = pygame.font.SysFont(None, 24)
        self.label_font = pygame.font.SysFont(None, 16)
        
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
            # Process events
            events = pygame.event.get()
            new_state, new_from_main_menu, continue_running = self.input_handler.handle_events(
                events, self.current_state, self.from_main_menu
            )
            
            # Update state if changed
            if new_state is not None:
                self.current_state = new_state
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
            self._update_simulation()
            
            # Render the current state
            self._render_current_state()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Cleanup resources
        self._cleanup()
    
    def _update_simulation(self):
        """Update the simulation state if appropriate."""
        if self.current_state == SIMULATION and not self.simulation.is_paused:
            # Only update simulation at a fraction of the visual framerate
            # This creates a slower simulation while keeping UI responsiveness
            if hasattr(self, 'frame_counter'):
                self.frame_counter += 1
            else:
                self.frame_counter = 0
                
            # Only step simulation every few frames based on SIMULATION_SPEED
            if self.frame_counter >= 1 / SIMULATION_SPEED:
                self.frame_counter = 0
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
        
        elif self.current_state == OPTIONS_MENU:
            return_text = "[ESC] Return to " + ("Main Menu" if self.from_main_menu else "Pause Menu")
            self.renderer.render_menu(
                "options_menu",
                [return_text, "[Q] Quit"],
                "OPTIONS",
                background_color=(30, 30, 30),
                title_color=(200, 200, 200)
            )
        
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
            # Use the new stats view renderer
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
