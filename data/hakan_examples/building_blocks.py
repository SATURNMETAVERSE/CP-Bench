#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/building_blocks.py
# Source description: http://brownbuffalo.sourceforge.net/BuildingBlocksClues.html
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Each of four alphabet blocks has a single letter of the alphabet on each
of its six sides. In all, the four blocks contain every letter but
Q and Z. By arranging the blocks in various ways, you can spell all of
the words listed below. Can you figure out how the letters are arranged
on the four blocks?

 BAKE ONYX ECHO OVAL
 GIRD SMUG JUMP TORN
 LUCK VINY LUSH WRAP

Print the solution as a list of 24 numbers representing at which block each letter is placed (dice), between 0 and 3.
"""

# Import libraries
from cpmpy import *
import json
import numpy as np


def count(a, val, c):
    """
    count(a,val,c)

    c is the number of occurrences of val in array a.
    """
    return [c == sum([a[i] == val for i in range(len(a))])]


def global_cardinality_count(a, gcc):
    """
    global_cardinality_count(a,gcc)

    Global cardinality count: Collect the number of occurrences of each value 0..a.ub
    in gcc. The array gcc must be of length 0..ub.
    """
    n = len(a)
    ub = max([a[i].ub for i in range(n)])
    constraints = []
    for i in range(ub + 1):
        constraints += [count(a, i, gcc[i])]

    return constraints


n = 4
num_words = 12
m = 24

# Index 1 based (adjusted below)
A = 1;
B = 2;
C = 3;
D = 4;
E = 5;
F = 6;
G = 7;
H = 8;
I = 9;
J = 10;
K = 11;
L = 12;
M = 13;
N = 14;
O = 15;
P = 16;
R = 17;
S = 18;
T = 19;
U = 20;
V = 21;
W = 22;
X = 23;
Y = 24;

alpha = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
         "N", "O", "P", "R", "S", "T", "U", "V", "W", "X", "Y"];

words = np.array([[B, A, K, E],
                  [O, N, Y, X],
                  [E, C, H, O],
                  [O, V, A, L],
                  [G, I, R, D],
                  [S, M, U, G],
                  [J, U, M, P],
                  [T, O, R, N],
                  [L, U, C, K],
                  [V, I, N, Y],
                  [L, U, S, H],
                  [W, R, A, P]])

dice = intvar(0, n - 1, shape=m, name="dice")

model = Model()

# the letters in a word must be on a different die
for word in range(num_words):
    # Also, adjust for 1-based
    model += (AllDifferent([dice[words[word] - 1]]))

# there must be exactly 6 letters of each die
model += (global_cardinality_count(dice, [6 for i in range(n)]))

# symmetry breaking (first word is placed)
model += (dice[0] <= dice[6])
model += (dice[6] <= dice[12])

model.solve()

# Print the solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
