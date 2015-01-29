"""
This base class for generators makes it easy to share common functionality,
like generating a plain coordinate file.

When creating a child airfoil class, you have two choices:

1. Define _fn_upper and _fn_lower methods, that calculate
   the coordinates of lower and upper surfaces, respectively.
2. Define _camberline and _thickness, which calculate
   the coordinates of camberline and thickness, respectively.

With the second method, ParametricAirfoil._fn_upper and
ParametricAirfoil._fn_lower are left to do their job, which is to
nicely join the camberline and thickness, taking into account the
camberline's direction, not simply summing camberline and thickness.
"""

from __future__ import division
import numpy as np

class ParametricAirfoil(object):
    """Base class for airfoil generators."""

    # x-position of trailing edge, usually 1.0 for normalized airfoil.
    # Only override when really needed.
    xte = 1.0
    
    def _fn_upper_lower(self, x):
        """Implements proper coordinate calculation, using camberline
        direction. Returns:
        (x_upper, y_upper, x_lower, y_lower, x_camber, y_camber)"""
        y_t = self._thickness(x)
        y_c = self._camberline(x)
        # Calculate camber line derivative using central difference
        dx = np.gradient(x)
        dyc_dx = np.gradient(y_c, dx)
        # np.gradient calculates the edges weirdly, replace them by fwd diff
        # Can be made even more accurate by using second-order fwd diff,
        # but that is not so straightforward when step size differs.
        # Numpy 1.9.1 supports edge_order=2 in np.gradient()
        dyc_dx[0] = (y_c[1]-y_c[0]) / (x[1]-x[0])
        dyc_dx[-1] = (y_c[-2]-y_c[-1]) / (x[-2]-x[-1])
        # Calculate camberline angle
        theta = np.arctan(dyc_dx)
        # Calculate x,y of upper, lower surfaces
        # From http://web.stanford.edu/~cantwell/AA200_Course_Material/
        # The%20NACA%20airfoil%20series.pdf
        x_u = x - y_t*np.sin(theta)
        y_u = y_c + y_t*np.cos(theta)
        x_l = x + y_t*np.sin(theta)
        y_l = y_c - y_t*np.cos(theta)
        return x_l, y_l, x_u, y_u, x, y_c

    def _camberline(self, xpts):
        raise Warning("""In child class,
        implement either _fn_upper_lower or _camberline and _thickness.""")
    def _thickness(self, xpts):
        raise Warning("""In child class,
        implement either _fn_upper_lower or _camberline and _thickness.""")

    def __str__(self):
        """Gives some information about the airfoil."""
        return "Airfoil object, implement __str__ method to give more info."

    def get_coords_plain(self, *args):
        """Returns string of coordinates in plain format."""
        # Ignore any camber line
        x_u, y_u, x_l, y_l = self.get_coords(*args)[:4]
        # Evaluate and re-order to start at TE, over bottom, then top
        # Use slicing [1:] to remove [0,0]
        ycoords = np.append(y_l[::-1], y_u[1:])
        xcoords = np.append(x_l[::-1], x_u[1:])
        # Use .T to transpose to [[x,y],[x,y],...]
        coordslist = np.array((xcoords, ycoords)).T
        coordstrlist = ["{:.6f} {:.6f}".format(coord[0], coord[1])
                        for coord in coordslist]
        # Join with linebreaks in between
        return '\n'.join(coordstrlist)

    def get_coords(self, npts=161):
        """Generates cosine-spaced coordinates, concentrated at LE and TE.
           Returns ([x_lower],[y_lower],[x_upper],[y_upper])"""
        xpts = (1 - np.cos(np.linspace(0, 1, np.ceil(npts/2))*np.pi)) / 2
        # Take TE position into account
        xpts *= self.xte
        return self._fn_upper_lower(xpts)
