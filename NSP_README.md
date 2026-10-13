# Single-rule nurse scheduling with Qwen3-1.7B

Same pipeline and settings as the paper (Michailidis, Tsouros & Guns). Only two things change:
the problems (`data_nsp/nsp_rules/`, six single-rule problems) and the LLM (Qwen3-1.7B via vLLM).

## Run (Baseline, Q1)

```bash
pip install -r requirements.txt "setuptools<81"   # cpmpy 0.9.25 needs pkg_resources
pip install vllm                                       # better in a separate venv
vllm serve Qwen/Qwen3-1.7B --served-model-name vllm-local-model --port 8001 --max-model-len 32768 &
python src/pipeline.py                                  # writes results/vllm-local-model/log_<time>.json
python src/semantic_check.py results/vllm-local-model/log_<time>.json
```

## Settings kept from the paper
System prompt level 3 (documentation), zero-shot, temperature 0, top_p 0.95, seed 42,
12k output tokens, 10 s execution timeout, Single Instance Accuracy as the metric.

Paper Q3 variants (change in `src/llm_config.py`):
- Sampling: `python src/pipeline.py 10` (k = 10, tau = 0.8, majority vote)
- Self-Verification: `MAX_SELF_VERIFICATION_ATTEMPTS = 10`
- Reasoning: `ENABLE_THINKING = True`

## Why `semantic_check.py`
Single Instance Accuracy checks one printed schedule. A model with no rule at all prints all Mornings,
which satisfies R1, R2, R4, R5 and R6, so it scores as correct on 5 of the 6 problems.
`semantic_check.py` is an extra diagnostic that does not change the paper's protocol. It reports:
- `under`: a schedule the generated model accepts but the rule forbids (exact, one solve);
- `over`: a schedule the rule allows but the generated model rejects (exact if the model declares
  no helper variables; otherwise exhaustive over 1 nurse x 7 days).

Ground-truth models were checked against the rule regexes on all 4^9 one-nurse, 9-day schedules.
