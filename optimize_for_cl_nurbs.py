"""
Test of PSO algorithm in combination with XFoil and NURBS Airfoil parametrization.
Trying to find high Re low drag airfoil.
"""

from __future__ import division, print_function 
from os import remove 
import numpy as np 
from copy import copy
from string import ascii_uppercase
from random import choice
import matplotlib.pyplot as plt
from optimization_algorithms.pso import Particle
from airfoil_generators import nurbs 
from xfoil import xfoil 

Re = 300000
constraints = np.array((
#ta_u	#ta_l  	#tb_l   #alpha_b

#ta_u = upward angle at front
#ta_1 = bottom angle at front

#tb_u = bottom angle at back
#tb_l

#alpha_a
#alph_b = top angle at back

(.01,.4), (.05,.4), (1,3),(0.05,3), (0.4,8), (1,10)

#(.1,.4), (.1,.4), (.1,2), (1,10)
#(.05,.15), (.05,.15), (.6,8), (1,1.3)
	))
# Good parameters at:
# http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
iterations, S, omega, theta_g, theta_p = 100, 12, -0.2, 2.8, 0

def construct_airfoil(*pts):
	k = {}
	k['ta_u'] = pts[0]
	k['ta_l'] = pts[1]
	k['tb_u'] = pts[2]
	k['tb_l'] = pts[3] 
	k['alpha_b'] = pts[4]
	k['alpha_c'] = pts[5]
	return nurbs.NURBS(k)

def plot(argv, ax, score=None, title=None, style='r-'):
	x_l = argv[0]
	y_l = argv[1]
	x_u = argv[2]
	y_u = argv[3]
	ax.set_xlim(0,1)
	ax.plot(y_l, x_l, style, y_u, x_u, style, linewidth=2)
	if score:
		ax.annotate(str(score), (.4,0))
	if title:
		ax.set_title(title)

def get_coords_plain(argv):
	x_l = argv[0]
	y_l = argv[1]
	x_u = argv[2]
	y_u = argv[3]
	ycoords = np.append(y_l[::-1], y_u[1:])
	xcoords = np.append(x_l[::-1], x_u[1:])
	coordslist = np.array((xcoords, ycoords)).T
	coordstrlist = ["{:.6f} {:.6f}".format(coord[1], coord[0])
					for coord in coordslist]

	return '\n'.join(coordstrlist)

def score_airfoil(airfoil):
	# Make unique filename
	randstr = ''.join(choice(ascii_uppercase) for i in range(20))
	filename = "parsec_{}.dat".format(randstr)
	# Save coordinates
	with open(filename, 'w') as af:
		af.write(get_coords_plain(airfoil._spline()))
	#Let Xfoil do its magic 
	polar = xfoil.oper_visc_cl(filename,0,Re,
									iterlim =80, show_seconds =0)
	polar2 = xfoil.oper_visc_cl(filename,0.4,Re,
									iterlim =80, show_seconds =0)

	try: 
		remove(filename)
	except WindowsError: 
		print("\n\n\n\nWindows was not capable of removing the file.\n\n\n\n")

	try:
		score = polar[0][0][2] * 0.5 + polar2[0][0][2] * 0.5
		print("Score: ", score)
		# If it's not NaN
		if np.isfinite(score):
			print("Return Score")
			return score
		else: 
			print("Return None")
			return None
	except IndexError: 
		print("Return None (IndexError)")
		return None 

# Show plot and make redrawing possible
fig, (cur_afplt, lastpbest_afplt, gbest_afplt, score_plt) = plt.subplots(4,1)
# Enable auto-clearing
cur_afplt.hold(False)
lastpbest_afplt.hold(False)
gbest_afplt.hold(False)
cur_afplt.axis('equal')
lastpbest_afplt.axis('equal')
gbest_afplt.axis('equal')
plt.tight_layout()
# Interactive mode
plt.ion()
#plt.pause(.0001)

# Initialize globals
global_bestscore   = None
global_bestpos     = None
global_bestairfoil = None

# Constructing a particle automatically initializes position and speed
particles = [Particle(constraints) for i in xrange(0, S)]

scores_y = []

for n in xrange(iterations+1):
	print("\nIteration {}".format(n))
	for i_par, particle in enumerate(particles):
		# Keep scoring until converged
		score = None 
		while not score: 
			if global_bestscore:
				print("Update Particle")
				particle.update(global_bestpos,omega,theta_p,theta_g)
			airfoil = construct_airfoil(*particle.pts)
			score = score_airfoil(airfoil)
			plotstyle = "{}-".format(choice("rgb"))
			af = airfoil._spline()
			plot(af,cur_afplt, score="Cd {}".format(score), style=plotstyle,
						  title="Current, particle n{}p{}".format(n, i_par))

			if not score and (not global_bestscore or n==0):
				print("Not converged, no global best, or first round. Randomizing particle.")
				particle.randomize()

			elif not score:
				print("Not converged, there is a global best. Randomizing.")
				particle.randomize()

		if not particle.bestscore or score < particle.bestscore:
			particle.new_best(score)
			txt = 'particle best'
			plot(af,lastpbest_afplt, score="Cd {}".format(score), style=plotstyle,
			title="Particle best, particle n{}p{}".format(n, i_par))
			print("Found particle best, score {}".format(score))
		if not global_bestscore or score < global_bestscore:
			global_bestscore = score
			# Copy to avoid globaL_bestpos becoming reference to array
			global_bestpos = copy(particle.pts)
			txt = 'global best'
			plot(af, gbest_afplt, score="Cd {}".format(score), style=plotstyle,
			  title="Global best, particle n{}p{}".format(n, i_par))
			#plt.pause(.0001)
			print("Found global best, score {}".format(score))
			global_bestairfoil = airfoil	
	scores_y.append(global_bestscore)
	score_plt.plot(scores_y, 'r-')
	score_plt.set_title("Global best per round")
	plt.pause(.0001)

print("Best airfoil found for Re={}, ".format(Re),
      "score = ", global_bestscore,
      ", pos = ", global_bestpos.__repr__(),
      ", airfoil points:\n{}".format(get_coords_plain(af)))

plt.show()