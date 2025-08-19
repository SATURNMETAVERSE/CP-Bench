from llm_config import SELF_VERIFICATION_TYPE, MAX_SELF_VERIFICATION_ATTEMPTS, MAX_TOKENS, SYSTEM_PROMPT
from utils import unwrap_python_code

SELF_DEBUG_PROMPT = """
You are an expert in combinatorial optimization and you are asked to verify (or debug) a code snippet that models a combinatorial problem.
You will be given a combinatorial problem description with instructions on how to model it, its code formulation according to these instructions, and the code output.
Explain the given code, especially elaborating on the decision variables, constraints, and the objective function (if applicable).

Then, evaluate the code's correctness in three aspects:

a) **Runtime**: Does the code run successfully without syntax errors, and does it correctly utilize the required libraries?

b) **Model**: 
    * Are the decision variables, constraints, and objective function (if applicable) correctly defined?
    * Does the generated solution satisfy the constraints and objective of the given problem description?

c) **Solution printing**: Does the code print the solution in the required JSON format, with the correct keys and values according to the given instructions?

If the code is correct, end your response with [[OK]].
If the code is incorrect, provide a corrected version of the code between ```python and ```, ensuring the fixed code is self-contained and runnable. End your response with [[FIXED]].

Note: Use [[OK]] and [[FIXED]] only once at the end of your response, and only one of them.
"""


def create_chat_based_self_debug_prompt(out, error_desc):
    return f"""
The output of the code that you generated above is:
```
{out}
```

The error description, if any, is:
```
{error_desc}
```

Explain the code, especially elaborating on the decision variables, constraints, and the objective function (if applicable).

Then, evaluate the code's correctness in three aspects:

a) **Runtime**: Does the code run successfully without syntax errors, and does it correctly utilize the required libraries?

b) **Model**: 
    * Are the decision variables, constraints, and objective function (if applicable) correctly defined?
    * Does the generated solution satisfy the constraints and objective of the given problem description?

c) **Solution printing**: Does the code print the solution in the required JSON format, with the correct keys and values according to the given instructions?

If the code is correct, end your response with [[OK]].
If the code is incorrect, provide a corrected version of the code between ```python and ```, ensuring the fixed code is self-contained and runnable. End your response with [[FIXED]].

Note: Use [[OK]] and [[FIXED]] only once at the end of your response, and only one of them.
"""


def create_chat_based_self_debug_prompt_cont(out, error_desc, attempts_remaining: int):
    return f"""
Being here means that you did not approve the code in the previous step or there was some kind of detectable error.
As a result, you generated a new version of the code.

Now apply the same evaluation process as before, but this time on the newly generated code and its output which is:
```
{out}
```

The error description, if any, is:
```
{error_desc}
```

Again, if the code is correct, end your response with [[OK]].
If the code is incorrect (according the three defined aspects above), provide a corrected version of the code between ```python and ```, ensuring the fixed code is self-contained and runnable. End your response with [[FIXED]].

Note: Use [[OK]] and [[FIXED]] only once at the end of your response, and only one of them.

Note 2: There are only {attempts_remaining} attempt(s) remaining to generate a correct response, so make sure to be thorough in your evaluation.
"""


def get_self_debug_messages(debug_idx, messages, answer, output, instance, error_desc: str):
    print("Self-Debug. Attempt " + str(debug_idx + 1) + " out of " + str(MAX_SELF_VERIFICATION_ATTEMPTS))

    if SELF_VERIFICATION_TYPE == 'chat':
        if debug_idx == 0:
            new_content = create_chat_based_self_debug_prompt(output, error_desc)
        else:
            new_content = create_chat_based_self_debug_prompt_cont(output, error_desc, MAX_SELF_VERIFICATION_ATTEMPTS - debug_idx - 1)
        self_debug_messages = (messages
                               + [{"role": "assistant", "content": answer}]
                               + [{"role": "user", "content": new_content}])
    elif SELF_VERIFICATION_TYPE == 'single':
        self_debug_prompt = (f"{SELF_DEBUG_PROMPT}\n\n"
                             f"Here are the instructions of the user (between ```instr and ```):"
                             f"\n\n```instr\n{SYSTEM_PROMPT}\n```\n\n"
                             f"Here is the given problem description (between ```desc and ```):"
                             f"\n\n```desc\n{instance.get_prompt()}\n```\n\n"
                             f"Here is the generated code (between ```python and ```):"
                             f"\n\n```python\n{unwrap_python_code(answer)}\n```\n\n"
                             f"Here is the output of the generated code (between ```out and ```):"
                             f"\n\n```out\n{output}\n```\n\n"
                             f"Here is the error description (between ```error and ```), if any:"
                             f"\n\n```error\n{error_desc}\n```\n\nYou have a maximum of {MAX_TOKENS} tokens to answer, DO NOT exceed this limit.")
        self_debug_messages = [{"role": "user", "content": self_debug_prompt}]
    else:
        raise ValueError(f"Not implemented self-verification type: {SELF_VERIFICATION_TYPE}")

    return self_debug_messages