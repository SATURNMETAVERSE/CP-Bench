### https://developers.google.com/optimization/cp

BASIC_INSTRUCTIONS = r"""
You are a coding assistant with expertise in Python, constraint programming, and modelling combinatorial problems. Your task is to create Python code using the OR-tools library to solve constraint problems. Only the standard Python libraries and OR-tools should be used.
"""

PRINT_OUTPUT_EXAMPLE = r"""
-------- PRINT OUTPUT EXAMPLE START --------

An example for printing, if the problem description ends with: "Print the number of apples and oranges (apples, oranges), the cost per round (cost), and the total cost (total_cost).". In this case, the output of the solution as JSON should be done as follows:

```python
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'apples': solver.Value(apples),
        'oranges': solver.Value(oranges),
        'cost': [solver.Value(c) for c in cost],
        'total_cost': solver.ObjectiveValue()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
```

-------- PRINT OUTPUT EXAMPLE END --------
"""

GUIDELINES = r"""
-------- GUIDELINES START --------

1. Import necessary libraries (ortools.sat.python.cp_model, json, etc.).
2. Extract and process the provided data.
3. Define decision variables.
4. Construct a model with appropriate constraints.
5. Set the objective, if applicable.
6. Solve the model.
7. Print the solution in JSON format using as keys exactly the same variable names as given in the problem description's parentheses (at the print description sentence, which is normally at the end of the problem description). The values should be the decision variables' values or the objective value.

Mandatory guidelines:

- Be clear, logically organized, and include comments explaining each step.
- Use .Value() method to get solution values from variables.
- Avoid deprecated functions.
- Keep your code simple and maintainable to prevent syntax errors.
- Consider edge cases and possible errors that may occur during the execution of the code.

You should generate self-contained and self-runnable code, between ```python and ``` tags. Nothing else should be included in the response, only the code. So, the response should look like this:

```python
from ortools.sat.python import cp_model
import json

# Input data
...

# Model definition
model = cp_model.CpModel()

# Decision Variables
...

# Constraints
...

# Objective function (if any)
model.Minimize(objective)
# or model.Maximize(objective)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {...}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
```

Important: 
The generated code should always print the solution in JSON format using as keys the decision variables as given in the parentheses in the problem description, and the only values allowed are integers (or booleans) and lists of (lists of ...) integers (or booleans). This is really important for the evaluation of your response, because I will directly assign these values to the variables of the ground-truth model and check if the constraints (and objective) are satisfied, so follow these guidelines carefully.

-------- GUIDELINES END --------
"""

ORTOOLS_DOC = r"""
-------- OR-TOOLS DOCUMENTATION START --------

OR-tools is an open-source software suite for optimization, including constraint programming, linear programming, and mixed-integer programming.

An example of an OR-tools model:
```python
from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Variables
b = model.NewBoolVar('b')
x = [model.NewIntVar(1, 10, f'x{i}') for i in range(3)]

# Constraints
model.Add(x[0] == 1)
model.AddAllDifferent(x)
model.Add(x[1] + x[2] > 5).OnlyEnforceIf(b)

# Objective function (optional)
model.Maximize(sum(x) + 100 * b)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {'b': solver.Value(b), 'x': [solver.Value(var) for var in x]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
```

Short Documentation:

### Model:
- `model = cp_model.CpModel()`: Create a new model.

### Variables:
- `model.NewIntVar(lb, ub, 'name')`: Create a new integer variable with lower bound `lb` and upper bound `ub`.
- `model.NewBoolVar('name')`: Create a new boolean variable.
- `model.NewIntervalVar(start, size, end, 'name')`: Create a new interval variable with start, size, and end. An interval variable is a constraint, that is itself used in other constraints like NoOverlap. Internally, it ensures that `start + size == end`.

### Constraints:
- `model.Add(expr)`: Add a constraint to the model.
- `model.AddAllDifferent(*expressions)`: This constraint forces all expressions to have different values.
- `model.AddCircuit(arcs: Sequence[ArcT])`: Adds a circuit constraint from a sparse list of arcs that encode the graph.
- `model.AddCumulative(interval_vars, demands, capacity)`: The cumulative constraint. Each interval in `interval_vars` requires `demands[i]` resources and the capacity is `capacity`.
- `model.AddElement(index, variables, target)`: Enforces `variables[index] == target`.
- `model.AddImplication(a, b)`: Adds the implication constraint `a -> b`.
- `model.AddAllowedAssignments(variables, tuple_list)`: An AllowedAssignments constraint is a constraint on an array of variables, which requires that when all variables are assigned values, the resulting array equals one of the tuples in `tuple_list`.
- `model.AddAbsEquality(target, expr)`: Adds `target == Abs(expr)`.
- `model.AddModuloEquality(target, expr, mod)`: Adds `target = expr % mod`.
- `model.AddBoolXOr(literals)`: Adds `XOr(literals) == true`.
- `model.AddBoolOr(literals)`: Adds `Or(literals) == true`.
- `model.AddBoolAnd(literals)`: Adds `And(literals) == true`.
- `model.AddAtLeastOne(literals)`: Same as `add_bool_or`: `sum(literals) >= 1`.
- `model.AddAtMostOne(literals)`: Adds `AtMostOne(literals)`: `sum(literals) <= 1`.
- `model.AddExactlyOne(literals)`: Adds `ExactlyOne(literals)`: `sum(literals) == 1`.
- `model.AddNoOverlap2D(x_intervals, y_intervals)`: Adds a 2D no-overlap constraint.
- `model.AddNoOverlap(intervals)`: Adds a no-overlap constraint.

### Reification:
- `constraint.OnlyEnforceIf(boolvar)`: Adds an enforcement literal to the constraint. The constraint is only enforced if the enforcement literal is true.

### Objective Function:
- `model.Maximize(expr)`: Define an expression to maximize.
- `model.Minimize(expr)`: Define an expression to minimize.

### Solver:
- `solver = cp_model.CpSolver()`: Create a solver.
- `solver.Solve(model)`: Solve the model.
- `solver.Value(var)`: Get the value of the variable `var` in the solution.
- `solver.ObjectiveValue()`: Get the value of the objective function.

### Solving:
- `solver.Solve(model)`: Find a solution that satisfies all constraints.
- `solver.SolveWithSolutionCallback(model, callback)`: Solve the model and call the callback at each solution found.
- `solver.SearchForAllSolutions(model, callback)`: Search for all solutions and call the callback for each one.

-------- OR-TOOLS DOCUMENTATION END --------
"""

SYS_PROMPT_START = "--- SYSTEM PROMPT START ---"
SYS_PROMPT_END = "--- SYSTEM PROMPT END ---"

ORT_SYS_PROMPT_LVL_1 = SYS_PROMPT_START + """
""" + BASIC_INSTRUCTIONS + """
""" + PRINT_OUTPUT_EXAMPLE + """
""" + SYS_PROMPT_END

ORT_SYS_PROMPT_LVL_2 = SYS_PROMPT_START + """
""" + BASIC_INSTRUCTIONS + """
""" + PRINT_OUTPUT_EXAMPLE + """
""" + GUIDELINES + """
""" + SYS_PROMPT_END

ORT_SYS_PROMPT_LVL_3 = SYS_PROMPT_START + """
""" + BASIC_INSTRUCTIONS + """
""" + PRINT_OUTPUT_EXAMPLE + """
""" + GUIDELINES + """
""" + ORTOOLS_DOC + """
""" + SYS_PROMPT_END