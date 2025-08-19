#!/usr/bin/python3
# Source: http://www.hakank.org/minizinc/farmer_and_cows.mzn

"""
A farmer has 25 cows numbered 1 to 25. number 1 cow gives 1kg milk, number 2 gives 2 kg... number and so on up to
number 25 that gives 25 kg per day. The farmer has 5 sons and he wants to distribute his cows to them: 7 to the
first, 6 to the second and so on down to 3 to the last, however, the total quantity of milk produced should be the
same: how can he distribute the cows?

Print the assignment of cows to sons (cow_assignments), as a list of 25 integers from 0 to 4.
"""

# Import libraries
from cpmpy import *
import json

# Parameters
num_cows = 25
num_sons = 5
milk_per_cow = list(range(1, num_cows + 1))
cows_per_son = [7, 6, 5, 4, 3]

total_milk = sum(milk_per_cow)  # Total milk produced by all cows
total_milk_per_son = total_milk // num_sons  # Total milk each son should get

# Decision variables
# Each cow is assigned to a son, represented by 0-4
cow_assignments = intvar(0, num_sons - 1, shape=num_cows)

# Constraints
model = Model()

# Each son gets a specific number of cows
for son in range(num_sons):
    model += sum(cow_assignments == son) == cows_per_son[son]

# The total milk production for each son is equal
for son in range(num_sons):
    model += sum(milk_per_cow[i] * (cow_assignments[i] == son) for i in range(num_cows)) == total_milk_per_son

# Solve
model.solve()

# Print the solution
solution = {"cow_assignments": cow_assignments.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
