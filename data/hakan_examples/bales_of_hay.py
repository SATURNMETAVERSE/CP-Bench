#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/bales_of_hay.py
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
You have five bales of hay.

For some reason, instead of being weighed individually, they were weighed
in all possible combinations of two. The weights of each of these
combinations were written down and arranged in numerical order, without
keeping track of which weight matched which pair of bales. The weights,
in kilograms, were 80, 82, 83, 84, 85, 86, 87, 88, 90, and 91.

Print the weights of each bale (bales).
"""

# Import libraries
from cpmpy import *
import json

# Parameters
n = 5
weights = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]

# variables
bales = intvar(0, 50, shape=n, name="bales")

model = Model()


def increasing(args):
    """
    Ensure that the values in args are increasing.
    """
    return [args[i - 1] <= args[i] for i in range(1, len(args))]


# constraints
model += [increasing(bales)]

for w in weights:
    i = intvar(0, n - 1)
    j = intvar(0, n - 1)
    model += [i < j]
    model += [w == bales[i] + bales[j]]

# Solve the model
model.solve()

# Print the solution
solution = {"bales": bales.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
