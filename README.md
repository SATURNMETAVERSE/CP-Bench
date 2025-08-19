# CP-Bench: Evaluating Large Language Models for Constraint Modelling"

> **CP-Bench Dataset**: https://huggingface.co/datasets/kostis-init/CP-Bench

> **CP-Bench Leaderboard**: https://huggingface.co/spaces/kostis-init/CP-Bench-Leaderboard 

This repo contains the code for the paper "CP-Bench: Evaluating Large Language Models for Constraint Modelling". The paper explores and systematically evaluates the potential of using Large Language Models (LLMs) to transform textual combinatorial problem descriptions into concrete and executable Constraint Programming (CP) specifications through various prompting-based and inference-time compute methods.
For more details, please refer to the [paper](#citation).

## Structure

The repository is structured as follows:
- `data/`: Contains the CP-Bench dataset. Also available on [Hugging Face](https://huggingface.co/datasets/kostis-init/CP-Bench) in a more user-friendly format.
- `results/`: Contains results from the experiments.
    - `cached_samples/`: Contains cached samples that have been used in the experiments.
    - The other directories contain the results of the experiments for various methods.
- `src/`: Contains the code for the pipeline presented in the paper.


## Getting Started

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/kostis-init/CP-Bench.git
    ```
2. Navigate to the cloned directory and install dependencies (preferably in a virtual environment):
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

Open the [configuration file](src/llm_config.py) and set the following:

- **API keys** for LLM platforms (e.g., `OPENAI_API_KEY`).
    - Only one key is required, depending on the LLM used. For example, for OpenAI's models fill only `OPENAI_API_KEY`.
- **LLM_ID**: Which LLM to use for generating the CP models.
- **MODELLING_LANGUAGE**: The modelling language to use for the generated CP models (e.g., `cpmpy`, `minizinc`, `or-tools`).
- The other parameters (e.g. number of samples, self-verification loop limits etc.) are already set to some reasonable defaults, but you can adjust them as needed.

### Usage

Run the pipeline with the following command (make sure you are in the root directory):
```sh
python src/pipeline.py
```

> **Note:** If minizinc is selected as the modelling framework, make sure you have it installed and available in your PATH.

## Citation

If our research is helpful for your work, please consider citing our paper as follows:
```bibtex
@misc{michailidis2025cpbench,
      title={CP-Bench: Evaluating Large Language Models for Constraint Modelling}, 
      author={Kostis Michailidis and Dimos Tsouros and Tias Guns},
      year={2025},
      eprint={2506.06052},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.06052}, 
}
```