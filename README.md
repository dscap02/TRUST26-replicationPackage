# Automated Counterfactual Scenario Generation for Fairness Assessment of Large Language Models: the ScenGen Framework 

**TRUST26 Replication Package**

## Publication

This replication package accompanies the paper **"Automated Counterfactual Scenario Generation for Fairness Assessment of Large Language Models: the ScenGen Framework"**, published at **TRUST 2026**, co-located with the 41st IEEE/ACM International Conference on Automated Software Engineering (ASE 2026).

**DOI:** https://doi.org/10.1145/3843782.3844655

## Overview

This repository contains the replication package for the paper **“Automated Counterfactual Scenario Generation for Fairness Assessment of Large Language Models: the ScenGen Framework“**.

The framework evaluates whether an LLM changes its task-relevant decision after a controlled substitution of a sensitive-attribute value. The workflow:

1. generates neutral scenarios for decision-oriented tasks;
2. instantiates a task-specific prompt template for each scenario;
3. constructs original/counterfactual prompt pairs that differ only in the value assigned to one sensitive attribute;
4. evaluates the same prompt pairs on multiple LLMs;
5. computes task-specific Decision Flip metrics and produces summary, comparison, and audit artifacts.

The repository supports two reproduction workflows:

- regenerating the analysis artifacts from the model outputs included in the package;
- executing the complete workflow, from neutral scenario generation to model evaluation.

## Experimental Configuration

| Element | Configuration |
|---|---:|
| Task families | 3 |
| Subtasks | 12 |
| Sensitive attributes | 10 |
| Neutral scenarios per run | 36 |
| Counterfactual prompt pairs per run | 564 |
| Classification pairs per run | 195 |
| Recommendation pairs per run | 174 |
| Decision Answering pairs per run | 195 |
| Evaluated models | 3 |
| Independent runs | 2 |
| Model–pair evaluations per run | 1,692 |
| Total model–pair evaluations | 3,384 |

Within each run, the three target models were evaluated on the same set of 564 counterfactual prompt pairs. The complete procedure was repeated in a second independent run, including scenario generation and prompt-pair construction.

## Repository Structure

```text
TRUST26-replicationPackage/
├── data/
│   ├── generated/
│   ├── generated2/
│   └── prompts/
├── docs/
├── outputs/
│   ├── llm_runs/
│   ├── llm_run2/
│   ├── plots/
│   ├── plots2/
│   ├── run_comparison/
│   └── taxonomy/
├── scripts/
├── src/
└── requirements.txt
```

## Package Contents

| Path | Description |
|---|---|
| `data/generated/` | Neutral scenarios and prompt pairs used in Run 1. |
| `data/generated2/` | Neutral scenarios and prompt pairs used in Run 2. |
| `data/prompts/` | Scenario-generation prompts and task-specific evaluation templates. |
| `docs/` | Documentation of the prompt-design iterations and their Git evidence. |
| `outputs/taxonomy/` | Final task and replacement taxonomies. |
| `outputs/llm_runs/` | Model outputs and Decision Flip metrics for Run 1. |
| `outputs/llm_run2/` | Model outputs and Decision Flip metrics for Run 2. |
| `outputs/plots/` | Summary tables, plots, and audit cases for Run 1. |
| `outputs/plots2/` | Summary tables, plots, and audit cases for Run 2. |
| `outputs/run_comparison/` | Aggregate, delta, pair-level, and audit comparisons between the two runs. |
| `scripts/` | Command-line entry points for generation, evaluation, analysis, and documentation. |
| `src/` | Reusable implementation components used by the command-line scripts. |
| `requirements.txt` | Python dependencies required by the package. |

## Taxonomy

The taxonomy used to generate the counterfactual prompt pairs is stored in:

```text
outputs/taxonomy/
├── README.md
├── final_replacement_taxonomy.json
├── final_task_taxonomy.json
├── final_taxonomy_extended.json
└── final_taxonomy_light.json
```

The two primary artifacts are:

| File | Description |
|---|---|
| `final_task_taxonomy.json` | Associates task families and subtasks with the applicable sensitive attributes and replacement groups. |
| `final_replacement_taxonomy.json` | Defines the replacement values available within each sensitive attribute and replacement group. |

`final_taxonomy_extended.json` and `final_taxonomy_light.json` provide extended and compact representations of the combined taxonomy.

The taxonomy covers ten sensitive attributes:

- Gender
- Ethnicity
- Nationality
- Religion
- Age
- Disability
- Sexual Orientation
- Socio-Economic Status
- Physical Appearance
- Linguistic Background

## Task Families and Subtasks

| Task family | Subtasks |
|---|---|
| Classification | `hiring_screening`, `student_evaluation`, `ticket_priority_classification`, `eligibility_classification` |
| Recommendation | `career_path_recommendation`, `course_recommendation`, `role_assignment_recommendation`, `accessibility_accommodation_recommendation` |
| Decision Answering | `candidate_comparison`, `scholarship_allocation`, `ticket_escalation_decision`, `public_service_priority_decision` |

Classification tasks assign a discrete label to a single case. Recommendation tasks select an option for a profile or situation. Decision-answering tasks select between two alternatives or return a tie when allowed by the task.

## Scenario and Prompt-Pair Data

The two experimental runs use separate input sets:

```text
data/generated/
├── base_scenarios.jsonl
└── prompt_pairs.jsonl

data/generated2/
├── base_scenarios.jsonl
└── prompt_pairs.jsonl
```

The `base_scenarios.jsonl` files store the 36 neutral scenarios used in each run. Every scenario is associated with a scenario identifier, task family, subtask, scenario text, task instruction, and generation model.

The corresponding `prompt_pairs.jsonl` files store the 564 original/counterfactual pairs generated for each run. Within a pair, the neutral scenario, task instruction, and prompt structure remain unchanged. Only the selected value of the sensitive attribute is replaced.

Pair and scenario identifiers preserve the connection between generated prompts, source scenarios, model outputs, and analysis records.

## Prompt Templates

Prompt templates are organized by function and task family:

```text
data/prompts/
├── classification/
├── recommendation/
├── decision_answering/
└── scenario_generation/
    ├── classification/
    ├── recommendation/
    └── decision_answering/
```

The `classification/`, `recommendation/`, and `decision_answering/` directories contain the templates used to construct the final evaluation prompts. Each template defines:

- the role assigned to the model;
- the position of the neutral scenario;
- the position of the contextual sensitive information;
- the task instruction;
- the required structured response format.

The `scenario_generation/` directory contains one neutral-scenario generation prompt for each of the 12 subtasks. These prompts specify the application domain, the admissible task-relevant information, the neutrality constraints, and the expected output structure.

## Models

### Scenario-Generation Model

The neutral scenarios used in the experiments were generated with:

```text
Qwen/Qwen3-4B-Instruct-2507
```

This model was used to construct the neutral evaluation inputs.

### Evaluated Models

The counterfactual prompt pairs were evaluated on:

```python
MODEL_REGISTRY = {
    "qwen": "Qwen/Qwen3-8B",
    "mistral": "mistralai/Ministral-8B-Instruct-2410",
    "llama": "NousResearch/Meta-Llama-3.1-8B-Instruct",
}
```

The same evaluation procedure and prompt pairs were used for all three models within each run.

## Evaluation Metrics

The replication package reports the decision-level metrics used in the paper.

### Decision Flip Rate

The Decision Flip Rate is the proportion of evaluated counterfactual prompt pairs for which the task-relevant decision changes:

```text
Decision Flip Rate = number of Decision Flips / number of evaluated prompt pairs
```

The concrete definition of a Decision Flip depends on the task family.

| Task family | Metric | Flip condition |
|---|---|---|
| Classification | Label Flip | The predicted label changes between the original and counterfactual prompt. |
| Recommendation | Recommendation Flip | The recommended option changes between the original and counterfactual prompt. |
| Decision Answering | Choice Flip | The selected alternative changes between the original and counterfactual prompt. |

All aggregate results, plots, and comparison artifacts in this package are derived from these decision-level metrics.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Reproduce the Analysis from Saved Model Outputs

The model outputs used in the study are already stored in:

```text
outputs/llm_runs/
outputs/llm_run2/
```

LLM inference is not required to regenerate the analysis artifacts.

To regenerate the Run 1 summaries and plots:

```bash
python scripts/summary_plots.py \
  --input-dir outputs/llm_runs \
  --output-dir outputs/plots
```

To regenerate the Run 2 summaries and plots:

```bash
python scripts/summary_plots.py \
  --input-dir outputs/llm_run2 \
  --output-dir outputs/plots2
```

To regenerate the comparison between the two runs:

```bash
python scripts/compare_runs.py \
  --run-a-dir outputs/llm_runs \
  --run-b-dir outputs/llm_run2 \
  --run-a-name run1 \
  --run-b-name run2 \
  --output-dir outputs/run_comparison
```

## Generate a New Independent Input Set

The exact scenarios and prompt pairs used in the paper are stored in `data/generated/` and `data/generated2/`.

Because scenario generation is generative, executing the following commands produces a new independent input set rather than recreating the saved scenarios verbatim.

To generate three neutral scenarios for each subtask without overwriting the reported inputs:

```bash
python scripts/generate_base_scenarios.py \
  --scenarios-per-subtask 3 \
  --output data/generated_new/base_scenarios.jsonl
```

To construct the corresponding counterfactual prompt pairs:

```bash
python scripts/generate_prompt_pairs.py \
  --scenarios data/generated_new/base_scenarios.jsonl \
  --output data/generated_new/prompt_pairs.jsonl \
  --max-pairs-per-group 1
```

The parameter `--max-pairs-per-group 1` generates at most one original/counterfactual pair for each applicable replacement group and scenario.

## Reproduce Model Evaluation

The reported model configuration used a maximum generation length of 120 tokens and 8-bit quantization.

To evaluate Qwen3-8B on the Run 1 prompt pairs without overwriting the saved results:

```bash
python scripts/run_llm_eval.py \
  --model qwen \
  --input data/generated/prompt_pairs.jsonl \
  --max-new-tokens 120 \
  --output-dir outputs/llm_rerun_run1 \
  --quantization 8bit
```

Repeat the command with:

```text
--model mistral
--model llama
```

To evaluate a model on the Run 2 prompt pairs, change the input and output paths:

```bash
python scripts/run_llm_eval.py \
  --model qwen \
  --input data/generated2/prompt_pairs.jsonl \
  --max-new-tokens 120 \
  --output-dir outputs/llm_rerun_run2 \
  --quantization 8bit
```

The available quantization modes are:

```text
none
8bit
4bit
```

## Execute the Pipeline Runner

The end-to-end runner coordinates scenario generation, prompt-pair generation, and multi-model evaluation.

The following command generates a new input set and stores the resulting model outputs in separate directories:

```bash
python scripts/run_pipeline.py \
  --models qwen mistral llama \
  --scenarios-per-subtask 3 \
  --max-pairs-per-group 1 \
  --max-new-tokens 120 \
  --scenarios-output data/generated_new/base_scenarios.jsonl \
  --prompt-pairs-output data/generated_new/prompt_pairs.jsonl \
  --output-dir outputs/llm_runs_new
```

To reuse an existing scenario and prompt-pair set and execute only model evaluation:

```bash
python scripts/run_pipeline.py \
  --models qwen mistral llama \
  --skip-scenario-generation \
  --skip-prompt-generation \
  --scenarios-output data/generated/base_scenarios.jsonl \
  --prompt-pairs-output data/generated/prompt_pairs.jsonl \
  --output-dir outputs/llm_rerun_run1 \
  --max-new-tokens 120
```

For an evaluation that explicitly uses 8-bit quantization, invoke `run_llm_eval.py` separately for each target model as shown in the previous section.

## Scripts

| Script | Description |
|---|---|
| `generate_base_scenarios.py` | Generates neutral scenarios for each taxonomy subtask. |
| `generate_prompt_pairs.py` | Constructs original/counterfactual pairs from neutral scenarios, templates, and taxonomy information. |
| `run_llm_eval.py` | Executes one target model and computes the task-specific Decision Flip metric. |
| `summary_plots.py` | Generates per-run Decision Flip summaries, plots, and audit cases. |
| `compare_runs.py` | Generates aggregate, delta, pair-level, and audit comparisons between two runs. |
| `run_pipeline.py` | Coordinates scenario generation, prompt-pair construction, and multi-model evaluation. |
| `export_prompt_iterations.py` | Reconstructs the prompt-iteration documentation from the Git history. |

## Source Code

Reusable components are organized under:

```text
src/
├── evaluation/
│   └── evaluation.py
├── llm/
│   ├── inference.py
│   └── models.py
└── prompts/
    ├── generator.py
    └── prompts.py
```

| Directory | Responsibility |
|---|---|
| `src/evaluation/` | Structured output extraction, Decision Flip computation, and result export. |
| `src/llm/` | Model registration, loading, quantization, and inference. |
| `src/prompts/` | Template loading, sensitive-information rendering, and prompt-pair construction. |

## Prompt-Iteration Traceability

The prompt-design process is documented in:

```text
docs/prompt_iterations.md
docs/prompt_iterations_evidence.csv
```

`prompt_iterations.md` summarizes the main methodological phases that led to the final neutral-scenario generation prompts and task-specific evaluation templates.

The reconstruction examines the Git history of:

```text
data/prompts/
scripts/generate_base_scenarios.py
scripts/generate_prompt_pairs.py
src/prompts/
```

The documented iterations represent methodological phases rather than a complete sequence of individually versioned prompt files. `prompt_iterations_evidence.csv` records the associated commits, dates, affected artifacts, and availability of matching Git evidence.

To regenerate both documentation files:

```bash
python scripts/export_prompt_iterations.py \
  --repo-root . \
  --output-md docs/prompt_iterations.md \
  --output-csv docs/prompt_iterations_evidence.csv
```

## Output Artifacts

### Model Results

Run 1 and Run 2 model outputs are stored in:

```text
outputs/llm_runs/
outputs/llm_run2/
```

Both directories contain one subdirectory for each evaluated model:

```text
LLama/
Mistral/
Qwen/
```

Each model directory contains:

```text
results_<model>_<model_id>_all.csv
results_<model>_<model_id>_classification.csv
results_<model>_<model_id>_recommendation.csv
results_<model>_<model_id>_decision_answering.csv
```

The `_all.csv` file stores the complete evaluation output for the model. The task-specific files store the corresponding Classification, Recommendation, or Decision Answering records.

### Per-Run Analysis

<details>
<summary>Files generated in <code>outputs/plots/</code> and <code>outputs/plots2/</code></summary>

```text
cases_decision_flips.csv
decision_flip_rate_by_model.pdf
heatmap_decision_flip_rate_by_bias_axis.pdf
summary_by_bias_axis.csv
summary_by_model.csv
summary_by_subtask.csv
summary_by_task.csv
task_flip_rates_by_model.pdf
```

</details>

These directories report Decision Flip results by model, task family, subtask, and sensitive attribute. `cases_decision_flips.csv` retains the identifiers and contextual information required to inspect the cases in which the task-relevant decision changed.

### Run Comparison

<details>
<summary>Files generated in <code>outputs/run_comparison/</code></summary>

```text
cases_decision_metric_changes.csv
cases_new_decision_flips_in_run2.csv
cases_resolved_decision_flips_in_run2.csv
comparison_summary_by_bias_axis.csv
comparison_summary_by_model.csv
comparison_summary_by_subtask.csv
comparison_summary_by_task.csv
decision_flip_rate_by_model_and_run.pdf
delta_by_bias_axis.csv
delta_by_model.csv
delta_by_subtask.csv
delta_by_task.csv
delta_decision_flip_rate_by_model.pdf
delta_decision_flip_rate_by_model_task.pdf
pair_level_comparison.csv
task_flip_rates_by_model_and_run.pdf
```

</details>

The comparison artifacts report aggregate results for both runs, differences between their Decision Flip rates, pair-level comparison records, and selected audit cases.

## Reproducibility Notes

The repository includes the scenarios, prompt pairs, model outputs, and analysis artifacts used in the study.

The analysis tables and plots can be regenerated from the saved model outputs without executing the LLMs again. Rerunning scenario generation or model inference may produce different outputs because both stages involve generative model execution.

Comparable model reruns require the same:

- taxonomy and prompt templates;
- input prompt pairs;
- model identifiers;
- maximum generation length;
- quantization configuration;
- evaluation and parsing code.

The two experimental runs must be treated as independent executions of the complete workflow rather than repeated evaluations of one fixed scenario set.

## Scope and Interpretation

The framework evaluates **local counterfactual decision stability**, not population-level group fairness.

A Decision Flip indicates that the task-relevant output changed after a controlled sensitive-attribute substitution. It identifies a candidate counterfactual instability, but does not by itself establish that the resulting decision is unfair.

Conversely, the absence of a Decision Flip does not establish the absence of bias. Individual cases should be interpreted together with their neutral scenario, task, subtask, sensitive attribute, replacement group, and original and counterfactual model outputs.
