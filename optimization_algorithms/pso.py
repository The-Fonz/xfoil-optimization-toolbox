"""
    This file contains classes to handle Particle Swarm Optimization.
    Its abstraction level is such that it should be similar to thinking about
    the algorithm.

Great paper on parameter selection: http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
"""

# Make sure that 7/2=3.5
from __future__ import division
import numpy as np
# Import N(mu, sigma) and U[0,1) function
from numpy.random import normal, uniform
from copy import copy

class Particle():
    '''A particle is an array of constrained numbers.
       The constraint array c is organized as [[low,high],[low,high]].'''
    def __init__(self, constraints):
        self.constraints = constraints
        self.pts  = np.zeros(len(constraints), dtype="float")
        self.spds = np.zeros(len(constraints), dtype="float")
        # Randomize positions and speeds
        self.randomize()
        # Set current point as best
        self.new_best(float('inf'))

    def new_best(self, score):
        '''Stores new personal best score and position.'''
        self.bestscore = score
        self.bestpts = self.pts

    def randomize(self):
        '''Randomize with uniform distribution within bounds.'''
        # Iterate over self.pts
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            self.pts[i]  = uniform(lowerbound, upperbound)
            absrange = abs(upperbound-lowerbound)
            self.spds[i] = uniform(-absrange, absrange)

    def update(self, global_best, omega, theta_p, theta_g):
        '''Update velocity and position'''
        # Copy to prevent self.oldpts becoming reference to self.pts array
        self.oldpts  = copy(self.pts)
        self.oldspds = copy(self.spds)
        r_p, r_g = uniform(0,1), uniform(0,1)
        # v_i,d <- omega*v_i,d + theta_p*r_p*(p_i,d-x_i,d) + theta_g*r_g*(g_d-x_i,d)
        self.spds = (omega*self.spds + theta_p*r_p*(self.bestpts-self.pts) +
                       theta_g*r_g*(global_best-self.pts))
        self._boundspds()
        self.pts += self.spds
        self._boundpts()
    def rewind(self):
        '''Go back to previous velocity and position'''
        # Copy to prevent self.pts becoming reference to self.oldpts array
        try:
            self.pts  = copy(self.oldpts)
            self.spds = copy(self.oldspds)
        except NameError:
            raise Warning("Update was never called, so no rewidn possible.")

    def _boundpts(self):
        '''Restrict points to lowerbound<x<upperbound'''
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            pt = self.pts[i]
            if pt < lowerbound: self.pts[i] = lowerbound
            if pt > upperbound: self.pts[i] = upperbound
    def _boundspds(self):
        '''Restrict speeds to -range<v<range'''
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            spd = self.spds[i]
            absrange = abs(upperbound-lowerbound)
            if spd < -absrange: self.pts[i] = -absrange
            if spd >  absrange: self.pts[i] =  absrange

    def __str__(self):
        '''Print values of Particle.'''
        return ("Constraints: "+self.constraints.__str__()+
        "\nValues: "+self.pts.__str__())
    
    def APSO(self, global_best, B, a):
        '''A simplified way of PSO, with no velocity, updating the particle
           in one step. http://arxiv.org/pdf/1203.6577.pdf
           Typically, a = 0.1L ~ 0.5L where L is the scale of each variable,
           while B = 0.1 ~ 0.7 is sufficient for most applications'''
        self.oldpts  = copy(self.pts)
        self.oldspds = copy(self.spds)
        for i, pt in enumerate(self.pts):
            mu, sigma = 0, 1
            e = normal(mu, sigma)
            c = self.constraints[i]
            L = abs(c[1]-c[0])
            self.pts[i] = (1-B)*L*pt + B*L*global_best[i] + a*L*e
        self._boundpts()


def test():
    '''Unit tests for this class.'''
    # __init__
    c = ((1,2), (4,5), (0,1))
    p = Particle(c)
    
    # randomize
    # Copy because Python makes a reference if you say var = obj
    from copy import copy
    a = copy(p.pts)
    p.randomize()
    try:
        np.testing.assert_array_almost_equal(a,p.pts)
        raise Warning("Randomized Particle has same pts as before")
    except AssertionError:
        pass
    
    # APSO
    # Make p.pts equal to globMin (first argument) with B=1 and a=0
    p.APSO( (3, 2, 0), 1, 0)
    p.APSO( (3, 1, 0), .5, 0)
    np.testing.assert_array_almost_equal(p.pts, np.array([3.0, 1.5, 0.0]))
    
# Run tests when running this file itself, and not when importing it.
if __name__ == "__main__":
    test()
    print("Tests succeeded.")