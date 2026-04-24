from base import BaseAgent
from vector2D import vector2D
from config import SimulationConfig

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

    def compute_steering(self, config, grid):
        """
        Method will override the base agent class, and implement five local steering behaviours:
            1. Spatial hash grid to get nearby candidates
            2. For each candidate, the "wrapped_offset" is computed and the distance. Then classify it as a neighbour, predator or a food source
            3. Call each of five behaviour methods
            4. Multiply each result by its corresponding weight (found in config.py)
            5. Apply each weighted force
        """
        pass
    
    #############################
    # Behaviour Methods
    #############################
    def _separation(self, neighbours, config: SimulationConfig):
        """
        Steer away from boids that are within the "separation_radius", not the "perception_radius"
        For each neighbour too close, compute a vector for repulsion 
        Negating the offset direction and dividing by distance (closer pushes harder)
        """
        steer_vector = vector2D(0,0)
        count = 0
        
        for neighbour in neighbours:
            offset_vector = self.position.wrapped_offset(neighbour.position, config.width, config.height)
            offset_distance = offset_vector.magnitude()
            if offset_distance < config.separation_radius and offset_distance > 0:
                # Negate and normalise
                offset_vector = -offset_vector 
                offset_vector = offset_vector.normalize()

                # Divide by distance, as closer will mean a stronger push away
                offset_vector = offset_vector/offset_distance
                steer_vector += offset_vector
                
                count += 1

        if count > 0:
            steer_vector = steer_vector/count
            return self.steer_towards(steer_vector)
        else:
            return vector2D(0, 0)

    def _alignment(self, neighbours, config: SimulationConfig):
        pass

    def _cohesion(self, neighbours, config: SimulationConfig):
        pass

    def _flee(self, predators, config: SimulationConfig):
        pass

    def _seek_food(self, foods, config: SimulationConfig):
        pass