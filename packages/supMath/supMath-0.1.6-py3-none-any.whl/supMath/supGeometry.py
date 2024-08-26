"""
Priovides geometrical formuals from advMath module
"""
def pythagor(a,b):
    """
    Hypotenuse of a right triangle is calculated
    using this formula: c**2 = a**2 + b**2, where a and b
    are legs of a right triangle and c is hypotenuse.

    """
    def sqrt(d):
        return float(d**0.5)
    c = a**2 + b**2
    return sqrt(c)

def circumfer(r):
    """
    Returns the circumference of a circle with radius given:
        
          C = 2*pi*r.
    """
    return 2 * 3.141 * r

def circle_area(r):
    """
    Returns circle's area with radius given:

        S = pi*r**2.
    """
    return 3.141*(r**2)

def sector_area(r,angle):
    """
    Returns circle sector's area with angle and radius given:

        S(sector) = ( (pi*r**2)/360 ) * angle
    """
    return ((3.141*r**2)/360)*angle