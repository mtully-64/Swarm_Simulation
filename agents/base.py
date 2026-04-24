from abc import ABC, abstractmethod
from vector2D import vector2D
from config import SimulationConfig

class BaseAgent(ABC):
    """
    Abstract class that all moving entities will inherit from in the simulation
    """
    def __init__(self, position: vector2D, velocity: vector2D, max_speed: float, max_force: float, perception_radius: float):
        """Instance variables"""
        self.position = position # the agent's current location in the world
        self.velocity = velocity # the agent's current movement direction and speed
        self.acceleration = vector2D(0, 0) # accumulated force for the tick, starting at zero for each frame
        self.max_speed = max_speed
        self.max_force = max_force # the max magnitude of any single steering force
        self.perception_radius = perception_radius # how far the agent can see

    @abstractmethod
    def compute_steering(self, config: SimulationConfig, grid):
        """
        This is where subclasses outline their own steering behaviours
        """
        pass

    def update(self, config: SimulationConfig, grid):
        """
        This method is called once per tick
        It executes four steps in a specific order
            1. Reset the self.acceleration to a zero vector
            2. Call "self.compute_steering(config, grid)", an abstract method
            3. Add acceleration to velocity, then clamp the velocity to the "max_speed" using the "limit()" method, then add velocity to the position
            4. Wrap the position with all the world boundaries
        """
        # 1. Reset acceleration
        self.acceleration = vector2D(0, 0)

        # 2. Call the method for steering
        self.compute_steering(config=config, grid=grid)

        # 3. Preform the physics
        self.velocity += self.acceleration
        self.velocity = self.velocity.limit(self.max_speed)
        self.position += self.velocity

        # 4. Wrap the position with the world boundaries
        #    - If position x is 1410 and the width of the world is 1400, then 1410 % 1400 = 10 (so agent should be at 10)
        self.position.x %= config.width
        self.position.y %= config.height

    def apply_force(self, force: vector2D):
        """Adds the given force vector to acceleration vector"""
        self.acceleration += force

    def steer_towards(self, target: vector2D):
        """
        Steering formula calculates the force required for an autonomous agent to move from its current trajectory to a new desired trajectory
        It takes the target direction vector and returns a steering force
        Calculation:
            - Get the desired velocity, by normalising the target vector and then scaling it to max_speed
            - Get the steering force, done by desired velocity minus current velocity
            - Clamp the steering force to the "max_force"
            - Return the clamped steering force 
        """
        desired_velocity = target.normalize() * self.max_speed
        steering_force = desired_velocity - self.velocity
        steering_force = steering_force.limit(self.max_force)
        return steering_force
    
    def to_dict(self):
        """
        Return a dictionary with keys 'x', 'y', 'vx', 'vy' that contain rounded position and velocity values
        This will be sent to the browser as JSON
        """
        return {
            "x": round(self.position.x, 1), 
            "y": round(self.position.y, 1), 
            "vx": round(self.velocity.x, 2), 
            "vy": round(self.velocity.y, 2)
        }