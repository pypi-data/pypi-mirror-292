# forward.py

try:
    import matplotlib.pyplot as plt
    pltsuccess = True
except:
    print('Matplotlib not found, built-in plotting will be unavailable')
import numpy as np
import scipy.integrate as integrate # For integration
import scipy.interpolate as spi
import math

# CatSolution -- class to make it easier to display important information about the result of the program
# Members:     status, int:         -1 -- failed, desired cable length is not long enough to reach desired cable endpoint
#                                    0 -- success, curve was found with endpoint within desired threshold
#                                    1 -- maximum number of loops occurred or variable increments are too small, 
#                                         returns the curve with the closest distance from desired endpoint to simulated endpoint
#              message, string:      describes result of attempt to find curve
#              type, string:         "Free-hanging" or "Loaded", depending on whether find_catenary() or find_loaded_catenary() was called
#              h, float:             h found as a result of attempt to find curve
#              idydx, float:         initial slope found as a result of attempt to find curve
#              x, array of floats:   list of x-coordinates that make up curve
#              y, array of floats:   list of y-coordinates that make up curve
class CatSolution:
    def __init__(self, status=None, x=None, y=None, h=None, dydx=None, message=None, type=None):
        if status is None: self.status = -1 
        else: self.status = status
        if x is None: self.x = None 
        else: self.x = x
        if y is None: self.y = None 
        else: self.y = y
        if message is None: self.message = "None" 
        else: self.message = message
        if h is None: self.h = None 
        else: self.h = h
        if dydx is None: self.idydx = None 
        else: self.idydx = dydx
        if type is None: self.type = None
        else: self.type = type
    def __str__(self):
        ret = f"\nMessage = {self.message}\n\tStatus = {self.status}\n\tType: {self.type}\n\th = {self.h}\n\tInitial Slope = {self.idydx}"
        if self.x is not None and self.y is not None:
            ret += f"\n\tEndpoint: ({self.x[-1]}, {self.y[-1]})"
        return ret
    
# arcSum() -- takes a point and calculates distance from the previous point to be added or
#             subtracted to a running sum that estimates arc length at a point on the curve
#          t, float:   x-value of current point
#          y, float:   y-value of current point
def arcSum(t, y): 
    global prev_Sum, prev_t, prev_y
    
    # add distance if the point is further along in the curve than the last point, otherwise subtract distance
    if t > prev_t: 
        prev_Sum += np.sqrt((prev_t-t)**2+(y-prev_y)**2)
        prev_t = t
        prev_y = y
        return prev_Sum
    else:
        prev_Sum -= np.sqrt((prev_t-t)**2+(y-prev_y)**2)
        prev_t = t
        prev_y = y
        return prev_Sum

# truncate() -- calculates length using distance between points and removes all x/y-points after the designated length has been achieved
#            t, array-like of floats:   list of x-values of every point on a curve
#            y, array-like of floats:   list of corresponding y-values of every point on a curve
#            length, float:             desired length of returned curve
def truncate(t, y, length):
    # Cast to Python list so list methods can be used
    t = list(t)
    y = list(y)
    if len(t) <= 10:
        return [t, y]
    
    # Creates an interpolated spline using the inputted x/y-points
    spline = spi.InterpolatedUnivariateSpline(t, y)
    # Clears x and y points so the list can be reused
    t.clear()
    y.clear()

    # Creates a bunch of points on the spline to make the length cutoff more precise
    tnew = np.linspace(0, math.ceil(length), 10000*math.ceil(length))
        
    # Adds points to new curve and keeps track of estimated arc length, once desired length is achieved returns new curve
    sum = 0
    for i in range(len(tnew)):
        t.append(tnew[i])
        y.append(spline(t[i]))
        if i > 0:
            sum += np.sqrt((t[i]-t[i-1])**2 + (y[i]-y[i-1])**2)
        if sum > length:
            break
    return [t, y]

def __hanging(t, y, length, h, dens):
    from catsolver.forward import arcSum

    # Initializes variables that represent the derivatives in the problem, so that they can be used in the return value
    x = y[0] # dy/dx = v -- first diff eq
    v = y[1] # dv/dx = (1/h)*w(s(t))*sqrt(1+v^2) -- second diff eq
    
    # Computes estimated arc length as diff eq solver is running, so that it can be used in the return value
    arc = arcSum(t, x)

    # If y-coordinate is larger than the length(+buffer), we know the cable is already longer than the length so we no longer care about the shape, make it a horizontal line (fixes some overflow errors)
    if x > length * 1.1: 
        return [0,0]

    # Returns a 2D array where index 0 is the solution to dy/dx, and index 1 is the solution to dv/dx -- solver computes both at the same time
    return [v, 1/h * dens(arc) * np.sqrt(1 + v**2)]

# Same as previous but the return values are adjusted for the loaded cable mechanics
def __loaded(t, y, length, h, dens):
    x = y[0] #dy/dx = v
    v = y[1] #dv/dx = (1/h)*w(x)
    if x > length * 1.1:
        return [0,0]
    return [v, 1/h * dens(t)]

# find_parameters() Main function to brute force h and the initial slope of a desired cable, given characteristics of the curve
#   required                    dens, function:      user-created function dens() that takes one argument and returns the mass density of the user's cable at specified 
#                                                    arc length (if using free-hanging model) or horizontal distance (if using loaded model)
#   required                    xdist, float:        desired horizontal distance between the two endpoints of the cable
#   required                    ydist, float:        desired vertical distance between the two endpoints of the cable
#   required                    length, float:       desired length of cable
#   optional, default=None      guess_h, float:      allows the user to set a starting value when searching for h, may decrease search times
#   optional, default=None      guess_dydx, float:   allows the user to set a starting value when searching for the initial slope of the curve, not recommended
#   optional, default=.01       thresh, float:       represents the maximum x/y-distance a generated curve's endpoint can be compared to the desired endpoint in order for
#                                                    the program to count a curve as successful, lower values take longer/more loops but give generally more accurate results
#   optional, default=500       max_attempts, int:   the maximum number of loops/curves to generate in an attempt to find the desired curve
#   optional, default=False     debug, boolean:      if set to True, prints information about each curve generated while searching for the correct curve
#   optional, default=hanging   type, function:      specifies if the free-hanging or loaded cable function should be used to solve the differential equation
def find_parameters(dens, xdist, ydist, length, guess_h=None, guess_dydx=None, thresh=None, max_attempts=500, debug=False, type=__hanging):
    from catsolver.forward import truncate
    from scipy.integrate import solve_ivp

    global prev_t, prev_Sum, prev_y
    
    # If the desired cable length is not long enough to reach the desired endpoint, no shape is possible, return -1
    if length < np.sqrt(xdist**2+ydist**2):
        return CatSolution(status=-1, message="Cable not long enough for desired endpoint")

    # Define x-points to evaluate the differential equation, the maximum we could possibly need to go is if the cable is perfectly horizontal, which is x = length
    start_t = 0
    end_t = math.ceil(length)
    numPoints = int(1000*length)
    time = np.linspace(start_t, end_t, numPoints)

    # Initialize starting h, intial slope, and threshold values based on guess_h and guess_dydx
    if(guess_h is None):
        h = 1
    else:
        h = guess_h
    if(guess_dydx is None):
        initial_dydx = ydist / xdist
    else:
        initial_dydx = guess_dydx
    if thresh is None:
        threshold = 0.01
    else:
        threshold = thresh

    # Initialize variables to be used over multiple loops
    increment_h = integrate.quad(lambda x : dens(x), 0, length)[0] / length * xdist # The starting amount h increases/decreases by
    increment_dydx = 1   # The starting amount the initial slope increases/decreases by
    max_s = .01          # The starting max step size to be used in the diff eq solver

    prev_checked_h = [0 for i in range(2)]      # Both used to check the previous 2 h/slope values
    prev_checked_dydx = [0 for i in range(2)]
    
    end_x = 0      # stores the x-coordinate of the current curve's endpoint
    old_x = -1     # stores the x-coordinate of the previous curve's endpoint
    end_y = 0      # stores the y-coordinate of the current curve's endpoint
    old_y = -1     # stores the y-coordinate of the previous curve's endpoint
    down = False   # keeps track of whether the last loop resulted in a decrease of the initial slope
    
    closest_combo = [-1, -1, -1000000, -1000000]   # Records information about the closest-generated curve: [h, initial slope, x-endpoint, y-endpoint]
    loopCount = 0   # Used to control how many loops the function is allowed to perform if a satisfying curve is never found
    
    while(loopCount < max_attempts):        
        # Reset global values every time a new curve is going to be generated
        prev_t = 0
        prev_Sum = 0
        prev_y = 0

        # Currently here just to show the function is running well
        # if not debug:
        #     print(f"\rLoop: {loopCount}", end = "")

        # horizonal tension cannot be negative, so neither can h
        if h <= 0:
            h = 0.001
        # The initial slope cannot exceed the slope of a line from the endpoint to the start since the curve would not have strictly positive curvature
        if initial_dydx > ydist/xdist:
            initial_dydx = ydist/xdist

        # Ends the function if increments are too small to have effect on the curve that is generated, returns closest curve
        if increment_h < 1e-12 and increment_dydx < 1e-12:
            sol = solve_ivp(fun = type, t_span=[time[0], time[-1]], y0 = [0, closest_combo[1]], t_eval=time, max_step = max_s, method = "DOP853", args=(length,closest_combo[0],dens))
            cat = truncate(sol.t, sol.y[0], length)
            return CatSolution(message="Process terminated due to precision loss. Cable may be too long to accurately obtain desired endpoint. Returning closest shape found.",
                               status = 1, 
                               h = closest_combo[0], 
                               dydx = closest_combo[1],
                               x = cat[0],
                               y = cat[1]
                              )

        # Allows the program to run faster at the start but become more precise as it gets closer to the solution, max_s has a high effect on program runtime if it is smaller
        if(increment_dydx < max_s and increment_dydx > .001):
            max_s = increment_dydx

        # Computes the curve using our differential equation and numerical solving methods
        #    fun: the derivative function to solve
        #    t_span: the range over which the solver should solve the diff eq (start and end values of x)
        #    y0: initial conditions for the differential equations, this is where we put initial_dydx so that it acts as the initial slope of the curve that is created
        #    t_eval: individual x-values to evaulate the differential equation at
        #    max_step: the maximum x-disance between points the solver can use to solve the equation, lower = more accurate, but more time, which is why we change max_s dynamically
        #    method: the method to be used to solve the differential equation, DOP853 is chosen for accuracy and does not require a Jacobian
        #    args: arguments to be passed into the derivative function (fun)
        sol = solve_ivp(fun = type, t_span=[time[0], time[-1]], y0 = [0, initial_dydx], t_eval=time, max_step = max_s, method = "DOP853", args=(length,h,dens))
            
        # Cut off all of the generated solution except for the length that we want, so now we have a curve that represents our desired length
        cat = truncate(sol.t, sol.y[0],  length)
        # Store endpoint of truncated curve
        end_x = cat[0][-1]
        end_y = cat[1][-1]

        # Prints debug information about each curve that is generated, so that it is easier to diagnose issues with the program
        if debug:
            print(f"Loop: {loopCount}")
            print(f"h = {h}, initial_dydx = {initial_dydx}")
            print(f"Endpoint = ({end_x}, {end_y})")
            print(f"h-increment = {increment_h}, dydx-increment = {increment_dydx}")
            if pltsuccess:
                plt.plot(cat[0], cat[1])
                plt.show()

        # If our endpoint is within the threshold we want, we have found a curve that is "close enough" and can return it as a CatSolution object
        if(xdist - threshold <= end_x and end_x <= xdist + threshold and ydist - threshold <= end_y and end_y <= ydist + threshold):
            return CatSolution(message=f"Success. Catenary found with endpoint = ({xdist}±{threshold}, {ydist}±{threshold}) after {loopCount} attempts.", 
                               status=0, 
                               x=cat[0], 
                               y=cat[1], 
                               h=h, 
                               dydx=initial_dydx
                              )
        
        # If the endpoint is closer to the desired endpoint than the previous closest endpoint, store this curve as our new closest curve
        if np.sqrt((xdist-end_x)**2 + (ydist-end_y)**2) < np.sqrt((xdist-closest_combo[2])**2 + (ydist-closest_combo[3])**2):
            closest_combo = [h, initial_dydx, end_x, end_y]

        # Sometimes the endpoint of the curve would increase in y-value when it is assumed to decrease as a result of decreasing the initial 
        # slope, and it would take too long to get the y-value to go back down under very small increments of change in initial slope. 
        # Therefore it is typically faster to increase the increment again, allowing for large changes in initial slope, until the increment 
        # goes back to getting smaller.
        if(down and end_y > old_y):
            increment_dydx *= 2
        # There is a similar phenomenon with the x-value of the endpoint that this code aims to address.
        if (end_x == old_x or (initial_dydx == prev_checked_dydx[loopCount % 2] and initial_dydx == prev_checked_dydx[1-loopCount % 2])) and end_y <= ydist + threshold and end_y >= ydist - threshold:
            increment_h *= 2

        # Values of h and initial slope will oscillate if their corresponding increments are too large, i.e. a curve might have an endpoint 
        # above the desired endpoint, then below, then above again. By dividing the increments when this happens, we allow more fine-tuning
        # of h and initial slope while still being fast by starting with a high increment that skips over many intermediate values
        #
        # ex: The actual value of h for a given curve is 42.25. h starts at 1 and has an increment of 5. It takes 9 loops for h to get to 46, where
        #     on the 10th loop it goes back down to 41. The increment of h becomes 2.5 and on the 11th loop h is 43.5. On the 12th loop it goes back
        #     down to 41 again, and the increment of h becomes 1.25. Now on the 13th loop h is 42.25, which is the correct value.
        #
        # There is more nuance due to the fact that both initial slope and h are being searched for at the same time and both have effects on the x
        # y endpoint of each curve, but for the most part that it how it works.
        if h == prev_checked_h[loopCount % 2] and h != prev_checked_h[1-loopCount % 2]:
            increment_h /= 2
        elif initial_dydx == prev_checked_dydx[loopCount % 2] and initial_dydx != prev_checked_dydx[1-loopCount % 2]:
            increment_dydx /= 2
        # Overwrite the oldest of the two last h and last initial_dydx values with the new ones
        prev_checked_dydx[loopCount % 2] = initial_dydx
        prev_checked_h[loopCount % 2] = h
        # Overwrite the previous endpoint coordinates
        old_y = end_y
        old_x = end_x

        # This brute force method works on some assumptions that are generally, but not always, true. They are:
        #    1) Increasing the initial slope will cause the y-value of the endpoint of a general catenary curve 
        #       to increase, and decreasing the initial slope will cause the y-value to decrease.
        #    2) Increasing the value of h will cause the x-value of the endpoint of a general catenary curve to 
        #       increase, and decreasing the value of h will cause the x-value to decrease.
        # Using these assumptions the following code attempts to move the endpoint closer to the desired endpoint
        # by adjusting the inital slope and value of h.
        if end_y < ydist - threshold:
            initial_dydx += increment_dydx
            down = False
        elif end_y > ydist + threshold:
            initial_dydx -= increment_dydx
            down = True
        else:
            down = False
        if end_x < xdist - threshold:
            h += increment_h
        elif end_x > xdist + threshold:
            h -= increment_h

        # Increase the number of loops that have passed by 1
        loopCount += 1

    # If the loop has ended, we were unable to find the curve within the threshold stated and we return the closest curve we found.
    prev_Sum = 0
    prev_t = 0
    prev_y = 0
    sol = solve_ivp(fun = type, t_span=[time[0], time[-1]], y0 = [0, closest_combo[1]], t_eval=time, max_step = max_s, method = "DOP853", args=(length,closest_combo[0],dens))
    cat = truncate(sol.t, sol.y[0], length)
    return CatSolution(message = f"Could not find shape after {loopCount} attempts, returning closest shape found", 
                       status = 1, 
                       h = closest_combo[0], 
                       dydx = closest_combo[1],
                       x = cat[0],
                       y = cat[1])

# find_catenary() -- Essentially calls find_parameters() with specific arguments to make compute time faster
#   required                    dens, function:      user-created function dens() that takes one argument and returns the mass density of the user's cable at specified 
#                                                    arc length (if using free-hanging model) or horizontal distance (if using loaded model)
#   required                    xdist, float:        desired horizontal distance between the two endpoints of the cable
#   required                    ydist, float:        desired vertical distance between the two endpoints of the cable
#   required                    length, float:       desired length of cable
#   optional, default=.01       thresh, float:       represents the maximum x/y-distance a generated curve's endpoint can be compared to the desired endpoint in order for
#                                                    the program to count a curve as successful, lower values take longer/more loops but give generally more accurate results
#   optional, default=500       max_attempts, int:   the maximum number of loops/curves to generate in an attempt to find the desired curve
#   optional, default=False     debug, boolean:      if set to True, prints information about each curve generated while searching for the correct curve
def find_catenary(dens, xdist, ydist, length, thresh=.01, max_attempts=500, debug=False):
    from catsolver.forward import find_parameters
    
    # Scales the density down by a factor of xdist so that it corresponds with the other scaled-down arguments later
    def scale_dens(s):
        return dens(s*xdist)
    # Ignore errors that don't seem to have an effect on the output of the function, always a good idea
    with np.errstate(all='ignore'):
        # Calls find_parameters() with arguments that are a scaled version of the find_catenary()'s arguments -- divide xdist, ydist, length, and thresh by xdist to get xdist ranging from 0-1
        scale_cat = find_parameters(scale_dens, 1, ydist/xdist, length/xdist, thresh=thresh/xdist, max_attempts=max_attempts, debug=debug)
    # Cleans up the message that is outputted so it shows the original endpoint+/-threshold, not the scaled one
    if scale_cat.status == 0:
        loopCount = scale_cat.message[scale_cat.message.find("after")+6:scale_cat.message.find("attempts")-1]
        scale_cat.message = f"Success. Catenary found with endpoint = ({xdist}±{thresh}, {ydist}±{thresh}) after {loopCount} attempts."
    return CatSolution(message = scale_cat.message,
                       status = scale_cat.status,
                       h = scale_cat.h * xdist,
                       dydx = scale_cat.idydx,
                       x = [scale_cat.x[i] * xdist for i in range(len(scale_cat.x))],
                       y = [scale_cat.y[i] * xdist for i in range(len(scale_cat.y))],
                       type = "Free-hanging"
                      )

# find_loaded_catenary() is the exact same as find_catenary(), but uses type=loaded in the find_parameters() function call to solve the loaded cable diff eq
def find_loaded_catenary(dens, xdist, ydist, length, thresh=.01, max_attempts=500, debug=False):
    from catsolver.forward import find_parameters
    
    def scale_dens(s):
        return dens(s*xdist)
    scale_cat = find_parameters(scale_dens, 1, ydist/xdist, length/xdist, thresh=thresh/xdist, max_attempts=max_attempts, debug=debug, type=__loaded)
    if scale_cat.status == 0:
        loopCount = scale_cat.message[scale_cat.message.find("after")+6:scale_cat.message.find("attempts")-1]
        scale_cat.message = f"Success. Catenary found with endpoint = ({xdist}±{thresh}, {ydist}±{thresh}) after {loopCount} attempts."
    return CatSolution(message = scale_cat.message,
                       status = scale_cat.status,
                       h = scale_cat.h * xdist,
                       dydx = scale_cat.idydx,
                       x = [scale_cat.x[i] * xdist for i in range(len(scale_cat.x))],
                       y = [scale_cat.y[i] * xdist for i in range(len(scale_cat.y))],
                       type = "Loaded"
                      )