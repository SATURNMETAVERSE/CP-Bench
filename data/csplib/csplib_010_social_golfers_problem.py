#!/usr/bin/python3
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob010_social_golfers.py
# Source description: https://www.csplib.org/Problems/prob010/

"""
010: Social Golfers Problem

The coordinator of a local golf club has come to you with the following problem. In their club, there are 32 social
golfers, each of whom play golf once a week, and always in groups of 4. They would like you to come up with a schedule
of play for these golfers, to last as many weeks as possible, such that no golfer plays in the same group as any other
golfer on more than one occasion. Possible variants of the above problem include: finding a 10-week schedule with
"maximum socialisation"; that is, as few repeated pairs as possible (this has the same solutions as the original
problem if it is possible to have no repeated pairs), and finding a schedule of minimum length such that each golfer
plays with every other golfer at least once ("full socialisation").

The problem can easily be generalized to that of scheduling \( m \) groups of \( n \) golfers over \( p \) weeks,
such that no golfer plays in the same group as any other golfer twice (i.e. maximum socialisation is achieved).

This problem is derived from a question posted to sci.op-research by bigwind777@aol.com (Bigwind777) in May 1998. It
is a generalisation of the problem of constructing a round-robin tournament schedule, where the number of players in
a "game" is more than two. The optimal solution for 32 golfers is not yet known.

Print the assignments of golfers to groups for each week (assign).
"""

# Data
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
# End of data

# Import libraries
from cpmpy import *
from cpmpy.expressions.utils import all_pairs
import numpy as np
import json


def social_golfers(n_weeks, n_groups, group_size):

    n_golfers = n_groups * group_size
    golfers = np.arange(n_golfers)
    weeks = np.arange(n_weeks)
    groups = np.arange(n_groups)

    # Possible configurations
    assign = intvar(0, n_groups - 1, shape=(n_golfers, n_weeks), name="assign")

    model = Model()

    # C1: Each group has exactly group_size players
    for gr in groups:
        for w in weeks:
            model += sum(assign[:, w] == gr) == group_size

    # C2: Each pair of players only meets at most once
    for g1, g2 in all_pairs(golfers):
        model += sum(assign[g1] == assign[g2]) <= 1

    # SBSA: Symmetry-breaking by selective assignment
    # On the first week, the first group_size golfers play in group 1, the
    # second group_size golfers play in group 2, etc. On the second week,
    # golfer 1 plays in group 1, golfer 2 plays in group 2, etc.
    # model += [assign[:, 0] == (golfers // group_size)]

    for g in golfers:
        if g < group_size:
            model += [assign[g, 1] == g]

    # First golfer always in group 0
    model += [assign[0, :] == 0]

    return model, assign

# Example usage
model, assign = social_golfers(n_weeks, n_groups, group_size)

# Solve
model.solve()

# Print
solution = {
    "assign": assign.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
