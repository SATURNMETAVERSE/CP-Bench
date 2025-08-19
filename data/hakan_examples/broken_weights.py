#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/broken_weights.py
# Source description: http://www.mathlesstraveled.com/?p=701
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Here's a fantastic problem I recently heard. Apparently it was first
posed by Claude Gaspard Bachet de Meziriac in a book of arithmetic problems
published in 1612, and can also be found in Heinrich Dorrie's 100
Great Problems of Elementary Mathematics.

  A merchant had a forty pound measuring weight that broke
  into four pieces as the result of a fall. When the pieces were
  subsequently weighed, it was found that the weight of each piece
  was a whole number of pounds and that the four pieces could be
  used to weigh every integral weight between 1 and 40 pounds. What
  were the weights of the pieces?

Note that since this was a 17th-century merchant, he of course used a
balance scale to weigh things. So, for example, he could use a 1-pound
weight and a 4-pound weight to weigh a 3-pound object, by placing the
3-pound object and 1-pound weight on one side of the scale, and
the 4-pound weight on the other side.

Print the weights of the four pieces (weights).
"""

# Import libraries
from cpmpy import *
import json


def increasing_strict(args):
    """
    Ensure that the values in args are strict increasing.
    """
    return [args[i - 1] < args[i] for i in range(1, len(args))]


# Parameters
m = 40
n = 4

# variables
weights = intvar(1, m, shape=n, name="weights")
x = intvar(-1, 1, shape=(m, n), name="x")

model = Model(minimize=weights[-1])
# model = Model()

# constraints

model += [AllDifferent(weights)]
model += [sum(weights) == m]

# Check that all weights from 1 to 40 can be made.
#
# Since all weights can be on either side
# of the side of the scale we allow either
# -1, 0, or 1 of the weights, assuming that
# -1 is the weights on the left and 1 is on the right.
#
for i in range(m):
    model += [sum([weights[j] * x[i, j] for j in range(n)]) == i + 1]
    # model += [i+1 == sum(weights * x[i])] # using numpy's magic

# symmetry breaking
# for j in range(1, n):
#   model += [weights[j-1] < weights[j]]
model += [increasing_strict(weights)]
model.solve()

# Print the solution
solution = {"weights": weights.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
