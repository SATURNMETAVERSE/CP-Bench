#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/archery_puzzle.py

"""
How close can the young archer come to scoring a total of 100 using as many arrows as she pleases? The targets are: 16, 17, 23, 24, 39, 40.

Print the number of hits on each target (hits).
"""

# Import libraries
from cpmpy import *
import json

# Parameters
targets = [16, 17, 23, 24, 39, 40]
n = len(targets)
target_score = 100

# Decision variables
hits = intvar(0, 100, shape=n, name="hits")
score = intvar(0, 100, name="score")
deviation = intvar(0, 100, name="deviation")

# Model
model = Model([
    score == sum(hits * targets),
    deviation == abs(target_score - score)
])

# Objective
model.minimize(deviation)

# Solve the model
model.solve()

# Print the solution
solution = {"hits": hits.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
