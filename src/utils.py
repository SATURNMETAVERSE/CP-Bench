import datetime
import subprocess
import sys
import tempfile
import minizinc
import re
from enums import ErrorType, InstanceCategory
from llm_config import TEMPERATURE, MAX_TOKENS, TOP_P, SYS_PROMPT_LVL, NUM_EXAMPLES, NUM_SAMPLES, \
    SAMPLING_TEMPERATURE, LLM_ID, MAX_SELF_VERIFICATION_ATTEMPTS, SELF_VERIFICATION_TYPE, \
    SAMPLES_CACHE_ENABLED, SAMPLES_CACHE_LOCATION, SEED, MAX_LLM_CALL_RETRIES, RESULTS_DIR, \
    MODELLING_LANGUAGE
from llm_utils import SYSTEM_PROMPT
import json
import os

from data_consistency import get_modified_script
from datetime import datetime, timedelta


def log_results_json(to_log):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # ensure LLM_ID is a valid directory name
    llm_id_safe = re.sub(r'[\\/*?:"<>|]', '_', LLM_ID)
    file_to_log = f"{RESULTS_DIR}/{llm_id_safe}/log_{timestamp}.json"
    os.makedirs(os.path.dirname(file_to_log), exist_ok=True)

    results = {
        "summary": {
            "total_instances": len(to_log),
            "successes": sum([1 for log_instance in to_log if log_instance.error_type == ErrorType.NO_ERROR]),
            "errors": sum([1 for log_instance in to_log if log_instance.error_type != ErrorType.NO_ERROR]),
            "accuracy": sum([1 for log_instance in to_log if log_instance.error_type == ErrorType.NO_ERROR]) / len(
                to_log) if len(to_log) > 0 else 0,
            "total_tokens": sum(
                [log_instance.total_prompt_tokens + log_instance.total_completion_tokens for log_instance in to_log])
        },
        "category_results": {
            category.name: {
                "successes": sum([1 for log_instance in to_log if
                                  log_instance.instance.category == category and log_instance.error_type == ErrorType.NO_ERROR]),
                "total": sum([1 for log_instance in to_log if log_instance.instance.category == category]),
                "accuracy": sum([1 for log_instance in to_log if
                                 log_instance.instance.category == category and log_instance.error_type == ErrorType.NO_ERROR]) / sum(
                    [1 for log_instance in to_log if log_instance.instance.category == category]) if sum(
                    [1 for log_instance in to_log if log_instance.instance.category == category]) > 0 else 0
            } for category in InstanceCategory
        },
        "error_type_results": {
            error_type.name: {
                "count": sum([1 for log_instance in to_log if log_instance.error_type == error_type]),
                "percentage": sum([1 for log_instance in to_log if log_instance.error_type == error_type]) / sum(
                    [1 for log_instance in to_log if log_instance.error_type != ErrorType.NO_ERROR]) if sum(
                    [1 for log_instance in to_log if log_instance.error_type != ErrorType.NO_ERROR]) > 0 else 0
            } for error_type in ErrorType if error_type != ErrorType.NO_ERROR
        },
        "config": {
            "model": LLM_ID,
            "top_p": TOP_P,
            "temperature": TEMPERATURE,
            "sampling_temperature": SAMPLING_TEMPERATURE,
            "in_context_examples": NUM_EXAMPLES,
            "repeated_sampling_number": NUM_SAMPLES,
            "samples_cache_enabled": SAMPLES_CACHE_ENABLED,
            "samples_cache_location": SAMPLES_CACHE_LOCATION,
            "seed": SEED,
            "max_llm_call_retries": MAX_LLM_CALL_RETRIES,
            "max_self_verification_attempts": MAX_SELF_VERIFICATION_ATTEMPTS,
            "self_debugging_type": SELF_VERIFICATION_TYPE,
            "max_tokens": MAX_TOKENS,
            "modelling_language": MODELLING_LANGUAGE,
            "system_prompt_level": SYS_PROMPT_LVL,
            "system_prompt": SYSTEM_PROMPT,
        },
        "instance_logs": [
            {
                "idx": idx,
                "total_prompt_tokens": log_instance.total_prompt_tokens,
                "total_completion_tokens": log_instance.total_completion_tokens,
                "file_path": str(log_instance.instance.file_path),
                "category": log_instance.instance.category.name,
                "success": log_instance.error_type == ErrorType.NO_ERROR,
                "error_type": log_instance.error_type.name,
                "final_answer": log_instance.answer,
                "initial_messages": log_instance.initial_messages,
                "samples": log_instance.samples,
                "self_debug_history": [step.to_dict() for step in log_instance.self_debug_history]
            } for idx, log_instance in enumerate(to_log)
        ]
    }

    with open(file_to_log, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


def exec_code_minizinc(code: str, timeout_sec: int = 10):
    """
    Executes a MiniZinc model string using the minizinc-python library.

    :param code: The MiniZinc model code as a string.
    :param timeout_sec: The maximum time to wait for the solver in seconds.
    :return: A tuple of (success, output, timeout_occured)
    """

    try:
        # 1. Create a MiniZinc model instance
        model = minizinc.Model()
        model.add_string(code)

        # 2. Find a default solver configured with MiniZinc
        # You can be more specific, e.g., solver = minizinc.Solver.lookup("gecode")
        # If the default solver isn't found or suitable, this will raise an error.
        gecode = minizinc.Solver.lookup("gecode")
        if gecode is None:
            raise RuntimeError("No suitable solver found. Please install a MiniZinc solver.")

        # 3. Create an Instance to solve
        instance = minizinc.Instance(gecode, model)

        # 4. Solve the instance with the specified timeout
        # The solve() method handles the timeout internally.
        result = instance.solve(timeout=timedelta(seconds=timeout_sec))

        # 5. Process the result
        if result.status in {minizinc.Status.SATISFIED, minizinc.Status.OPTIMAL_SOLUTION}:
            successfully_executed = True
            output = str(result.solution) if result.solution is not None else ""
            timeout_occurred = False
        elif result.status == minizinc.Status.UNKNOWN:
            successfully_executed = False
            output = f"Timeout Error: Solver stopped after {timeout_sec} seconds (Status: UNKNOWN)."
            timeout_occurred = True
        else:
            # Handle other non-success statuses (UNSAT, ERROR, etc.)
            successfully_executed = False
            output = f"Solving failed. Status: {result.status}"
            timeout_occurred = False

    except minizinc.MiniZincError as e:
        # Catch MiniZinc specific errors (e.g., syntax errors, solver not found)
        successfully_executed = False
        output = f"MiniZinc Error: {e}"
        timeout_occurred = False
    except Exception as e:
        # Catch other unexpected errors
        successfully_executed = False
        output = f"Unexpected Error during MiniZinc execution: {e}"
        timeout_occurred = False

    return successfully_executed, output, timeout_occurred


def exec_code(code: str, timeout=10, modelling_language=MODELLING_LANGUAGE):
    """
    Execute the given code and return the output

    :param code: The code to execute as a string
    :param timeout: The maximum time to wait for the code to execute in seconds
    :param modelling_language: The language to use for execution (cpmpy, minizinc, or-tools)
    :return: A tuple of (success, output, timeout_occured)
    """

    # create a temp directory to store the temporary file
    temp_dir_name = "_temp_dir_for_exec_code"
    temp_dir = os.path.join(os.getcwd(), temp_dir_name)
    os.makedirs(temp_dir, exist_ok=True)

    # write the code to a temporary file
    suffix = '.__hidden_py__' if modelling_language == "cpmpy" or modelling_language == "or-tools" else '.mzn'
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix, dir=temp_dir,
                                     encoding='utf-8') as temp_file:
        temp_instance_path = temp_file.name
        temp_file.write(code)

    try:
        # execute the code
        if modelling_language == "cpmpy" or modelling_language == "or-tools":
            command = [sys.executable, temp_instance_path]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, encoding='utf-8')

            successfully_executed = (result.returncode == 0)
            output = result.stdout if successfully_executed else result.stderr
            timeout_occurred = False
        elif modelling_language == "minizinc":
            successfully_executed, output, timeout_occurred = exec_code_minizinc(code, timeout)
        else:
            raise ValueError(f"MODELLING_LANGUAGE not supported: {modelling_language}")

    except subprocess.TimeoutExpired as e:
        successfully_executed = False
        output = f"Timeout Error: Execution time exceeded {timeout} seconds"
        timeout_occurred = True
    except Exception as e:
        successfully_executed = False
        output = f"Error: {e}"
        timeout_occurred = False

    os.remove(temp_instance_path)

    return successfully_executed, output, timeout_occurred


def evaluate_single_turn(answer, file_path, max_tokens_reached):
    code = unwrap_python_code(answer)
    successfully_executed, output, timeout_occurred = exec_code(code)

    if max_tokens_reached:
        error_type = ErrorType.MAX_TOKENS_REACHED
    elif timeout_occurred:
        error_type = ErrorType.TIMEOUT_RUNNING_GENERATED_CODE
    elif not successfully_executed:
        error_type = ErrorType.RUNNING_GENERATED_CODE
    elif is_unsat(output):
        error_type = ErrorType.NO_SOLUTION_FOUND
    elif extract_json_from_code_output(output) is None:
        error_type = ErrorType.DECODING_JSON_FROM_GENERATED_CODE
    elif not isinstance(extract_json_from_code_output(output), dict):
        error_type = ErrorType.SOLUTION_AS_JSON_IS_NOT_DICT
    else:
        # Load the original script as a string
        with open(file_path, 'r', encoding='utf-8') as file:
            script_content = file.read()

        # Add the predicted solutions as constraints to the original script
        modified_script = get_modified_script(script_content, extract_json_from_code_output(output))

        # Run the modified script
        successfully_executed_gt, modified_code_output, timeout_occurred_gt = exec_code(modified_script,
                                                                                        modelling_language="cpmpy")

        if timeout_occurred_gt:
            error_type = ErrorType.TIMEOUT_RUNNING_MODIFIED_GROUND_TRUTH_CODE
        elif not successfully_executed_gt:
            error_type = ErrorType.RUNNING_MODIFIED_GROUND_TRUTH_CODE
        elif 'ERROR' in modified_code_output:
            error_type = ErrorType.SOLUTION_FROM_GENERATED_CODE_DOES_NOT_SATISFY_CONSTRAINTS
        else:
            error_type = ErrorType.NO_ERROR

    return error_type, output


def unwrap_python_code(code):
    # remove wrappers
    if '```python' in code:
        return code.split('```python')[-1].split('```')[0]

    if '```minizinc' in code:
        return code.split('```minizinc')[-1].split('```')[0]

    # no tags found
    _ret = f'No code generated (possibly, context limit reached, or code was not wrapped with tags). Here are the first 1000 characters:\n'
    _ret += code[:min(1000, len(code))]
    return _ret


def extract_json_from_code_output(output: str):
    try:
        start_index = output.find('{')
        end_index = output.rfind('}') + 1
        # Extract the JSON part
        json_part = output[start_index:end_index]
        return json.loads(json_part)
    except json.JSONDecodeError:
        return None


def is_unsat(output: str):
    if 'no solution found' in output.lower() or 'unsatisfiable' in output.lower():
        return True

    json_output = extract_json_from_code_output(output)

    if json_output is None:
        return False

    # if all values are none then it is a no solution found. Tricky: there can be arrays and nested arrays
    def check_none(obj):
        if isinstance(obj, dict):
            return all(check_none(value) for value in obj.values())
        elif isinstance(obj, list):
            return all(check_none(value) for value in obj)
        else:
            return obj is None

    return check_none(json_output)


def test():
    # test check cpmpy no solution found
    candidate_is = '{"a": null, "b": [null, null], "c": [[null], [null], [null]], "d": null}'
    candidate_is_not = '{"a": 1, "b": [1, 2], "c": [[1], [2], [null]], "d": null}'
    candidate_is_not_2 = '{"a": 1, "b": [1, 2]}'
    candidate_is_2 = 'No Solution Found'

    assert is_unsat(candidate_is)
    assert not is_unsat(candidate_is_not)
    assert not is_unsat(candidate_is_not_2)
    assert is_unsat(candidate_is_2)

    # test extract json from code output
    output = "Hello World! {\"a\": 1, \"b\": 2, \"c\": 3, \"d\": 4}"
    assert extract_json_from_code_output(output) == {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    output = "Hello World! {\"a\": 1, \"b\": 2, \"c\": 3, \"d\": 4"
    assert extract_json_from_code_output(output) is None

    code = """
print("Hello World!")
        """
    success, output, timeout = exec_code(code)
    assert success
    assert output.startswith("Hello World!")
    assert not timeout

    code = """
from cpmpy import *
import json

# Decision Variables
a, b, c, d = intvar(0, 9, shape=4)  # a, b, c, d are the four digits of the PIN

# Constraints
model = Model()

model += AllDifferent([a, b, c, d])  # no two digits are the same
model += 10 * c + d == 3 * (10 * a + b)  # cd is 3 times ab
model += 10 * d + a == 2 * (10 * b + c)  # da is 2 times bc

# Solve
model.solve()

# Print the solution
solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
print(json.dumps(solution))
    """
    success, output, timeout = exec_code(code)
    assert success
    assert output.startswith('{') and 'a' in output and 'b' in output and 'c' in output and 'd' in output
    assert not timeout

    code = """
import time
time.sleep(15)
print("Hello World!")
    """
    success, output, timeout = exec_code(code, timeout=2)
    assert not success
    assert "Timeout Error" in output
    assert timeout

    code = """
print("Hello World!"
    """
    success, output, timeout = exec_code(code)
    assert not success
    assert not timeout

    print("All tests passed.")


def mnz_test():
    code = """
% Include necessary libraries
include "globals.mzn";

% Input data
int: n_slots = 9;
int: n_templates = 2;
int: n_var = 7;
array[1..n_var] of int: demand = [250, 255, 260, 500, 500, 800, 1100];

% Decision variables
% Layout of each template (each slot is a variation from 1 to n_var)
array[1..n_templates, 1..n_slots] of var 1..n_var: layout;
% Number of times each template is printed (must be at least 1)
array[1..n_templates] of var 1..2000: templates_used;

% Constraints
% Ensure each variation's total meets or exceeds demand
constraint forall(v in 1..n_var)(
  sum( [ 
    (sum( [ bool2int( layout[i,s] == v ) | s in 1..n_slots ]) ) * templates_used[i] 
    | i in 1..n_templates 
  ] ) >= demand[v]
);

% Objective: minimize total printed sheets
solve minimize sum(templates_used);

% Output in JSON format with keys "production" and "layout"
output [
  "{\\n",
  "  \\"production\\": " ++ show(sum(templates_used)) ++ ",\\n",
  "  \\"layout\\": " ++ show(layout) ++ "\\n",
  "}"
];    
"""

    success, output, timeout = exec_code(code, timeout=2, modelling_language="minizinc")
    print(output)
    assert success
    assert not timeout

    print("Minizinc test 1 passed.")

    code = """
include "globals.mzn";

% Decision variables: my age (m) and husband's age (h)
var 1..1000: m;
var 1..1000: h;

% Two different permutations of the four operations
array[1..4] of var 1..4: perm1;
array[1..4] of var 1..4: perm2;

% Intermediate results of applying the operations
array[0..4] of var int: t1;  % starting from m
array[0..4] of var int: t2;  % starting from h

% Each perm is a permutation of {1:+2, 2:/8, 3:-3, 4:*7}
constraint all_different(perm1);
constraint all_different(perm2);
% Ensure the two orders are not identical
constraint not forall(i in 1..4)(perm1[i] = perm2[i]);

% Initial values
constraint t1[0] = m;
constraint t2[0] = h;

% Apply operations in the order perm1 to m to get h
constraint
  forall(k in 1..4) (
    if perm1[k] = 1 then
      t1[k] = t1[k-1] + 2
    elseif perm1[k] = 2 then
      % exact division by 8
      t1[k] * 8 = t1[k-1]
    elseif perm1[k] = 3 then
      t1[k] = t1[k-1] - 3
    else
      t1[k] = t1[k-1] * 7
    endif
  );
constraint t1[4] = h;

% Apply operations in the order perm2 to h to get m
constraint
  forall(k in 1..4) (
    if perm2[k] = 1 then
      t2[k] = t2[k-1] + 2
    elseif perm2[k] = 2 then
      t2[k] * 8 = t2[k-1]
    elseif perm2[k] = 3 then
      t2[k] = t2[k-1] - 3
    else
      t2[k] = t2[k-1] * 7
    endif
  );
constraint t2[4] = m;

% Ages must be positive
constraint m > 0 /\ h > 0;

solve satisfy;

output [
  "{",
    "\\"m\\": ", show(m), ",",
    "\\"h\\": ", show(h),
  "}"
];
    """
    success, output, timeout = exec_code(code, timeout=2, modelling_language="minizinc")
    assert success
    assert not timeout


if __name__ == '__main__':
    # test()

    mnz_test()
