import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_RUN_A_DIR = Path("outputs/llm_runs")
DEFAULT_RUN_B_DIR = Path("outputs/llm_run2")
DEFAULT_OUTPUT_DIR = Path("outputs/run_comparison")


def infer_model_name(path: Path) -> str:
    match = re.match(r"results_(.*?)_", path.stem)

    if match:
        return match.group(1)

    return path.parent.name.lower()


def as_bool(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(False, index=df.index)

    return df[column].astype(str).str.lower().isin(["true", "1", "yes"])


def load_run_results(run_dir: Path, run_name: str) -> pd.DataFrame:
    csv_paths = sorted(run_dir.rglob("results_*_all.csv"))

    if not csv_paths:
        raise FileNotFoundError(
            f"No results_*_all.csv files found recursively in {run_dir}"
        )

    frames = []

    for path in csv_paths:
        df = pd.read_csv(path)

        if "model_key" not in df.columns:
            df["model_key"] = infer_model_name(path)

        df["run"] = run_name
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def add_flip_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["label_flip_bool"] = as_bool(df, "label_flip")
    df["recommendation_flip_bool"] = as_bool(df, "recommendation_flip")
    df["choice_flip_bool"] = as_bool(df, "choice_flip")

    if "decision_flip" in df.columns:
        df["decision_flip_bool"] = as_bool(df, "decision_flip")
    else:
        df["decision_flip_bool"] = (
            df["label_flip_bool"]
            | df["recommendation_flip_bool"]
            | df["choice_flip_bool"]
        )

    return df


def compute_summary_by_model(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for (run, model), group in df.groupby(["run", "model_key"]):
        classification_mask = group["task"].eq("classification")
        recommendation_mask = group["task"].eq("recommendation")
        decision_answering_mask = group["task"].eq("decision_answering")

        rows.append(
            {
                "run": run,
                "model": model,
                "total_pairs": len(group),
                "classification_pairs": int(classification_mask.sum()),
                "recommendation_pairs": int(recommendation_mask.sum()),
                "decision_answering_pairs": int(decision_answering_mask.sum()),
                "label_flips": int(group["label_flip_bool"].sum()),
                "label_flip_rate": (
                    group.loc[classification_mask, "label_flip_bool"].mean()
                    if classification_mask.sum()
                    else 0
                ),
                "recommendation_flips": int(group["recommendation_flip_bool"].sum()),
                "recommendation_flip_rate": (
                    group.loc[recommendation_mask, "recommendation_flip_bool"].mean()
                    if recommendation_mask.sum()
                    else 0
                ),
                "choice_flips": int(group["choice_flip_bool"].sum()),
                "choice_flip_rate": (
                    group.loc[decision_answering_mask, "choice_flip_bool"].mean()
                    if decision_answering_mask.sum()
                    else 0
                ),
                "decision_flips": int(group["decision_flip_bool"].sum()),
                "decision_flip_rate": group["decision_flip_bool"].mean(),
            }
        )

    return pd.DataFrame(rows)


def compute_group_summary(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    rows = []

    for (run, model, group_value), group in df.groupby(
        ["run", "model_key", group_column]
    ):
        rows.append(
            {
                "run": run,
                "model": model,
                group_column: group_value,
                "pairs": len(group),
                "label_flips": int(group["label_flip_bool"].sum()),
                "recommendation_flips": int(group["recommendation_flip_bool"].sum()),
                "choice_flips": int(group["choice_flip_bool"].sum()),
                "decision_flips": int(group["decision_flip_bool"].sum()),
                "decision_flip_rate": group["decision_flip_bool"].mean(),
            }
        )

    return pd.DataFrame(rows)


def compute_delta(
    summary: pd.DataFrame,
    id_columns: list[str],
    run_a_name: str,
    run_b_name: str,
) -> pd.DataFrame:
    run_a = summary[summary["run"] == run_a_name].drop(columns=["run"])
    run_b = summary[summary["run"] == run_b_name].drop(columns=["run"])

    merged = run_a.merge(
        run_b,
        on=id_columns,
        how="outer",
        suffixes=(f"_{run_a_name}", f"_{run_b_name}"),
    )

    metric_columns = [
        column
        for column in run_a.columns
        if column not in id_columns and pd.api.types.is_numeric_dtype(run_a[column])
    ]

    for column in metric_columns:
        col_a = f"{column}_{run_a_name}"
        col_b = f"{column}_{run_b_name}"

        if col_a in merged.columns and col_b in merged.columns:
            merged[f"{column}_delta"] = merged[col_b] - merged[col_a]

    return merged


def compute_pair_level_comparison(
    run_a_df: pd.DataFrame,
    run_b_df: pd.DataFrame,
    run_a_name: str,
    run_b_name: str,
) -> pd.DataFrame:
    key_columns = ["model_key", "pair_id"]

    selected_columns = [
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
        "original_label",
        "counterfactual_label",
        "original_recommended_option",
        "counterfactual_recommended_option",
        "original_selected_subject",
        "counterfactual_selected_subject",
        "decision_flip_bool",
        "label_flip_bool",
        "recommendation_flip_bool",
        "choice_flip_bool",
    ]

    selected_columns_a = [
        column for column in selected_columns if column in run_a_df.columns
    ]

    selected_columns_b = [
        column for column in selected_columns if column in run_b_df.columns
    ]

    run_a = run_a_df[selected_columns_a].copy()
    run_b = run_b_df[selected_columns_b].copy()

    merged = run_a.merge(
        run_b,
        on=key_columns,
        how="outer",
        suffixes=(f"_{run_a_name}", f"_{run_b_name}"),
        indicator=True,
    )

    flip_columns = [
        "decision_flip_bool",
        "label_flip_bool",
        "recommendation_flip_bool",
        "choice_flip_bool",
    ]

    for column in flip_columns:
        col_a = f"{column}_{run_a_name}"
        col_b = f"{column}_{run_b_name}"

        if col_a in merged.columns and col_b in merged.columns:
            a_values = merged[col_a].fillna(False).astype(bool)
            b_values = merged[col_b].fillna(False).astype(bool)

            merged[f"{column}_changed"] = a_values != b_values
            merged[f"{column}_new_in_{run_b_name}"] = (~a_values) & b_values
            merged[f"{column}_resolved_in_{run_b_name}"] = a_values & (~b_values)

    return merged


def save_grouped_run_plot(
    summary_by_model: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    if metric not in summary_by_model.columns:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    pivot = summary_by_model.pivot(
        index="model",
        columns="run",
        values=metric,
    ).fillna(0)

    ax = pivot.plot(kind="bar", figsize=(10, 6))
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=0)

    figure = ax.get_figure()
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def save_task_flip_rates_by_model_and_run(
    summary_by_model: pd.DataFrame,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = summary_by_model.copy()
    plot_data["model_run"] = (
        plot_data["model"].astype(str) + " / " + plot_data["run"].astype(str)
    )

    columns = [
        "label_flip_rate",
        "recommendation_flip_rate",
        "choice_flip_rate",
    ]

    available_columns = [
        column for column in columns if column in plot_data.columns
    ]

    if not available_columns:
        return

    ax = plot_data.set_index("model_run")[available_columns].plot(
        kind="bar",
        figsize=(12, 6),
    )

    ax.set_title("Task-specific flip rates by model and run")
    ax.set_ylabel("Flip rate")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)

    figure = ax.get_figure()
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def save_delta_plot(
    delta_df: pd.DataFrame,
    x_column: str,
    metric_delta: str,
    title: str,
    ylabel: str,
    output_path: Path,
    rotation: int = 0,
) -> None:
    if metric_delta not in delta_df.columns:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = delta_df.copy()
    plot_data[x_column] = plot_data[x_column].astype(str)

    plt.figure(figsize=(10, 6))
    plt.bar(plot_data[x_column], plot_data[metric_delta])
    plt.axhline(0, linewidth=1)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_model_task_delta_plot(
    delta_by_task: pd.DataFrame,
    output_path: Path,
) -> None:
    metric_delta = "decision_flip_rate_delta"

    if metric_delta not in delta_by_task.columns:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = delta_by_task.copy()
    plot_data["model_task"] = (
        plot_data["model"].astype(str)
        + " / "
        + plot_data["task"].astype(str)
    )

    plt.figure(figsize=(14, 6))
    plt.bar(plot_data["model_task"], plot_data[metric_delta])
    plt.axhline(0, linewidth=1)
    plt.title("Decision flip rate delta by model and task")
    plt.ylabel("Decision flip rate delta")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_pair_case_files(
    pair_comparison: pd.DataFrame,
    output_dir: Path,
    run_b_name: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    changed_columns = [
        "decision_flip_bool_changed",
        "label_flip_bool_changed",
        "recommendation_flip_bool_changed",
        "choice_flip_bool_changed",
    ]

    available_changed_columns = [
        column for column in changed_columns if column in pair_comparison.columns
    ]

    if available_changed_columns:
        changed_cases = pair_comparison[
            pair_comparison[available_changed_columns].any(axis=1)
        ].copy()

        changed_cases.to_csv(
            output_dir / "cases_decision_metric_changes.csv",
            index=False,
        )

    new_column = f"decision_flip_bool_new_in_{run_b_name}"
    resolved_column = f"decision_flip_bool_resolved_in_{run_b_name}"

    if new_column in pair_comparison.columns:
        pair_comparison[pair_comparison[new_column]].to_csv(
            output_dir / f"cases_new_decision_flips_in_{run_b_name}.csv",
            index=False,
        )

    if resolved_column in pair_comparison.columns:
        pair_comparison[pair_comparison[resolved_column]].to_csv(
            output_dir / f"cases_resolved_decision_flips_in_{run_b_name}.csv",
            index=False,
        )


def compare_runs(
    run_a_dir: Path,
    run_b_dir: Path,
    run_a_name: str,
    run_b_name: str,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    run_a_df = add_flip_columns(
        load_run_results(
            run_dir=run_a_dir,
            run_name=run_a_name,
        )
    )

    run_b_df = add_flip_columns(
        load_run_results(
            run_dir=run_b_dir,
            run_name=run_b_name,
        )
    )

    all_df = pd.concat([run_a_df, run_b_df], ignore_index=True)

    summary_by_model = compute_summary_by_model(all_df)
    summary_by_task = compute_group_summary(all_df, "task")
    summary_by_subtask = compute_group_summary(all_df, "subtask")
    summary_by_bias_axis = compute_group_summary(all_df, "bias_axis")

    delta_by_model = compute_delta(
        summary=summary_by_model,
        id_columns=["model"],
        run_a_name=run_a_name,
        run_b_name=run_b_name,
    )

    delta_by_task = compute_delta(
        summary=summary_by_task,
        id_columns=["model", "task"],
        run_a_name=run_a_name,
        run_b_name=run_b_name,
    )

    delta_by_subtask = compute_delta(
        summary=summary_by_subtask,
        id_columns=["model", "subtask"],
        run_a_name=run_a_name,
        run_b_name=run_b_name,
    )

    delta_by_bias_axis = compute_delta(
        summary=summary_by_bias_axis,
        id_columns=["model", "bias_axis"],
        run_a_name=run_a_name,
        run_b_name=run_b_name,
    )

    pair_comparison = compute_pair_level_comparison(
        run_a_df=run_a_df,
        run_b_df=run_b_df,
        run_a_name=run_a_name,
        run_b_name=run_b_name,
    )

    summary_by_model.to_csv(
        output_dir / "comparison_summary_by_model.csv",
        index=False,
    )

    summary_by_task.to_csv(
        output_dir / "comparison_summary_by_task.csv",
        index=False,
    )

    summary_by_subtask.to_csv(
        output_dir / "comparison_summary_by_subtask.csv",
        index=False,
    )

    summary_by_bias_axis.to_csv(
        output_dir / "comparison_summary_by_bias_axis.csv",
        index=False,
    )

    delta_by_model.to_csv(output_dir / "delta_by_model.csv", index=False)
    delta_by_task.to_csv(output_dir / "delta_by_task.csv", index=False)
    delta_by_subtask.to_csv(output_dir / "delta_by_subtask.csv", index=False)
    delta_by_bias_axis.to_csv(output_dir / "delta_by_bias_axis.csv", index=False)

    pair_comparison.to_csv(
        output_dir / "pair_level_comparison.csv",
        index=False,
    )

    save_pair_case_files(
        pair_comparison=pair_comparison,
        output_dir=output_dir,
        run_b_name=run_b_name,
    )

    save_grouped_run_plot(
        summary_by_model=summary_by_model,
        metric="decision_flip_rate",
        title="Decision flip rate by model and run",
        ylabel="Decision flip rate",
        output_path=output_dir / "decision_flip_rate_by_model_and_run.pdf",
    )

    save_task_flip_rates_by_model_and_run(
        summary_by_model=summary_by_model,
        output_path=output_dir / "task_flip_rates_by_model_and_run.pdf",
    )

    save_delta_plot(
        delta_df=delta_by_model,
        x_column="model",
        metric_delta="decision_flip_rate_delta",
        title=f"Decision flip rate delta by model ({run_b_name} - {run_a_name})",
        ylabel="Decision flip rate delta",
        output_path=output_dir / "delta_decision_flip_rate_by_model.pdf",
    )

    save_model_task_delta_plot(
        delta_by_task=delta_by_task,
        output_path=output_dir / "delta_decision_flip_rate_by_model_task.pdf",
    )

    print(f"Run A rows: {len(run_a_df)} from {run_a_dir}")
    print(f"Run B rows: {len(run_b_df)} from {run_b_dir}")
    print(f"Saved paper-only run comparison outputs to: {output_dir}")

    if "decision_flip_bool_changed" in pair_comparison.columns:
        changed = int(pair_comparison["decision_flip_bool_changed"].sum())
        print(f"Pairs with changed decision-flip status: {changed}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare two SE4AI evaluation runs using paper flip metrics only."
    )

    parser.add_argument(
        "--run-a-dir",
        default=str(DEFAULT_RUN_A_DIR),
        help="Directory containing the first run results.",
    )

    parser.add_argument(
        "--run-b-dir",
        default=str(DEFAULT_RUN_B_DIR),
        help="Directory containing the second run results.",
    )

    parser.add_argument(
        "--run-a-name",
        default="run1",
        help="Name used for the first run.",
    )

    parser.add_argument(
        "--run-b-name",
        default="run2",
        help="Name used for the second run.",
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where comparison outputs are saved.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    compare_runs(
        run_a_dir=Path(args.run_a_dir),
        run_b_dir=Path(args.run_b_dir),
        run_a_name=args.run_a_name,
        run_b_name=args.run_b_name,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()