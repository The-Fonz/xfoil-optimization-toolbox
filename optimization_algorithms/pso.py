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
# Import built-in array module (lists of one type)
import array

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
		self.new_best(-float('inf'))

	def new_best(self, score):
		'''Stores new personal best score and position.'''
		self.best = score
		self.bestpos = self.pts

	def randomize(self):
		'''Randomize with uniform distribution within bounds.'''
		# Iterate over self.pts
		for i, (lowerbound, upperbound) in enumerate(self.constraints):
			self.pts[i]  = lowerbound + uniform(lowerbound, upperbound)
			absdiff = abs(upperbound-lowerbound)
			self.spds[i] = uniform(-absdiff, absdiff)

	def update(self, global_best, omega, theta_p, theta_g):
		'''Update velocity and position'''
		r_p, r_g = uniform(0,1), uniform(0,1)
		# v_i,d <- omega*v_i,d + theta_p*r_p*(p_i,d-x_i,d) + theta_g*r_g*(g_d-x_i,d)
		self.spds = (omega*self.spds + theta_p*r_p*(self.best-self.pts) +
		               theta_g*r_g*(global_best-self.pts))
		self.pts += self.spds
     

	def __str__(self):
		'''Print values of Particle.'''
		return ("Constraints: "+self.constraints.__str__()+
		"\nValues: "+self.pts.__str__())
	
	def APSO(self, globMin, B, a):
		'''A simplified way of PSO, with no velocity, updating the particle
		   in one step. http://arxiv.org/pdf/1203.6577.pdf
		   Typically, a = 0.1L ~ 0.5L where L is the scale of each variable,
		   while B = 0.1 ~ 0.7 is sufficient for most applications'''
		for i in xrange(0,len(self.pts)):
			pt = self.pts[i]
			mu, sigma = 0, 1
			e = normal(mu, sigma)
			self.pts[i] = (1-B)*pt + B*globMin[i] + a*e


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
	assert(a != p.pts), "Randomized Particle has same pts as before"
	
	# APSO
	# Make p.pts equal to globMin (first argument) with B=1 and a=0
	p.APSO( (3, 2, 0), 1, 0)
	p.APSO( (3, 1, 0), .5, 0)
	assert(p.pts == array.array('f', [3.0, 1.5, 0.0]))
	
# Run tests when running this file itself, and not when importing it.
if __name__ == "__main__":
	test()
	print("Tests succeeded.")