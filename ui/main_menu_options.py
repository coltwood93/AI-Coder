import pygame

class MainMenuOptions:
    def __init__(self, config_manager, font):
        self.config_manager = config_manager
        self.font = font
        self.selected_option = 0
        self.editing = False
        self.edit_value = ""
        self.text_selected = False  # Track if text is selected for replacement

        # Define menu options with getters/setters
        self.options = [
            ("Grid Width", lambda: self.config_manager.get_grid_width(),
             lambda v: self.config_manager.set_grid_width(int(v))),
            ("Grid Height", lambda: self.config_manager.get_grid_height(),
             lambda v: self.config_manager.set_grid_height(int(v))),
            ("Initial Producers", lambda: self.config_manager.get_initial_count("producers"),
             lambda v: self.config_manager.set_initial_count("producers", int(v))),
            ("Initial Herbivores", lambda: self.config_manager.get_initial_count("herbivores"),
             lambda v: self.config_manager.set_initial_count("herbivores", int(v))),
            ("Initial Carnivores", lambda: self.config_manager.get_initial_count("carnivores"),
             lambda v: self.config_manager.set_initial_count("carnivores", int(v))),
            ("Initial Omnivores", lambda: self.config_manager.get_initial_count("omnivores"),
             lambda v: self.config_manager.set_initial_count("omnivores", int(v))),
            ("Simulation Speed", lambda: self.config_manager.get_simulation_speed(),
             lambda v: self.config_manager.set_simulation_speed(float(v))),
            ("FPS", lambda: self.config_manager.get_fps(),
             lambda v: self.config_manager.set_fps(int(v))),
            ("Return", None, None)
        ]
        # Add a flag to signal return to main menu
        self.return_to_menu = False

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.editing:
                    self._handle_editing_key(event.key)
                else:
                    # Add ESC key handling to return to main menu
                    if event.key == pygame.K_ESCAPE:
                        self.return_to_menu = True
                    else:
                        self._handle_navigation_key(event.key)
                    
                # Debug info to verify input processing
                print(f"Key pressed: {pygame.key.name(event.key)}")

    def draw(self, surface):
        surface.fill((20, 20, 40))
        title_font = pygame.font.SysFont(None, 48)
        title_surf = title_font.render("Main Menu Options", True, (220, 220, 220))
        title_rect = title_surf.get_rect(center=(surface.get_width() // 2, 60))
        surface.blit(title_surf, title_rect)

        instruction_surf = self.font.render("Arrow keys to navigate, Enter to edit, Esc to cancel edit", True, (180, 180, 180))
        instruction_rect = instruction_surf.get_rect(center=(surface.get_width() // 2, 110))
        surface.blit(instruction_surf, instruction_rect)

        y_start = 160
        line_height = 35
        for i, (option_name, getter, _) in enumerate(self.options):
            is_selected = (i == self.selected_option)
            color = (255, 255, 255) if is_selected else (180, 180, 180)
            rect = pygame.Rect(
                surface.get_width() // 4,
                y_start + i * line_height,
                surface.get_width() // 2,
                30
            )
            pygame.draw.rect(surface, (50, 50, 70) if is_selected else (40, 40, 60), rect)
            pygame.draw.rect(surface, (100, 100, 150), rect, 1)

            if option_name == "Return":
                text_surf = self.font.render("Return", True, color)
                text_rect = text_surf.get_rect(center=rect.center)
                surface.blit(text_surf, text_rect)
            else:
                val_text = self.edit_value if (is_selected and self.editing) else str(getter())
                name_surf = self.font.render(f"{option_name}:", True, color)
                name_rect = name_surf.get_rect(midleft=(rect.left + 10, rect.centery))
                surface.blit(name_surf, name_rect)

                val_surf = self.font.render(val_text, True, color)
                val_rect = val_surf.get_rect(midright=(rect.right - 10, rect.centery))
                surface.blit(val_surf, val_rect)
                
                # Draw highlight selection rectangle and highlight text when first entering edit mode
                if is_selected and self.editing:
                    # Draw highlight background
                    if self.text_selected:
                        # Show text as selected with a different background color
                        highlight_rect = val_rect.inflate(4, 4)
                        pygame.draw.rect(surface, (0, 120, 215), highlight_rect)
                        # Redraw text on top of highlight
                        val_surf = self.font.render(val_text, True, (255, 255, 255))
                        surface.blit(val_surf, val_rect)
                    else:
                        # Regular edit mode (cursor-like)
                        pygame.draw.rect(surface, (200, 200, 100), val_rect.inflate(4, 4), 2)

    def _handle_navigation_key(self, key):
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            if self.selected_option == len(self.options) - 1:
                # Set the flag to return to main menu
                self.return_to_menu = True
            else:
                self.editing = True
                current_val = self.options[self.selected_option][1]()
                self.edit_value = str(current_val)
                self.text_selected = True  # Text is selected when first entering edit mode

    def _handle_editing_key(self, key):
        if key == pygame.K_ESCAPE:
            print(f"Canceling edit of {self.options[self.selected_option][0]}")
            self.editing = False
            self.text_selected = False
        elif key == pygame.K_RETURN:
            option_name, _, setter = self.options[self.selected_option]
            try:
                # Check if we're editing a float value (simulation speed)
                if "Speed" in option_name:
                    new_value = float(self.edit_value)
                    setter(new_value)
                    print(f"Set {option_name} to {new_value} (float)")
                else:
                    new_value = int(self.edit_value)
                    setter(new_value)
                    print(f"Set {option_name} to {new_value} (int)")
                
                # Save settings after each change
                self.config_manager.save_config()
            except ValueError as e:
                print(f"Error setting value: {e}")
            finally:
                self.editing = False
                self.text_selected = False
        elif key == pygame.K_BACKSPACE:
            if self.text_selected:
                # If text is selected, pressing backspace clears everything
                self.edit_value = ""
                self.text_selected = False
            elif len(self.edit_value) > 0:
                self.edit_value = self.edit_value[:-1]
            print(f"Backspace: now {self.edit_value}")
        elif (pygame.K_0 <= key <= pygame.K_9) or key == pygame.K_PERIOD or key == pygame.K_KP_PERIOD:
            # Check if we need to clear the field first (when text is selected)
            if self.text_selected:
                self.edit_value = ""
                self.text_selected = False
            
            # Add the digit or decimal point
            if pygame.K_0 <= key <= pygame.K_9:
                self.edit_value += chr(key)
                print(f"Added digit: now {self.edit_value}")
            elif (key == pygame.K_PERIOD or key == pygame.K_KP_PERIOD) and "Speed" in self.options[self.selected_option][0] and "." not in self.edit_value:
                self.edit_value += "."
                print(f"Added decimal: now {self.edit_value}")

    # Add a method to check and reset the return flag
    def should_return_to_menu(self):
        """Check if we should return to the main menu and reset the flag."""
        if self.return_to_menu:
            self.return_to_menu = False
            return True
        return False
