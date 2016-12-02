"""
An example to show how to combine NURBS airfoil_generator and XFOIL
"""

from airfoil_generators.nurbs import NURBS 
from xfoil.xfoil import oper_visc_cl 

import matplotlib.pyplot as plt 
import numpy as np 
import os 

Re = 100000
Cl = 0.2

drags = np.zeros((5,3))

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
'''k= {}
k['ta_u'] = 0.1584
k['ta_l'] = 0.1565
k['tb_u'] = 2.1241
k['tb_l'] = 1.8255
k['alpha_b'] = 11.6983
k['alpha_c'] = 3.8270
x = NURBS(k)
pts = x._spline()
coords = get_coords_plain(pts)
'''
ta_u = 0.1584
ta_l = 0.1565
tb_u = np.linspace(1.8,2.2,6)
tb_l = 1.8255
alpha_c = 3.8270
alpha_b = np.linspace(11.1,12,4)

for i in xrange(1,6):
	for j in xrange(1,4):
		#make new airfoil 
		k = {}
		k['ta_u'] = 0.1584
		k['ta_l'] = 0.1565
		k['tb_u'] = tb_u[i]
		k['tb_l'] = 1.8255
		k['alpha_b'] = alpha_b[j]
		k['alpha_c'] = 3.8270
		af = NURBS(k)
		airfoil = af._spline()

		#make unique filename
		temp_af_filename = "temp_airfoil_{}{}.dat".format(i,j)

		#Save coordinates
		with open(temp_af_filename, 'w') as af:
			af.write(get_coords_plain(airfoil))

		#Let Xfoil do its thing 
		polar = oper_visc_cl(temp_af_filename, Cl, Re,iterlim=1000)

		#Save Cd
		try: 
			drags[i-1][j-1] = polar[0][0][2]
		except IndexError:
			raise Warning("Shit! XFOIL didn't converge on NACA{}{}15 at Cl={}."
							.format(i,j,Cl))
 
		xl = airfoil[0]
		yl = airfoil[1]
		xu = airfoil[2]
		yu = airfoil[3]
		def translated_plt(x, y, *args):
			plt.plot(x*0.8 + (j-.9), y*0.8 + (i-0.5) , *args)
		translated_plt(yl, xl, 'w')
		translated_plt(yu, xu, 'w')
		
		os.remove(temp_af_filename)

print drags

plt.pcolor(drags, cmap=plt.cm.RdBu)
plt.pcolor(drags, cmap=plt.cm.coolwarm)

cbar = plt.colorbar()
cbar.ax.set_ylabel("Drag coefficient $C_d$")
plt.yticks( (.5,1.5,2.5,3.5,4.5), ("1", "2", "3", "4", "5") )
plt.xticks( (.5,1.5,2.5), ("1", "2", "3") )
plt.tight_layout()
plt.show()