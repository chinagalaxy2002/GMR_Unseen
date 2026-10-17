"""Figure 4: FlashVTG-GMR existence-head oracle analysis.

The temporal windows from the published E0 Test predictions are frozen.  The
oracle changes only the binary keep/reject decision using the Test labels, so
the gap is the maximum G-mIoU@1 gain attributable to existence classification
for this fixed localizer.  Test labels make this an analysis-only upper bound.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.metrics import compute_G_mIoU, prepare_submission_for_gmiou


PREDICTIONS = (
    ROOT
    / "experiments/agy_test/soccer_flash_event_query_20261015/runs/E0/"
    / "test_predictions.jsonl"
)
MINNEG_PREDICTIONS = (
    ROOT
    / "experiments/agy_test/soccer_flash_kim_mechanism_20261016/"
    / "task_a_enhancement/runs/A3_similarity_hardneg_s2024/test_predictions.jsonl"
)
GROUND_TRUTH = ROOT / "data/label/Standard/test.jsonl"
THRESHOLDS = np.round(np.linspace(0.0, 1.0, 101), 2)
OPERATING_POINTS = (0.4, 0.5, 0.6)

BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
GREY = "#6B7280"
LIGHT_ORANGE = "#FDE6D8"
LIGHT_GREEN = "#D9F0E8"


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def evaluate():
    predictions = read_jsonl(PREDICTIONS)
    minneg_predictions = read_jsonl(MINNEG_PREDICTIONS)
    ground_truth = read_jsonl(GROUND_TRUTH)
    is_positive = {
        row["qid"]: bool(row.get("relevant_windows")) for row in ground_truth
    }

    # Ground-truth gating is intentionally independent of threshold: it is an
    # oracle binary decision, not a classifier tuned on Test.
    oracle_submission = []
    for row in predictions:
        oracle_submission.append(
            {
                "qid": row["qid"],
                "pred_relevant_windows": (
                    row.get("pred_relevant_windows", [])
                    if is_positive[row["qid"]]
                    else []
                ),
            }
        )
    oracle = compute_G_mIoU(oracle_submission, ground_truth, (1,))["G-mIoU@1"]

    records = []
    for threshold in THRESHOLDS:
        gated, _ = prepare_submission_for_gmiou(
            predictions, cls_threshold=float(threshold), max_pred_windows=10
        )
        baseline = compute_G_mIoU(gated, ground_truth, (1,))["G-mIoU@1"]
        minneg_gated, _ = prepare_submission_for_gmiou(
            minneg_predictions, cls_threshold=float(threshold), max_pred_windows=10
        )
        minneg = compute_G_mIoU(minneg_gated, ground_truth, (1,))["G-mIoU@1"]
        records.append(
            {
                "threshold": float(threshold),
                "baseline_G-mIoU@1": baseline,
                "minneg_G-mIoU@1": minneg,
                "perfect_existence_G-mIoU@1": oracle,
                "minneg_gain_pp": minneg - baseline,
                "oracle_gain_pp": oracle - baseline,
                "oracle_gap_closed_pct": (
                    100.0 * (minneg - baseline) / (oracle - baseline)
                    if oracle != baseline
                    else 0.0
                ),
            }
        )
    return records, len(ground_truth), sum(is_positive.values())


def plot(records, sample_count: int, positive_count: int):
    threshold = np.asarray([row["threshold"] for row in records])
    baseline = np.asarray([row["baseline_G-mIoU@1"] for row in records])
    minneg = np.asarray([row["minneg_G-mIoU@1"] for row in records])
    oracle = np.asarray([row["perfect_existence_G-mIoU@1"] for row in records])
    minneg_gain = np.asarray([row["minneg_gain_pp"] for row in records])
    oracle_gain = np.asarray([row["oracle_gain_pp"] for row in records])
    gap_closed = np.asarray([row["oracle_gap_closed_pct"] for row in records])

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 9,
            "axes.linewidth": 0.9,
        }
    )
    fig, (ax_score, ax_gain) = plt.subplots(1, 2, figsize=(8.4, 3.35), dpi=300)

    ax_score.plot(
        threshold,
        baseline,
        color=BLUE,
        linestyle="-",
        linewidth=2.0,
        marker="o",
        markevery=10,
        markersize=3.5,
        label="E0 baseline head",
    )
    ax_score.plot(
        threshold,
        minneg,
        color=GREEN,
        linestyle="-.",
        linewidth=2.1,
        marker="^",
        markevery=10,
        markersize=4.0,
        label="Our min neg (A3)",
    )
    ax_score.plot(
        threshold,
        oracle,
        color=ORANGE,
        linestyle="--",
        linewidth=2.1,
        marker="s",
        markevery=10,
        markersize=3.5,
        label="Perfect existence oracle",
    )
    ax_score.fill_between(
        threshold, baseline, minneg, where=minneg >= baseline,
        color=LIGHT_GREEN, alpha=0.75,
        label="Gain realized by A3",
    )
    ax_score.fill_between(
        threshold, minneg, oracle, color=LIGHT_ORANGE, alpha=0.55,
        label="Remaining oracle gap",
    )
    ax_score.set_title("(a) Fixed-localizer performance", loc="left", fontweight="bold")
    ax_score.set_xlabel(r"Existence threshold $\tau$")
    ax_score.set_ylabel("G-mIoU@1 (%)")
    ax_score.set_xlim(0.0, 1.0)
    ax_score.set_ylim(0.0, 66.0)
    ax_score.legend(loc="lower right", frameon=True, edgecolor="#D1D5DB", fontsize=7.4)

    ax_gain.plot(
        threshold,
        oracle_gain,
        color=ORANGE,
        linestyle="--",
        linewidth=2.0,
        marker="s",
        markevery=10,
        markersize=3.5,
        label="Oracle upper-bound gain",
    )
    ax_gain.plot(
        threshold,
        minneg_gain,
        color=GREEN,
        linestyle="-",
        linewidth=2.2,
        marker="D",
        markevery=10,
        markersize=3.5,
        label="Gain realized by A3",
    )
    ax_gain.axhline(0.0, color=GREY, linewidth=0.9, linestyle="--")
    ax_gain.set_title("(b) A3 gain vs oracle potential", loc="left", fontweight="bold")
    ax_gain.set_xlabel(r"Existence threshold $\tau$")
    ax_gain.set_ylabel(r"$\Delta$ G-mIoU@1 (pp)")
    ax_gain.set_xlim(0.0, 1.0)
    ax_gain.set_ylim(min(-10.0, float(minneg_gain.min()) - 1.0), max(50.0, float(oracle_gain.max()) + 3.0))
    ax_gain.legend(loc="upper right", frameon=True, edgecolor="#D1D5DB", fontsize=7.5)

    annotation_layout = {
        0.4: ((0, 12), "center"),
        0.5: ((-18, -34), "right"),
        0.6: ((22, 12), "left"),
    }
    for operating_point in OPERATING_POINTS:
        index = int(round(operating_point * 100))
        for axis in (ax_score, ax_gain):
            axis.axvline(operating_point, color="#9CA3AF", linewidth=0.75, linestyle=":")
        ax_score.scatter(operating_point, baseline[index], color=BLUE, s=22, zorder=5)
        ax_score.scatter(operating_point, minneg[index], color=GREEN, s=24, marker="^", zorder=5)
        ax_gain.scatter(operating_point, minneg_gain[index], color=GREEN, s=24, marker="D", zorder=5)
        offset, alignment = annotation_layout[operating_point]
        ax_gain.annotate(
            f"{minneg_gain[index]:+.2f}\n({gap_closed[index]:.0f}% closed)",
            (operating_point, minneg_gain[index]),
            xytext=offset,
            textcoords="offset points",
            ha=alignment,
            va="center",
            fontsize=7.5,
            color=GREEN,
            fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": GREEN, "lw": 0.7},
        )

    for axis in (ax_score, ax_gain):
        axis.grid(axis="y", color="#D1D5DB", linewidth=0.65, linestyle=":", alpha=0.8)
        axis.spines[["top", "right"]].set_visible(False)
        axis.set_xticks(np.linspace(0, 1, 6))

    negative_count = sample_count - positive_count
    fig.text(
        0.5,
        0.01,
        (
            f"Official Test: N={sample_count} ({positive_count} positive, {negative_count} negative). "
            "Temporal windows are unchanged; the oracle uses Test labels and is analysis-only."
        ),
        ha="center",
        va="bottom",
        fontsize=8,
        color="#374151",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=2.2)

    figures = ROOT / "figures"
    assets = ROOT / "assets"
    figures.mkdir(exist_ok=True)
    assets.mkdir(exist_ok=True)
    stem = "fig4_existence_oracle_gmiou"
    fig.savefig(figures / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(figures / f"{stem}.svg", bbox_inches="tight")
    # Versioned README asset name avoids GitHub's stale-image CDN cache when
    # the figure gains an additional method curve.
    fig.savefig(assets / f"{stem}_a3.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    svg_path = figures / f"{stem}.svg"
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n"
    )

    with (figures / f"{stem}.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    values, n_samples, n_positives = evaluate()
    plot(values, n_samples, n_positives)
