#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/among.py
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Requires exactly m variables in x to take one of the values in v.

Print the array x (x).
"""

# Data
n = 5  # Length of x
m = 3  # Number of values
v = [1, 5, 8]  # Values to be among in x
# End of data

# Import libraries
from cpmpy import *
import json


def among(m,x,v):
  """
  among(m,x,v)

  Requires exactly m variables in x to take one of the values in v.
  """
  return [m == sum([x[i] == j for i in range(len(x)) for j in v])]


# Decision variables
x = intvar(1, 8, shape=n, name="x")

# Model
model = Model([
    among(m, x, v)
])

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
