import json

from tqdm import tqdm

from llm_config import TEMPERATURE, MAX_TOKENS, TOP_P, NUM_EXAMPLES, NUM_SAMPLES, SAMPLING_TEMPERATURE, SEED, \
    LLM_ID, LLM_CLIENT, EXAMPLE_SELECTOR, LOG_FILE, DATASET, SYS_PROMPT_LVL, SYSTEM_PROMPT
import os
from utils import unwrap_python_code, extract_json_from_code_output, is_unsat, exec_code, evaluate_single_turn
from datetime import datetime, UTC
import concurrent.futures
from ollama import chat
from ollama import ChatResponse


def get_llm_best_response(responses_content):
    if NUM_SAMPLES == 1:
        return responses_content[0], 0

    ######################
    # Solution Consensus #
    ######################
    print("####### Solution Consensus check to select the best response.")

    solutions = []
    for idx, candidate_code in enumerate(responses_content):

        if idx >= NUM_SAMPLES:
            break

        code = unwrap_python_code(candidate_code)
        successfully_executed, output, timeout_occurred = exec_code(code)

        if not successfully_executed or is_unsat(output):
            continue

        output_json = extract_json_from_code_output(output)

        if output_json is None or not isinstance(output_json, dict):
            continue

        solutions.append({"idx": idx, "solution_dict": output_json})

    # if no solutions found, return the first one
    if len(solutions) == 0:
        return responses_content[0], 0

    # find the solution that appears the most and return the corresponding response
    solutions_count = {}
    for solution in solutions:
        solution_dict_str = json.dumps(solution["solution_dict"], sort_keys=True)
        if solution_dict_str in solutions_count:
            print("Found an existing solution!")
            solutions_count[solution_dict_str] += 1
        else:
            solutions_count[solution_dict_str] = 1

    # get the first idx that has as solution the most common solution
    most_common_solution_str = max(solutions_count, key=solutions_count.get)
    most_common_solution_idx = -1
    for solution in solutions:
        solution_dict_str = json.dumps(solution["solution_dict"], sort_keys=True)
        if solution_dict_str == most_common_solution_str:
            most_common_solution_idx = solution["idx"]
            break

    best_response_content = responses_content[most_common_solution_idx]

    print("Best response index (0-based):", most_common_solution_idx)
    print("Best response:", best_response_content)

    return best_response_content, most_common_solution_idx


def call_llm(messages, temp=TEMPERATURE):
    if 'claude' in LLM_ID:
        if messages[0]['role'] == 'system':
            response = LLM_CLIENT.messages.create(model=LLM_ID, max_tokens=MAX_TOKENS, messages=messages[1:],
                                                  temperature=temp, top_p=TOP_P, system=messages[0]['content'])
        else:
            response = LLM_CLIENT.messages.create(model=LLM_ID, max_tokens=MAX_TOKENS, messages=messages,
                                                  temperature=temp, top_p=TOP_P)
        max_tokens_reached = (response.stop_reason == 'max_tokens')
        response_content = response.content[0].text
        completion_tokens = response.usage.output_tokens
        prompt_tokens = response.usage.input_tokens
    elif 'o1-' in LLM_ID or 'o4-' in LLM_ID:
        if messages[0]['role'] == 'system':
            new_messages = [{"role": "user", "content": messages[0]['content'] + '\n' + messages[1]['content']}]
            if len(messages) > 2:
                new_messages.extend(messages[2:])
            messages = new_messages

        response = LLM_CLIENT.chat.completions.create(messages=messages, model=LLM_ID, seed=SEED,
                                                      max_completion_tokens=MAX_TOKENS)
        max_tokens_reached = (response.choices[0].finish_reason == 'length')
        response_content = response.choices[0].message.content
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens
    elif LLM_ID.startswith('ollama_'):
        # remove ollama_ prefix from LLM_ID
        model_name = LLM_ID.split('_', 1)[1]
        response: ChatResponse = chat(model=model_name, messages=messages)
        max_tokens_reached = not (response.done_reason == 'stop')
        prompt_tokens = response.prompt_eval_count
        completion_tokens = response.eval_count
        response_content = response.message.content
    elif LLM_ID.startswith('gpt-5-'):
        response = LLM_CLIENT.chat.completions.create(messages=messages, model=LLM_ID, seed=SEED,
                                                      max_completion_tokens=MAX_TOKENS)
        max_tokens_reached = (response.choices[0].finish_reason == 'length')
        response_content = response.choices[0].message.content
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens
    else:
        response = LLM_CLIENT.chat.completions.create(messages=messages, model=LLM_ID, temperature=temp, seed=SEED,
                                                      max_tokens=MAX_TOKENS, top_p=TOP_P)
        max_tokens_reached = (response.choices[0].finish_reason == 'length')
        response_content = response.choices[0].message.content
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

    # Log the interaction
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "input_messages": messages,
        "response_content": response_content,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens
    }

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

    return response_content, prompt_tokens, completion_tokens, max_tokens_reached


def get_llm_responses(instance, max_workers=4):
    if NUM_EXAMPLES == 0:
        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": instance.get_prompt()}]
    else:
        examples = EXAMPLE_SELECTOR.select_examples({"prompt": instance.get_prompt()})

        # find the same instance and remove it, check by id. If not found, then just remove the last one
        idx_to_remove = -1
        for idx, example in enumerate(examples):
            if str(instance.id) == example['instance_id']:
                idx_to_remove = idx
                break
        examples.pop(idx_to_remove)
        examples = examples[::-1]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for example in examples:
            messages.append({"role": "user", "content": example['prompt']})
            messages.append({"role": "assistant", "content": example['wrapped_code']})
        messages.append({"role": "user", "content": instance.get_prompt()})

    responses = []
    max_token_reached_list = []
    total_prompt_tokens = 0
    total_completion_tokens = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(call_llm, messages, TEMPERATURE if i == 0 else SAMPLING_TEMPERATURE)
                   for i in range(NUM_SAMPLES)]

        for i, future in enumerate(futures):
            try:
                response_content, prompt_tokens, completion_tokens, max_tokens_reached = future.result()
                responses.append(response_content)
                max_token_reached_list.append(max_tokens_reached)
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
            except Exception as e:
                print(f"LLM call {i} failed: {e}")
                responses.append("Error while calling LLM")
                max_token_reached_list.append(False)

    return messages, responses, max_token_reached_list, total_prompt_tokens, total_completion_tokens


def generate_and_store_samples():
    samples_file = f"results/cached_samples/{LLM_ID}/llm_samples_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"

    os.makedirs(os.path.dirname(samples_file), exist_ok=True)

    with open(samples_file, "a", encoding="utf-8") as f:
        config = {
            "model": LLM_ID,
            "top_p": TOP_P,
            "temperature": TEMPERATURE,
            "sampling_temperature": SAMPLING_TEMPERATURE,
            "in_context_examples": NUM_EXAMPLES,
            "repeated_sampling_number": NUM_SAMPLES,
            "max_tokens": MAX_TOKENS,
            "system_prompt_level": SYS_PROMPT_LVL,
            "system_prompt": SYSTEM_PROMPT
        }
        f.write(json.dumps(config) + "\n")

    total_p_tokens = 0
    total_c_tokens = 0
    for i, instance in tqdm(enumerate(DATASET)):
        messages, responses_content, max_token_reached_list, p_tok, c_tok = get_llm_responses(instance)

        total_p_tokens += p_tok
        total_c_tokens += c_tok

        log_entry = {
            "file_path": str(instance.file_path),
            "responses_content": responses_content,
            "max_tokens_reached": max_token_reached_list,
            "total_prompt_tokens": p_tok,
            "total_completion_tokens": c_tok,
        }

        with open(samples_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"Generated samples: {i + 1}/{len(DATASET)}")

    with open(samples_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"total_prompt_tokens": total_p_tokens,
                            "total_completion_tokens": total_c_tokens,
                            "total_tokens": total_p_tokens + total_c_tokens}) + "\n")

    print(f"Generated samples for all {len(DATASET)} instances.")


# test samples
def test_multiple_samples_for_best_solution():
    samples = [
        '```python\nimport cpmpy as cp\nimport numpy as np\nimport json\n\n# Data\ndemands = [4, 8, 10, 7, 12, 4]\n\n# Model definition\nmodel = cp.Model()\n\n# Decision Variables\nx = cp.intvar(0, 100, shape=len(demands), name="x")\n\n# Constraints\nfor i in range(len(demands)):\n    # Each bus can operate only 8 successive hours a day, \n    # so for each 4-hour interval, we need to consider the previous and next intervals\n    if i == 0:\n        model += x[i] >= demands[i]\n    elif i == len(demands) - 1:\n        model += x[i] + x[i-1] >= demands[i]\n    else:\n        model += x[i] + x[i-1] >= demands[i]\n\n# Objective function (optional)\nmodel.minimize(cp.sum(x))\n\n# Solve and print\nif model.solve():\n    solution = {\'x\': x.value().tolist()}\n    print(json.dumps(solution, indent=4))\nelse:\n    print("No solution found.")\n```',
        '```python\nimport cpmpy as cp\nimport json\n\n# Input data\ndemands = [4, 8, 10, 7, 12, 4]\n\n# Model definition\nmodel = cp.Model()\n\n# Decision Variables\nx = cp.intvar(0, 100, shape=len(demands), name="x")  # number of buses scheduled in each time slot\n\n# Constraints\nfor i in range(len(demands)):\n    model += (x[i] >= demands[i])\n\n# To account for buses transitioning between intervals, \n# we need to ensure that the number of buses available \n# in each 4-hour interval meets the demand for that interval\n# and the next interval (if it exists)\nfor i in range(len(demands) - 1):\n    model += (x[i] + x[i+1] >= demands[i+1])\n\n# Objective function: minimize the total number of buses scheduled\nmodel.minimize(cp.sum(x))\n\n# Solve and print\nif model.solve():\n    solution = {\'x\': x.value().tolist()}\n    print(json.dumps(solution, indent=4))\nelse:\n    print("No solution found.")\n```',
        '```python\nimport cpmpy as cp\nimport json\n\n# Input data\ndemands = [4, 8, 10, 7, 12, 4]\n\n# Model definition\nmodel = cp.Model()\n\n# Decision Variables\nx = cp.intvar(0, 100, shape=len(demands), name="x")  # number of buses scheduled in each time slot\n\n# Constraints\n# Ensure the number of buses available in each 4-hour interval meets the demand for that interval\nfor i in range(len(demands)):\n    model += x[i] >= demands[i]\n\n# Due to overlapping shifts, the schedule must account for buses transitioning between intervals\nfor i in range(len(demands) - 1):\n    model += x[i] + x[i+1] >= demands[i+1]\n\n# Objective function (minimize the total number of buses scheduled)\nmodel.minimize(cp.sum(x))\n\n# Solve and print\nif model.solve():\n    solution = {\'x\': x.value().tolist()}\n    print(json.dumps(solution, indent=4))\nelse:\n    print("No solution found.")\n```']

    best_response = get_llm_best_response(samples)
    assert best_response == samples[1]


if __name__ == "__main__":
    generate_and_store_samples()
    # test_multiple_samples_for_best_solution()
