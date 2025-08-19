#!/usr/bin/python3
# Source: http://www.hakank.org/minizinc/climbing_stairs.mzn

"""
We want to climb a stair of n steps with [m1, m2] steps at a time. For example a stair of 4 steps with m1 = 1,
and m2 = 2 can be climbed with a sequence of four one-step moves or with two two-steps moves. Find a way to climb a
stair of 20 steps with m1 = 3 and m2 = 5, i.e. you can take only 3 or 4 or 5 steps at a time.

Print the number of steps (steps) taken at each move as a list of 20 integers, where each integer is between 3 and 5,
or 0 if no steps are taken at that move, i.e. after we reach the top of the stair with the last move.
"""

# Import libraries
from cpmpy import *
import json
import numpy as np

# Parameters
n = 20  # total number of steps in the stair
m1, m2 = 3, 5  # number of steps that can be taken at a time

# Decision variables
# In the worst case, we take all steps one at a time, so we have 'n' decision variables
steps = intvar(0, m2, shape=n)  # steps taken at each move

# Model setup
model = Model()

# Constraint: the sum of steps should equal the total number of stairs
model += sum(steps) == n

# Constraint: the number of steps taken at each move should be between m1 and m2 or 0
model += [(steps[i] >= m1) | (steps[i] == 0) for i in range(n)]
model += [steps[i] <= m2 for i in range(n)]

# Trailing zeros: If a step is 0, then all the following steps should be 0
for i in range(1, n):
    model += (steps[i - 1] == 0).implies(all(steps[j] == 0 for j in range(i, n)))

# Solve
model.solve()

# Print the solution
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
