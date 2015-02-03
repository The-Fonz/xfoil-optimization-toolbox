"""
Test of Particle Swarm Optimization algorithm in combination with Xfoil and
the PARSEC airfoil parametrization. Trying to find high Re low drag airfoil.
"""

from __future__ import division, print_function
from os import remove
import numpy as np
from copy import copy
from string import ascii_uppercase
from random import choice
import matplotlib.pyplot as plt
from optimization_algorithms.pso import Particle
from airfoil_generators import parsec
from xfoil import xfoil


constraints = np.array((
#rle    x_pre    d2ydx2_pre/suc  th_pre/suc
(0,.1), (.2,.7), (-4,.5),        (0,45)
))

fig, (cur_afplt, lastpbest_afplt, gbest_afplt) = plt.subplots(3,1)
# Show plot and make redrawing possible

def construct_airfoil(*pts):
    # Construct PARSEC coefficients
    k = {}
    k['rle'] = pts[0]
    k['x_pre'] = pts[1]
    # Thickness 21%
    k['y_pre'] = -.105
    k['d2ydx2_pre'] = pts[2]
    # Trailing edge angle
    k['th_pre'] = pts[3]

    k['x_suc'] = k['x_pre']
    k['y_suc'] = -k['y_pre']
    k['d2ydx2_suc'] = -k['d2ydx2_pre']
    k['th_suc'] = -k['th_pre']
    # Trailing edge x and y position
    k['xte'] = 1
    k['yte'] = 0
    return parsec.PARSEC(k)

def score_airfoil(airfoil):    
    # Make unique filename
    randstr = ''.join(choice(ascii_uppercase) for i in range(12))
    filename = "parsec_{}.dat".format(randstr)
    # Save coordinates
    with open(filename, 'w') as af:
        af.write(airfoil.get_coords_plain())
    polar = xfoil.oper_visc_alpha(filename, 0, 2E6,
                                  iterlim=300, show_seconds=0)
    remove(filename)

    try:
        score = polar[0][0][2]
        print("Score: ", score)
        # If it's not NaN
        if np.isfinite(score):
            print("Return score")
            return score
        else:
            print("Return None")
            return None
    except IndexError:
        print("Return None (IndexError)")
        return None

iterations = 10
# Parameters for 5 iterations, 1,000 function evaluations from:
# http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
S, omega, theta_p, theta_g = 47, -0.1832, 0.5287, 3.1913
global_bestscore = None
global_bestpos   = None

# Constructing a particle automatically initializes position and speed
particles = [Particle(constraints) for i in xrange(0, S)]

for n in xrange(iterations+1):
    print("\nIteration {}".format(n))
    for particle in particles:
        # Keep scoring until converged
        score = None
        while not score:
            # Update particle's velocity and position, if global best
            if global_bestscore:
                print("Update particle")
                particle.update(global_bestpos, omega, theta_p, theta_g)
                #particle.APSO(global_bestpos, .5, .5)
            # None if not converged
            airfoil = construct_airfoil(*particle.pts)
            #airfoil.plot(cur_afplt)
            #plt.draw()
            score = score_airfoil(airfoil)
            if not score:
                print("Not converged. Randomizing particle")
                particle.randomize()

        #plt.plot(particle.pts[0], particle.pts[1], 'yx')
        if score > particle.bestscore:
            particle.new_best(score)
            txt = 'particle best'
            airfoil.plot(lastpbest_afplt)
            #plt.draw()
        if score > global_bestscore:
            global_bestscore = score
            # Copy to avoid globaL_bestpos becoming reference to array
            global_bestpos = copy(particle.pts)
            txt = 'global best'
            airfoil.plot(gbest_afplt)
            #plt.draw()
        print("Found {}, score {}\n".format(txt, score))
            #plt.pause(0.00001)
            #plt.plot(particle.pts[0], particle.pts[1], style)

print("Global best score: ", global_bestscore,
      "Global best pos: ", global_bestpos)
#plt.plot(global_bestpos[0], global_bestpos[1], 'yx', markersize=12)
