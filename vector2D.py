import math

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
        return math.sqrt(self.x**2+self.y**2)

    def magnitude_sq(self):
        """Returns the squared length"""
        return (self.x**2+self.y**2)    # This prevents the expensive square root done in the magnitude function

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
            return vector2D(self.x/self.magnitude(), self.y/self.magnitude())
        
    def limit(self, ceiling):
        """Returns a copy of the vector, with its magnitude within a ceiling"""

        # If the magnitude is greater then the ceiling
        if self.magnitude() > ceiling:
            # Clamp the magnitude to the ceiling
            pass
        # If the magnitude is already shorter then the ceiling, return the unchanged copy
        else: 
            return vector2D(self.x, self.y)

    def distance_to(self, other):
        """Returns the Euclidean distance between two vectors"""

    def distance_sq_to(self, other):
        """Returns the squared distance"""