"""Redraw Figure 4 with four paired seeds and Val-AUROC-selected A3 models.

By default this script plots the bundled per-seed CSV.  Pass ``--source-root``
to rebuild that CSV from the local four-seed experiment.  The oracle freezes
each seed's E0 temporal windows and changes only the keep/reject decision using
Test labels.  It is therefore an analysis-only upper bound, not a model result.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "figures" / "data" / "four_seed_auroc"
DATA_FILE = DATA_DIR / "oracle_gmiou_per_seed.csv"
METADATA_FILE = DATA_DIR / "oracle_gmiou_metadata.json"
FIGURES = ROOT / "figures"
ASSETS = ROOT / "assets"
SEEDS = (2024, 2025, 2026, 2027)
THRESHOLDS = np.round(np.linspace(0.0, 1.0, 101), 2)
OPERATING_POINTS = (0.4, 0.5, 0.6)

BLUE = "#64748B"
GREEN = "#009E73"
ORANGE = "#D55E00"
GREY = "#475569"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_metric(source_root: Path):
    eval_dir = source_root / "minneg" / "baseline_source" / "eval"
    sys.path.insert(0, str(eval_dir))
    spec = importlib.util.spec_from_file_location("gmr_oracle_metrics", eval_dir / "metrics.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the frozen GMR metric implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compute_G_mIoU


def build_data(source_root: Path) -> tuple[list[dict], int, int]:
    sweep_path = DATA_DIR / "threshold_sweep_per_seed.csv"
    with sweep_path.open(newline="") as stream:
        sweep = list(csv.DictReader(stream))
    lookup = {
        (row["stage"], int(row["seed"]), round(float(row["threshold"]), 2)):
        float(row["G-mIoU@1"])
        for row in sweep
    }

    ground_truth = read_jsonl(source_root / "minneg" / "data" / "test.jsonl")
    is_positive = {row["qid"]: bool(row.get("relevant_windows")) for row in ground_truth}
    compute_gmiou = load_metric(source_root)
    records: list[dict] = []

    for seed in SEEDS:
        predictions = read_jsonl(
            source_root / "baseline" / "runs" / f"E0_s{seed}" / "test_predictions.jsonl"
        )
        prediction_qids = {row["qid"] for row in predictions}
        if prediction_qids != set(is_positive):
            raise RuntimeError(f"Seed {seed} predictions do not match the Test query IDs")
        oracle_submission = [
            {
                "qid": row["qid"],
                "pred_relevant_windows": (
                    row.get("pred_relevant_windows", []) if is_positive[row["qid"]] else []
                ),
            }
            for row in predictions
        ]
        oracle = float(compute_gmiou(oracle_submission, ground_truth, (1,))["G-mIoU@1"])
        for threshold in THRESHOLDS:
            key = round(float(threshold), 2)
            baseline = lookup[("baseline", seed, key)]
            minneg = lookup[("minneg", seed, key)]
            oracle_gain = oracle - baseline
            minneg_gain = minneg - baseline
            records.append(
                {
                    "seed": seed,
                    "threshold": key,
                    "baseline_G-mIoU@1": baseline,
                    "minneg_G-mIoU@1": minneg,
                    "perfect_existence_G-mIoU@1": oracle,
                    "minneg_gain_pp": minneg_gain,
                    "oracle_gain_pp": oracle_gain,
                    "oracle_gap_closed_pct": (
                        100.0 * minneg_gain / oracle_gain if oracle_gain != 0 else 0.0
                    ),
                }
            )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    METADATA_FILE.write_text(
        json.dumps(
            {
                "test_samples": len(ground_truth),
                "positive_queries": sum(is_positive.values()),
                "negative_queries": len(ground_truth) - sum(is_positive.values()),
                "seeds": list(SEEDS),
                "oracle_definition": (
                    "Per-seed E0 temporal windows with the keep/reject decision replaced by Test labels; "
                    "analysis-only and not a model result."
                ),
            },
            indent=2,
        )
        + "\n"
    )
    return records, len(ground_truth), sum(is_positive.values())


def load_data() -> list[dict]:
    with DATA_FILE.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    numeric = set(records[0])
    for row in records:
        for key in numeric:
            row[key] = int(row[key]) if key == "seed" else float(row[key])
    return records


def matrix(records: list[dict], field: str) -> np.ndarray:
    by_seed: dict[int, dict[float, float]] = defaultdict(dict)
    for row in records:
        by_seed[int(row["seed"])][round(float(row["threshold"]), 2)] = float(row[field])
    return np.asarray(
        [[by_seed[seed][round(float(threshold), 2)] for seed in SEEDS] for threshold in THRESHOLDS]
    )


def mean_sd(records: list[dict], field: str) -> tuple[np.ndarray, np.ndarray]:
    values = matrix(records, field)
    return values.mean(axis=1), values.std(axis=1, ddof=1)


def plot(records: list[dict], sample_count: int, positive_count: int) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.9,
        }
    )
    curves = {
        "baseline": mean_sd(records, "baseline_G-mIoU@1"),
        "minneg": mean_sd(records, "minneg_G-mIoU@1"),
        "oracle": mean_sd(records, "perfect_existence_G-mIoU@1"),
        "minneg_gain": mean_sd(records, "minneg_gain_pp"),
        "oracle_gain": mean_sd(records, "oracle_gain_pp"),
    }
    fig, (ax_score, ax_gain) = plt.subplots(1, 2, figsize=(10.0, 4.0), dpi=300)

    score_styles = (
        ("baseline", "E0 baseline", BLUE, "--", "^"),
        ("minneg", "min neg (A3)", GREEN, "-", "o"),
        ("oracle", "Perfect-existence oracle", ORANGE, ":", "s"),
    )
    for key, label, color, linestyle, marker in score_styles:
        mean, sd = curves[key]
        ax_score.plot(
            THRESHOLDS, mean, color=color, linestyle=linestyle, linewidth=2.0,
            marker=marker, markevery=10, markersize=3.5, label=label, zorder=3,
        )
        ax_score.fill_between(THRESHOLDS, mean - sd, mean + sd, color=color, alpha=0.12)
    ax_score.set(
        title="(a) Fixed-localizer performance",
        xlabel=r"Existence threshold $\tau$",
        ylabel="G-mIoU@1, mean ± sample SD (%)",
        xlim=(0.0, 1.0),
        ylim=(0.0, 70.0),
    )
    ax_score.title.set_fontweight("bold")
    ax_score.title.set_ha("left")
    ax_score.title.set_position((0.0, 1.0))
    ax_score.legend(frameon=False, loc="lower right")

    gain_styles = (
        ("oracle_gain", "Oracle upper-bound gain", ORANGE, ":", "s"),
        ("minneg_gain", "Gain realized by A3", GREEN, "-", "D"),
    )
    for key, label, color, linestyle, marker in gain_styles:
        mean, sd = curves[key]
        ax_gain.plot(
            THRESHOLDS, mean, color=color, linestyle=linestyle, linewidth=2.1,
            marker=marker, markevery=10, markersize=3.5, label=label, zorder=3,
        )
        ax_gain.fill_between(THRESHOLDS, mean - sd, mean + sd, color=color, alpha=0.12)
    ax_gain.axhline(0.0, color=GREY, linewidth=0.9, linestyle="--")
    ax_gain.set(
        title="(b) Paired gain vs oracle potential",
        xlabel=r"Existence threshold $\tau$",
        ylabel=r"Paired $\Delta$ G-mIoU@1, mean ± SD (pp)",
        xlim=(0.0, 1.0),
    )
    ax_gain.title.set_fontweight("bold")
    ax_gain.title.set_ha("left")
    ax_gain.title.set_position((0.0, 1.0))
    ax_gain.legend(frameon=False, loc="best")

    a3_gain, _ = curves["minneg_gain"]
    oracle_gain, _ = curves["oracle_gain"]
    offsets = {0.4: (-16, -29), 0.5: (0, 13), 0.6: (18, -28)}
    for threshold in OPERATING_POINTS:
        idx = int(round(threshold * 100))
        closed = 100.0 * a3_gain[idx] / oracle_gain[idx]
        for axis in (ax_score, ax_gain):
            axis.axvline(threshold, color="#CBD5E1", linewidth=0.75, linestyle=":", zorder=1)
        ax_gain.scatter(threshold, a3_gain[idx], color=GREEN, marker="D", s=25, zorder=5)
        ax_gain.annotate(
            f"{a3_gain[idx]:+.2f} pp\n({closed:.0f}% closed)",
            (threshold, a3_gain[idx]), xytext=offsets[threshold], textcoords="offset points",
            ha="center", va="center", fontsize=7.4, color=GREEN, fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": GREEN, "lw": 0.7},
        )

    for axis in (ax_score, ax_gain):
        axis.grid(True, color="#94A3B8", linewidth=0.65, linestyle=":", alpha=0.4)
        axis.spines[["top", "right"]].set_visible(False)
        axis.set_xticks(np.linspace(0, 1, 6))

    negative_count = sample_count - positive_count
    fig.text(
        0.5, 0.012,
        f"Official Test: N={sample_count} ({positive_count} positive, {negative_count} negative); "
        "four paired seeds. Oracle uses Test labels and is analysis-only.",
        ha="center", va="bottom", fontsize=8, color="#334155",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=2.0)

    FIGURES.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    stem = "fig4_existence_oracle_gmiou_multiseed"
    for suffix in ("png", "pdf", "svg"):
        target = FIGURES / f"{stem}.{suffix}"
        fig.savefig(target, dpi=300 if suffix == "png" else None, bbox_inches="tight")
        if suffix == "svg":
            target.write_text(
                "\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n"
            )
    fig.savefig(ASSETS / f"{stem}_auroc.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root", type=Path,
        help="Local multiseed_reproduction directory; rebuilds the bundled oracle CSV.",
    )
    args = parser.parse_args()
    if args.source_root:
        records, sample_count, positive_count = build_data(args.source_root.resolve())
    else:
        records = load_data()
        metadata = json.loads(METADATA_FILE.read_text())
        sample_count = int(metadata["test_samples"])
        positive_count = int(metadata["positive_queries"])
    expected = len(SEEDS) * len(THRESHOLDS)
    if len(records) != expected:
        raise RuntimeError(f"Expected {expected} rows, found {len(records)}")
    plot(records, sample_count, positive_count)


if __name__ == "__main__":
    main()
