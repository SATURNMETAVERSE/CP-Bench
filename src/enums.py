from enum import Enum


class InstanceCategory(Enum):
    APLAI = 1
    CPMPY_EXAMPLES = 2
    CSPLIB = 3
    HAKANK_EXAMPLES = 4
    COMPLEX_OR = 5
    NSP_RULES = 6

class ErrorType(Enum):
    TIMEOUT_RUNNING_GENERATED_CODE = 1
    RUNNING_GENERATED_CODE = 2
    NO_SOLUTION_FOUND = 3
    DECODING_JSON_FROM_GENERATED_CODE = 4
    SOLUTION_AS_JSON_IS_NOT_DICT = 5
    RUNNING_MODIFIED_GROUND_TRUTH_CODE = 6
    TIMEOUT_RUNNING_MODIFIED_GROUND_TRUTH_CODE = 7
    SOLUTION_FROM_GENERATED_CODE_DOES_NOT_SATISFY_CONSTRAINTS = 8
    NO_ERROR = 9
    LLM_CALL_ERROR = 10
    SELF_VERIFICATION_ERROR = 11
    MAX_TOKENS_REACHED = 12

    def description(self):
        descriptions = {
            ErrorType.TIMEOUT_RUNNING_GENERATED_CODE: "Timeout running generated code",
            ErrorType.RUNNING_GENERATED_CODE: "Error running generated code",
            ErrorType.NO_SOLUTION_FOUND: "No solution found",
            ErrorType.DECODING_JSON_FROM_GENERATED_CODE: "Error decoding JSON from generated code",
            ErrorType.SOLUTION_AS_JSON_IS_NOT_DICT: "Solution as JSON is not a dictionary (e.g. a list)",
            ErrorType.RUNNING_MODIFIED_GROUND_TRUTH_CODE: "The printed JSON contains invalid keys or value types",
            ErrorType.TIMEOUT_RUNNING_MODIFIED_GROUND_TRUTH_CODE: "Timeout running modified ground truth code",
            ErrorType.SOLUTION_FROM_GENERATED_CODE_DOES_NOT_SATISFY_CONSTRAINTS: "Wrong solution",
            ErrorType.NO_ERROR: "No detectable error occurred",
            ErrorType.LLM_CALL_ERROR: "Error while calling LLM API",
            ErrorType.SELF_VERIFICATION_ERROR: "Error during self-verification, LLM did not return OK or FIXED",
            ErrorType.MAX_TOKENS_REACHED: "LLM output reached the maximum token limit",
        }
        return descriptions.get(self, "Unknown error")

    def is_detectable(self):
        # Errors that can be detected automatically for a problem instance, without human intervention
        # e.g. NO_SOLUTION_FOUND is not detectable, as it requires human judgment to determine if the output is correct (some problems may indeed have no solution)
        return self in [
            ErrorType.TIMEOUT_RUNNING_GENERATED_CODE,
            ErrorType.RUNNING_GENERATED_CODE,
            ErrorType.DECODING_JSON_FROM_GENERATED_CODE,
            ErrorType.SOLUTION_AS_JSON_IS_NOT_DICT,
            ErrorType.RUNNING_MODIFIED_GROUND_TRUTH_CODE,  # this can be detected by mapping the requested json keys to the output
        ]
