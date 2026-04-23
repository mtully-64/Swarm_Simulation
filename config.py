from dataclasses import dataclass

@dataclass
class SimulationConfig:
    """
    This is a dataclass, a class that allows you to store data (.__init__(), .__repr__(), and __eq__(), are generated automatically)
    This object will store every tunable number for this entire project, where no code should have a 'magic' number
    """

    ###############################
    # World params
    ###############################
    width: int = 1400 # world width
    height: int = 800 # world height

    ###############################
    # Boid params
    ###############################
    num_boids: int = 120 # no. of boids to spawn
    boid_max_speed: float = 4.0 # max velocity magnitude
    boid_max_force: float = 0.3 # max steering force magnitude
    boid_perception_radius: float = 80.0 # how far the boid can see neighbours to
    separation_radius: float = 30.0 # tighter radius for the separation rule
    separation_weight: float = 1.5 # multiplier for separation force
    alignment_weight: float = 1.0 # multiplier for alignment force
    cohesion_weight: float = 1.0 # multiplier for cohesion force
    flee_weight: float = 2.5 # multiplier for predator flee force
    seek_food_weight: float = 1.2 # multiplier for food seeking force

    ###############################
    # Predator params
    ###############################
    num_predators: int = 2
    predator_max_speed: float = 3.2 # should be slower than a boid
    predator_max_force: float = 0.15
    predator_perception_radius: float = 160.0
    predator_kill_radius: float = 12.0

    ###############################
    # Food params
    ###############################
    num_food: int = 8
    food_attraction_radius: float = 160.0
    food_consume_radius: float = 10.0
    food_respawn_time: float = 6.0 # 6 seconds

    ###############################
    # Simulation params
    ###############################
    tick_rate: float = 1/60 # time inbetween ticks in seconds
    cell_size: float = 100.0 # spatial hash cell size