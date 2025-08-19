# Dataset Breakdown

> **Recommended to use HuggingFace:** https://huggingface.co/datasets/kostis-init/CP-Bench

The dataset is divided into different folders, each containing problems of different sources.

- `aplai_course`: Problems from the APLAI course of KU Leuven, 2023-2024. As modelled here: https://github.com/kostis-init/LLM-CP-Modeling/tree/main/data/APLAI_course
  - [x] All 18 problems are added.
- `cpmpy_examples`: Problems from the cpmpy examples folder, https://github.com/CPMpy/cpmpy/tree/master/examples
  - All included, except for the ones that require enumeration of all solutions (e.g. `solveAll`).
- `csplib`: Problems from the csplib, https://www.csplib.org/Problems/
  - For now, only the ones modelled in the cpmpy repository are included (https://github.com/CPMpy/cpmpy/tree/master/examples/csplib), and the ones modelled by Hakan Kjellerstrand (http://www.hakank.org/cpmpy/).
- `hakan_examples`: Models created by Hakan Kjellerstrand, http://www.hakank.org/cpmpy/
  - In progress with alphabetical order. Currently includes all problems until `crypta.py`, excluding the following:
    - Those already modelled in other folders (e.g. aplai_course, cpmpy_examples, csplib)
    - Those that contain `solveAll`.
    - Global constraints tests, e.g. http://www.hakank.org/cpmpy/atmost_test.py

## Structure

Each instance is represented by a python file containing (with the same order) the following elements:

1. Metadata and sources at the beginning of the file.
2. A problem description in a multi-line comment.
3. The problem data after ```# Data``` and before ```# End of data```.
4. The CPMpy model:
    * Imports: Always use ```from cpmpy import *``` and any additional libraries required (e.g., ```numpy```
      or ```json```).
    * Parameters (based on the problem data).
    * Decision Variables: Always use ```intvar``` or ```boolvar```.
    * Model/Constraints: Always use ```model = Model()```.
    * Objective Function (if applicable): Always use ```model.minimize()``` or ```model.maximize()```.
    * Solve and print statements.

## Design

The following design choices were made:

* All instances are designed to be solvable, i.e., they have at least one feasible solution.
* Print statements are used to showcase the required output format.
* The problem descriptions are designed to be as human-readable as possible avoiding technical terms.
* It is the responsibility of the system under evaluation to parse the input problem data and use the information in it
  to generate the constraint model.

## Evaluation

This dataset is designed to facilitate the evaluation of systems that generate constraint models from natural language
problem
descriptions.
A generated CP model is considered correct if the solution it prints is correct.
This can be evaluated by adding this solution as a constraint to the provided ground-truth model and checking if the
model is consistent.
For optimization problems, the objective value should also be checked.