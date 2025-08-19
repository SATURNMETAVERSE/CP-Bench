#!/usr/bin/python3
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob054_n_queens.py
# Source description: https://www.csplib.org/Problems/prob054/

"""
054: N-Queens Problem

Can \( n \) queens (of the same color) be placed on a \( n \times n \) chessboard so that none of the queens can attack
each other? In chess, a queen attacks other squares on the same row, column, or either diagonal as itself. So the
\( n \)-queens problem is to find a set of \( n \) locations on a chessboard, no two of which are on the same row,
column or diagonal.

A simple arithmetical observation may be helpful in understanding models. Suppose a queen is represented by an ordered
pair \((\alpha, \beta)\), the value \(\alpha\) represents the queen’s column, and \(\beta\) its row on the chessboard.
Then two queens do not attack each other iff they have different values of all of \(\alpha\), \(\beta\), \(\alpha - \beta\),
and \(\alpha + \beta\). It may not be intuitively obvious that chessboard diagonals correspond to sums and differences,
but consider moving one square along the two orthogonal diagonals: in one direction the sum of the coordinates does not
change, while in the other direction the difference does not change. (We do not suggest that pairs \((\alpha, \beta)\)
is a good representation for solving.)

The problem has inherent symmetry. That is, for any solution we obtain another solution by any of the 8 symmetries of
the chessboard (including the identity) obtained by combinations of rotations by 90 degrees and reflections.

Print the positions of the queens on the chessboard (queens).
"""

# Data
n = 10  # Size of the chessboard and number of queens
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def n_queens(n=8):

    queens = intvar(1, n, shape=n, name="queens")

    # Constraints on columns and left/right diagonal
    model = Model([
        AllDifferent(queens),
        AllDifferent(queens - np.arange(n)),
        AllDifferent(queens + np.arange(n)),
    ])

    return model, (queens,)

# Example usage
model, (queens,) = n_queens(n)
model.solve()

# Print
solution = {"queens": queens.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
