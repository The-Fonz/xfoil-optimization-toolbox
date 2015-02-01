"""
An example to show how to combine an airfoil_generator and XFOIL.
"""

from airfoil_generators.naca4series import NACA4
from xfoil.xfoil import oper_visc_cl
import os

import matplotlib.pyplot as plt
import numpy as np

# Operating point
Re = 1000000
Cl = .4

drags = np.zeros((5, 3))

# m is camber in percent, p is position of max. camber in tenths
for m in xrange(1,6):
    for p in xrange(4,7):
        
        # Make new airfoil NACAmp15
        airfoil = NACA4(m, p, 15)

        # Make unique filename
        temp_af_filename = "temp_airfoil_{}{}.dat".format(m,p)

        # Save coordinates
        with open(temp_af_filename, 'w') as af:
            af.write(airfoil.get_coords_plain())

        # Let XFOIL do its thing
        polar = oper_visc_cl(temp_af_filename, Cl, Re, iterlim=500)

        # Save Cd
        try:
            drags[m-1][p-4] = polar[0][0][2]
        except IndexError:
            raise Warning("Shit! XFOIL didn't converge on NACA{}{}15 at Cl={}."
                          .format(m,p,Cl))

        # Remove temporary file
        os.remove(temp_af_filename)

        # Plot airfoil shape
        xl, yl, xu, yu, xc, yc = airfoil.get_coords()
        def translated_plt(x, y, *args):
            plt.plot(x*.8 + (p-3.9), y*.8 + (m-.5), *args)
        translated_plt(xl, yl, 'w')
        translated_plt(xu, yu, 'w')
        translated_plt(xc, yc, 'w--')

# Plot drag values in color
plt.pcolor(drags, cmap=plt.cm.coolwarm)

# Make plot pretty
plt.title(r"$C_d$ of $NACAmp15$ at $C_l={}$ and $Re={:g}$".format(Cl, Re))
plt.xlabel("Location of max. camber $p$")
plt.ylabel("Max. camber $m$")
cbar = plt.colorbar()
cbar.ax.set_ylabel("Drag coefficient $C_d$")
plt.yticks( (.5,1.5,2.5,3.5,4.5), ("1p15", "2p15", "3p15", "4p15", "5p15") )
plt.xticks( (.5,1.5,2.5), ("m415", "m515", "m615") )
plt.tight_layout()

# Show our artwork
plt.show()
