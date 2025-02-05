#!/usr/bin/env python3
"""
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
GRID_WIDTH = 20  # Width of the grid
GRID_HEIGHT = 20  # Height of the grid
INITIAL_POPULATION = 10
INITIAL_ENERGY = 10

# Movement & Energy
BASE_MOVE_COST = 1  # Base energy cost per "step"
EAT_GAIN = 5  # Energy gained from eating one food unit
REPRODUCTION_THRESHOLD = 20  # Energy needed to reproduce
TIMESTEPS = 80
FOOD_REGEN_PROB = 0.01  # Probability that an empty cell spawns food each turn

# Genome & Mutation
MUTATION_RATE = 0.1  # Probability of a mutation happening on reproduction
GENE_SPEED_INITIAL = 1  # Initial speed for all organisms (you can randomize if desired)
GENE_SPEED_MIN = 0  # Minimum allowed speed
GENE_SPEED_MAX = 5  # Maximum allowed speed (optional clamp)
GENE_METABOLISM_MIN = 0.5  # Minimum allowed metabolism (50% of base move cost)
GENE_METABOLISM_MAX = 2.0  # Maximum allowed metabolism (200% of base move cost)
GENE_VISION_MIN = 1  # Minimum allowed vision
GENE_VISION_MAX = 5  # Maximum allowed vision

# For reproducibility, uncomment:
# random.seed(42)

# -----------------------
# **DEAP Setup**
# -----------------------


# Define a fitness function (this might need adjustment based on your needs)
def evaluate(individual):
    # Fitness is a combination of speed, metabolism, vision, and offspring count
    speed = individual[0]
    metabolism = individual[1]
    vision = individual[2]
    offspring_count = individual.offspring_count
    fitness = (
        speed - (metabolism * BASE_MOVE_COST) + (vision * 0.5) + (offspring_count * 2)
    )
    return (fitness,)


# Create a fitness class that minimizes the value, for example
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# Create the Individual class, inheriting from the list class.
# You can replace the single speed value with a more complex genome.
creator.create("Individual", list, fitness=creator.FitnessMax)

# Initialize the toolbox
toolbox = base.Toolbox()

# Register the individual creator, mutation, and selection
toolbox.register(
    "individual",
    tools.initRepeat,
    creator.Individual,
    lambda: [
        random.randint(GENE_SPEED_MIN, GENE_SPEED_MAX),  # Speed gene
        random.randint(GENE_METABOLISM_MIN, GENE_METABOLISM_MAX),  # Metabolism gene
        random.randint(GENE_VISION_MIN, GENE_VISION_MAX),
    ],  # Vision gene
    n=1,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# mutation operator
toolbox.register(
    "mutate",
    tools.mutGaussian,
    mu=[
        (GENE_SPEED_MIN + GENE_SPEED_MAX) / 2,
        (GENE_METABOLISM_MIN + GENE_METABOLISM_MAX) / 2,
        (GENE_VISION_MIN + GENE_VISION_MAX) / 2,
    ],
    sigma=[1, 0.1, 1],
    indpb=MUTATION_RATE,
)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)


def clamp_genes(individual):
    individual[0] = max(GENE_SPEED_MIN, min(GENE_SPEED_MAX, individual[0]))
    individual[1] = max(GENE_METABOLISM_MIN, min(GENE_METABOLISM_MAX, individual[1]))
    individual[2] = max(GENE_VISION_MIN, min(GENE_VISION_MAX, individual[2]))
    return individual


toolbox.register(
    "mutate",
    tools.mutGaussian,
    mu=[
        (GENE_SPEED_MIN + GENE_SPEED_MAX) / 2,
        (GENE_METABOLISM_MIN + GENE_METABOLISM_MAX) / 2,
        (GENE_VISION_MIN + GENE_VISION_MAX) / 2,
    ],
    sigma=[1, 0.1, 1],
    indpb=MUTATION_RATE,
)
toolbox.register("clamp_genes", clamp_genes)


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
        self.offspring_count = 0
        # if individual is not None, use that, otherwise create a random one.
        if individual is None:
            self.individual = creator.Individual(
                [
                    random.randint(GENE_SPEED_MIN, GENE_SPEED_MAX),  # Speed gene
                    random.uniform(
                        GENE_METABOLISM_MIN, GENE_METABOLISM_MAX
                    ),  # Metabolism gene
                    random.randint(GENE_VISION_MIN, GENE_VISION_MAX),  # Vision gene
                ]
            )
        else:
            self.individual = individual

    @property
    def speed(self):
        # this is how we get the speed of an organism from its genome
        return self.individual[0]

    @property
    def metabolism(self):
        return self.individual[1]

    @property
    def vision(self):
        return self.individual[2]

    def move(self, grid_width, grid_height, food_grid):
        """
        Move towards food if within vision range, or move randomly if not.
        Each step costs BASE_MOVE_COST energy.
        """
        food_direction = self.find_food(grid_width, grid_height, food_grid)
        if food_direction:
            self.move_towards_food(food_direction, grid_width, grid_height)
        else:
            self.move_randomly(grid_width, grid_height)

        # Pay energy cost for each step
        self.energy -= BASE_MOVE_COST * self.metabolism

    def find_food(self, grid_width, grid_height, food_grid):
        vision_range = int(self.vision)  # Convert vision to an integer
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                nx, ny = (self.x + dx) % grid_width, (self.y + dy) % grid_height
                if food_grid[ny][nx] == 1:
                    return (dx, dy)
        return None

    def move_towards_food(self, food_direction, grid_width, grid_height):
        dx, dy = food_direction
        if dx > 0:
            self.x = (self.x + 1) % grid_width
        elif dx < 0:
            self.x = (self.x - 1) % grid_width
        if dy > 0:
            self.y = (self.y + 1) % grid_height
        elif dy < 0:
            self.y = (self.y - 1) % grid_height

    def move_randomly(self, grid_width, grid_height):
        direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        if direction == "UP":
            self.y = (self.y - 1) % grid_height
        elif direction == "DOWN":
            self.y = (self.y + 1) % grid_height
        elif direction == "LEFT":
            self.x = (self.x - 1) % grid_width
        elif direction == "RIGHT":
            self.x = (self.x + 1) % grid_width

        # Pay energy cost for each step
        self.energy -= BASE_MOVE_COST * self.metabolism

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

            # create an offspring genome from an existing genome
            cloned_genome = toolbox.clone(self.individual)
            # apply mutation, we are using the mutate method we added to the toolbox
            (mutated_genome,) = toolbox.mutate(cloned_genome)
            mutated_genome = toolbox.clamp_genes(mutated_genome)

            offspring = Organism(
                x=self.x,
                y=self.y,
                energy=child_energy,
                individual=mutated_genome,
                generation=child_generation,
            )
            self.offspring_count += 1
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
        organism = Organism(x=x, y=y, energy=INITIAL_ENERGY, generation=0)
        population.append(organism)
    return population


# -----------------------
# Simulation Loop
# -----------------------
def run_simulation():
    # Create environment
    food_grid = create_food_grid(GRID_WIDTH, GRID_HEIGHT)

    # Create initial population
    organisms = create_initial_population(
        INITIAL_POPULATION, GRID_WIDTH, GRID_HEIGHT, toolbox
    )

    # Prepare CSV logging
    output_file = "results.csv"
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Add columns for population, average speed, average generation, average metabolism, average vision
        writer.writerow(
            [
                "Timestep",
                "PopulationSize",
                "AverageSpeed",
                "AverageGeneration",
                "AverageMetabolism",
                "AverageVision",
            ]
        )

        # Log initial state (t=0)
        pop_size = len(organisms)
        avg_speed = average_speed(organisms)
        avg_gen = average_generation(organisms)
        avg_metabolism = average_metabolism(organisms)
        avg_vision = average_vision(organisms)
        writer.writerow([0, pop_size, avg_speed, avg_gen, avg_metabolism, avg_vision])
        print(
            f"Timestep 0: Pop={pop_size}, AvgSpeed={avg_speed:.2f}, AvgGen={avg_gen:.2f}, AvgMetabolism={avg_metabolism:.2f}, AvgVision={avg_vision:.2f}"
        )

        # Main simulation loop
        for t in range(1, TIMESTEPS + 1):
            # 1. Movement
            for org in organisms:
                org.move(GRID_WIDTH, GRID_HEIGHT, food_grid)

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
            avg_metabolism = average_metabolism(organisms)
            avg_vision = average_vision(organisms)
            max_offspring = (
                max(org.offspring_count for org in organisms) if organisms else 0
            )

            # Log to CSV
            writer.writerow([t, pop_size, avg_speed, avg_gen])
            print(
                f"Timestep {t}: Pop={pop_size}, AvgSpeed={avg_speed:.2f}, AvgGen={avg_gen:.2f}, AvgMetabolism={avg_metabolism:.2f}, AvgVision={avg_vision:.2f}, maxOffspring={max_offspring}"
            )

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


def average_metabolism(organisms):
    """Compute average metabolism across living organisms."""
    if len(organisms) == 0:
        return 0
    return sum(org.individual[1] for org in organisms) / len(organisms)


def average_vision(organisms):
    """Compute average vision across living organisms."""
    if len(organisms) == 0:
        return 0
    return sum(org.individual[2] for org in organisms) / len(organisms)


# -----------------------
# Main Entry Point
# -----------------------
if __name__ == "__main__":
    run_simulation()
