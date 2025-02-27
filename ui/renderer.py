"""
Rendering functionality for the A-Life simulation.
Handles drawing the simulation grid, organisms, and UI elements.
"""

import pygame
from utils.constants import (
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, CELL_SIZE_X, CELL_SIZE_Y,
    STATS_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    GRID_DISPLAY_WIDTH, GRID_DISPLAY_HEIGHT
)
from simulation.environment import current_season
from simulation.stats import calc_traits_avg
from simulation.stats_visualizer import SimulationGraphRenderer

class SimulationRenderer:
    """Class to handle all rendering operations for the simulation."""
    
    def __init__(self, screen, main_font, label_font):
        self.screen = screen
        self.main_font = main_font
        self.label_font = label_font
        self.stats_scroll_y = 0
        self.max_scroll_y = 0
        self.title_font = pygame.font.SysFont(None, 28)
        self.graph_renderer = SimulationGraphRenderer(main_font)
    
    def render_simulation(self, environment, producers, herbivores, carnivores, omnivores, 
                        current_step, is_paused, is_replaying):
        """Renders the complete simulation state to the screen."""
        self.screen.fill((0, 0, 0))
        
        # Render environment grid and organisms
        self._render_environment(environment)
        self._render_producers(producers)
        self._render_herbivores(herbivores)
        self._render_carnivores(carnivores)
        self._render_omnivores(omnivores)
        
        # Render stats panel
        self._render_stats_panel(
            producers, herbivores, carnivores, omnivores,
            current_step, is_paused, is_replaying
        )
    
    def render_menu(self, menu_type, items, title, background_color=(0, 0, 50), title_color=(255, 255, 255)):
        """Renders a menu with given items and title."""
        self.screen.fill(background_color)
        
        # Draw title
        font = pygame.font.SysFont(None, 48)
        title_surf = font.render(title, True, title_color)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Draw menu items
        small_font = pygame.font.SysFont(None, 32)
        y = 200
        for line in items:
            text = small_font.render(line, True, (200, 200, 200))
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 40
    
    def render_pause_overlay(self, menu_items):
        """Renders a semi-transparent overlay with menu items."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        font = pygame.font.SysFont(None, 48)
        text_surf = font.render("PAUSED", True, (255, 255, 255))
        rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(text_surf, rect)
        
        # Draw menu items
        small_font = pygame.font.SysFont(None, 32)
        y = 200
        for item in menu_items:
            line_surf = small_font.render(item, True, (200, 200, 200))
            rect = line_surf.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(line_surf, rect)
            y += 40
    
    def handle_scroll(self, event, mouse_x, scroll_speed=15):
        """Handle scrolling of the stats panel."""
        if mouse_x > GRID_DISPLAY_WIDTH:
            self.stats_scroll_y -= event.y * scroll_speed
            self.stats_scroll_y = max(0, min(self.stats_scroll_y, self.max_scroll_y))
            return True
        return False
    
    def render_stats_view(self, simulation):
        """Renders a detailed statistics view for the simulation."""
        # Fill background
        self.screen.fill((15, 25, 35))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 36)
        title_surf = title_font.render("Simulation Statistics", True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 20))
        self.screen.blit(title_surf, title_rect)
        
        # Layout settings - adjust to give more space to population history
        graph_height = 280
        stats_height = 200  # Increased from 150
        padding = 20
        
        # Draw population history graph
        graph_rect = (padding, 60, WINDOW_WIDTH - padding*2, graph_height)
        self.graph_renderer.render_population_history(
            self.screen, 
            simulation.population_history, 
            graph_rect
        )
        
        # Draw current statistics summary
        stats_rect = (padding, 60 + graph_height + 10, WINDOW_WIDTH - padding*2, stats_height)
        self.graph_renderer.render_stats_summary(
            self.screen, 
            simulation.get_current_stats(),
            stats_rect
        )
        
        # Draw instructions at bottom
        instructions_surf = self.main_font.render("Press [ESC] to return", True, (200, 200, 200))
        instructions_rect = instructions_surf.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 10))
        self.screen.blit(instructions_surf, instructions_rect)
    
    # Private rendering methods
    def _render_environment(self, environment):
        """Render the nutrient environment grid."""
        # Create a surface for the environment grid
        grid_surface = pygame.Surface((GRID_DISPLAY_WIDTH, GRID_DISPLAY_HEIGHT))
        grid_surface.fill((0, 0, 0))
        
        # Draw the environment cells onto the surface
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                val = environment[x, y]
                r = int(0 * val)
                g = int(0 * val)
                b = int(255 * val)
                cell_rect = pygame.Rect(
                    int(x * CELL_SIZE_X), 
                    int(y * CELL_SIZE_Y), 
                    int(CELL_SIZE_X) + 1, 
                    int(CELL_SIZE_Y) + 1
                )
                pygame.draw.rect(grid_surface, (r, g, b), cell_rect)
        
        # Draw the grid surface onto the screen
        self.screen.blit(grid_surface, (0, 0))
    
    def _render_producers(self, producers):
        """Render all producer organisms."""
        for p in producers:
            px = int(p.x * CELL_SIZE_X)
            py = int(p.y * CELL_SIZE_Y)
            pygame.draw.rect(self.screen, (0, 200, 0), 
                            (px, py, int(CELL_SIZE_X) + 1, int(CELL_SIZE_Y) + 1))
    
    def _render_herbivores(self, herbivores):
        """Render all herbivore organisms with labels."""
        for h in herbivores:
            hx = int(h.x * CELL_SIZE_X)
            hy = int(h.y * CELL_SIZE_Y)
            radius = int(min(CELL_SIZE_X, CELL_SIZE_Y) / 2)
            center = (hx + int(CELL_SIZE_X / 2), hy + int(CELL_SIZE_Y / 2))
            pygame.draw.circle(self.screen, (255, 255, 255), center, radius)
            self._render_centered_label(f"H{h.id}", hx, hy, (0, 0, 0), (255, 255, 255))
    
    def _render_carnivores(self, carnivores):
        """Render all carnivore organisms with labels."""
        for c in carnivores:
            cx = int(c.x * CELL_SIZE_X)
            cy = int(c.y * CELL_SIZE_Y)
            radius = int(min(CELL_SIZE_X, CELL_SIZE_Y) / 2)
            center = (cx + int(CELL_SIZE_X / 2), cy + int(CELL_SIZE_Y / 2))
            pygame.draw.circle(self.screen, (255, 0, 0), center, radius)
            self._render_centered_label(f"C{c.id}", cx, cy, (0, 0, 0), (255, 0, 0))
    
    def _render_omnivores(self, omnivores):
        """Render all omnivore organisms with labels."""
        for o in omnivores:
            ox = int(o.x * CELL_SIZE_X)
            oy = int(o.y * CELL_SIZE_Y)
            radius = int(min(CELL_SIZE_X, CELL_SIZE_Y) / 2)
            center = (ox + int(CELL_SIZE_X / 2), oy + int(CELL_SIZE_Y / 2))
            pygame.draw.circle(self.screen, (255, 165, 0), center, radius)
            self._render_centered_label(f"O{o.id}", ox, oy, (0, 0, 0), (255, 165, 0))
    
    def _render_centered_label(self, text, pos_x, pos_y, color, bg_color):
        """Helper to render centered text on organisms."""
        # Calculate appropriate label size based on cell size
        label_size = max(10, min(24, int(min(CELL_SIZE_X, CELL_SIZE_Y) * 0.6)))
        dynamic_font = pygame.font.SysFont(None, label_size)
        
        # Render text with background
        text_surf = dynamic_font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(
            pos_x + int(CELL_SIZE_X / 2), 
            pos_y + int(CELL_SIZE_Y / 2)
        ))
        padding = 2
        bg_rect = pygame.Rect(
            text_rect.x - padding, 
            text_rect.y - padding, 
            text_rect.width + padding*2, 
            text_rect.height + padding*2
        )
        pygame.draw.rect(self.screen, bg_color, bg_rect)
        self.screen.blit(text_surf, text_rect)
    
    def _render_stats_panel(self, producers, herbivores, carnivores, omnivores, 
                          current_step, is_paused, is_replaying):
        """Render the scrollable stats panel with organism statistics."""
        panel_x = GRID_DISPLAY_WIDTH  # Use the calculated display width, not grid width * cell size
        panel_width = STATS_PANEL_WIDTH
        panel_height = WINDOW_HEIGHT
        
        # Create a separate surface for the stats panel
        stats_panel = pygame.Surface((panel_width, panel_height * 2))
        stats_panel.fill((30, 30, 30))
        
        p_count = len(producers)
        (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)
        h_count = len(herbivores)
        (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)
        c_count = len(carnivores)
        (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(omnivores)
        o_count = len(omnivores)
        
        # Draw each section of stats
        row_y = 20
        
        # Simulation info section
        row_y = self._draw_section_header(stats_panel, "SIMULATION INFO", row_y)
        season_now = current_season(current_step)
        status_str = "PAUSED" if is_paused else "RUNNING"
        info_lines = [
            f"Timestep: {current_step}",
            f"Season: {season_now}",
            f"Status: {status_str}",
            f"Replay Mode: {'ON' if is_replaying else 'OFF'}"
        ]
        row_y = self._draw_section_lines(stats_panel, info_lines, row_y)
        row_y += 20  # Extra spacing
        
        # Population counts section
        row_y = self._draw_section_header(stats_panel, "POPULATION", row_y)
        pop_lines = [
            f"Producers: {p_count}",
            f"Herbivores: {h_count}",
            f"Carnivores: {c_count}",
            f"Omnivores: {o_count}",
            f"Total: {p_count + h_count + c_count + o_count}"
        ]
        row_y = self._draw_section_lines(stats_panel, pop_lines, row_y)
        row_y += 20  # Extra spacing
        
        # Draw organism-specific stats sections
        row_y = self._draw_organism_stats(stats_panel, "HERBIVORES", h_count, 
                                       (h_sp, h_gen, h_met, h_vis), (200, 200, 200), row_y)
        row_y = self._draw_organism_stats(stats_panel, "CARNIVORES", c_count, 
                                       (c_sp, c_gen, c_met, c_vis), (255, 100, 100), row_y)
        row_y = self._draw_organism_stats(stats_panel, "OMNIVORES", o_count, 
                                       (o_sp, o_gen, o_met, o_vis), (255, 165, 0), row_y)
        
        # Controls section
        row_y = self._draw_section_header(stats_panel, "CONTROLS", row_y)
        control_lines = [
            "P - Pause/Resume",
            "Left/Right - Step",
            "ESC - Menu",
            "Mouse Wheel - Scroll Stats"
        ]
        row_y = self._draw_section_lines(stats_panel, control_lines, row_y)
        
        # Set the max scroll position and clamp current scroll
        self.max_scroll_y = max(0, row_y - panel_height + 20)
        self.stats_scroll_y = max(0, min(self.stats_scroll_y, self.max_scroll_y))
        
        # Draw scroll indicators if needed
        self._draw_scroll_indicators(stats_panel, panel_width, panel_height)
        
        # Blit the visible portion of the stats panel
        self.screen.blit(stats_panel, (panel_x, 0), 
                       (0, self.stats_scroll_y, panel_width, panel_height))
        
        # Add a dividing line between simulation and stats panel
        pygame.draw.line(self.screen, (100, 100, 100), (panel_x, 0), (panel_x, panel_height), 2)
    
    def _draw_section_header(self, surface, title, y_pos):
        """Draw a section header on the stats panel."""
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        surface.blit(title_surf, (10, y_pos))
        return y_pos + 30
    
    def _draw_section_lines(self, surface, lines, y_pos):
        """Draw a list of text lines on the stats panel."""
        for line in lines:
            text = self.main_font.render(line, True, (220, 220, 220))
            surface.blit(text, (20, y_pos))
            y_pos += 20
        return y_pos
    
    def _draw_organism_stats(self, surface, title, count, stats, color, y_pos):
        """Draw stats for a specific organism type."""
        y_pos = self._draw_section_header(surface, title, y_pos)
        
        if count > 0:
            speed, gen, met, vis = stats
            stats_lines = [
                f"Speed: {speed:.1f}",
                f"Generation: {gen:.1f}",
                f"Metabolism: {met:.1f}",
                f"Vision: {vis:.1f}"
            ]
            
            for line in stats_lines:
                text = self.main_font.render(line, True, color)
                surface.blit(text, (20, y_pos))
                y_pos += 20
        else:
            text = self.main_font.render("None alive", True, color)
            surface.blit(text, (20, y_pos))
            y_pos += 20
        
        return y_pos + 20  # Return new y position with extra spacing
    
    def _draw_scroll_indicators(self, surface, panel_width, panel_height):
        """Draw scroll indicators on the stats panel if needed."""
        if self.max_scroll_y > 0:
            # Draw up arrow if not at top
            if self.stats_scroll_y > 0:
                pygame.draw.polygon(surface, (200, 200, 200), 
                                  [(panel_width - 15, 20), 
                                   (panel_width - 5, 20), 
                                   (panel_width - 10, 10)])
            
            # Draw down arrow if not at bottom
            if self.stats_scroll_y < self.max_scroll_y:
                pygame.draw.polygon(surface, (200, 200, 200), 
                                  [(panel_width - 15, panel_height - 20), 
                                   (panel_width - 5, panel_height - 20), 
                                   (panel_width - 10, panel_height - 10)])
