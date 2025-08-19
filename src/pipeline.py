from dataset_classes import LogInstance, SelfDebugStep
from enums import ErrorType
from llm_config import LIMIT, DATASET, MAX_LLM_CALL_RETRIES, MAX_SELF_VERIFICATION_ATTEMPTS, SAMPLES_CACHE_ENABLED, \
    SAMPLES_CACHE_LOCATION, NUM_SAMPLES
from llm_utils import get_llm_best_response, call_llm, get_llm_responses
from self_debug_prompt import get_self_debug_messages
from utils import evaluate_single_turn, log_results_json
import json

def process_single_instance(instance, curr_num_retries=0):
    log_instance = LogInstance(instance)
    print(f'Prompt for the instance: {instance.get_prompt()}')

    total_p_tokens, total_c_tokens = 0, 0
    max_tokens_reached_list = []
    for k in range(NUM_SAMPLES):
        max_tokens_reached_list.append(False)

    if SAMPLES_CACHE_ENABLED:
        loc_as_str = SAMPLES_CACHE_LOCATION
        # open the jsonl file and find the instance
        with open(loc_as_str, "r", encoding="utf-8") as f:
            # read the first line and get the system prompt
            sys_prompt = json.loads(f.readline())["system_prompt"]

            for line in f:
                sample = json.loads(line)
                sample_path = sample["file_path"].replace("\\", "/")  # Normalize stored path
                instance_path = instance.file_path.as_posix().replace("\\", "/")  # Normalize instance path

                if instance_path == sample_path:
                    messages = [{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': instance.get_prompt()}]
                    answers = sample["responses_content"][:NUM_SAMPLES]
                    max_tokens_reached_list = sample["max_tokens_reached"][:NUM_SAMPLES]
                    break
    else:
        try:
            messages, answers, max_tokens_reached_list, total_p_tokens, total_c_tokens = get_llm_responses(instance)
        except Exception as e:
            print("Error while calling LLM:" + str(e))
            if curr_num_retries + 1 >= MAX_LLM_CALL_RETRIES:
                print(f"Skipping instance {instance.file_path} after {MAX_LLM_CALL_RETRIES} retries.")
                log_instance.error_type = ErrorType.LLM_CALL_ERROR
                return log_instance
            return process_single_instance(instance, curr_num_retries + 1)  # Try again with the same problem

    best_answer, best_answer_idx = get_llm_best_response(answers)
    print(f"Best Answer after Repeated Sampling:\n{best_answer}\n")

    log_instance.samples = answers[:NUM_SAMPLES]
    log_instance.answer = best_answer
    log_instance.initial_messages = messages
    log_instance.total_prompt_tokens = total_p_tokens
    log_instance.total_completion_tokens = total_c_tokens
    log_instance.error_type, output = evaluate_single_turn(log_instance.answer, instance.file_path, max_tokens_reached_list[best_answer_idx])

    self_deb_msg = messages
    for debug_loop_idx in range(MAX_SELF_VERIFICATION_ATTEMPTS):
        if log_instance.error_type.is_detectable():
            error_desc = log_instance.error_type.description() + ": " + output
        else:
            error_desc = "No syntax error detected."

        self_deb_msg = get_self_debug_messages(debug_loop_idx, self_deb_msg, log_instance.answer, output, instance, error_desc)

        try:
            response_content, prompt_tokens, completion_tokens, max_tokens_reached = call_llm(self_deb_msg)
        except Exception as e:
            print("Error while calling LLM for self-verification (fail, exiting the loop):" + str(e))
            log_instance.error_type = ErrorType.LLM_CALL_ERROR
            break

        self_deb_step = SelfDebugStep()
        self_deb_step.messages = self_deb_msg + [{"role": "assistant", "content": response_content}]
        self_deb_step.error_type = log_instance.error_type
        self_deb_step.output = output
        self_deb_step.prompt_tokens = prompt_tokens
        self_deb_step.completion_tokens = completion_tokens
        log_instance.total_completion_tokens += completion_tokens
        log_instance.total_prompt_tokens += prompt_tokens
        log_instance.self_debug_history.append(self_deb_step)

        # check if the response is OK or FIXED
        if "[[OK]]" in response_content and not log_instance.error_type.is_detectable():
            break

        if "[[FIXED]]" not in response_content and not log_instance.error_type.is_detectable() and not max_tokens_reached:
            print("Error: The response does not contain [[OK]] or [[FIXED]]")
            log_instance.error_type = ErrorType.SELF_VERIFICATION_ERROR
            break

        log_instance.answer = response_content
        log_instance.error_type, output = evaluate_single_turn(log_instance.answer, instance.file_path, max_tokens_reached)

    return log_instance


def pipeline():
    to_log = []

    for i, instance in enumerate(DATASET):
        if LIMIT is not None and i >= LIMIT:
            break

        print(f"#############\nProcessing instance: {instance.file_path}. {i + 1}/{len(DATASET)}\n#############\n")
        log_instance = process_single_instance(instance)
        to_log.append(log_instance)
        print(f"Error type: {log_instance.error_type}")
        print('*' * 50)

    log_results_json(to_log)

    print("Done. Bye!")


def main():
    pipeline()


if __name__ == "__main__":
    main()
