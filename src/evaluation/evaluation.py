import gc
import json
import re
from pathlib import Path

import pandas as pd
import torch

from llm.inference import run_prompt
from llm.models import load_model


def load_prompt_pairs(input_path: Path) -> list[dict]:
    rows = []

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    return {}


def compute_task_metrics(
    task: str,
    original_output: dict,
    counterfactual_output: dict,
) -> dict:
    if task == "classification":
        original_label = original_output.get("label")
        counterfactual_label = counterfactual_output.get("label")

        label_flip = None

        if original_label is not None and counterfactual_label is not None:
            label_flip = original_label != counterfactual_label

        return {
            "decision_flip": label_flip,
            "label_flip": label_flip,
            "recommendation_flip": None,
            "choice_flip": None,
        }

    if task == "recommendation":
        original_recommended_option = original_output.get("recommended_option")
        counterfactual_recommended_option = counterfactual_output.get(
            "recommended_option"
        )

        recommendation_flip = None

        if (
            original_recommended_option is not None
            and counterfactual_recommended_option is not None
        ):
            recommendation_flip = (
                original_recommended_option != counterfactual_recommended_option
            )

        return {
            "decision_flip": recommendation_flip,
            "label_flip": None,
            "recommendation_flip": recommendation_flip,
            "choice_flip": None,
        }

    if task == "decision_answering":
        original_selected_subject = original_output.get("selected_subject")
        counterfactual_selected_subject = counterfactual_output.get("selected_subject")

        choice_flip = None

        if (
            original_selected_subject is not None
            and counterfactual_selected_subject is not None
        ):
            choice_flip = original_selected_subject != counterfactual_selected_subject

        return {
            "decision_flip": choice_flip,
            "label_flip": None,
            "recommendation_flip": None,
            "choice_flip": choice_flip,
        }

    return {
        "decision_flip": None,
        "label_flip": None,
        "recommendation_flip": None,
        "choice_flip": None,
    }


def build_result_row(
    model_key: str,
    pair: dict,
    original_output: dict,
    counterfactual_output: dict,
    metrics: dict,
) -> dict:
    task = pair.get("task")

    row = {
        "model_key": model_key,
        "pair_id": pair.get("pair_id"),
        "scenario_id": pair.get("scenario_id"),
        "task": task,
        "subtask": pair.get("subtask"),
        "bias_axis": pair.get("bias_axis"),
        "replacement_group": pair.get("replacement_group"),
        "original_value": pair.get("original_value"),
        "counterfactual_value": pair.get("counterfactual_value"),
        "original_term": pair.get("original_term"),
        "counterfactual_term": pair.get("counterfactual_term"),
        "decision_flip": metrics.get("decision_flip"),
        "label_flip": metrics.get("label_flip"),
        "recommendation_flip": metrics.get("recommendation_flip"),
        "choice_flip": metrics.get("choice_flip"),
    }

    if task == "classification":
        row.update(
            {
                "original_label": original_output.get("label"),
                "counterfactual_label": counterfactual_output.get("label"),
                "original_recommended_option": None,
                "counterfactual_recommended_option": None,
                "original_selected_subject": None,
                "counterfactual_selected_subject": None,
            }
        )

    elif task == "recommendation":
        row.update(
            {
                "original_label": None,
                "counterfactual_label": None,
                "original_recommended_option": original_output.get(
                    "recommended_option"
                ),
                "counterfactual_recommended_option": counterfactual_output.get(
                    "recommended_option"
                ),
                "original_selected_subject": None,
                "counterfactual_selected_subject": None,
            }
        )

    elif task == "decision_answering":
        row.update(
            {
                "original_label": None,
                "counterfactual_label": None,
                "original_recommended_option": None,
                "counterfactual_recommended_option": None,
                "original_selected_subject": original_output.get("selected_subject"),
                "counterfactual_selected_subject": counterfactual_output.get(
                    "selected_subject"
                ),
            }
        )

    else:
        row.update(
            {
                "original_label": None,
                "counterfactual_label": None,
                "original_recommended_option": None,
                "counterfactual_recommended_option": None,
                "original_selected_subject": None,
                "counterfactual_selected_subject": None,
            }
        )

    return row


def save_results(
    results: list[dict],
    output_dir: Path,
    model_key: str,
    model_id: str,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_model_name = model_id.replace("/", "__")

    all_output_path = output_dir / f"results_{model_key}_{safe_model_name}_all.csv"

    df = pd.DataFrame(results)
    df.to_csv(all_output_path, index=False)

    output_paths = {
        "all": all_output_path,
    }

    common_columns = [
        "model_key",
        "pair_id",
        "scenario_id",
        "task",
        "subtask",
        "bias_axis",
        "replacement_group",
        "original_value",
        "counterfactual_value",
        "original_term",
        "counterfactual_term",
        "decision_flip",
        "label_flip",
        "recommendation_flip",
        "choice_flip",
        "original_label",
        "counterfactual_label",
        "original_recommended_option",
        "counterfactual_recommended_option",
        "original_selected_subject",
        "counterfactual_selected_subject",
    ]

    task_column_sets = {
        "classification": [
            "model_key",
            "pair_id",
            "scenario_id",
            "task",
            "subtask",
            "bias_axis",
            "replacement_group",
            "original_value",
            "counterfactual_value",
            "original_term",
            "counterfactual_term",
            "decision_flip",
            "label_flip",
            "original_label",
            "counterfactual_label",
        ],
        "recommendation": [
            "model_key",
            "pair_id",
            "scenario_id",
            "task",
            "subtask",
            "bias_axis",
            "replacement_group",
            "original_value",
            "counterfactual_value",
            "original_term",
            "counterfactual_term",
            "decision_flip",
            "recommendation_flip",
            "original_recommended_option",
            "counterfactual_recommended_option",
        ],
        "decision_answering": [
            "model_key",
            "pair_id",
            "scenario_id",
            "task",
            "subtask",
            "bias_axis",
            "replacement_group",
            "original_value",
            "counterfactual_value",
            "original_term",
            "counterfactual_term",
            "decision_flip",
            "choice_flip",
            "original_selected_subject",
            "counterfactual_selected_subject",
        ],
    }

    available_common_columns = [
        column
        for column in common_columns
        if column in df.columns
    ]

    df[available_common_columns].to_csv(all_output_path, index=False)

    for task, columns in task_column_sets.items():
        task_df = df[df["task"] == task].copy()

        if task_df.empty:
            continue

        available_columns = [
            column
            for column in columns
            if column in task_df.columns
        ]

        task_output_path = output_dir / f"results_{model_key}_{safe_model_name}_{task}.csv"
        task_df[available_columns].to_csv(task_output_path, index=False)

        output_paths[task] = task_output_path

    return output_paths


def run_evaluation(
    model_key: str,
    model_id: str,
    project_root: Path,
    input_path: Path,
    output_dir: Path,
    max_new_tokens: int = 180,
    quantization: str = "none",
) -> Path:
    tokenizer, model, _ = load_model(
        model_id=model_id,
        quantization=quantization,
    )

    prompt_pairs = load_prompt_pairs(input_path)

    results = []

    for index, pair in enumerate(prompt_pairs, start=1):
        print(f"\nRunning pair {index}/{len(prompt_pairs)}")
        print(f"{pair.get('original_term')} -> {pair.get('counterfactual_term')}")

        original_text = run_prompt(
            tokenizer=tokenizer,
            model=model,
            prompt=pair["original_prompt"],
            max_new_tokens=max_new_tokens,
        )

        counterfactual_text = run_prompt(
            tokenizer=tokenizer,
            model=model,
            prompt=pair["counterfactual_prompt"],
            max_new_tokens=max_new_tokens,
        )

        original_output = extract_json(original_text)
        counterfactual_output = extract_json(counterfactual_text)

        metrics = compute_task_metrics(
            task=pair["task"],
            original_output=original_output,
            counterfactual_output=counterfactual_output,
        )

        row = build_result_row(
            model_key=model_key,
            pair=pair,
            original_output=original_output,
            counterfactual_output=counterfactual_output,
            metrics=metrics,
        )

        results.append(row)

        print("Original parsed output:", original_output)
        print("Counterfactual parsed output:", counterfactual_output)
        print("Metrics:", metrics)

    output_paths = save_results(
        results=results,
        output_dir=output_dir,
        model_key=model_key,
        model_id=model_id,
    )

    del model
    del tokenizer
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("\nSaved results:")
    for name, path in output_paths.items():
        print(f"- {name}: {path}")

    return output_paths["all"]