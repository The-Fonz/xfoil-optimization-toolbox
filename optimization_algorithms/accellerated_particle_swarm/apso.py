"""
	This file contains classes to handle Particle Swarm Optimization.
	Its abstraction level is such that it should be similar to thinking about
	the algorithm.
"""

# Make sure that 7/2=3.5
from __future__ import division
# Import N(mu, sigma) and U[0,1) function
from random import normalvariate, random
# Import built-in array module (lists of one type)
import array

class Particle():
	'''A particle is an n-dimensional array of constrained numbers.
	   The constraint array c is organized as [[low,high],[low,high],0].
	   A 0 means it's a constant.'''
	def __init__(self, c):
		assert(type(tuple(c)) == type(tuple())), "Constraint array not of type 'list'"
		for p in c:
			#Constraint can either be list/array or a float.
			if (type(p)==type(list()) or type(p)==type(array.array('f')) ):
				assert(1 <= len(p) <= 2), "Constraint array not correct size"
				assert(p[1] > p[0]), "Upperbound > lowerbound"
		self.c = c
		self.pts = array.array('f', (0,)*len(c))
		self.randomize()
	
	def __str__(self):
		'''Print values of Particle.'''
		return ("Constraints: "+self.c.__str__()+
		"\nValues: "+self.pts.__str__())
	
	def randomize(self):
		'''Randomize with uniform distribution within bounds.'''
		# Iterate over self.pts
		for i in xrange(0,len(self.pts)):
			constraints = self.c[i]
			# Check if the constraint is a constant or a range [min,max]
			try:
				type(float(constraints))
			except TypeError:
				lowerbound = constraints[0]
				upperbound = constraints[1]
				self.pts[i] = lowerbound + random() * (upperbound-lowerbound)
	
	def APSO(self, globMin, B, a):
		'''A simplified way of PSO, with no velocity, updating the particle
		   in one step. http://arxiv.org/pdf/1203.6577.pdf
		   Typically, a = 0.1L ~ 0.5L where L is the scale of each variable,
		   while B = 0.1 ~ 0.7 is sufficient for most applications'''
		for i in xrange(0,len(self.pts)):
			pt = self.pts[i]
			mu, sigma = 0, 1
			e = normalvariate(mu, sigma)
			self.pts[i] = (1-B)*pt + B*globMin[i] + a*e


def test():
	'''Unit tests for this class.'''
	# __init__
	c = (3,(1,2), 0, (4,5), (0,1),6)
	p = Particle(c)
	assert(p.c == c), "Particle constraints are not the given constraints"
	
	# randomize
	# Normally Python makes a reference if you say var = obj
	from copy import copy
	a = copy(p.pts)
	p.randomize()
	assert(a != p.pts), "Randomized Particle has same pts as before"
	
	# APSO
	# Make p.pts equal to globMin (first argument) with B=1 and a=0
	p.APSO( (3, 2, 0, 5, 1, 6), 1, 0)
	p.APSO( (3, 1, 0, 4, 1, 6), .5, 0)
	assert(p.pts == array.array('f', [3.0, 1.5, 0.0, 4.5, 1.0, 6.0]))
	
# Run tests when running this file itself, and not when importing it.
if __name__ == "__main__":
	test()
	print("Tests succeeded.")