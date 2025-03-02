"""
Options menu UI for the A-Life simulation.
"""

import pygame
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class OptionsMenu:
    """Options menu interface for configuring simulation settings."""
    
    def __init__(self, config_manager, font):
        self.config_manager = config_manager
        self.font = font
        self.selected_option = 0
        self.editing = False
        
        # Define options
        self.options = [
            ("Simulation Speed", lambda: self.config_manager.get_simulation_speed(), 
             lambda v: self.config_manager.set_simulation_speed(v)),
            ("FPS", lambda: self.config_manager.get_fps(), 
             lambda v: self.config_manager.set_fps(v)),
            ("Skip Steps", self._get_step_skip, self._set_step_skip),  # Add skip steps option
            ("Return", None, None)  # Special option to return
        ]
        
        # Value being edited
        self.edit_value = ""
    
    def handle_key(self, key):
        """Handle key press for option selection and editing."""
        if self.editing:
            return self._handle_editing_key(key)
        else:
            return self._handle_navigation_key(key)
    
    def _handle_navigation_key(self, key):
        """Handle keys for menu navigation."""
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            # If "Return" option is selected
            if self.selected_option == len(self.options) - 1:
                return True  # Signal to exit options menu
            else:
                # Start editing the selected option
                self.editing = True
                current_value = self.options[self.selected_option][1]()
                self.edit_value = str(current_value)
        return False
    
    def _handle_editing_key(self, key):
        """Handle keys for option value editing."""
        if key == pygame.K_ESCAPE:
            # Cancel editing
            self.editing = False
        elif key == pygame.K_RETURN:
            # Apply changes
            try:
                option_name, _, set_func = self.options[self.selected_option]
                if "Speed" in option_name:
                    value = float(self.edit_value)
                    set_func(value)
                    print(f"Updated {option_name} to {value}")
                else:
                    value = int(self.edit_value)
                    set_func(value)
                    print(f"Updated {option_name} to {value}")
                
                # Save config after each change
                self.config_manager.save_config()
            except (ValueError, TypeError) as e:
                print(f"Error updating value: {e}")
                pass  # Ignore invalid input
            finally:
                self.editing = False
        elif key == pygame.K_BACKSPACE:
            # Delete last character
            if self.edit_value:
                self.edit_value = self.edit_value[:-1]
        elif pygame.K_0 <= key <= pygame.K_9:
            # Add digit (both regular and numpad keys)
            self.edit_value += pygame.key.name(key)
        elif key == pygame.K_PERIOD or key == pygame.K_KP_PERIOD:
            # Add decimal point for float values if not already present
            if "Speed" in self.options[self.selected_option][0] and "." not in self.edit_value:
                self.edit_value += "."
        return False
    
    def render(self, surface):
        """Render the options menu to the screen."""
        # Draw background
        surface.fill((30, 30, 40))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 48)
        title_surf = title_font.render("Options", True, (220, 220, 220))
        title_rect = title_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 50))
        surface.blit(title_surf, title_rect)
        
        # Draw instructions
        instruction_text = "Arrow keys to navigate, Enter to edit, Esc to cancel edit"
        instruction_surf = self.font.render(instruction_text, True, (180, 180, 180))
        instruction_rect = instruction_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 100))
        surface.blit(instruction_surf, instruction_rect)
        
        # Draw options
        start_y = 160
        option_height = 35
        
        for i, (option_name, get_value, _) in enumerate(self.options):
            is_selected = i == self.selected_option
            text_color = (255, 255, 255) if is_selected else (200, 200, 200)
            bg_color = (60, 60, 100) if is_selected else (40, 40, 60)
            
            # Option box
            option_rect = pygame.Rect(
                WINDOW_WIDTH // 4,
                start_y + i * option_height,
                WINDOW_WIDTH // 2,
                30
            )
            pygame.draw.rect(surface, bg_color, option_rect)
            pygame.draw.rect(surface, (100, 100, 150), option_rect, 1)
            
            # Option text
            if option_name == "Return":
                # Special handling for the Return option
                option_text = option_name
                text_surf = self.font.render(option_text, True, text_color)
                text_rect = text_surf.get_rect(center=option_rect.center)
                surface.blit(text_surf, text_rect)
            else:
                # Normal option with name and value
                value_text = self.edit_value if (self.editing and is_selected) else str(get_value())
                
                # Draw option name
                name_surf = self.font.render(option_name + ":", True, text_color)
                name_rect = name_surf.get_rect(midleft=(option_rect.left + 10, option_rect.centery))
                surface.blit(name_surf, name_rect)
                
                # Draw option value
                value_surf = self.font.render(value_text, True, text_color)
                value_rect = value_surf.get_rect(midright=(option_rect.right - 10, option_rect.centery))
                surface.blit(value_surf, value_rect)
                
                # Draw edit indicator
                if self.editing and is_selected:
                    pygame.draw.rect(surface, (200, 200, 100), value_rect.inflate(4, 4), 2)
        
        # Draw version
        version_text = "Settings will apply to new simulations"
        version_surf = self.font.render(version_text, True, (150, 150, 150))
        version_rect = version_surf.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        surface.blit(version_surf, version_rect)
    
    def _get_step_skip(self):
        """Get the step skip setting."""
        return str(self.config_manager.get_step_skip())

    def _set_step_skip(self, value):
        """Set the step skip setting."""
        try:
            skip = int(value)
            if 1 <= skip <= 20:
                self.config_manager.set_step_skip(skip)
                print(f"Set step skip to {skip}")
                return True
            else:
                print("Step skip must be between 1 and 20")
                return False
        except ValueError:
            print("Invalid step skip value")
            return False
