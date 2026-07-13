import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().eq("true")


def load_results(input_dir: Path) -> pd.DataFrame:
    csv_paths = sorted(input_dir.rglob("results_*_all.csv"))

    if not csv_paths:
        raise FileNotFoundError(
            f"No results_*_all.csv files found recursively in {input_dir}"
        )

    frames = []

    for path in csv_paths:
        df = pd.read_csv(path)

        if "model_key" not in df.columns:
            model_key = path.stem.split("_")[1]
            df["model_key"] = model_key

        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def add_flip_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["label_flip_bool"] = as_bool(df["label_flip"]) if "label_flip" in df.columns else False
    df["recommendation_flip_bool"] = (
        as_bool(df["recommendation_flip"])
        if "recommendation_flip" in df.columns
        else False
    )
    df["choice_flip_bool"] = as_bool(df["choice_flip"]) if "choice_flip" in df.columns else False

    df["any_decision_flip"] = (
        df["label_flip_bool"]
        | df["recommendation_flip_bool"]
        | df["choice_flip_bool"]
    )

    return df


def compute_summary_by_model(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for model, group in df.groupby("model_key"):
        classification = group["task"].eq("classification")
        recommendation = group["task"].eq("recommendation")
        decision_answering = group["task"].eq("decision_answering")

        rows.append(
            {
                "model": model,
                "total_pairs": len(group),
                "classification_pairs": int(classification.sum()),
                "recommendation_pairs": int(recommendation.sum()),
                "decision_answering_pairs": int(decision_answering.sum()),
                "label_flips": int(group["label_flip_bool"].sum()),
                "label_flip_rate": (
                    group.loc[classification, "label_flip_bool"].mean()
                    if classification.sum()
                    else 0
                ),
                "recommendation_flips": int(group["recommendation_flip_bool"].sum()),
                "recommendation_flip_rate": (
                    group.loc[recommendation, "recommendation_flip_bool"].mean()
                    if recommendation.sum()
                    else 0
                ),
                "choice_flips": int(group["choice_flip_bool"].sum()),
                "choice_flip_rate": (
                    group.loc[decision_answering, "choice_flip_bool"].mean()
                    if decision_answering.sum()
                    else 0
                ),
                "decision_flips": int(group["any_decision_flip"].sum()),
                "decision_flip_rate": group["any_decision_flip"].mean(),
            }
        )

    return pd.DataFrame(rows)


def compute_summary_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []

    for (model, value), group in df.groupby(["model_key", group_col]):
        rows.append(
            {
                "model": model,
                group_col: value,
                "pairs": len(group),
                "label_flips": int(group["label_flip_bool"].sum()),
                "recommendation_flips": int(group["recommendation_flip_bool"].sum()),
                "choice_flips": int(group["choice_flip_bool"].sum()),
                "decision_flips": int(group["any_decision_flip"].sum()),
                "decision_flip_rate": group["any_decision_flip"].mean(),
            }
        )

    return pd.DataFrame(rows)


def save_bar_plot(data, x, y, title, ylabel, output_path, rotation=0):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.bar(data[x].astype(str), data[y])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_grouped_task_flip_plot(summary_by_model: pd.DataFrame, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = summary_by_model.set_index("model")[
        [
            "label_flip_rate",
            "recommendation_flip_rate",
            "choice_flip_rate",
        ]
    ]

    plt.figure(figsize=(10, 6))
    plot_data.plot(kind="bar")
    plt.title("Task-specific flip rates by model")
    plt.ylabel("Flip rate")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_heatmap(summary_by_bias_axis: pd.DataFrame, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pivot = summary_by_bias_axis.pivot(
        index="bias_axis",
        columns="model",
        values="decision_flip_rate",
    ).fillna(0)

    plt.figure(figsize=(12, 7))
    plt.imshow(pivot.values, aspect="auto")
    plt.title("Decision flip rate by bias axis and model")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="Decision flip rate")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_decision_flip_cases(df: pd.DataFrame, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    columns = [
        "model_key",
        "pair_id",
        "scenario_id",
        "task",
        "subtask",
        "bias_axis",
        "replacement_group",
        "original_term",
        "counterfactual_term",
        "original_label",
        "counterfactual_label",
        "original_recommended_option",
        "counterfactual_recommended_option",
        "original_selected_subject",
        "counterfactual_selected_subject",
        "label_flip",
        "recommendation_flip",
        "choice_flip",
    ]

    columns = [col for col in columns if col in df.columns]

    cases = df[df["any_decision_flip"]].copy()
    cases[columns].to_csv(output_dir / "cases_decision_flips.csv", index=False)


def generate_outputs(input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_results(input_dir)
    df = add_flip_columns(df)

    summary_by_model = compute_summary_by_model(df)
    summary_by_task = compute_summary_by_group(df, "task")
    summary_by_subtask = compute_summary_by_group(df, "subtask")
    summary_by_bias_axis = compute_summary_by_group(df, "bias_axis")

    summary_by_model.to_csv(output_dir / "summary_by_model.csv", index=False)
    summary_by_task.to_csv(output_dir / "summary_by_task.csv", index=False)
    summary_by_subtask.to_csv(output_dir / "summary_by_subtask.csv", index=False)
    summary_by_bias_axis.to_csv(output_dir / "summary_by_bias_axis.csv", index=False)

    save_decision_flip_cases(df, output_dir)

    save_bar_plot(
        data=summary_by_model,
        x="model",
        y="decision_flip_rate",
        title="Decision flip rate by model",
        ylabel="Decision flip rate",
        output_path=output_dir / "decision_flip_rate_by_model.pdf",
    )

    save_grouped_task_flip_plot(
        summary_by_model=summary_by_model,
        output_path=output_dir / "task_flip_rates_by_model.pdf",
    )

    save_heatmap(
        summary_by_bias_axis=summary_by_bias_axis,
        output_path=output_dir / "heatmap_decision_flip_rate_by_bias_axis.pdf",
    )

    print(f"Loaded results from: {input_dir}")
    print(f"Saved paper-only plots and summaries to: {output_dir}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate paper-only summary CSVs and plots using flip metrics."
    )

    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing sanitized results_*_all.csv files.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where paper-only outputs are saved.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    generate_outputs(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()