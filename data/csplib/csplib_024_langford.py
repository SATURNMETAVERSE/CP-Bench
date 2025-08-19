#!/usr/bin/python3
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob024_langford.py
# Source description: https://www.csplib.org/Problems/prob024/

"""
024: Langford's Number Problem

Consider two sets of the numbers from 1 to 4. The problem is to arrange the eight numbers in the two sets into a
single sequence in which the two 1’s appear one number apart, the two 2’s appear two numbers apart, the two 3’s
appear three numbers apart, and the two 4’s appear four numbers apart.

The problem generalizes to the L(k, n) problem, which is to arrange k sets of numbers 1 to n, so that each appearance
of the number m is m numbers on from the last. For example, the L(3, 9) problem is to arrange 3 sets of the numbers
1 to 9 so that the first two 1’s and the second two 1’s appear one number apart, the first two 2’s and the second
two 2’s appear two numbers apart, etc.

Print the positions (position) and the solution sequence (solution).
"""

# Data
k = 4  # Number of sets
# End of data

# Import libraries
import json
from cpmpy import *


def langford(k):
    model = Model()

    if not (k % 4 == 0 or k % 4 == 3):
        print("There is no solution for K unless K mod 4 == 0 or K mod 4 == 3")
        return None, None

    # Variables
    position = intvar(0, 2 * k - 1, shape=2 * k, name="position")
    solution = intvar(1, k, shape=2 * k, name="solution")

    # Constraints
    model += [AllDifferent(position)]

    for i in range(1, k + 1):
        model += [position[i + k - 1] == position[i - 1] + i + 1]
        model += [i == solution[position[i - 1]]]
        model += [i == solution[position[k + i - 1]]]

    # Symmetry breaking
    model += [solution[0] < solution[2 * k - 1]]

    return model, (position, solution)


# Example usage
model, (position, solution) = langford(k)
if model:
    model.solve()

    # Print
    solution_dict = {
        "position": position.value().tolist(),
        "solution": solution.value().tolist()
    }
    print(json.dumps(solution_dict))
# End of CPMPy script
