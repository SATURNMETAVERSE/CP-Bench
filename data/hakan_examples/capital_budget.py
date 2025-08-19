#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/capital_budget.py
# Source description: Winston 'Operations Research', page 478: Capital budgeting

"""
Stockco is considering four investments. Investment 1 will yield a net present value (NPV) of $16,000; investment
2, an NPV of $22,000; investment 3, an NPV of $12,000; and investment 4, an NPV of $8,000. Each investment requires a
certain cash outflow at the present time: investment 1, $5,000; investment 2, $7,000; investment 3, $4,000; and
investment 4, $3,000. Currently, $14,000 is available for investment. How to maximize the NPV obtained from
investments 1–4?

Print whether each investment is chosen (x) as a list of 0/1 values.
"""

# Import libraries
from cpmpy import *
import json

# Parameters
budget = 14
npv = [16, 22, 12, 8]
cash_flow = [5, 7, 4, 3]
n = 4

# variables
x = boolvar(shape=n, name="x")  # x[i] = 1 if investments i
z = intvar(0, 1000, name="z")  # total NPV

# constraints
model = Model([
    # the sum of all choosen investments must be less than the budget
    sum(x * cash_flow) <= budget,
    z == sum(x * npv)
])

# Objective: maximize the NPV
model.maximize(z)

# Solve the model
model.solve()

# Print the solution
solution = {"z": z.value(), "x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
