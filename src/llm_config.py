from dataset_utils import load_dataset
from langchain_core.example_selectors import SemanticSimilarityExampleSelector, MaxMarginalRelevanceExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from anthropic import Anthropic
from openai import OpenAI
from together import Together
import os
from datetime import datetime, UTC
import sys

from prompts.cpmpy_prompt import CPMPY_SYS_PROMPT_LVL_1, CPMPY_SYS_PROMPT_LVL_2, CPMPY_SYS_PROMPT_LVL_3
from prompts.minizinc_prompt import MNZ_SYS_PROMPT_LVL_1, MNZ_SYS_PROMPT_LVL_2, MNZ_SYS_PROMPT_LVL_3
from prompts.or_tools_prompt import ORT_SYS_PROMPT_LVL_1, ORT_SYS_PROMPT_LVL_2, ORT_SYS_PROMPT_LVL_3

# Set your API key(s) here
OPENAI_API_KEY = "TODO"
TOGETHER_API_KEY = "TODO"
DEEPSEEK_API_KEY = "TODO"
ANTHROPIC_API_KEY = "TODO"

#############################
# Choose the LLM #
#############################
# LLM_ID = "ollama_deepseek-r1:1.5b"
# LLM_ID = "ollama_gemma3:4b"
# LLM_ID = 'ollama_qwen3:8b'

# LLM_ID = "gpt-5-mini-2025-08-07"
# LLM_ID = "gpt-5-2025-08-07"

# LLM_ID = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
# LLM_ID = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
# LLM_ID = "gpt-4.1-2025-04-14"
# LLM_ID = "gpt-4.1-mini-2025-04-14"
# LLM_ID = "deepseek-chat"  # V3
# LLM_ID = 'deepseek-ai/DeepSeek-V3'

# FOR reasoning change MAX TOKENS to much more!
# LLM_ID = "deepseek-reasoner"  # r1
# LLM_ID = "Qwen/QwQ-32B"
# LLM_ID = "o4-mini-2025-04-16"
# LLM_ID = "gpt-4.1-nano-2025-04-14"
# LLM_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"
# LLM_ID = "Qwen/Qwen3-235B-A22B-fp8-tput"
# LLM_ID = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
# LLM_ID = 'meta-llama/Llama-3.3-70B-Instruct-Turbo'
# LLM_ID = 'claude-3-7-sonnet-20250219'
# LLM_ID = 'claude-sonnet-4-20250514'
LLM_ID = 'vllm-local-model'  # Qwen/Qwen3-1.7B served by vLLM as 'vllm-local-model'
ENABLE_THINKING = False  # Qwen3 hybrid model: non-thinking mode for the Baseline

if LLM_ID.startswith('gpt') or LLM_ID.startswith('o1-') or LLM_ID.startswith('o4-'):
    LLM_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
elif LLM_ID == 'deepseek-coder' or LLM_ID == 'deepseek-chat' or LLM_ID == 'deepseek-reasoner':
    LLM_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
elif 'claude' in LLM_ID:
    LLM_CLIENT = Anthropic(api_key=ANTHROPIC_API_KEY)
elif 'vllm-local' in LLM_ID:
    LLM_CLIENT = OpenAI(api_key='EMPTY', base_url='http://localhost:8001/v1')
elif LLM_ID.startswith('ollama_'):
    LLM_CLIENT = None
else:
    LLM_CLIENT = Together(api_key=TOGETHER_API_KEY)


###############################
# Choose the modelling language #
###############################
MODELLING_LANGUAGE = "cpmpy"
# MODELLING_LANGUAGE = "minizinc"
# MODELLING_LANGUAGE = "or-tools"

####################################################
# Choose what system prompt to use for the LLMs #
####################################################
# SYS_PROMPT_LVL = 0  # No system prompt
# SYS_PROMPT_LVL = 1  # Basic system prompt
# SYS_PROMPT_LVL = 2  # Basic system prompt + guidelines
SYS_PROMPT_LVL = 3  # Basic system prompt + guidelines + documentation


def get_sys_prompt(level, lang):
    sys_prompts = {
        "cpmpy": {
            1: CPMPY_SYS_PROMPT_LVL_1,
            2: CPMPY_SYS_PROMPT_LVL_2,
            3: CPMPY_SYS_PROMPT_LVL_3,
        },
        "minizinc": {
            1: MNZ_SYS_PROMPT_LVL_1,
            2: MNZ_SYS_PROMPT_LVL_2,
            3: MNZ_SYS_PROMPT_LVL_3,
        },
        "or-tools": {
            1: ORT_SYS_PROMPT_LVL_1,
            2: ORT_SYS_PROMPT_LVL_2,
            3: ORT_SYS_PROMPT_LVL_3,
        },
    }
    try:
        return sys_prompts[lang][level]
    except KeyError:
        raise ValueError(
            f"Unknown language/level: lang={lang}, level={level}. "
            f"Supported: languages={list(sys_prompts)}, levels={list(next(iter(sys_prompts.values())))}"
        )

SYSTEM_PROMPT = get_sys_prompt(SYS_PROMPT_LVL, MODELLING_LANGUAGE)

###########################################################################
# Choose the number of in-context examples, i.e. zero-shot or few-shot #
###########################################################################
NUM_EXAMPLES = 0  # Default, no in-context examples, only the system prompt
# NUM_EXAMPLES = 4
# NUM_EXAMPLES = 8
# NUM_EXAMPLES = 12

########################
# Multiple Sampling #
########################
SAMPLES_CACHE_ENABLED = False  # If True, the samples will be loaded from a cache file instead of generating them again
SAMPLES_CACHE_LOCATION = 'results/cached_samples/deepseek-chat/llm_samples_2025-05-02_11-27-23.jsonl'

DEFAULT_NUM_SAMPLES = 1  # Default number of samples to generate for each instance (use 1 for no sampling)
NUM_SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_NUM_SAMPLES
SAMPLING_TEMPERATURE = 0.8  # Sampling temperature for the multiple samples, only applied if (and for) NUM_SAMPLES > 1
assert NUM_SAMPLES >= 1
assert SAMPLING_TEMPERATURE >= 0.0

#####################
# Self-Debugging #
#####################
SELF_VERIFICATION_TYPE = 'single'  # 'chat' or 'single'
MAX_SELF_VERIFICATION_ATTEMPTS = 0  # Baseline (Q1): 0. Paper Q3 Self-Verification: 10.  # Maximum number of attempts to generate a correct response with self-verification (use 0 for no retries)
assert MAX_SELF_VERIFICATION_ATTEMPTS >= 0

###################
# Other constants #
###################
TEMPERATURE = 0.0
TOP_P = 0.95
MAX_TOKENS = 12_000  # Maximum number of tokens to generate (12k, as reported in the paper)
LIMIT = None  # How many instances to run in the pipeline (if we want to run them all, set to None)
SEED = 42  # Random seed for the LLM sampling
MAX_LLM_CALL_RETRIES = 3  # Maximum number of retries for calling the LLM API in case of an error

DATASET = load_dataset('data_nsp')

# RAICL
EXAMPLE_SELECTOR = None
if NUM_EXAMPLES > 0:
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    # Retrieval pool = the paper's original benchmark ('data'), not the NSP problems: retrieving from
    # data_nsp would show the model the ground truth of the other rules. Ids are prefixed so they never
    # match an NSP instance id; the leave-one-out step then drops the extra (k+1)-th example as usual.
    examples = [{"instance_id": f"pool_{p.id}", "prompt": p.get_prompt(), "wrapped_code": p.get_content_after_description(wrapped=True)} for p in load_dataset('data')]
    # we ask for 1 more, so that we can omit the first one (it's the prompt itself)
    # EXAMPLE_SELECTOR = MaxMarginalRelevanceExampleSelector.from_examples(examples, OpenAIEmbeddings(model='text-embedding-3-large'), Chroma, k=NUM_EXAMPLES + 1, fetch_k=len(DATASET))
    EXAMPLE_SELECTOR = SemanticSimilarityExampleSelector.from_examples(examples, OpenAIEmbeddings(model='text-embedding-3-large'), Chroma, k=NUM_EXAMPLES + 1)

RESULTS_DIR = 'results'

LOG_FILE = f"llm_logs/llm_logs_{datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")}.jsonl"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

print('=== Configuration ===')
print(f'LLM_ID: {LLM_ID}')
print(f'MODELLING_LANGUAGE: {MODELLING_LANGUAGE}')
print(f'SYS_PROMPT_LVL: {SYS_PROMPT_LVL}')
print(f'NUM_EXAMPLES_ICL: {NUM_EXAMPLES}')
print(f'NUM_SAMPLES: {NUM_SAMPLES}')
print(f'SAMPLING_TEMPERATURE: {SAMPLING_TEMPERATURE}')
print(f'SAMPLES_CACHE_ENABLED: {SAMPLES_CACHE_ENABLED}')
print(f'SAMPLES_CACHE_LOCATION: {SAMPLES_CACHE_LOCATION}')
print(f'SELF_VERIFICATION_TYPE: {SELF_VERIFICATION_TYPE}')
print(f'MAX_SELF_VERIFICATION_ATTEMPTS: {MAX_SELF_VERIFICATION_ATTEMPTS}')
print(f'TEMPERATURE: {TEMPERATURE}')
print(f'TOP_P: {TOP_P}')
print(f'MAX_TOKENS: {MAX_TOKENS}')
print(f'LIMIT: {LIMIT}')
print(f'SEED: {SEED}')
print(f'MAX_LLM_CALL_RETRIES: {MAX_LLM_CALL_RETRIES}')
print(f'DATASET LENGTH: {len(DATASET)}')
print(f'EXAMPLE_SELECTOR: {EXAMPLE_SELECTOR}')
print(f'LOG_FILE: {LOG_FILE}')
print(f'RESULTS_DIR: {RESULTS_DIR}')
print('=====================')
