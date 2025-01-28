#!/usr/bin/env python3
"""
Step 5: Introduce Genetic Variation & Evolution

Features:
- Organisms have a genome (speed gene).
- Mutation occurs on reproduction (speed can change).
- Each organism tracks its generation.
- We log population size, average speed, and average generation over time.
"""

import random
import csv
from deap import base, creator, tools

# -----------------------
# Simulation Parameters
# -----------------------
GRID_WIDTH = 20              # Width of the grid
GRID_HEIGHT = 20             # Height of the grid
INITIAL_POPULATION = 10
INITIAL_ENERGY = 10

# Movement & Energy
BASE_MOVE_COST = 1           # Base energy cost per "step"
EAT_GAIN = 5                 # Energy gained from eating one food unit
REPRODUCTION_THRESHOLD = 20  # Energy needed to reproduce
TIMESTEPS = 80
FOOD_REGEN_PROB = 0.01       # Probability that an empty cell spawns food each turn

# Genome & Mutation
MUTATION_RATE = 0.1          # Probability of a mutation happening on reproduction
GENE_SPEED_INITIAL = 1       # Initial speed for all organisms (you can randomize if desired)
GENE_SPEED_MIN = 0           # Minimum allowed speed
GENE_SPEED_MAX = 5           # Maximum allowed speed (optional clamp)

# For reproducibility, uncomment:
# random.seed(42)

# -----------------------
# **DEAP Setup**
# -----------------------

# Define a fitness function (this might need adjustment based on your needs)
def evaluate(individual):
    # For now, we are using the speed parameter, but you can create a more complex function to evaluate your organisms.
    return individual.speed,

# Create a fitness class that minimizes the value, for example
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# Create the Individual class, inheriting from the list class.
# You can replace the single speed value with a more complex genome.
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialize the toolbox
toolbox = base.Toolbox()

# Register the individual creator, mutation, and selection
toolbox.register("individual", tools.initRepeat, creator.Individual, lambda: random.randint(GENE_SPEED_MIN, GENE_SPEED_MAX), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# mutation operator
toolbox.register("mutate", tools.mutUniformInt, low=GENE_SPEED_MIN, up=GENE_SPEED_MAX, indpb=MUTATION_RATE)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

# -----------------------
# Organism Class
# -----------------------
class Organism:
    """
    An organism with:
    - x, y position
    - energy
    - genome: currently just 'speed'
    - generation
    """
    def __init__(self, x, y, energy=INITIAL_ENERGY, individual=None, generation=0):
        self.x = x
        self.y = y
        self.energy = energy
        self.generation = generation
        #if individual is not None, use that, otherwise create a random one.
        if individual is None:
            self.individual = creator.Individual([random.randint(GENE_SPEED_MIN, GENE_SPEED_MAX)])
        else:
            self.individual = individual

    @property
    def speed(self):
        #this is how we get the speed of an organism from its genome
        return self.individual

    def move(self, grid_width, grid_height):
        """
        Move 'speed' times (each move is in one of 4 directions).
        Each step costs BASE_MOVE_COST energy.
        """
        for _ in range(self.individual[0]):
            direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            if direction == 'UP':
                self.y = (self.y - 1) % grid_height
            elif direction == 'DOWN':
                self.y = (self.y + 1) % grid_height
            elif direction == 'LEFT':
                self.x = (self.x - 1) % grid_width
            elif direction == 'RIGHT':
                self.x = (self.x + 1) % grid_width

            # Pay energy cost for each step
            self.energy -= BASE_MOVE_COST

    def eat(self, food_grid):
        """If there's food at my location, eat it for an energy boost."""
        if food_grid[self.y][self.x] == 1:
            self.energy += EAT_GAIN
            food_grid[self.y][self.x] = 0  # Consume the food

    def can_reproduce(self):
        """Check if energy is above threshold."""
        return self.energy >= REPRODUCTION_THRESHOLD

    def reproduce(self):
        """
        Create one offspring, splitting energy between parent and child.
        Offspring may mutate 'speed'.
        Returns a new Organism or None if no reproduction happens.
        """
        if self.can_reproduce():
            child_energy = self.energy // 2
            self.energy -= child_energy
            child_generation = self.generation + 1

            #create an offspring from an existing genome
            offspring = toolbox.clone(self.individual)
            #apply mutation, we are using the mutate method we added to the toolbox
            offspring, = toolbox.mutate(offspring)

            offspring = Organism(
                x=self.x,
                y=self.y,
                energy=child_energy,
                individual=offspring,
                generation=child_generation
            )
            return offspring
        return None

    def is_dead(self):
        """If energy <= 0, organism is considered dead."""
        return self.energy <= 0

# -----------------------
# Environment Setup
# -----------------------
def create_food_grid(width, height):
    """
    Initialize a grid indicating where food is available.
    We start with a random distribution of food.
    """
    grid = []
    for _ in range(height):
        row = [1 if random.random() < 0.1 else 0 for _ in range(width)]
        grid.append(row)
    return grid

def create_initial_population(n, width, height, toolbox):
    """Create n organisms in random positions."""
    population = []
    for _ in range(n):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        organism = Organism(
            x=x,
            y=y,
            energy=INITIAL_ENERGY,
            generation=0
        )
        population.append(organism)
    return population

# -----------------------
# Simulation Loop
# -----------------------
def run_simulation():
    # Create environment
    food_grid = create_food_grid(GRID_WIDTH, GRID_HEIGHT)

    # Create initial population
    organisms = create_initial_population(INITIAL_POPULATION, GRID_WIDTH, GRID_HEIGHT, toolbox)

    # Prepare CSV logging
    output_file = "results.csv"
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Add columns for population, average speed, average generation
        writer.writerow(["Timestep", "PopulationSize", "AverageSpeed", "AverageGeneration"])

        # Log initial state (t=0)
        pop_size = len(organisms)
        avg_speed = average_speed(organisms)
        avg_gen = average_generation(organisms)
        writer.writerow([0, pop_size, avg_speed, avg_gen])
        print(f"Timestep 0: Pop={pop_size}, AvgSpeed={avg_speed:.2f}, AvgGen={avg_gen:.2f}")

        # Main simulation loop
        for t in range(1, TIMESTEPS + 1):
            # 1. Movement
            for org in organisms:
                org.move(GRID_WIDTH, GRID_HEIGHT)

            # 2. Eating
            for org in organisms:
                org.eat(food_grid)

            # 3. Reproduction
            new_babies = []
            for org in organisms:
                baby = org.reproduce()
                if baby:
                    new_babies.append(baby)
            organisms.extend(new_babies)

            # 4. Death check
            organisms = [org for org in organisms if not org.is_dead()]

            # 5. Food regeneration
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if food_grid[y][x] == 0:
                        if random.random() < FOOD_REGEN_PROB:
                            food_grid[y][x] = 1

            # Collect stats
            pop_size = len(organisms)
            avg_speed = average_speed(organisms)
            avg_gen = average_generation(organisms)

            # Log to CSV
            writer.writerow([t, pop_size, avg_speed, avg_gen])
            print(f"Timestep {t}: Pop={pop_size}, AvgSpeed={avg_speed:.2f}, AvgGen={avg_gen:.2f}")

    print(f"Simulation complete. Results written to {output_file}.")

# -----------------------
# Helper Functions
# -----------------------
def average_speed(organisms):
    """Compute average speed across living organisms."""
    if len(organisms) == 0:
        return 0
    return sum(org.individual[0] for org in organisms) / len(organisms)

def average_generation(organisms):
    """Compute average generation across living organisms."""
    if len(organisms) == 0:
        return 0
    return sum(org.generation for org in organisms) / len(organisms)

# -----------------------
# Main Entry Point
# -----------------------
if __name__ == "__main__":
    run_simulation()
