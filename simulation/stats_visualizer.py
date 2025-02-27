"""
Visualization tools for simulation statistics.
"""

import pygame
import numpy as np
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class SimulationGraphRenderer:
    """Class to handle rendering statistical graphs for the simulation."""
    
    def __init__(self, font):
        self.font = font
        # Default colors for different populations
        self.colors = {
            "producers": (0, 200, 0),      # Green
            "herbivores": (200, 200, 200), # White
            "carnivores": (200, 0, 0),     # Red
            "omnivores": (255, 165, 0)     # Orange
        }
        
    def render_population_history(self, surface, history_data, rect, 
                                max_steps_to_show=100, title="Animal Population History"):
        """
        Render a line graph showing population changes over time.
        
        Parameters:
        - surface: The pygame surface to draw on
        - history_data: List of dictionaries with population counts
        - rect: The rectangle (x, y, width, height) to draw the graph in
        - max_steps_to_show: Maximum number of steps to show on the graph
        - title: Title of the graph
        """
        x, y, width, height = rect
        
        # Draw background and border
        background_color = (20, 30, 40)
        border_color = (100, 100, 100)
        pygame.draw.rect(surface, background_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)
        
        # Draw title
        title_surf = self.font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(x + width//2, y + 5))
        surface.blit(title_surf, title_rect)
        
        # Skip if no data
        if not history_data:
            no_data_surf = self.font.render("No data available", True, (200, 200, 200))
            no_data_rect = no_data_surf.get_rect(center=(x + width//2, y + height//2))
            surface.blit(no_data_surf, no_data_rect)
            return
        
        # Extract data series
        steps = [entry['step'] for entry in history_data]
        # We're no longer plotting producers in the graph
        # producers = [entry['producers'] for entry in history_data]
        herbivores = [entry['herbivores'] for entry in history_data]
        carnivores = [entry['carnivores'] for entry in history_data]
        omnivores = [entry['omnivores'] for entry in history_data]
        
        # Calculate max value for y-axis (excluding producers)
        max_value = max([
            max(herbivores) if herbivores else 0, 
            max(carnivores) if carnivores else 0,
            max(omnivores) if omnivores else 0
        ])
        max_value = max(max_value, 1)  # Ensure we don't divide by zero
        
        # Graph margins and metrics
        margin_top = 30    # Space for title
        margin_bottom = 30 # Space for x-axis labels
        margin_left = 40   # Space for y-axis labels
        margin_right = 15
        
        # Graph dimensions
        graph_width = width - margin_left - margin_right
        graph_height = height - margin_top - margin_bottom
        
        # Limit data to the last max_steps_to_show steps
        if len(history_data) > max_steps_to_show:
            steps = steps[-max_steps_to_show:]
            herbivores = herbivores[-max_steps_to_show:]
            carnivores = carnivores[-max_steps_to_show:]
            omnivores = omnivores[-max_steps_to_show:]
        
        # Draw axes
        axis_color = (150, 150, 150)
        pygame.draw.line(surface, axis_color, 
                        (x + margin_left, y + height - margin_bottom), 
                        (x + width - margin_right, y + height - margin_bottom))
        pygame.draw.line(surface, axis_color,
                        (x + margin_left, y + height - margin_bottom),
                        (x + margin_left, y + margin_top))
        
        # Draw Y-axis labels (values)
        for i in range(5):
            value = max_value * (4-i) / 4
            value_y = y + margin_top + (i * graph_height // 4)
            value_text = self.font.render(f"{int(value)}", True, (200, 200, 200))
            surface.blit(value_text, (x + 5, value_y - value_text.get_height()//2))
            
            # Draw horizontal grid line
            pygame.draw.line(surface, (50, 50, 50), 
                           (x + margin_left, value_y), 
                           (x + width - margin_right, value_y), 1)
        
        # Draw X-axis labels (steps)
        if steps:
            num_labels = 5
            steps_interval = max(1, len(steps) // num_labels)
            for i in range(0, len(steps), steps_interval):
                if i >= len(steps): break
                step_x = x + margin_left + (i * graph_width // len(steps))
                step_text = self.font.render(f"{steps[i]}", True, (200, 200, 200))
                text_rect = step_text.get_rect(midtop=(step_x, y + height - margin_bottom + 5))
                surface.blit(step_text, text_rect)
                
                # Draw vertical grid line
                pygame.draw.line(surface, (50, 50, 50), 
                               (step_x, y + margin_top), 
                               (step_x, y + height - margin_bottom), 1)
        
        # Draw data lines
        def plot_line(data, color, label=None):
            if not data:
                return
            
            # Calculate points and convert to screen coordinates
            points = []
            for i, value in enumerate(data):
                point_x = x + margin_left + (i * graph_width // len(data))
                point_y = y + height - margin_bottom - (value * graph_height / max_value)
                points.append((point_x, point_y))
            
            # Draw line connecting points
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 2)
            
            # Draw label if provided
            if label:
                idx = len(data) - 1
                label_x = points[idx][0] + 5
                label_y = points[idx][1] - 5
                label_surf = self.font.render(label, True, color)
                surface.blit(label_surf, (label_x, label_y))
        
        # Plot each population line (excluding producers)
        # plot_line(producers, self.colors["producers"], "Producers")
        plot_line(herbivores, self.colors["herbivores"], "Herbivores")
        plot_line(carnivores, self.colors["carnivores"], "Carnivores")
        plot_line(omnivores, self.colors["omnivores"], "Omnivores")
        
        # Add a legend
        legend_y = y + 20
        legend_x = x + width - 130
        
        # Draw legend header
        legend_title = self.font.render("Legend", True, (200, 200, 200))
        surface.blit(legend_title, (legend_x, legend_y))
        legend_y += 20
        
        # Draw legend items (animal types only)
        for name, color in [
            ("Herbivores", self.colors["herbivores"]),
            ("Carnivores", self.colors["carnivores"]), 
            ("Omnivores", self.colors["omnivores"])
        ]:
            # Draw color indicator
            pygame.draw.line(surface, color, 
                           (legend_x, legend_y + 5), 
                           (legend_x + 20, legend_y + 5), 3)
            
            # Draw label
            label_surf = self.font.render(name, True, color)
            surface.blit(label_surf, (legend_x + 25, legend_y))
            legend_y += 15
        
    def render_stats_summary(self, surface, current_stats, rect):
        """Render a summary of current statistics."""
        x, y, width, height = rect
        
        # Draw background
        background_color = (25, 35, 45)
        pygame.draw.rect(surface, background_color, rect)
        pygame.draw.rect(surface, (100, 100, 100), rect, 2)
        
        # Draw title
        title_surf = self.font.render("Current Statistics", True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(x + width//2, y + 5))
        surface.blit(title_surf, title_rect)
        
        # Calculate optimal column widths based on available space
        # Use 3 columns instead of 4 to allow more horizontal space
        col_width = width // 3
        
        # Row spacing and starting position (smaller to fit more rows)
        row_height = 22  # Reduced from 25
        start_y = y + 30  # Reduced from 40
        
        # Headers
        headers = ["Organism Type", "Count", "Avg Stats"]
        for i, header in enumerate(headers):
            header_x = x + (i * col_width) + 10
            header_surf = self.font.render(header, True, (220, 220, 220))
            surface.blit(header_surf, (header_x, start_y))
        
        # Horizontal line after headers
        pygame.draw.line(surface, (150, 150, 150), 
                       (x + 5, start_y + row_height - 5), 
                       (x + width - 5, start_y + row_height - 5))
        
        # Define organisms to display
        organisms = [
            ("Producers", self.colors["producers"]),
            ("Herbivores", self.colors["herbivores"]),
            ("Carnivores", self.colors["carnivores"]),
            ("Omnivores", self.colors["omnivores"])
        ]
        
        # Data rows
        row_y = start_y + row_height
        for organism, color in organisms:
            # Create row data
            org_key = organism.lower()
            if org_key in current_stats:
                stats = current_stats[org_key]
                count = stats.get("count", 0)
                
                # Column 1: Organism name
                name_surf = self.font.render(organism, True, color)
                surface.blit(name_surf, (x + 10, row_y))
                
                # Column 2: Count
                count_surf = self.font.render(str(count), True, (200, 200, 200))
                surface.blit(count_surf, (x + col_width + 10, row_y))
                
                # Column 3: Average Stats (combined for space efficiency)
                if org_key != "producers":  # Producers don't have these stats
                    speed = stats.get("speed", 0)
                    gen = stats.get("generation", 0)
                    met = stats.get("metabolism", 0)
                    vis = stats.get("vision", 0)
                    stats_text = f"Sp:{speed:.1f} Gen:{gen:.1f} Met:{met:.1f} Vis:{vis:.1f}"
                else:
                    stats_text = "N/A"
                    
                stats_surf = self.font.render(stats_text, True, (200, 200, 200))
                surface.blit(stats_surf, (x + col_width*2 + 10, row_y))
            
            row_y += row_height
            
        # Add total population count at the bottom
        total_pop = sum(current_stats.get(org.lower(), {}).get("count", 0) for org, _ in organisms)
        row_y += 5  # Add some spacing
        pygame.draw.line(surface, (150, 150, 150), 
                       (x + 5, row_y - 5), 
                       (x + width - 5, row_y - 5))
        
        total_text = self.font.render("Total Population:", True, (255, 255, 255))
        surface.blit(total_text, (x + 10, row_y))
        
        total_count = self.font.render(str(total_pop), True, (255, 255, 255))
        surface.blit(total_count, (x + col_width + 10, row_y))
