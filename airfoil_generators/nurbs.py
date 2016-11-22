"""
Generates airfoil using NURBS. 
Original Paper: http://eprints.soton.ac.uk/50031/1/Sobe07.pdf
"""
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt 
from math import * 

class NURBS():
	def __init__(self,k):
		"""Takes a dictionary of coefficients to define NURBS airfoil. 
		Coefficient names: ta_u,ta_l,tb_u,tb_l,alpha_b,alpha_c """

		self.k = k 

		self.ta_u = k['ta_u']
		self.ta_l = k['ta_l']
		self.tb_u = k['tb_u']
		self.tb_l = k['tb_l']
		self.alpha_b = k['alpha_b']
		self.alpha_c = k['alpha_c']

		'''try:
			self.coeff = []
			self.coeff = self._spline()
			print self.coeff 
			self._coef()
		except TypeError:
			raise Warning("Pass a dict with named coefficients")'''


	def _spline(self):
		"""
		Calculates the spline interpolation for the airfoil params specified
		"""
		u = np.linspace(0,1,100)
		x_u = []
		y_u = []
		x_l = []
		y_l = []
		temp_var1 = np.array([[1,0,0,0],[0,0,1,0],[-3,3,-2,-1],[2,-2,1,1]])
		A = [0,0]
		B = [1,0]
		ta_u = self.ta_u
		ta_l = self.ta_l
		tb_u = self.tb_u
		tb_l = self.tb_l 
		alpha_b = self.alpha_b
		alpha_c = self.alpha_c

		#initialize end tangent magnitudes and directions
		TA_u = [(ta_u*cos(-pi/2)),ta_u*abs(sin(-pi/2))]
		TB_u = [(tb_u*cos(-((alpha_c+alpha_b)*pi/180))),(tb_u*sin(-((alpha_b+alpha_c)*pi/180)))] 
		TA_l = [(ta_l*cos(-pi/2)),ta_l*(sin(-pi/2))]
		TB_l = [(tb_l*cos(-((alpha_c)*pi/180))),(tb_l*sin(-((alpha_c)*pi/180)))] 

		#calculate (x,y) for the upper curve of the airfoil
		for j in range(2):
			temp_var =  np.array([[A[j]],[B[j]],[TA_u[j]],[TB_u[j]]]) #control points for x and y coords
			temp_var_coord = np.dot(temp_var1,temp_var)
			for i in range(len(u)):
				temp_var4 = [1,u[i],u[i]**2, pow(u[i],3)]
				if j==1:
					x_u.append(np.dot(temp_var4,temp_var_coord)) #calculate x coords
				else:
					y_u.append(np.dot(temp_var4,temp_var_coord)) #calculate y coords

		#calculate (x,y) for the lower curve of the airfoil 
		for j in range(2):
			temp_var =  np.array([[A[j]],[B[j]],[TA_l[j]],[TB_l[j]]]) #control points for x and y coords
			temp_var_coord = np.dot(temp_var1,temp_var)
			for i in range(len(u)):
				temp_var4 = [1,u[i],u[i]**2, pow(u[i],3)]
				if j==1:
					x_l.append(np.dot(temp_var4,temp_var_coord)) #calculate x coords
				else:
					y_l.append(np.dot(temp_var4,temp_var_coord)) #calculate y coords
		#coords = np.array([x_u,y_u,x_l,y_l])
		coords = np.array([x_l,y_l,x_u,y_u])
		return coords 

	'''def _coef(self):
		coeff = self.coeff
		return coeff '''


def _example(): 
	'''Runs an example'''
	k ={}
	#sample coefficients: Coefficients for generating NACA5410
	k['ta_u'] = 0.1584
	k['ta_l'] = 0.1565
	k['tb_u'] = 2.1241
	k['tb_l'] = 1.8255
	k['alpha_b'] = 11.6983
	k['alpha_c'] = 3.8270

	x = NURBS(k)
	pts = x._spline()

	plt.xlim(0,1)
	plt.ylim(-.2,.2)
	colour = np.random.rand(3,1)
	plt.plot(pts[3],pts[2], color = colour) #plot the spline
	plt.plot(pts[1],pts[0], color = colour)

	plt.show()

#If this file is run, execute example
if __name__ == "__main__":
	_example()