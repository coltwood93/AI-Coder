"""
Input handling for the A-Life simulation.
Processes user input and returns state changes.
"""

import pygame

# Import the state constants
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE_X, CELL_SIZE_Y,
    STATS_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    GRID_DISPLAY_WIDTH, GRID_DISPLAY_HEIGHT,
    STEP_BACK_KEY, STEP_FORWARD_KEY
)
from utils.app_states import MAIN_MENU, MAIN_MENU_OPTIONS, OPTIONS_MENU, SIMULATION, PAUSE_MENU, STATS_VIEW

class InputHandler:
    """Centralizes input handling for the simulation."""
    
    def __init__(self, simulation_manager):
        self.sim = simulation_manager
    
    def handle_events(self, events, current_state, from_main_menu):
        """Process all pygame events and return updated state information."""
        new_state = None
        new_from_main_menu = None
        continue_running = True

        for event in events:
            if event.type == pygame.QUIT:
                return current_state, from_main_menu, False  # signal to quit
            
            # Handle key presses based on current state
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)} in state: {current_state}")
                
                state_handlers = {
                    MAIN_MENU: self._handle_main_menu_input,
                    OPTIONS_MENU: self._handle_options_menu_input,
                    SIMULATION: self._handle_simulation_input,
                    PAUSE_MENU: self._handle_pause_menu_input,
                    STATS_VIEW: self._handle_stats_view_input  # New handler for stats view
                }
                
                # Call the appropriate handler based on current state
                if current_state in state_handlers:
                    result = state_handlers[current_state](event, from_main_menu)
                    if result:
                        return result
        
        # Return unchanged state if no state changes occurred
        return new_state, new_from_main_menu, continue_running
    
    def _handle_main_menu_input(self, event, from_main_menu):
        """Handle input in the main menu state."""
        app = self._find_app_instance()  # Get reference to SimulationApp
        
        if event.key == pygame.K_s:
            print("Starting new simulation from main menu")
            # Reset the simulation before starting
            self.sim.reset()
            self.sim.is_paused = False
            # Update app state
            if app:
                app.has_simulation_started = True
            return SIMULATION, from_main_menu, True
        elif event.key == pygame.K_c and app and app.has_simulation_started:
            print("Continuing simulation from main menu")
            self.sim.is_paused = False
            return SIMULATION, from_main_menu, True
        elif event.key == pygame.K_o:
            print("Opening options from main menu")
            return MAIN_MENU_OPTIONS, True, True
        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            print("Quitting from main menu")
            return None, None, False  # Signal to quit
        return None  # No state change
    
    def _find_app_instance(self):
        """Find the instance of SimulationApp."""
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, 'has_simulation_started') and hasattr(obj, 'current_state'):
                return obj
        return None
    
    def _handle_options_menu_input(self, event, from_main_menu):
        """Handle input in the options menu state."""
        app = self._find_app_instance()
        
        if event.key == pygame.K_ESCAPE:
            # Exit options menu if no option is being edited
            if not app.options_menu.editing:
                next_state = MAIN_MENU if from_main_menu else PAUSE_MENU
                print(f"Returning from options to {next_state}")
                return next_state, from_main_menu, True
        elif event.key == pygame.K_q and not app.options_menu.editing:
            print("Quitting from options menu")
            return None, None, False  # Signal to quit
        else:
            # Pass the keypress to the options menu
            if app and hasattr(app, 'options_menu'):
                exit_options = app.options_menu.handle_key(event.key)
                if exit_options:
                    next_state = MAIN_MENU if from_main_menu else PAUSE_MENU
                    print(f"Returning from options to {next_state}")
                    return next_state, from_main_menu, True
        return None  # No state change
    
    def _handle_simulation_input(self, event, from_main_menu):
        """Handle input in the simulation state."""
        if event.key == pygame.K_p:
            print(f"{'Pausing' if not self.sim.is_paused else 'Resuming'} simulation")
            self.sim.is_paused = not self.sim.is_paused
        elif event.key == pygame.K_ESCAPE:
            print("Opening pause menu")
            return PAUSE_MENU, from_main_menu, True
        elif event.key == STEP_BACK_KEY:
            self._handle_step_back()
        elif event.key == STEP_FORWARD_KEY:
            self._handle_step_forward()
        elif event.key == pygame.K_o:
            print("Opening options from simulation")
            return OPTIONS_MENU, from_main_menu, True
        return None  # No state change
    
    def _handle_pause_menu_input(self, event, from_main_menu):
        """Handle input in the pause menu state."""
        if event.key in (pygame.K_r, pygame.K_p, pygame.K_ESCAPE):
            print("Resuming simulation from pause menu")
            return SIMULATION, from_main_menu, True
        elif event.key == pygame.K_x:
            print("Restarting simulation")
            self.sim.reset()
            # Update app state if found
            app = self._find_app_instance()
            if app:
                app.has_simulation_started = True
            return SIMULATION, from_main_menu, True
        elif event.key == pygame.K_o:
            print("Opening options from pause menu")
            return OPTIONS_MENU, False, True
        elif event.key == pygame.K_s:
            print("Opening stats view from pause menu")
            return STATS_VIEW, False, True
        elif event.key == pygame.K_m:
            print("Returning to main menu from pause menu")
            return MAIN_MENU, True, True
        elif event.key == pygame.K_q:
            print("Quitting from pause menu")
            return None, None, False  # Signal to quit
        return None  # No state change
    
    def _handle_stats_view_input(self, event, from_main_menu):
        """Handle input in the stats view state."""
        if event.key == pygame.K_ESCAPE:
            print("Returning to pause menu from stats view")
            return PAUSE_MENU, False, True
        return None  # No state change
    
    def _handle_step_back(self):
        """Handle stepping back in the simulation."""
        if not self.sim.is_paused:
            print("Auto-pausing for step back")
            self.sim.is_paused = True
        
        if self.sim.step_back():
            print(f"Stepping back to {self.sim.current_step}")
    
    def _handle_step_forward(self):
        """Handle stepping forward in the simulation."""
        if not self.sim.is_paused:
            print("Auto-pausing for step forward")
            self.sim.is_paused = True
        
        if self.sim.step_forward() or (self.sim.current_step == len(self.sim.history) - 1 and self.sim.step_simulation()):
            print(f"Stepping forward to {self.sim.current_step}")
