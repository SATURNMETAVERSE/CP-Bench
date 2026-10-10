# Source: own problem, single-rule nurse scheduling (R6, forbidden pattern NNNR+[EN])
# Source description: Settati, rule R6 of the six-rule nurse scheduling family

"""
There are n_nurses nurses and n_days days, numbered 0 to n_days-1. Each day, each nurse is assigned
exactly one of: Morning (0), Evening (1), Night (2), Rest (3). A working day is any day that is not
Rest. The schedule does not wrap around: day n_days-1 is not followed by day 0.

The schedule must satisfy one rule, for each nurse separately:
whenever a nurse works Night shifts on 3 consecutive days and rests on the day right after
the third of these Nights, her first working day after this rest period must be a Morning. This holds
whatever the number of rest days. If she rests until the last day of the schedule, the rule imposes
nothing.

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
        last = d + 2  # third Night
        for f in range(last + 2, n_days):
            # Nights on d..last, only Rest on last+1..f-1, first working day f is Evening or Night
            three_nights = cp.all([s[k] == N for k in range(d, last + 1)])
            rest_gap = cp.all([s[k] == R for k in range(last + 1, f)])
            model += ~(three_nights & rest_gap & ((s[f] == E) | (s[f] == N)))

# Solve
model.solve()

# Print the solution
solution = {"schedule": schedule.value().tolist()}
print(json.dumps(solution))
