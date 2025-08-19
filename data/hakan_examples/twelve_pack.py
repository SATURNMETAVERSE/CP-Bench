#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/12_pack_problem.py

"""
Given a target number of beers, find the closest combination of 7-packs and 13-packs that meets or exceeds the target.

Print the counts of 7-packs and 13-packs used (counts).
"""

# Data
target = 20  # Target number of beers
# End of data

# Import libraries
from cpmpy import *
import json
import builtins

# Parameters
n = 2  # Number of pack sizes
packs = [7, 13]  # Pack sizes
max_val = target * 2  # Arbitrary max limit of pack counts

# Decision variables
counts = intvar(0, max_val, shape=n, name="counts")  # Count of each pack size used
total = intvar(0, max_val * n, name="total")  # Total number of beers

# Model
model = Model([
    total == (counts * packs).sum(),
    total >= target,
])

# Objective
model.minimize(total)

# Solve the model
model.solve()

# Print the solution
solution = {"counts": counts.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
