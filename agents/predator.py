from base import BaseAgent
from config import SimulationConfig
from vector2D import vector2D
from boid import Boid
import random
import math

class Predator(BaseAgent):
    def __init__(self, position: vector2D, velocity: vector2D, config: SimulationConfig):
        super().__init__(
            position=position,
            velocity=velocity,
            max_speed=config.predator_max_speed,
            max_force=config.predator_max_force,
            perception_radius=config.predator_perception_radius
        )
        # How many boids the predator has caught
        self.kills = 0
        # Wandering angle for the predator, if no prey found
        # Start it in a random direction
        self._wander_angle = random.uniform(0, 2 * math.pi) # Private variable (albeit it should be a double leading underscore)

    ####################################
    # Private Methods
    ####################################

    def _wander(self):
        """
        This will take the predator's heading angle and nudge it by a small random amount each tick, so it will drift when there is no prey
        The steering force is then returned in that direction
        """
        # Nudge the angle by a small random amount
        self._wander_angle += random.uniform(-0.5, 0.5)

        # Change this angle into a directional vector, using cos and sin
        x = math.cos(self._wander_angle)
        y = math.sin(self._wander_angle)
        nudged_angle = vector2D(x, y)

        return self.steer_towards(nudged_angle * 0.5)

    ###########################################
    # Public Methods
    ########################################### 

    def compute_steering(self, config: SimulationConfig, grid):
        """
        Method will override the base agent class, and do the following:
            1. Query nearby agents from the grid
            2. Find the nearest and alive boid within its perception radius
            3. If a boid is found: compute the "wrapped_offset" and steer towards it (chase it). 
               - If the dist is within the kill radius, then the boid is killed
            4. If no boid is found: a gentle "wander" force is applied 
        """
        closest_distance = float('inf')
        prey = None

        for agent in grid:
            if isinstance(agent, Boid) and agent.alive:
                offset_vector = self.position.wrapped_offset(agent.position, config.width, config.height) 
                offset_distance = offset_vector.magnitude()

                if offset_distance <= self.perception_radius and offset_distance < closest_distance:
                    closest_distance = offset_distance
                    prey = agent

        # Found prey/boid
        if prey is not None:
            # Recompute the wrapped offset - vector and distance
            # And, steer towards the prey
            offset_vector = self.position.wrapped_offset(prey.position, config.width, config.height)
            self.apply_force(self.steer_towards(offset_vector))
            offset_distance = offset_vector.magnitude()
            # If the prey is within the predator kill radius, then kill it
            if offset_distance <= config.predator_kill_radius:
                prey.alive = False
                self.kills += 1
        else:
            # Apply the wander force
            nudge_force = self._wander()
            self.apply_force(nudge_force)