#!/usr/bin/python3
# Source: http://www.hakank.org/cpmpy/cabling.py
# Source description: https://yurichev.com/blog/cabling_Z3/
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Take a rack cabinet, like this one:
  [ an image ]

Let's say, there are 8 1U devices, maybe servers, routers and whatnot, named
as A, B, C, D, E, F, G, H. Devices must be connected by cables: probably
twisted pair or whatever network engineers using today. Some devices must be
connected by several cables (2 cables, 3 or 4):

A <--- 1 cable  ---> H
A <--- 2 cables ---> E
B <--- 4 cables ---> F
C <--- 1 cable  ---> G
C <--- 1 cable  ---> D
C <--- 1 cable  ---> E
D <--- 3 cables ---> H
G <--- 1 cable  ---> H

The problem: how we can place these 8 devices in such an order, so that sum
of all cable lengths would be as short as possible?

Print the optimal sum of all cable lengths (final_sum).
"""

# Import libraries
from cpmpy import *
import json

# Parameters
n = 8

model = Model()

# A <--- 1 cable  ---> H
# A <--- 2 cables ---> E
# B <--- 4 cables ---> F
# C <--- 1 cable  ---> G
# C <--- 1 cable  ---> D
# C <--- 1 cable  ---> E
# D <--- 3 cables ---> H
# G <--- 1 cable  ---> H
A, B, C, D, E, F, G, H = list(range(n))

cable_struct = [[A, H, 1],
                [A, E, 2],
                [B, F, 4],
                [C, G, 1],
                [C, D, 1],
                [C, E, 1],
                [D, H, 3],
                [G, H, 1]]

x = intvar(0, n - 1, shape=n, name="x")  # position of the device in the rack
t = intvar(1, n * n, shape=len(cable_struct), name="t")  # cable lengths
final_sum = intvar(0, n * n, name="final_sum")  # sum of all cable lengths

# all "devices" has distinct positions in rack:
model += [AllDifferent(x),
          final_sum == sum(t)]

for i in range(len(cable_struct)):
    a, b, num = cable_struct[i]
    model += [t[i] == abs(x[a] - x[b]) * num]

model.minimize(final_sum)

# Solve
model.solve()

# Print the solution
solution = {"final_sum": final_sum.value()}
print(json.dumps(solution))
# End of CPMPy script
