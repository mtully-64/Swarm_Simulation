from agents import Boid, Predator, Food
from spatial_hash import SpatialHash 
from config import SimulationConfig
from vector2D import vector2D
import time

class World:
    """
    This class creates the World that owns all agents, the spatial hash, and orchestrates the simulation
    """
    def __init__(self, config: SimulationConfig):
        # Creating the spatial hash grid
        self.spatial_hash_grid = SpatialHash(config.cell_size, config.width, config.height)
        
        # Creating empty lists of agents - will be made via composition later 
        self.boids = list()
        self.predators = list()
        self.food = list()

        # Spawning in the initial agents at random positions
        self._spawn_initial_agents(config)

        # Tick counter, incremented by 1 everytime "tick()" will be called
        self.tick_counter = int(0)

        # Last tick timestamp
        self._last_tick_time = time.time()

        # FPS tracker
        self._FPS = 0.0

    ####################################
    # Private Methods
    ####################################

    def _spawn_initial_agents(self, config: SimulationConfig):
        """Private method to spawn agents"""

        for _ in range(config.num_boids):
            # Position of the boid is set randomly
            position = vector2D.random_position(config.width, config.height)

            # Velocity of the boid is random scaled to the max speed, starting pointing in different directions too
            # Cannot start the speed at zero until their flocking behaviour begins, as it would look dead
            # Cannot start the speed at max until their flocking behaviour, as it looks terrible
            velocity = vector2D.random_unit() * (config.boid_max_speed * 0.5)

            # Append the boids to the world's list
            self.boids.append(Boid(position, velocity, config))

        for _ in range(config.num_predators):   
            position = vector2D.random_position(config.width, config.height)
            velocity = vector2D.random_unit() * (config.predator_max_speed * 0.5)
            self.predators.append(Predator(position, velocity, config))

        for _ in range(config.num_food):
            position = vector2D.random_position(config.width, config.height)
            self.food.append(Food(position, config))

    ####################################
    # Public Methods
    ####################################
        
    def tick(self, config: SimulationConfig):
        """
        Advances the simulation by one frame, and performs the following:
            - Clears the spatial hash and re-inserts living boids, predators and food
            - Updates every live boid
            - Updates every predator
            - Updates every food source
            - Processes the food consumption
            - Respawns dead boids
            - Increments the tick counter and computes the FPS
        """
        # Clear the spatial hash grid
        self.spatial_hash_grid.clear()

        # Reinserting the agents
        for boid in self.boids:
            if boid.alive:
                self.spatial_hash_grid.insert(boid)
        for predator in self.predators:
            self.spatial_hash_grid.insert(predator)
        for food in self.food:
            if food.active:
                self.spatial_hash_grid.insert(food)

        # Update every agent
        for boid in self.boids:
            boid.update(config, self.spatial_hash_grid)
        for predator in self.predators:
            predator.update(config, self.spatial_hash_grid)
        for food in self.food:
            food.update(config, self.spatial_hash_grid)

        # Process food consumption
        for food in self.food:
            if food.active:
                for boid in self.boids:
                    if boid.alive:
                        boid_food_offset = boid.position.wrapped_offset(food.position, config.width, config.height)
                        if boid_food_offset.magnitude() < config.food_consume_radius:
                            food.consume()
                            break # So only one boid consumes each food per tick

        # Respawn dead boids
        for i, boid in enumerate(self.boids):
            if not boid.alive:
                # Replace with a boid in a random position to keep the population stable
                position = vector2D.random_position(config.width, config.height)
                velocity = vector2D.random_unit() * (config.boid_max_speed * 0.5)
                self.boids[i] = Boid(position, velocity, config)

        # Tick counter
        now = time.time()
        dt = now - self._last_tick_time
        self._FPS = 1.0 / dt if dt > 0 else 0.0
        self._last_tick_time = now
        self.tick_counter += 1

    def snapshot(self):
        """
        Returns a dictionary that contains the entire world state, suited for JSON serialisation
        It will include:
            - 'boids' a list of to_dict() for all alive boids
            - 'predators' a list of to_dict() for all predators
            - 'food' a list of to_dict() for all food sources
            - 'stats' a dict with fps, tick, alive_boids, and total_kills
        """
        # Simulation stats
        stats = {"fps": round(self._FPS, 1), "tick": self.tick_counter, "alive_boids": sum(1 for b in self.boids if b.alive), "total_kills": sum(p.kills for p in self.predators)}

        snapshot = {
            "boids": [b.to_dict() for b in self.boids if b.alive],
            "predators": [p.to_dict() for p in self.predators],
            "food": [f.to_dict() for f in self.food],
            "stats": stats
        }

        # Return the dict of world state
        return snapshot