#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/big_bang2.py
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Nontransitive dice a la The Big Bang Theory in Comet
Thore Graepel (thoregraepel@googlemail.com)

The idea is to create a set of five dice such that the dominance relationships
between the dice is isomorphic to the corresponding relationships in the game
Rock-Paper-Scissors extended by the choices Lizard and Spock.
(originally from http://www.samkass.com/theories/RPSSL.html).

Each choice beats two other choices and is beaten by two other choices.
In particular, we have the following ten 'beats' relationships

1:  Rock(1) crushes Scissors(3)
2:  Rock(1) crushes Lizard(4)
3:  Paper(2) covers Rock(1)
4:  Paper(2) disproves Spock(5)
5:  Scissors(3) cuts Paper(2)
6:  Scissors(3) decapitate Lizard(4)
7:  Lizard(4) eats Paper(2)
8:  Lizard(4) poisons Spock(5)
9:  Spock(5) vaporizes Rock(1)
10: Spock(5) smashes Scissors(3)

Print the dice (dice) as a list of lists where each sublist is a die.
"""

# Import libraries
from cpmpy import *
import json


def increasing(args):
    """
    Ensure that the values in args are increasing.
    """
    return [args[i - 1] <= args[i] for i in range(1, len(args))]


rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4

m = 5  # number of dice
n = 8  # number of faces of each die
f = 2 * n  # max face value of dice
k = 10  # number of competitions
edge = [
    [rock, scissors],
    [rock, lizard],
    [paper, rock],
    [paper, spock],
    [scissors, paper],
    [scissors, lizard],
    [lizard, paper],
    [lizard, spock],
    [spock, rock],
    [spock, scissors]
]

#
# declare variables
#

dice = intvar(1, f, shape=(m, n), name="dice")
comp = intvar(0, n * n, shape=(k, 2), name="comp")
max_val = intvar(0, f, name="max_val")

model = Model()
#
# constraints
#
model += (max_val == max(dice))

# Symmetry breaking
# order of the number of each die, lowest first
model += [increasing(dice[i]) for i in range(m)]
# This is faster but yield max_val = 11 instead of the correct 9!
# model += [lex_less(dice[i],dice[i+1]) for i in range(m-1)]
model += [dice[0, 0] == 1]
model += [AllDifferent([dice[i, 0] for i in range(m)])]

# and now we roll...
for c in range(k):
    model += (comp[c, 0] == sum([dice[edge[c][0], r1] > dice[edge[c][1], r2]
                                 for r1 in range(n) for r2 in range(n)]))

    model += (comp[c, 1] == sum([dice[edge[c][1], r1] > dice[edge[c][0], r2]
                                 for r1 in range(n) for r2 in range(n)]))

    model += (comp[c, 0] > comp[c, 1])

    # added later by Thore:
    model += (comp[c, 0] + comp[c, 1] == n * n)  # make sure there are no ties

# Solve the model
model.solve()

# Print the solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
