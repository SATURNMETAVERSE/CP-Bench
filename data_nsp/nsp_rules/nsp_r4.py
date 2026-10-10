# Source: own problem, single-rule nurse scheduling (R4, forbidden pattern NNN([MEN]|R[MEN]))
# Source description: Settati, rule R4 of the six-rule nurse scheduling family

"""
There are n_nurses nurses and n_days days, numbered 0 to n_days-1. Each day, each nurse is assigned
exactly one of: Morning (0), Evening (1), Night (2), Rest (3). A working day is any day that is not
Rest. The schedule does not wrap around: day n_days-1 is not followed by day 0.

The schedule must satisfy one rule, for each nurse separately:
whenever a nurse works Night shifts on 3 consecutive days, the next 2 days after the
third of these Nights must both be Rest days. If the schedule ends before these 2 days, only the
days inside the schedule must be Rest.

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
    for d in range(n_days - 2):
        three_nights = cp.all([s[d + k] == N for k in range(3)])
        for k in (3, 4):
            if d + k < n_days:
                model += three_nights.implies(s[d + k] == R)

# Solve
model.solve()

# Print the solution
solution = {"schedule": schedule.value().tolist()}
print(json.dumps(solution))
