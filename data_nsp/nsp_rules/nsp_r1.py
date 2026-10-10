# Source: own problem, single-rule nurse scheduling (R1, forbidden pattern N[ME])
# Source description: Settati, rule R1 of the six-rule nurse scheduling family

"""
There are n_nurses nurses and n_days days, numbered 0 to n_days-1. Each day, each nurse is assigned
exactly one of: Morning (0), Evening (1), Night (2), Rest (3). A working day is any day that is not
Rest. The schedule does not wrap around: day n_days-1 is not followed by day 0.

The schedule must satisfy one rule, for each nurse separately:
if a nurse works a Night on day d, then on day d+1 she must not work a Morning or an Evening.

There are no other rules. Any sequence not forbidden above is allowed.

Print the schedule (schedule) as a list of n_nurses lists of n_days integers, where entry [i][d] is
the shift of nurse i on day d.
"""

# Data
n_nurses = 3  # number of nurses
n_days = 14  # number of days
# End of data

# Import libraries
import json
import cpmpy as cp

M, E, N, R = 0, 1, 2, 3

# Decision variables
schedule = cp.intvar(0, 3, shape=(n_nurses, n_days), name="schedule")

model = cp.Model()

# Constraints
for i in range(n_nurses):
    s = schedule[i]
    for d in range(n_days - 1):
        model += ~((s[d] == N) & ((s[d + 1] == M) | (s[d + 1] == E)))

# Solve
model.solve()

# Print the solution
solution = {"schedule": schedule.value().tolist()}
print(json.dumps(solution))
