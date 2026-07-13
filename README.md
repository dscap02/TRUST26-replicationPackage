# TRUST26 Replication Package

## Paper

**Automated Counterfactual Scenario Generation for Fairness
Assessment of Large Language Models**

> The paper title may be updated to match the final accepted version.

---

## Overview

This repository contains the replication package for the paper **“Automated Counterfactual Scenario Generation for Fairness
Assessment of Large Language Models”**.

The package supports the reproduction of the counterfactual fairness evaluation workflow described in the paper. It includes:

- the final task and replacement taxonomy;
- prompt templates for all task families and subtasks;
- neutral base scenarios;
- original/counterfactual prompt pairs;
- evaluation scripts for the target LLMs;
- paper-only evaluation results;
- paper-only summary tables and plots;
- run-comparison artifacts;
- documentation of the main prompt-iteration process.

The evaluation focuses on whether an LLM changes its task-relevant output when the prompt is modified only with respect to a controlled sensitive attribute replacement.

The repository is designed to support two levels of reproducibility:

1. **Result reproduction from saved outputs**, without rerunning LLM inference.
2. **Full pipeline reproduction**, including scenario generation, prompt-pair generation, model evaluation, plots, and run comparison.

---

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

## Directory Description

### `data/`

Contains the inputs used by the prompt-generation and evaluation pipeline.

```text
data/
├── generated/
├── generated2/
└── prompts/
```

#### `data/generated/`

Contains the neutral scenarios and prompt pairs used for the first evaluation run:

```text
data/generated/base_scenarios.jsonl
data/generated/prompt_pairs.jsonl
```

#### `data/generated2/`

Contains the neutral scenarios and prompt pairs used for the second evaluation run:

```text
data/generated2/base_scenarios.jsonl
data/generated2/prompt_pairs.jsonl
```

#### `data/prompts/`

Contains the prompt templates used by the pipeline:

```text
data/prompts/classification/
data/prompts/recommendation/
data/prompts/decision_answering/
data/prompts/scenario_generation/
```

The task-specific prompt templates are organized into three task families:

- classification;
- recommendation;
- decision answering.

The scenario-generation templates are organized by task family and subtask.

### `docs/`

Contains methodological documentation related to the replication package.

```text
docs/
├── prompt_iterations.md
└── prompt_iterations_evidence.csv
```

#### `prompt_iterations.md`

Documents the main prompt-related iterations that led to the final neutral scenario-generation prompts and task-specific evaluation templates.

The iterations should be interpreted as methodological phases, not as one-to-one versions of individual prompt files. Each iteration summarizes a relevant design change, its motivation, and the affected files.

#### `prompt_iterations_evidence.csv`

Provides structured evidence used to support the prompt-iteration summary.

### `outputs/taxonomy/`

Contains the final taxonomy used for prompt-pair generation.

```text
outputs/taxonomy/
├── README.md
├── final_task_taxonomy.json
├── final_replacement_taxonomy.json
├── final_taxonomy_extended.json
└── final_taxonomy_light.json
```

The taxonomy defines:

- task families;
- subtasks;
- sensitive attribute axes;
- replacement groups;
- valid replacement values.

The two main files are:

- `final_task_taxonomy.json`, which defines which bias axes and replacement groups are valid for each task and subtask;
- `final_replacement_taxonomy.json`, which defines the concrete terms that can be substituted within each replacement group.

### `outputs/llm_runs/`

Contains the saved model outputs and paper-only evaluation metrics for the first run.

```text
outputs/llm_runs/
├── LLama/
├── Mistral/
└── Qwen/
```

Each model folder contains:

```text
results_<model>_<model_id>_all.csv
results_<model>_<model_id>_classification.csv
results_<model>_<model_id>_recommendation.csv
results_<model>_<model_id>_decision_answering.csv
```

### `outputs/llm_run2/`

Contains the saved model outputs and paper-only evaluation metrics for the second run.

```text
outputs/llm_run2/
├── LLama/
├── Mistral/
└── Qwen/
```

The structure is the same as `outputs/llm_runs/`.

### `outputs/plots/`

Contains paper-only summary tables and plots for the first run.

```text
outputs/plots/
├── cases_decision_flips.csv
├── decision_flip_rate_by_model.pdf
├── heatmap_decision_flip_rate_by_bias_axis.pdf
├── summary_by_bias_axis.csv
├── summary_by_model.csv
├── summary_by_subtask.csv
├── summary_by_task.csv
└── task_flip_rates_by_model.pdf
```

### `outputs/plots2/`

Contains paper-only summary tables and plots for the second run.

```text
outputs/plots2/
├── cases_decision_flips.csv
├── decision_flip_rate_by_model.pdf
├── heatmap_decision_flip_rate_by_bias_axis.pdf
├── summary_by_bias_axis.csv
├── summary_by_model.csv
├── summary_by_subtask.csv
├── summary_by_task.csv
└── task_flip_rates_by_model.pdf
```

### `outputs/run_comparison/`

Contains paper-only comparison artifacts between the first and second evaluation runs.

```text
outputs/run_comparison/
├── cases_decision_metric_changes.csv
├── cases_new_decision_flips_in_run2.csv
├── cases_resolved_decision_flips_in_run2.csv
├── comparison_summary_by_bias_axis.csv
├── comparison_summary_by_model.csv
├── comparison_summary_by_subtask.csv
├── comparison_summary_by_task.csv
├── decision_flip_rate_by_model_and_run.pdf
├── delta_by_bias_axis.csv
├── delta_by_model.csv
├── delta_by_subtask.csv
├── delta_by_task.csv
├── delta_decision_flip_rate_by_model.pdf
├── delta_decision_flip_rate_by_model_task.pdf
├── pair_level_comparison.csv
└── task_flip_rates_by_model_and_run.pdf
```

These files compare decision-level flip behavior across two independent runs.

### `scripts/`

Contains the executable scripts used to reproduce the pipeline.

```text
scripts/
├── compare_runs.py
├── export_prompt_iterations.py
├── generate_base_scenarios.py
├── generate_prompt_pairs.py
├── run_llm_eval.py
├── run_pipeline.py
└── summary_plots.py
```

Main scripts:

| Script | Purpose |
|---|---|
| `generate_base_scenarios.py` | Generates neutral base scenarios. |
| `generate_prompt_pairs.py` | Generates original/counterfactual prompt pairs. |
| `run_llm_eval.py` | Runs model inference and computes paper metrics. |
| `summary_plots.py` | Generates paper-only summaries and plots. |
| `compare_runs.py` | Compares two evaluation runs. |
| `run_pipeline.py` | Runs the main pipeline. |
| `export_prompt_iterations.py` | Regenerates prompt-iteration documentation. |

### `src/`

Contains the source code used by the scripts.

```text
src/
├── evaluation/
├── llm/
└── prompts/
```

Main components:

| Directory | Purpose |
|---|---|
| `src/evaluation/` | Metric computation and result export. |
| `src/llm/` | Model loading and inference utilities. |
| `src/prompts/` | Prompt-template loading and prompt-pair generation utilities. |

---

## Task Families and Subtasks

The replication package evaluates three task families.

### Classification

Classification tasks require the model to assign a discrete label to a single case.

Subtasks:

- `hiring_screening`
- `student_evaluation`
- `ticket_priority_classification`
- `eligibility_classification`

### Recommendation

Recommendation tasks require the model to recommend one option among possible alternatives.

Subtasks:

- `career_path_recommendation`
- `course_recommendation`
- `role_assignment_recommendation`
- `accessibility_accommodation_recommendation`

### Decision Answering

Decision-answering tasks require the model to make or support a choice between alternatives.

Subtasks:

- `candidate_comparison`
- `scholarship_allocation`
- `ticket_escalation_decision`
- `public_service_priority_decision`

---

## Metrics Included in the Paper

This replication package includes only the metrics reported in the paper.

### Decision Flip Rate

Measures the proportion of prompt pairs for which the model changes its task-relevant decision between the original and counterfactual prompt.

This is the aggregate decision-level metric.

### Label Flip

Used for classification tasks. A label flip occurs when the predicted label changes between the original and counterfactual prompt:

```text
original_label != counterfactual_label
```

### Recommendation Flip

Used for recommendation tasks. A recommendation flip occurs when the recommended option changes between the original and counterfactual prompt:

```text
original_recommended_option != counterfactual_recommended_option
```

### Choice Flip

Used for decision-answering tasks. A choice flip occurs when the selected subject changes between the original and counterfactual prompt:

```text
original_selected_subject != counterfactual_selected_subject
```

No reasoning-similarity, confidence-shift, ranking-instability, or other auxiliary metrics are included in this replication package.

---

## Target Models

The evaluation scripts support the following target models:

```python
MODEL_REGISTRY = {
    "qwen": "Qwen/Qwen3-8B",
    "mistral": "mistralai/Ministral-8B-Instruct-2410",
    "llama": "NousResearch/Meta-Llama-3.1-8B-Instruct",
}
```

The package supports quantized model loading through the `--quantization` option:

- `none`
- `8bit`
- `4bit`

The saved runs were produced using the same evaluation pipeline and prompt-pair structure across all models.

---

## Quick Start

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Reproduce Existing Tables and Plots Without Rerunning LLMs

The repository already includes saved model outputs in:

```text
outputs/llm_runs/
outputs/llm_run2/
```

To regenerate the first-run summaries and plots:

```bash
python scripts/summary_plots.py \
  --input-dir outputs/llm_runs \
  --output-dir outputs/plots
```

To regenerate the second-run summaries and plots:

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

---

## Reproduce Prompt Pair Generation

To regenerate neutral base scenarios for the first run:

```bash
python scripts/generate_base_scenarios.py \
  --scenarios-per-subtask 3 \
  --output data/generated/base_scenarios.jsonl
```

To regenerate prompt pairs for the first run:

```bash
python scripts/generate_prompt_pairs.py \
  --scenarios data/generated/base_scenarios.jsonl \
  --output data/generated/prompt_pairs.jsonl \
  --max-pairs-per-group 1
```

For the second run:

```bash
python scripts/generate_base_scenarios.py \
  --scenarios-per-subtask 3 \
  --output data/generated2/base_scenarios.jsonl

python scripts/generate_prompt_pairs.py \
  --scenarios data/generated2/base_scenarios.jsonl \
  --output data/generated2/prompt_pairs.jsonl \
  --max-pairs-per-group 1
```

---

## Reproduce Model Evaluation

To evaluate one model on the first-run prompt pairs:

```bash
python scripts/run_llm_eval.py \
  --model qwen \
  --input data/generated/prompt_pairs.jsonl \
  --max-new-tokens 120 \
  --output-dir outputs/llm_runs \
  --quantization 8bit
```

Repeat with:

```text
--model mistral
--model llama
```

To evaluate one model on the second-run prompt pairs:

```bash
python scripts/run_llm_eval.py \
  --model qwen \
  --input data/generated2/prompt_pairs.jsonl \
  --max-new-tokens 120 \
  --output-dir outputs/llm_run2 \
  --quantization 8bit
```

---

## Full Pipeline Execution

The full pipeline can be executed with:

```bash
python scripts/run_pipeline.py \
  --models qwen mistral llama \
  --scenarios-per-subtask 3 \
  --max-pairs-per-group 1 \
  --max-new-tokens 120 \
  --quantization 8bit
```

To reuse existing scenarios and prompt pairs and only rerun model evaluation:

```bash
python scripts/run_pipeline.py \
  --models qwen mistral llama \
  --skip-scenario-generation \
  --skip-prompt-generation \
  --max-new-tokens 120 \
  --quantization 8bit
```

---

## Prompt Iteration Traceability

The prompt-design process is documented in:

```text
docs/prompt_iterations.md
```

This file summarizes the main methodological iterations that led to the final prompts.

The iterations should be read as major design phases, including:

- initial single-task prompt template;
- structured prompt-pair generation;
- full task/subtask template coverage;
- subtask-specific neutral scenario generation;
- scenario generation and export refinement;
- proxy-name rendering correction;
- neutral contextual labels in final prompts.

The supporting structured evidence is stored in:

```text
docs/prompt_iterations_evidence.csv
```

To regenerate the prompt-iteration documentation:

```bash
python scripts/export_prompt_iterations.py \
  --repo-root . \
  --output-md docs/prompt_iterations.md \
  --output-csv docs/prompt_iterations_evidence.csv
```

---

## Reproducibility Notes

The package includes both input artifacts and output artifacts.

Input artifacts include:

```text
data/prompts/
data/generated/
data/generated2/
outputs/taxonomy/
```

Output artifacts include:

```text
outputs/llm_runs/
outputs/llm_run2/
outputs/plots/
outputs/plots2/
outputs/run_comparison/
```

This allows reproducing the paper tables and plots without rerunning LLM inference.

Rerunning model inference may produce small differences depending on hardware, quantization mode, model implementation, and decoding behavior. For direct comparability, the same models, prompt pairs, maximum generation length, and quantization configuration should be used.

---

## Expected Output Artifacts

After running the first-run plotting script, the following files should be produced in `outputs/plots/`:

```text
summary_by_model.csv
summary_by_task.csv
summary_by_subtask.csv
summary_by_bias_axis.csv
cases_decision_flips.csv
decision_flip_rate_by_model.pdf
task_flip_rates_by_model.pdf
heatmap_decision_flip_rate_by_bias_axis.pdf
```

After running the second-run plotting script, the same files should be produced in `outputs/plots2/`.

After running the run-comparison script, the following files should be produced in `outputs/run_comparison/`:

```text
comparison_summary_by_model.csv
comparison_summary_by_task.csv
comparison_summary_by_subtask.csv
comparison_summary_by_bias_axis.csv
delta_by_model.csv
delta_by_task.csv
delta_by_subtask.csv
delta_by_bias_axis.csv
pair_level_comparison.csv
cases_decision_metric_changes.csv
cases_new_decision_flips_in_run2.csv
cases_resolved_decision_flips_in_run2.csv
decision_flip_rate_by_model_and_run.pdf
task_flip_rates_by_model_and_run.pdf
delta_decision_flip_rate_by_model.pdf
delta_decision_flip_rate_by_model_task.pdf
```


---

## Notes and Limitations

This package evaluates counterfactual stability, not population-level group fairness.

A flip indicates that the model changed its task-relevant output after a controlled sensitive attribute replacement. Such cases should be interpreted as candidate counterfactual instabilities and inspected in context.

The package does not compute demographic parity, equalized odds, equal opportunity, or other group-level fairness metrics because the generated evaluation data does not represent a population distribution with ground-truth outcomes.