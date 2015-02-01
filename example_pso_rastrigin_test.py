"""
Test of Particle Swarm Optimization algorithm, using the Rastrigin function.
"""

import matplotlib.pyplot as plt
import numpy as np
from optimization_algorithms.pso import Particle

def rastrigin_nd(*xi):
    """
    n-dimensional rastrigin function. Every argument should be a single
    value or meshgrid, and is another dimension.
    """
    return -(10*len(xi)+ np.sum(a**2 - (10*np.cos(2*np.pi*a)) for a in xi))

iterations = 100
# From http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
# For 5 iterations, 1,000 function evaluations
S, omega, theta_p, theta_g = 47, -0.1832, 0.5287, 3.1913
global_best = -float('inf')
global_bestpos   = None

constraints = ((-5,5),(-5,5))
# Constructing a particle automatically initializes position and speed
particles = [Particle(constraints) for i in xrange(0, S)]

x, y = np.meshgrid(np.arange(-5,5,.05), np.arange(-5,5,.05))
plt.title("Rastrigin function")
plt.contourf(x, y, rastrigin_nd(x,y), cmap=plt.cm.coolwarm)
plt.ion()
plt.axis([-5,5,-5,5])
#plt.show()
# Make sure to only accept particle if it converges.
# Also, try to avoid separate initialization loop, do smart stuff in main

for n in xrange(iterations):
    for particle in particles:
        # Update particle's velocity and position, after first loop
        if n>0:
            particle.update(global_bestpos, omega, theta_p, theta_g)
        # Score
        score = rastrigin_nd(*particle.pts)
        
        if score > particle.best:
            particle.new_best(score)
            style = 'bo'
            if score > global_best:
                global_best = score
                global_bestpos = particle.pts
                style = 'ro'
            print "Plotting ({}, {})".format(*particle.pts)
            plt.pause(0.0001)
            plt.plot(particle.pts[0], particle.pts[1], style)

print "Global best: ", global_best, "Global best pos: ", global_bestpos
#plt.plot(global_bestpos[0], global_bestpos[1], 'bo')

plt.show()
