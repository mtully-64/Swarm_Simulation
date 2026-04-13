import math
import random

class vector2D:
    """
    A 2D vector is defined by both magnitude and direction.
        Example - the force of thrust from a plane's engine is strength of that force, and direction in which it is applied.
    """
    def __init__(self, x:float, y:float):
        # x is a float that represents the horizontal
        self.x = x
        # y is a float that represents the vertical
        self.y = y

    ####################
    # Magic Methods
    ####################

    def __add__(self, other):
        return vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar:float):
        return vector2D(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar:float):
        """This magic method looks for the usual __mul__ but in the left operand, so __rmul__ is the right operand"""
        return self.__mul__(scalar) # Just delegate it to the __mul__ method
    
    def __truediv__(self, scalar:float):
        """
        __truediv__ = divison that returns a float ("/")
        __floordiv__ = division that returns the quotient ("//")

        Returns a new Vector2D divided by the float
        If the scalar is 0 then it returns a zero vector
        """
        if scalar == 0:
            return vector2D(0,0)
        else:
            return vector2D(self.x / scalar, self.y / scalar)
        
    def __neg__(self):
        """
        Returns the negated vector
        """
        return vector2D(self.x * -1, self.y * -1)
    
    ####################
    # Utility Methods
    ####################

    def magnitude(self):
        """Returns the length of the vector as a float"""
        return math.sqrt(self.x**2 + self.y**2)

    def magnitude_sq(self):
        """Returns the squared length"""
        return (self.x**2 + self.y**2)    # This prevents the expensive square root done in the magnitude function

    def normalize(self):
        """
        Returns a new unit vector pointing in the same direction
        If the magnitude is 0 then it returns a zero vector
        """

        # If the magnitude is 0
        if self.magnitude() == 0:
            # Return a zero vector
            return vector2D(0, 0)
        # Else, if the magnitude is not 0
        else:
            # Return new vector with a magnitude of 1, while keeping it in the same direction
            return vector2D(self.x / self.magnitude(), self.y / self.magnitude())
        
    def limit(self, ceiling):
        """Returns a copy of the vector, with its magnitude within a ceiling"""

        # If the magnitude is greater then the ceiling
        if self.magnitude() > ceiling:
            # Clamp the magnitude to the ceiling
            # Therefore, take the normalised vector to keep direction and a magnitude of 1, and multiply it by the ceiling
            return self.normalize()*ceiling
        # If the magnitude is already shorter then the ceiling, return the unchanged copy
        else: 
            return vector2D(self.x, self.y)

    def distance_to(self, other):
        """Returns the Euclidean distance between two vectors"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def distance_sq_to(self, other):
        """Returns the squared distance"""
        return (self.x - other.x)**2 + (self.y - other.y)**2
    
    # The simulation world wraps around on itself, like Pac-Man
    # This means that if an agent walks off the right side of the map, then it appears on the left
    # This is called a "toroidal" world
    def wrapped_offset(self, other, width, height):
        """
        Returns a new vector
        Representing the shortest path from self to other, on a toroidal surface of the given width and height

        E.g. if the world is a width of 1000 pixels, an object is at x=950 (near right edge) and its neighbour is at x=50 (near left edge)
        Then the naive distance is 950-50=900px apart, but since the world wraps around, they're actually only 100 pixels apart

        For each axis, if the raw difference is more then half the world size, then subtract the world size
        If less than negative half, add the world size
        """
        
        dx = other.x - self.x # The difference in x
        dy = other.y - self.y # The difference in y

        ####################
        # Difference in x
        ####################

        # If the difference is bigger than half the world size,
        # The short path is the other way
        if dx > (0.5*width):
            dx = dx - width
        # If the difference is less than negative half the world size,
        # Add the world size
        elif dx < ((-width)*0.5):
            dx = dx + width

        ####################
        # Difference in y
        ####################

        if dy > (0.5*height):
            dy = dy - height
        elif dy < ((-height)*0.5):
            dy = dy + height

        # Now return a vector2D with those dx and dy values
        return vector2D(dx, dy)
    
    ####################
    # Static Methods
    ####################

    # These methods will create and return brand new vector2D instances
    # Hence these will be static methods
    
    @staticmethod
    def random_position(x_max:float, y_max:float):
        """Returns a vector with random x value and random y value"""
        x = random.uniform(0, x_max) # uniform is randint for floats instead of integers
        y = random.uniform(0, y_max)

        return vector2D(x, y)
        
    @staticmethod
    def random_unit():
        """Returns a vector of length 1 pointing in a random direction"""
        # Calculate a random angle, where angle is random from [0, 2*pi]
        max_value = 2*math.pi
        angle = random.uniform(0, max_value)

        x = math.cos(angle)
        y = math.sin(angle)

        # Return vector now with the random direction and length will be 1
        return vector2D(x, y)