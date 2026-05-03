from base import BaseAgent
from vector2D import vector2D
from config import SimulationConfig
import time

class Food(BaseAgent):
    def __init__(self, position: vector2D, config: SimulationConfig):
        super().__init__(
            position=position,
            velocity=vector2D(0, 0),
            max_speed=0,
            max_force=0,
            perception_radius=0
        )
        # Whether the food is available to eat or not
        self.active = True
        # Timestamp for recording when food was last eaten, will be used for food respawning
        self._eaten_timestamp = None

    ####################################
    # Private Methods
    ####################################

    def consume(self):
        "Once food is consumed, turn it to inactive and record the timestamp of its consumption"
        self.active = False
        self._eaten_timestamp = time.time()

    ###########################################
    # Public Methods
    ########################################### 

    def try_respawn(self, config: SimulationConfig):
        """
        Check the respawn time from the food's consumption
        Set to active if enough time has passed and randomise its position
        """
        if not self.active and self._eaten_timestamp is not None:
            current_time = time.time()
            time_elapsed = current_time - self._eaten_timestamp

            if time_elapsed >= config.food_respawn_time:
                self.active = True
                self.position = vector2D.random_position(config.width, config.height)

    def compute_steering(self, config: SimulationConfig, grid):
        """Overridden to do nothing, as food doesn't steer"""
        pass

    def update(self, config: SimulationConfig, grid):
        """Overridden to only call the try_respawn method"""
        self.try_respawn(config)

    def to_dict(self):
        """
        Return a dictionary with keys 'x', 'y', and 'active'
        This will be sent to the browser as JSON
        """
        return {
            "x": round(self.position.x, 1), 
            "y": round(self.position.y, 1), 
            "active": self.active
        }