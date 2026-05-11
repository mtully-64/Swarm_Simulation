"""
With 120 boids, I realised that I cannot distance check every agent against every other agent for each tick
That would be 120 x 120 = 14,400 checks per frame!
That is O(n^2) for anyone that cares about optimisation

Instead - a spatial hash grid
This divides the world into a grid of cells
Each tick, every agent is put into a cell based on its position
When a boid wants to find nearby agents, then it only searchs the cells that overlap its perception circle (not the entire world)
"""

from collections import defaultdict
from agents.base import BaseAgent

class SpatialHash:
    def __init__(self, cell_size: float, width: float, height: float):
        # Width and height of each cell
        self.cell_size = cell_size
        # World width
        self.width = width
        # World height
        self.height = height
        # Internal dictionary for tracking agents
        # Dictionary -> (col, row) tuples for list of agents
        self._cells = defaultdict(list) # defaultdict allows me to create a dict that doesnt throw a KeyError if I call a key that doesn't exist

        self.cols = width // cell_size
        self.rows = height // cell_size

    def clear(self):
        """
        This will empty the internal dictionary for tracking agents
        This will be called at the start of every tick before re-inserting agents
        """
        self._cells.clear()

    def insert(self, agent: BaseAgent):
        """
        Computes which cell the agent should belong to based on its position
        Then it appends the agent to the internal dictionary
        """
        col = int(agent.position.x // self.cell_size) % self.cols
        row = int(agent.position.y // self.cell_size) % self.rows

        # Now append the agent into the dict
        self._cells[(col, row)].append(agent) # The key in which we use to query is location (what agent is present at a cell)

    def query_radius(self, x: float, y: float, radius: float):
        """
        Return a list of all agents in cells that 'could' be overlapping a circle (center is x, y with a given radius)
        Calculating how many cells that the radius spans, then checking all the cells in that range from the centre cell
        Handling the torodial boundaries is needed too

        This is like a broadphase filter to reduce the candidates from 120 to a handful
        The caller will still be forced to do a more precise distance check
        """
        # List of agents that potentially overlap
        overlap_agents = list()

        # Find the centre cell and its spanning radius
        centre_col = int(x // self.cell_size) % self.cols
        centre_row = int(y // self.cell_size) % self.rows
        radius_span = (int(radius // self.cell_size) + 1)

        # From the centre point (x,y), you need to search in a square
        """
        - When we are searching we can either stay in the centre, left or right
        - Therefore, it is either '0', '-1', or '1'
        - You search the rows (delta row) or the columns (delta col)  
        """
        for delta_col in range(-radius_span, radius_span + 1):
            for delta_row in range(-radius_span, radius_span + 1):
                # Therefore delta_col and delta_row are the offets from the centre cell
                col = (centre_col + delta_col) % self.cols # the modulo is to do the torodial wrapping again
                row = (centre_row + delta_row) % self.rows

                # Grab any agents in that cell and add them to the list of overlapping
                overlap_agents.extend(self._cells.get((col, row), []))

        # Return the list of agents
        return overlap_agents