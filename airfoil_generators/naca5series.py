"""
Generates NACA 5 series airfoil.
For an explanation on equations used, see NASA Technical Memorandum 4741
Short explanation: http://web.stanford.edu/~cantwell/AA200_Course_Material/
The%20NACA%20airfoil%20series.pdf
"""

from __future__ import division
import numpy as np
from naca4series import NACA4

# Inherits the thickness profile from the NACA 4-series
class NACA5(NACA4):
    # mean-line designation, position max. camber (p), m, k1
    lookup_table = np.array(
       ((10, .05, .0580, 361.400),
        (20, .10, .1260,  51.640),
        (30, .15, .2025,  15.957),
        (40, .20, .2900,   6.643),
        (50, .25, .3910,   3.230)))

    def __init__(self, cl23, p, t):
        """Takes maximum camber m, position of max. camber in tenths of chord,
           and thickness in percent."""
        self.t  = t/100
        try:
            # Some magic to get right values from lookup_table
            mld = self.lookup_table.T[0]
            self.p, self.m, self.k1 = self.lookup_table[mld==p][0][1:]
            # Values in lookup_table are for a Cl of .3 (thus with a cl2/3
            # of .2, e.g. NACA2xxxxx). From NASA Technical
            # Memorandum 4741: "The value of k 1 can be linearly scaled to
            # give any desired design lift coefficient."
            self.k1 *= (cl23/2)
        except IndexError:
            raise Warning("2nd and 3rd digit must be 10, 20, 30, 40 or 50.")

    def _camberline(self, xpts):
        """Still needs to be implemented. See
        https://www.unibw.de/lrt13_1/lehre/xtras/profildaten/nasa-tm-4741.pdf"""
        k1, m = self.k1, self.m
        x0 = xpts[xpts<self.p]
        x1 = xpts[xpts>self.p]
        # From x=0 to x=p
        y_c0 = k1/6 * (x0**3 - 3*m*x0**2 + m**2*(3-m)*x0)
        # From x=p to x=c
        y_c1 = k1*m**3/6 * (1-x1)
        return np.append(y_c0, y_c1)


def _example():
    '''Runs an example.'''
    cl23, p, t = 2, 30, 15
    test_airfoil = NACA5(cl23, p, t)

    # Get and print plain list of coordinates
    print test_airfoil

    # Get list of coordinates
    pts = test_airfoil.get_coords()

    import matplotlib.pyplot as plt
    plt.title("NACA {}{}{}".format(cl23, p, t))
    plt.plot(pts[0], pts[1], 'o--')
    plt.plot(pts[2], pts[3], 'o--')
    plt.plot(pts[4], pts[5], 'o--')
    plt.gca().axis('equal')
    plt.show()


# If this file is run, execute example
if __name__ == "__main__":
    _example()
