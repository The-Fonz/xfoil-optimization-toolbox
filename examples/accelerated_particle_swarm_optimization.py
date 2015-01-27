"""
	Using Particle Swarm Optimization to optimize airfoils, and eventually
	propeller blades.
	
	Use PARSEC for airfoil paramterization!
"""

#from airfoil import Airfoil
#from xfoil import XfoilPy
# Maybe add Swarm class later, that can be a simple list at the start, having
# properties like global min.
from pso import Particle

# Number of particles
N = 8
# Number of iterations
M = 10

def main():
	# Init n Particles, setting particle constraints
	constraints = "something"
	particles = []
	for i in xrange(N):
		particles.append( Particle(constraints) )
	
	globScore = 0
	#globScoreParticle = 0
	# For loop that iterates m times
	for j in xrange(M):
		# For each particle
		for particle in particles:
			pass
			# Call APSO routine to change it on Particle, indicating its coefficients
			# (Make APSO random coefficient decline with time)
			# Generate airfoil from particle
			# Score particle
			# If score is higher than global score, update global score, and
			# remember particle
	print globScore#, globScoreParticle
	# Print highest score and particle