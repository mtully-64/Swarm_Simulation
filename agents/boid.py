from base import BaseAgent
from vector2D import vector2D
from config import SimulationConfig
from food import Food
from predator import Predator

class Boid(BaseAgent):
    def __init__(self, position: vector2D, velocity: vector2D, config: SimulationConfig):
        super().__init__(
            position=position,
            velocity=velocity,
            max_speed=config.boid_max_speed,
            max_force=config.boid_max_force,
            perception_radius=config.boid_perception_radius
        )
        self.alive = True

    ###########################################
    # Private Methods - Behaviour Methods
    ###########################################
    
    # For boids that are too close, still keep a buffer zone
    def _separation(self, neighbours, config: SimulationConfig):
        """
        Steer away from boids that are within the "separation_radius", not the "perception_radius"
        For each neighbour too close, compute a vector for repulsion 
        Negating the offset direction and dividing by distance (closer pushes harder)
        """
        steer_vector = vector2D(0,0)
        count = 0
        
        # Neighbours is a list of neighbours
        for neighbour in neighbours:
            offset_vector = self.position.wrapped_offset(neighbour.position, config.width, config.height) # Direction neighbour is from the boid
            offset_distance = offset_vector.magnitude() # Distance neighbour is from the boid

            # If the neighbour is in the seperate vicinity
            if offset_distance < config.separation_radius and offset_distance > 0: # offset distance cannot be zero as I will hit a fucking division error
                # Negate and normalise
                offset_vector = -offset_vector # Flip the direction of the boid to point away
                offset_vector = offset_vector.normalize() # This means that length is 1, and all that matters is direction

                # Divide by distance, as closer will mean a stronger push away
                offset_vector = offset_vector/offset_distance
                steer_vector += offset_vector
                
                # Internal count to track how many neighbours the boid is now steering away from
                count += 1

        if count > 0:
            # I need to average all the pushes
            # As if I had 10 neighbours then I would be pushed x10 harder than having 1
            steer_vector = steer_vector/count
            # Return a new steering vector to the boid
            return self.steer_towards(steer_vector)
        else:
            # Else, if nothing in vicinity then I don't need to steer away
            return vector2D(0, 0)

    # Follow the overall direction of neighbour boids
    def _alignment(self, neighbours):
        """
        Steer towards the average velocity of all the visible neighbour boids
        This new velocity vector will be passed through "steer_towards"
        """
        avg_velocity = vector2D(0, 0)
        count = 0

        for neighbour in neighbours:
            avg_velocity += neighbour.velocity
            count += 1

        if count > 0:
            avg_velocity = avg_velocity / count
            return self.steer_towards(avg_velocity)
        else:
            # Else, if nothing in vicinity then I don't need to toward anything
            return vector2D(0, 0)

    # Join the mass of neighbour boids
    def _cohesion(self, neighbours, config: SimulationConfig):
        """
        Steer towards the centre of mass for all visible neighbours
        For each neighbour, get their "wrapped_offset" 
        Average these offsets for the centre direction and pass it through "steer_towards"

        This is similar to alignment but instead of average velocity, it is average position
        """
        centre_vector = vector2D(0, 0)
        count = 0

        for neighbour in neighbours:
            centre_vector += self.position.wrapped_offset(neighbour.position, config.width, config.height)
            count += 1

        if count > 0:
            # This is the average direction to the centre of the mass of neighbours
            centre_vector = centre_vector / count
            # Return the new steer towards the centre of the boids
            return self.steer_towards(centre_vector)
        else:
            return vector2D(0, 0)

    # Stay away from predators
    def _flee(self, predators, config: SimulationConfig):
        """
        Steer away from every visible
        For each predator, negate the offset direction and divide by distance
        Sum up all of these vectors and pass through "steer_towards"
        """
        steer_vector = vector2D(0, 0)
        count = 0

        for predator in predators:
            offset_vector = self.position.wrapped_offset(predator.position, config.width, config.height)
            offset_distance = offset_vector.magnitude()

            if offset_distance > 0: # I will hit a division by zero error if the boid was same position as predator
                # Negate and normalise
                offset_vector = -offset_vector
                offset_vector = offset_vector.normalize()

                # Divide by distance, as closer will mean a stronger push away
                offset_vector = offset_vector/offset_distance
                steer_vector += offset_vector
                    
                # Internal count to track how many neighbours the boid is now steering away from
                count += 1
        
        if count > 0:
            return self.steer_towards(steer_vector)
        else:
            return vector2D(0, 0)

    # Look for food
    def _seek_food(self, foods, config: SimulationConfig):
        """
        Steer to nearest active food source - food with the smallest "wrapped_offset"
        This will be passed through the "steer_towards"
        """
        nearest_food = None
        nearest_dist = float('inf') # Infinity ensures that any number that is compared, will be the replacement

        for food in foods:
            offset_vector = self.position.wrapped_offset(food.position, config.width, config.height)
            offset_distance = offset_vector.magnitude()

            if offset_distance < nearest_dist:
                nearest_dist = offset_distance
                nearest_food = offset_vector

        if nearest_food is not None:
            return self.steer_towards(nearest_food)
        else:
            return vector2D(0, 0)
        
    ###########################################
    # Public Methods
    ###########################################

    def compute_steering(self, config: SimulationConfig, grid):
        """
        Method will override the base agent class, and implement five local steering behaviours:
            1. Spatial hash grid to get nearby candidates
            2. For each candidate, the "wrapped_offset" is computed and the distance. Then classify it as a neighbour, predator or a food source
            3. Call each of five behaviour methods
            4. Multiply each result by its corresponding weight (found in config.py)
            5. Apply each weighted force
        """
        neighbours = []
        predators = []
        foods = []

        for agent in grid:
            if isinstance(agent, Boid) and agent is not self and agent.alive:
                neighbours.append(agent)
            elif isinstance(agent, Predator):
                predators.append(agent)
            elif isinstance(agent, Food):
                foods.append(agent)

        # Call each of the methods, multiplied by its weight set in the config
        self.apply_force(self._separation(neighbours, config) * config.separation_weight)
        self.apply_force(self._alignment(neighbours) * config.alignment_weight)
        self.apply_force(self._cohesion(neighbours, config) * config.cohesion_weight)
        self.apply_force(self._flee(predators, config)*config.flee_weight)
        self.apply_force(self._seek_food(foods, config) * config.seek_food_weight)
    