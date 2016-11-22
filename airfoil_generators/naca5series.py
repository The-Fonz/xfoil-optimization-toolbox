#!/usr/bin/env python
from __future__ import division

"""naca5series.py: Generates NACA 5 series airfoil. For explanation of the equations used refer to: 
http://web.stanford.edu/~cantwell/AA200_Course_Material/The%20NACA%20airfoil%20series.pdf"""
__author__ = "Karan Chawla"
__email__  = "karangc2@illinois.edu"
__version__= "0.1"


import numpy as np
from airfoilgen_baseclass import ParametricAirfoil
import matplotlib.pyplot as plt


class NACA5(ParametricAirfoil):

	def __init__(self, mld,t):
		#t is thickness in percentage of chord
		self.mld = mld #mean line designation
		self.t = t/100
		if mld == 210:
			self.m = .0580
			self.k1 = 361.40
			self.p = 0.05
		elif mld ==220:
			self.m = .1260
			self.k1 = 51.640
			self.p = 0.10
		elif mld == 230:
			self.m = .2025
			self.k1 = 15.957
			self.p = .15
		elif mld == 240:
			self.m = .2900
			self.k1 = 6.643
			self.p = 0.20
		elif mld == 250:
			self.m = .3910
			self.k1 = 3.23
			self.p = .25
		else: 
			raise Warning("Unknown airfoil number. Try again.")	
		#print self.m,self.k1,self.p

	def _camberline(self,xpts):
		m,p = self.m, self.p
		k1 = self.k1
		if m==0:
			return np.zeros(len(xpts))
		elif m!=0 and p==0:
			raise Warning("Position of maximum camber is zero while the mean camber is non-zero")
		else: 
			xpts0 = xpts[xpts<=p]
			xpts1 = xpts[xpts>p]
			
			#from x=0 to x=p 
			yc_0 = k1/6 * (xpts0**3 - 3*m*xpts0**2 + m**2 * (3-m)*xpts0)
			#from x=p to x=callable
			yc_1 = k1*m**3/6 * (1-xpts1)
			return np.append(yc_0,yc_1)
		

	def _thickness(self,x):
		t= self.t
		c = (.2969, .1260, .3516, .2843, .1015)
		y_t = t/.2 * (c[0]*x**.5-c[1]*x-c[2]*x**2+c[3]*x**3-c[4]*x**4)
		return y_t 

	def __str__(self):
		return ("""NACA 5-series (pos. {}, thickness {})"""
	    .format(self.p, self.t))

def _example():
	'''Runs an example'''
	mld,t = 230,15
	test_airfoil = NACA5(mld,t)
		
	#print test airfoil 
	print test_airfoil
	
	#get thickness
	print ("Real thickness (including camber): {:.1%}"
      .format(test_airfoil.max_thickness()))
	print ("Volume: {:.3f} chord^2".format(test_airfoil.area()))

	pts = test_airfoil.get_coords()

	import matplotlib.pyplot as plt
	#plt.title("NACA {}{}{}".format(mld, t))
	plt.plot(pts[0], pts[1], 'o--')
	plt.plot(pts[2], pts[3], 'o--')
	plt.plot(pts[4], pts[5], 'o--')
	plt.gca().axis('equal')
	plt.show()


	# If this file is run, execute example
if __name__ == "__main__":
	_example()
