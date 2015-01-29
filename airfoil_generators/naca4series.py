"""
Generates NACA 4 series airfoil.
For an explanation on equations used, see NASA Technical Memorandum 4741
Short explanation:
http://web.stanford.edu/~cantwell/AA200_Course_Material/
The%20NACA%20airfoil%20series.pdf
"""

from __future__ import division
import numpy as np
from airfoilgen_baseclass import ParametricAirfoil

class NACA4(ParametricAirfoil):

    def __init__(self, m, p, t):
        """Takes maximum camber m, position of max. camber in tenths of chord,
           and thickness in percent."""
        self.m = m/100
        self.p = p/10
        self.t = t/100

    def _camberline(self, xpts):
        m, p = self.m, self.p
        if m == 0:
            return np.zeros(len(xpts))
        elif m!=0 and p==0:
            raise Warning(
            "Position of max camber is zero while camber is nonzero.")
        else:
            xpts0 = xpts[xpts<=p]
            xpts1 = xpts[xpts>p]
            # From x=0 to x=p
            y_c0 = m/p**2 * (2*p*xpts0 - xpts0**2)
            # From x=p to x=c
            y_c1 = m/(1-p)**2 * ((1-2*p)+2*p*xpts1 - xpts1**2)
            return np.append(y_c0, y_c1)

    def _thickness(self, x):
        t = self.t
        c = (.2969, .1260, .3516, .2843, .1015)
        y_t = t/.2 * (c[0]*x**.5-c[1]*x-c[2]*x**2+c[3]*x**3-c[4]*x**4)
        return y_t
    
    def __str__(self):
        return ("""NACA 4-series (camber {}, pos. {}, thickness {})"""
        .format(self.m, self.p, self.t))


def _example():
    '''Runs an example.'''
    c,l,t = 8,4,15
    test_airfoil = NACA4(c, l, t)

    # Get and print plain list of coordinates
    print test_airfoil

    pts = test_airfoil.get_coords()

    import matplotlib.pyplot as plt
    plt.title("NACA {}{}{}".format(c, l, t))
    plt.plot(pts[0], pts[1], 'o--')
    plt.plot(pts[2], pts[3], 'o--')
    plt.plot(pts[4], pts[5], 'o--')
    plt.gca().axis('equal')
    plt.show()


# If this file is run, execute example
if __name__ == "__main__":
    _example()
