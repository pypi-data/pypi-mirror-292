# __init__.py

# Initialize global variables for arcSum(), need to be global so they can store values over multiple calls of the derivative function
prev_t = 0
prev_Sum = 0
prev_y = 0

# Optional flag for having matplotlib installed
pltsuccess = False

from catsolver import forward, inverse

# Version of the catenary-solver package
__version__ = "1.1.0"