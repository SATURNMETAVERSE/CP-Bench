#!/usr/bin/python3
# Source: http://www.hakank.org/minizinc/money_change.mzn

"""
Alice has to give Bob change of 199 euros. She has 6 different types of coins of different value ([1, 2, 5, 10,
25, 50]) and she has a certain number of coins of each value available ([20, 10, 15, 8, 4, 2]). How can the change be
composed with the available coins minimizing the number of coins used?

Print the number of coins of each type to give to Bob (coin_counts).
"""

# Import libraries
from cpmpy import *
import json

# Parameters
amount = 199  # amount of money to give to Bob
n = 6  # number of types of coins
types_of_coins = [1, 2, 5, 10, 25, 50]  # value of each type of coin
available_coins = [20, 10, 15, 8, 4, 2]  # number of available coins of each type

# Decision Variables
coin_counts = intvar(0, 20, shape=n)  # number of coins of each type to give to Bob

# Constraints
model = Model()

# The sum of the coins given to Bob must be equal to the amount of money to give him
model += sum(coin_counts[i] * types_of_coins[i] for i in range(n)) == amount

# The number of each type of coin given to Bob must not exceed the available coins
for i in range(n):
    model += coin_counts[i] <= available_coins[i]

# Objective: Minimize the total number of coins given to Bob
model.minimize(sum(coin_counts))

# Solve
model.solve()

# Print the solution
solution = {"coin_counts": coin_counts.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
