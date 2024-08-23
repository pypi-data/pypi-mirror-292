# inverse.py

import numpy as np
import scipy.integrate as integrate

# dens_from_eq() -- outputs arc length vs density when an exact function for the shape of the curve is known
#   x, sympy.Symbol():   x-variable in the equation of the curve
#   shape:               expression that defines the shape of the curve, e.g. shape = x**2
#   xdist:               the first and last x-points to be evaluated on the shape/curve, used to define the range to create (x, y) points on the shape
def dens_from_eq(x, shape, xrange, type="hanging"):
    import sympy as sym
    from catsolver.inverse import standardize

    y = sym.sympify(shape)
    yprime = y.diff()
    y2prime = yprime.diff()
    dy = sym.lambdify(x, yprime, 'numpy')
    d2y = sym.lambdify(x, y2prime, 'numpy')
    x_points = np.linspace(xrange[0], xrange[1], int(1000*(xrange[1]-xrange[0])))
    for x in x_points:
        if d2y(x) < -0.001:
            print(f"WARNING: {y} does not have positive curvature for the entirety of the desired x-range, curve is impossible without negative density")
            break
    def arc_func(x):
        return np.sqrt(1 + dy(x)**2)
    def arc_length(x):
        return integrate.quad(arc_func, xrange[0], x)[0]
    arc_lengths = [arc_length(i) for i in x_points]
    if type == "loaded":
        def density(x):
            return d2y(x)
    else:
        def density(x):  
            return d2y(x) / np.sqrt(1+dy(x)**2)
    densities = [density(i) for i in x_points]
    densities = standardize(densities)
    return [arc_lengths, densities]

# dens_from_spline() -- outputs arc length vs density when given a spline that starts at x=0 and ends at x=xdist, form = [arc length array, density array]
#   spline:                      any spline-related object from scipy.interpolate(), models the curve that we want to know the mass density of
#   xrange, array of 2 floats:   the first and last x-points on the spline, used to define the range to create (x, y) points from the spline
def dens_from_spline(spline, xrange, type="hanging"):
    from catsolver.inverse import standardize
    
    # creates first and second derivative approximations of the spline using .derivative()
    dy = spline.derivative()
    d2y = dy.derivative()

    # create the x-points using the range defined by xdist, 500 points per unit length
    x_points = np.linspace(xrange[0], xrange[1], int(500*(xrange[1]-xrange[0])))#arc_length(xdist)))
    # create corresponding y-points using by evaluating the given spline at each x-point
    y_points = spline(x_points)
    
    # creates corresponding arc lengths for every x-point on the curve/spline
    sum = 0
    arc_lengths = [0]
    for i in range(len(x_points) - 1):
        sum += np.sqrt((x_points[i+1]-x_points[i])**2 + (y_points[i+1]-y_points[i])**2)
        arc_lengths.append(sum)
    
    # Each point also has a density value that we know to be w(x) = h0 * d^2y/dx^2 / sqrt(1+(dy/dx)^2). However, since we know
    # multiplying density by a positive scalar does not change the shape that is created and h0 fits this description, we don't need
    # to include it when finding the density (essentially we multiply density by 1/h0, which is a positive scalar)
    if type == "loaded":
        def density(x):
            return d2y(x)
    else:
        def density(x):  
            return d2y(x) / np.sqrt(1+dy(x)**2)
    # Calculate corrresponding densities for every point on the curve/spline
    densities = [density(i) for i in x_points]
    densities = standardize(densities)

    # Now we have 3 arrays which represent the points' x-values, arc lengths, and densities, with each index representing a different point. 
    # Since we care about arc length vs density, we can return the list of arc lengths and the list of densities so that we can plot them.
    return [arc_lengths, densities]

# standardize() -- takes in an array of values and scales them so their average value is 1, used to more easily compare arc length vs density
#                  optionally, you can specify an average value other than 1 using the avg_value argument
def standardize(dens, avg_value=1):
    avg = np.average(dens)
    for i in range(len(dens)):
        dens[i] = (dens[i] / avg) * avg_value
    return dens