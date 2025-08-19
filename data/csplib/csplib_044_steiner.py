#!/usr/bin/python3
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob044_steiner.py
# Source description: https://www.csplib.org/Problems/prob044/

"""
044: Steiner Triple Systems

The ternary Steiner problem of order \( n \) consists of finding a set of \( n \cdot (n-1)/6 \) triples of distinct
integer elements in \(\{1, \ldots, n\}\) such that any two triples have at most one common element. It is a hypergraph
problem coming from combinatorial mathematics [luneburg1989tools] where \( n \) modulo 6 has to be equal to 1 or 3
[lindner2011topics]. One possible solution for \( n = 7 \) is \(\{\{1, 2, 3\}, \{1, 4, 5\}, \{1, 6, 7\}, \{2, 4, 6\},
\{2, 5, 7\}, \{3, 4, 7\}, \{3, 5, 6\}\}\). The solution contains \( 7 \cdot (7-1)/6 = 7 \) triples.

This is a particular case of the more general Steiner system.

More generally still, you may refer to Balanced Incomplete Block Designs. In fact, a Steiner Triple System with \( n \)
elements is a BIBD(\( n, n \cdot (n-1)/6, (n-1)/2, 3, 1 \)).

Print the set of triples (sets).
"""

# Data
n = 9  # Order of the Steiner Triple System
# End of data

# Import libraries
import json
from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def steiner(n=15):
    assert n % 6 == 1 or n % 6 == 3, "N must be (1|3) modulo 6"

    n_sets = int(n * (n - 1) // 6)

    model = Model()

    # boolean representation of sets
    # sets[i,j] = true iff item j is part of set i
    sets = boolvar(shape=(n_sets, n), name="sets")

    # cardinality of set if 3
    # can be written cleaner, see issue #117
    # model += sum(sets, axis=0) == 3
    model += [sum(s) == 3 for s in sets]

    # cardinality of intersection <= 1
    for s1, s2 in all_pairs(sets):
        model += sum(s1 & s2) <= 1

    # symmetry breaking
    model += (sets[(0, 0)] == 1)

    return model, (sets,)

# Example usage
model, (sets,) = steiner(n)
model.solve()

# Print
solution = {"sets": sets.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
