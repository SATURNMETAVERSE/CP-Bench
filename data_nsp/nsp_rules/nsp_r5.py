# Source: own problem, single-rule nurse scheduling (R5, forbidden pattern NR+N)
# Source description: Settati, rule R5 of the six-rule nurse scheduling family

"""
There are n_nurses nurses and n_days days, numbered 0 to n_days-1. Each day, each nurse is assigned
exactly one of: Morning (0), Evening (1), Night (2), Rest (3). A working day is any day that is not
Rest. The schedule does not wrap around: day n_days-1 is not followed by day 0.

The schedule must satisfy one rule, for each nurse separately:
if a nurse works a Night on day d and rests on day d+1, then her first working day after
day d must not be a Night. This holds whatever the number of consecutive rest days in between. If she
rests until the last day of the schedule, the rule imposes nothing.

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
    for d in range(n_days):
        for e in range(d + 2, n_days):
            # Night on d, only Rest on d+1..e-1, Night on e
            rest_gap = cp.all([s[k] == R for k in range(d + 1, e)])
            model += ~((s[d] == N) & rest_gap & (s[e] == N))

# Solve
model.solve()

# Print the solution
solution = {"schedule": schedule.value().tolist()}
print(json.dumps(solution))
