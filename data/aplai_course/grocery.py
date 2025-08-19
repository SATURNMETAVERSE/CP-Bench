#!/usr/bin/python3
# Source: http://www.hakank.org/minizinc/grocery2.mzn

"""
A kid goes into a grocery store and buys four items. The cashier charges $7.11, the kid pays and is about to leave
when the cashier calls the kid back, and says "Hold on, I multiplied the four items instead of adding them; I’ll try
again; Hah, with adding them the price still comes to $7.11". What were the prices of the four items?

Print the prices of the four items (prices) in cents.
"""

# Import libraries
from cpmpy import *
import json
import numpy as np

# Parameters
total_price = 711  # total price in cents
num_items = 4

# Decision variables (prices are considered in cents)
prices = intvar(1, total_price, shape=num_items)

# Constraints
model = Model()

# The sum of the prices in cents is equal to the total price in cents
model += sum(prices) == total_price

# The product of the prices should equal to the scaled total price in cents (to account for the multiplication)
model += np.prod(prices) == total_price * (100 ** (num_items - 1))

# Solve
model.solve()

# Print the solution
solution = {"prices": prices.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
