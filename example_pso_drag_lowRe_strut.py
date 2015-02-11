"""
Test of Particle Swarm Optimization algorithm in combination with Xfoil and
the PARSEC airfoil parametrization. Trying to find low Re low drag airfoil
for given thickness (thus varying Re).
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

strut_thickness = .01 #m
velocity = 10 #m/s
def calcRe(thickness):
    # At 1atm and 10*C
    kinematic_viscosity_air = 1.4207E-5
    l = strut_thickness/thickness
    return velocity*l/kinematic_viscosity_air
# Weigh score on frontal surface
def weighScore(Cd, thickness):
    return Cd / thickness
constraints = np.array((
#rle        x_pre/suc    d2ydx2_pre/suc  th_pre/suc   y_pre/suc
(.015,.05), (.3,.75),     (-2,.1),          (0,40),   (.03, .2)
))
# Good parameters at:
# http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
iterations, S, omega, theta_g, theta_p = 14, 18, -0.2, 2.8, 0

def construct_airfoil(*pts):
    k = {}
    k['rle'] = pts[0]
    k['x_pre'] = pts[1]
    k['y_pre'] = -pts[4]
    k['d2ydx2_pre'] = -pts[2]
    # Trailing edge angle
    k['th_pre'] = pts[3]
    # Suction part
    k['x_suc'] = k['x_pre']
    k['y_suc'] = -k['y_pre']
    k['d2ydx2_suc'] = -k['d2ydx2_pre']
    k['th_suc'] = -k['th_pre']
    # Trailing edge x and y position
    k['xte'] = 1
    k['yte'] = 0
    return parsec.PARSEC(k)

def score_airfoil(airfoil):
    max_thickness = airfoil.max_thickness()
    Re = calcRe(max_thickness)
    print("RE is ", Re, "MT is ", max_thickness)
    # Make unique filename
    randstr = ''.join(choice(ascii_uppercase) for i in range(20))
    filename = "parsec_{}.dat".format(randstr)
    # Save coordinates
    with open(filename, 'w') as af:
        af.write(airfoil.get_coords_plain())
    # Let Xfoil do its magic
    polar = xfoil.oper_visc_alpha(filename, 0, Re,
                                  iterlim=80, show_seconds=0)
    try:
        remove(filename)
    except WindowsError:
        print("\n\n\n\nWindows was not capable of removing the file.\n\n\n\n")

    try:
        score = polar[0][0][2]
        score = weighScore(score, max_thickness)
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

# Show plot and make redrawing possible
fig, (cur_afplt, lastpbest_afplt, gbest_afplt, score_plt) = plt.subplots(4,1)
# Enable auto-clearing
cur_afplt.hold(False)
lastpbest_afplt.hold(False)
gbest_afplt.hold(False)
plt.tight_layout()
# Interactive mode
plt.ion()
plt.pause(.0001)

# Initialize globals
global_bestscore   = None
global_bestpos     = None
global_bestairfoil = None

# Constructing a particle automatically initializes position and speed
particles = [Particle(constraints) for i in xrange(0, S)]

scores_y = []

for n in xrange(iterations+1):
    print("\n\nIteration {}".format(n))
    for i_par, particle in enumerate(particles):
        # Keep scoring until converged
        score = None
        while not score:
            # Update particle's velocity and position, if global best
            if global_bestscore:
                print("\nUpdate particle n{}p{}".format(n, i_par))
                particle.update(global_bestpos, omega, theta_p, theta_g)
            # None if not converged
            airfoil = construct_airfoil(*particle.pts)
            score = score_airfoil(airfoil)
            plotstyle = "{}-".format(choice("rgb"))
            airfoil.plot(cur_afplt, score="Cd {}".format(score), style=plotstyle,
                         title="Current, particle n{}p{}".format(n, i_par))
            plt.pause(.0001)
            if not score and (not global_bestscore or n==0):
                print("Not converged, no global best, or first round. Randomizing particle.")
                particle.randomize()
            elif not score:
                print("Not converged, there is a global best. Randomizing.")
                particle.randomize()

        if not particle.bestscore or score < particle.bestscore:
            particle.new_best(score)
            txt = 'particle best'
            airfoil.plot(lastpbest_afplt, score="Cd {}".format(score), style=plotstyle,
            title="Particle best, particle n{}p{}".format(n, i_par))
            #plt.pause(.0001)
            print("Found particle best, score {}".format(score))
        if not global_bestscore or score < global_bestscore:
            global_bestscore = score
            # Copy to avoid globaL_bestpos becoming reference to array
            global_bestpos = copy(particle.pts)
            txt = 'global best'
            airfoil.plot(gbest_afplt, score="Cd {}".format(score), style=plotstyle,
              title="Global best, particle n{}p{}".format(n, i_par))
            #plt.pause(.0001)
            print("Found global best, score {}".format(score))
            global_bestairfoil = airfoil
        
    scores_y.append(global_bestscore)
    score_plt.plot(scores_y, 'r-')
    score_plt.set_title("Global best per round")
    plt.pause(.0001)


print("# score = ", global_bestscore,
      ", pos = ", global_bestpos.__repr__(),
      ", airfoil points:\n{}".format(airfoil.get_coords_plain()))

plt.show()

# 11-2-14
# RE is  72047.1359611 MT is  0.0976969258288
#score =  0.0235421941938 , pos =  array([  0.04028559,   0.56905154,  -0.15051354,  12.75297732,   0.03010498]) , airfoil points:
#1.000000 -0.000000
#0.999615 -0.000094
#0.998459 -0.000373
#0.996534 -0.000832
#0.993844 -0.001462
#0.990393 -0.002253
#0.986185 -0.003188
#0.981228 -0.004253
#0.975528 -0.005428
#0.969096 -0.006695
#0.961940 -0.008034
#0.954072 -0.009426
#0.945503 -0.010850
#0.936248 -0.012291
#0.926320 -0.013730
#0.915735 -0.015155
#0.904508 -0.016551
#0.892658 -0.017909
#0.880203 -0.019219
#0.867161 -0.020476
#0.853553 -0.021675
#0.839400 -0.022812
#0.824724 -0.023885
#0.809547 -0.024893
#0.793893 -0.025836
#0.777785 -0.026712
#0.761249 -0.027521
#0.744311 -0.028264
#0.726995 -0.028938
#0.709330 -0.029544
#0.691342 -0.030078
#0.673059 -0.030541
#0.654508 -0.030931
#0.635720 -0.031247
#0.616723 -0.031489
#0.597545 -0.031659
#0.578217 -0.031759
#0.558769 -0.031794
#0.539230 -0.031771
#0.519630 -0.031700
#0.500000 -0.031593
#0.480370 -0.031465
#0.460770 -0.031332
#0.441231 -0.031214
#0.421783 -0.031131
#0.402455 -0.031104
#0.383277 -0.031155
#0.364280 -0.031304
#0.345492 -0.031571
#0.326941 -0.031973
#0.308658 -0.032521
#0.290670 -0.033225
#0.273005 -0.034086
#0.255689 -0.035102
#0.238751 -0.036261
#0.222215 -0.037548
#0.206107 -0.038936
#0.190453 -0.040395
#0.175276 -0.041885
#0.160600 -0.043362
#0.146447 -0.044777
#0.132839 -0.046076
#0.119797 -0.047204
#0.107342 -0.048102
#0.095492 -0.048715
#0.084265 -0.048990
#0.073680 -0.048876
#0.063752 -0.048331
#0.054497 -0.047318
#0.045928 -0.045811
#0.038060 -0.043793
#0.030904 -0.041259
#0.024472 -0.038215
#0.018772 -0.034679
#0.013815 -0.030682
#0.009607 -0.026265
#0.006156 -0.021481
#0.003466 -0.016390
#0.001541 -0.011061
#0.000385 -0.005572
#0.000000 0.000000
#0.000385 0.005572
#0.001541 0.011061
#0.003466 0.016390
#0.006156 0.021481
#0.009607 0.026265
#0.013815 0.030682
#0.018772 0.034679
#0.024472 0.038215
#0.030904 0.041259
#0.038060 0.043793
#0.045928 0.045811
#0.054497 0.047318
#0.063752 0.048331
#0.073680 0.048876
#0.084265 0.048990
#0.095492 0.048715
#0.107342 0.048102
#0.119797 0.047204
#0.132839 0.046076
#0.146447 0.044777
#0.160600 0.043362
#0.175276 0.041885
#0.190453 0.040395
#0.206107 0.038936
#0.222215 0.037548
#0.238751 0.036261
#0.255689 0.035102
#0.273005 0.034086
#0.290670 0.033225
#0.308658 0.032521
#0.326941 0.031973
#0.345492 0.031571
#0.364280 0.031304
#0.383277 0.031155
#0.402455 0.031104
#0.421783 0.031131
#0.441231 0.031214
#0.460770 0.031332
#0.480370 0.031465
#0.500000 0.031593
#0.519630 0.031700
#0.539230 0.031771
#0.558769 0.031794
#0.578217 0.031759
#0.597545 0.031659
#0.616723 0.031489
#0.635720 0.031247
#0.654508 0.030931
#0.673059 0.030541
#0.691342 0.030078
#0.709330 0.029544
#0.726995 0.028938
#0.744311 0.028264
#0.761249 0.027521
#0.777785 0.026712
#0.793893 0.025836
#0.809547 0.024893
#0.824724 0.023885
#0.839400 0.022812
#0.853553 0.021675
#0.867161 0.020476
#0.880203 0.019219
#0.892658 0.017909
#0.904508 0.016551
#0.915735 0.015155
#0.926320 0.013730
#0.936248 0.012291
#0.945503 0.010850
#0.954072 0.009426
#0.961940 0.008034
#0.969096 0.006695
#0.975528 0.005428
#0.981228 0.004253
#0.986185 0.003188
#0.990393 0.002253
#0.993844 0.001462
#0.996534 0.000832
#0.998459 0.000373
#0.999615 0.000094
#1.000000 0.000000


# score =  0.00870235341255 , pos =  array([  0.02875577,   0.52143075,  -1.31975537,  19.25893881,   0.10054965]) , airfoil points:
#1.000000 -0.000000
#0.999615 -0.000101
#0.998459 -0.000398
#0.996534 -0.000883
#0.993844 -0.001537
#0.990393 -0.002337
#0.986185 -0.003257
#0.981228 -0.004270
#0.975528 -0.005345
#0.969096 -0.006458
#0.961940 -0.007585
#0.954072 -0.008710
#0.945503 -0.009824
#0.936248 -0.010925
#0.926320 -0.012022
#0.915735 -0.013131
#0.904508 -0.014278
#0.892658 -0.015496
#0.880203 -0.016825
#0.867161 -0.018307
#0.853553 -0.019989
#0.839400 -0.021913
#0.824724 -0.024120
#0.809547 -0.026645
#0.793893 -0.029511
#0.777785 -0.032731
#0.761249 -0.036305
#0.744311 -0.040217
#0.726995 -0.044435
#0.709330 -0.048912
#0.691342 -0.053584
#0.673059 -0.058376
#0.654508 -0.063198
#0.635720 -0.067952
#0.616723 -0.072534
#0.597545 -0.076838
#0.578217 -0.080759
#0.558769 -0.084199
#0.539230 -0.087067
#0.519630 -0.089287
#0.500000 -0.090800
#0.480370 -0.091567
#0.460770 -0.091568
#0.441231 -0.090807
#0.421783 -0.089312
#0.402455 -0.087131
#0.383277 -0.084335
#0.364280 -0.081012
#0.345492 -0.077266
#0.326941 -0.073213
#0.308658 -0.068974
#0.290670 -0.064675
#0.273005 -0.060439
#0.255689 -0.056380
#0.238751 -0.052602
#0.222215 -0.049193
#0.206107 -0.046222
#0.190453 -0.043735
#0.175276 -0.041757
#0.160600 -0.040284
#0.146447 -0.039293
#0.132839 -0.038734
#0.119797 -0.038538
#0.107342 -0.038619
#0.095492 -0.038876
#0.084265 -0.039198
#0.073680 -0.039472
#0.063752 -0.039583
#0.054497 -0.039423
#0.045928 -0.038894
#0.038060 -0.037911
#0.030904 -0.036410
#0.024472 -0.034347
#0.018772 -0.031701
#0.013815 -0.028476
#0.009607 -0.024699
#0.006156 -0.020422
#0.003466 -0.015717
#0.001541 -0.010674
#0.000385 -0.005396
#0.000000 0.000000
#0.000385 0.005396
#0.001541 0.010674
#0.003466 0.015717
#0.006156 0.020422
#0.009607 0.024699
#0.013815 0.028476
#0.018772 0.031701
#0.024472 0.034347
#0.030904 0.036410
#0.038060 0.037911
#0.045928 0.038894
#0.054497 0.039423
#0.063752 0.039583
#0.073680 0.039472
#0.084265 0.039198
#0.095492 0.038876
#0.107342 0.038619
#0.119797 0.038538
#0.132839 0.038734
#0.146447 0.039293
#0.160600 0.040284
#0.175276 0.041757
#0.190453 0.043735
#0.206107 0.046222
#0.222215 0.049193
#0.238751 0.052602
#0.255689 0.056380
#0.273005 0.060439
#0.290670 0.064675
#0.308658 0.068974
#0.326941 0.073213
#0.345492 0.077266
#0.364280 0.081012
#0.383277 0.084335
#0.402455 0.087131
#0.421783 0.089312
#0.441231 0.090807
#0.460770 0.091568
#0.480370 0.091567
#0.500000 0.090800
#0.519630 0.089287
#0.539230 0.087067
#0.558769 0.084199
#0.578217 0.080759
#0.597545 0.076838
#0.616723 0.072534
#0.635720 0.067952
#0.654508 0.063198
#0.673059 0.058376
#0.691342 0.053584
#0.709330 0.048912
#0.726995 0.044435
#0.744311 0.040217
#0.761249 0.036305
#0.777785 0.032731
#0.793893 0.029511
#0.809547 0.026645
#0.824724 0.024120
#0.839400 0.021913
#0.853553 0.019989
#0.867161 0.018307
#0.880203 0.016825
#0.892658 0.015496
#0.904508 0.014278
#0.915735 0.013131
#0.926320 0.012022
#0.936248 0.010925
#0.945503 0.009824
#0.954072 0.008710
#0.961940 0.007585
#0.969096 0.006458
#0.975528 0.005345
#0.981228 0.004270
#0.986185 0.003257
#0.990393 0.002337
#0.993844 0.001537
#0.996534 0.000883
#0.998459 0.000398
#0.999615 0.000101
#1.000000 0.000000