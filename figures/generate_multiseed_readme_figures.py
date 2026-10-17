"""Create README-ready four-seed threshold figures from the frozen Test sweep.

The input files are produced by ``threshold_report.py``.  Every comparison is
paired by seed.  Curves show the four-seed mean and sample standard deviation;
fixed-threshold panels also expose the individual seed values.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "figures" / "data" / "four_seed_auroc"
FIGURES = ROOT / "figures"
ASSETS = ROOT / "assets"
SEEDS = (2024, 2025, 2026, 2027)
STAGES = ("baseline", "task_a", "minneg")
FIXED_THRESHOLDS = (0.4, 0.5, 0.6)

DISPLAY = {
    "baseline": "E0 Baseline",
    "task_a": "Task A",
    "minneg": "min neg (A3)",
}
COLORS = {
    "baseline": "#64748b",
    "task_a": "#0072B2",
    "minneg": "#D55E00",
}
MARKERS = {"baseline": "^", "task_a": "s", "minneg": "o"}
LINESTYLES = {"baseline": "--", "task_a": "-.", "minneg": "-"}
METRIC_LABELS = {
    "G-mIoU@1": "G-mIoU@1 (%)",
    "G-mIoU@3": "G-mIoU@3 (%)",
    "G-mIoU@5": "G-mIoU@5 (%)",
    "Rej-F1": "Rejection F1 (%)",
    "negative_recall": "Negative recall / N-acc (%)",
    "positive_recall": "Positive recall (%)",
    "balanced_accuracy": "Balanced accuracy (%)",
    "AUROC": "AUROC (%)",
}


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.linewidth": 0.9,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "savefig.facecolor": "white",
    }
)


def _load_csv(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    numeric = {
        "seed",
        "threshold",
        "G-mIoU@1",
        "G-mIoU@3",
        "G-mIoU@5",
        "Rej-F1",
        "negative_recall",
        "positive_recall",
        "balanced_accuracy",
    }
    for row in rows:
        for key in numeric & row.keys():
            row[key] = int(row[key]) if key == "seed" else float(row[key])
        row["threshold"] = round(float(row["threshold"]), 2)
    return rows


def _load_auroc() -> dict[tuple[str, int], float]:
    report = json.loads((REPORTS / "REPORT.json").read_text())
    return {
        (row["stage"], int(row["seed"])): float(row["AUROC"])
        for row in report["invariant_metrics"]
    }


def _index(rows: list[dict]) -> dict[tuple[str, int, float], dict]:
    return {
        (row["stage"], int(row["seed"]), round(float(row["threshold"]), 2)): row
        for row in rows
    }


def _values(index, stage: str, threshold: float, metric: str, auroc) -> np.ndarray:
    if metric == "AUROC":
        return np.asarray([auroc[(stage, seed)] for seed in SEEDS], dtype=float)
    return np.asarray(
        [index[(stage, seed, round(float(threshold), 2))][metric] for seed in SEEDS],
        dtype=float,
    )


def _curve(index, stage: str, metric: str, thresholds: np.ndarray, auroc):
    matrix = np.vstack([_values(index, stage, t, metric, auroc) for t in thresholds])
    return matrix.mean(axis=1), matrix.std(axis=1, ddof=1), matrix


def _paired_delta(index, stage: str, metric: str, threshold: float, auroc):
    values = _values(index, stage, threshold, metric, auroc)
    baseline = _values(index, "baseline", threshold, metric, auroc)
    return values - baseline


def _style_axis(axis):
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(True, color="#94a3b8", linestyle=":", linewidth=0.7, alpha=0.38)


def _plot_mean_sd(axis, index, stage, metric, thresholds, auroc, label=None):
    mean, sd, _ = _curve(index, stage, metric, thresholds, auroc)
    axis.plot(
        thresholds,
        mean,
        color=COLORS[stage],
        linestyle=LINESTYLES[stage],
        linewidth=2.0 if stage == "minneg" else 1.7,
        label=label or DISPLAY[stage],
        zorder=3,
    )
    axis.fill_between(
        thresholds,
        mean - sd,
        mean + sd,
        color=COLORS[stage],
        alpha=0.12,
        linewidth=0,
        zorder=2,
    )
    return mean, sd


def _save(fig, stem: str):
    FIGURES.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        target = FIGURES / f"{stem}.{suffix}"
        kwargs = {"dpi": 300} if suffix == "png" else {}
        fig.savefig(target, bbox_inches="tight", **kwargs)
        if suffix == "svg":
            target.write_text(
                "\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n"
            )
    fig.savefig(ASSETS / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def figure_gmiou(index, thresholds, auroc):
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.5))

    axis = axes[0]
    for stage in STAGES:
        _plot_mean_sd(axis, index, stage, "G-mIoU@1", thresholds, auroc)
    for threshold in FIXED_THRESHOLDS:
        axis.axvline(threshold, color="#cbd5e1", linewidth=0.8, linestyle=":", zorder=1)
    axis.set(xlim=(0, 1), xlabel=r"Existence threshold $\tau$", ylabel="G-mIoU@1 (%)")
    axis.set_title("(a) Four-seed threshold trajectory", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    axis = axes[1]
    axis.axhline(0, color=COLORS["baseline"], linewidth=1.0, linestyle="--")
    for stage in ("task_a", "minneg"):
        matrix = np.vstack(
            [_paired_delta(index, stage, "G-mIoU@1", t, auroc) for t in thresholds]
        )
        mean = matrix.mean(axis=1)
        sd = matrix.std(axis=1, ddof=1)
        axis.plot(
            thresholds,
            mean,
            color=COLORS[stage],
            linestyle=LINESTYLES[stage],
            linewidth=2.0,
            label=f"{DISPLAY[stage]} - E0",
        )
        axis.fill_between(thresholds, mean - sd, mean + sd, color=COLORS[stage], alpha=0.12)
    axis.set(xlim=(0, 1), xlabel=r"Existence threshold $\tau$", ylabel=r"Paired $\Delta$ G-mIoU@1 (pp)")
    axis.set_title("(b) Paired gain over same-seed E0", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    axis = axes[2]
    x = np.arange(len(FIXED_THRESHOLDS), dtype=float)
    width = 0.24
    offsets = dict(zip(STAGES, (-width, 0.0, width)))
    jitter = np.asarray((-0.045, -0.015, 0.015, 0.045))
    for stage in STAGES:
        means, sds = [], []
        for threshold in FIXED_THRESHOLDS:
            values = _values(index, stage, threshold, "G-mIoU@1", auroc)
            means.append(values.mean())
            sds.append(values.std(ddof=1))
        positions = x + offsets[stage]
        axis.bar(
            positions,
            means,
            width,
            yerr=sds,
            capsize=3,
            color=COLORS[stage],
            alpha=0.86,
            edgecolor="#0f172a",
            linewidth=0.5,
            label=DISPLAY[stage],
        )
        for position, threshold in zip(positions, FIXED_THRESHOLDS):
            values = _values(index, stage, threshold, "G-mIoU@1", auroc)
            axis.scatter(
                position + jitter,
                values,
                marker=MARKERS[stage],
                s=18,
                facecolor="white",
                edgecolor="#0f172a",
                linewidth=0.55,
                zorder=4,
            )
    axis.set_xticks(x, [rf"$\tau={value:.1f}$" for value in FIXED_THRESHOLDS])
    axis.set_ylabel("G-mIoU@1, mean ± sample SD (%)")
    axis.set_title("(c) Fixed operating points", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    fig.subplots_adjust(wspace=0.28)
    _save(fig, "fig1_gmiou_threshold_dynamics_multiseed")


def figure_rejection(index, thresholds, auroc):
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.5))

    axis = axes[0]
    for stage in STAGES:
        _, _, neg = _curve(index, stage, "negative_recall", thresholds, auroc)
        _, _, pos = _curve(index, stage, "positive_recall", thresholds, auroc)
        for seed_index in range(len(SEEDS)):
            axis.plot(
                neg[:, seed_index],
                pos[:, seed_index],
                color=COLORS[stage],
                alpha=0.12,
                linewidth=0.8,
            )
        mean_neg = neg.mean(axis=1)
        mean_pos = pos.mean(axis=1)
        axis.plot(
            mean_neg,
            mean_pos,
            color=COLORS[stage],
            linestyle=LINESTYLES[stage],
            linewidth=2.0,
            label=DISPLAY[stage],
        )
        for threshold in FIXED_THRESHOLDS:
            idx_t = int(np.where(np.isclose(thresholds, threshold))[0][0])
            axis.scatter(
                mean_neg[idx_t],
                mean_pos[idx_t],
                color=COLORS[stage],
                marker=MARKERS[stage],
                s=28,
                edgecolor="white",
                linewidth=0.5,
                zorder=4,
            )
    axis.set(xlabel="Negative recall / N-acc (%)", ylabel="Positive recall (%)")
    axis.set_title("(a) Rejection–retention trade-off", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    axis = axes[1]
    for stage in STAGES:
        _plot_mean_sd(axis, index, stage, "Rej-F1", thresholds, auroc)
    for threshold in FIXED_THRESHOLDS:
        axis.axvline(threshold, color="#cbd5e1", linewidth=0.8, linestyle=":", zorder=1)
    axis.set(xlim=(0, 1), xlabel=r"Existence threshold $\tau$", ylabel="Rejection F1 (%)")
    axis.set_title("(b) Rejection F1 across all thresholds", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    axis = axes[2]
    x = np.arange(len(FIXED_THRESHOLDS), dtype=float)
    width = 0.34
    jitter = np.asarray((-0.045, -0.015, 0.015, 0.045))
    for stage, offset in (("task_a", -width / 2), ("minneg", width / 2)):
        deltas = [
            _paired_delta(index, stage, "negative_recall", threshold, auroc)
            for threshold in FIXED_THRESHOLDS
        ]
        means = [values.mean() for values in deltas]
        sds = [values.std(ddof=1) for values in deltas]
        positions = x + offset
        axis.bar(
            positions,
            means,
            width,
            yerr=sds,
            capsize=3,
            color=COLORS[stage],
            alpha=0.86,
            edgecolor="#0f172a",
            linewidth=0.5,
            label=f"{DISPLAY[stage]} - E0",
        )
        for position, values in zip(positions, deltas):
            axis.scatter(
                position + jitter,
                values,
                marker=MARKERS[stage],
                s=18,
                facecolor="white",
                edgecolor="#0f172a",
                linewidth=0.55,
                zorder=4,
            )
    axis.axhline(0, color=COLORS["baseline"], linestyle="--", linewidth=1.0)
    axis.set_xticks(x, [rf"$\tau={value:.1f}$" for value in FIXED_THRESHOLDS])
    axis.set_ylabel(r"Paired $\Delta$ negative recall (pp)")
    axis.set_title("(c) Same-seed gain over E0", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="best")
    _style_axis(axis)

    fig.subplots_adjust(wspace=0.28)
    _save(fig, "fig2_rejection_metrics_tradeoff_multiseed")


def figure_profiles(index, auroc):
    metric_keys = (
        "G-mIoU@1",
        "G-mIoU@3",
        "G-mIoU@5",
        "Rej-F1",
        "negative_recall",
        "AUROC",
    )
    metric_names = ("G@1", "G@3", "G@5", "Rej-F1", "N-acc", "AUROC")
    angles = np.linspace(0, 2 * np.pi, len(metric_keys), endpoint=False)
    closed_angles = np.r_[angles, angles[0]]
    fig = plt.figure(figsize=(14.2, 4.8))

    for panel, threshold in enumerate(FIXED_THRESHOLDS, start=1):
        axis = fig.add_subplot(1, 4, panel, projection="polar")
        for stage in STAGES:
            matrix = np.vstack(
                [_values(index, stage, threshold, metric, auroc) for metric in metric_keys]
            ).T
            mean = matrix.mean(axis=0)
            sd = matrix.std(axis=0, ddof=1)
            axis.plot(
                closed_angles,
                np.r_[mean, mean[0]],
                color=COLORS[stage],
                linestyle=LINESTYLES[stage],
                linewidth=1.8,
                marker=MARKERS[stage],
                markersize=3.5,
                label=DISPLAY[stage],
            )
            axis.fill_between(
                closed_angles,
                np.r_[np.maximum(mean - sd, 0), max(mean[0] - sd[0], 0)],
                np.r_[np.minimum(mean + sd, 100), min(mean[0] + sd[0], 100)],
                color=COLORS[stage],
                alpha=0.08,
            )
        axis.set_xticks(angles, metric_names)
        axis.set_ylim(0, 100)
        axis.set_yticks((25, 50, 75, 100))
        axis.set_yticklabels(("25", "50", "75", "100"), fontsize=7)
        axis.grid(color="#94a3b8", linestyle=":", linewidth=0.6, alpha=0.45)
        axis.set_title(rf"({chr(96 + panel)}) $\tau={threshold:.1f}$", fontweight="bold", pad=14)
        if panel == 1:
            axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), frameon=False, ncol=1)

    axis = fig.add_subplot(1, 4, 4)
    row_labels, delta_rows = [], []
    for stage in ("task_a", "minneg"):
        for threshold in FIXED_THRESHOLDS:
            delta_rows.append(
                [
                    _paired_delta(index, stage, metric, threshold, auroc).mean()
                    for metric in metric_keys
                ]
            )
            compact_name = "Task A" if stage == "task_a" else "A3"
            row_labels.append(f"{compact_name} · {threshold:.1f}")
    matrix = np.asarray(delta_rows)
    extent = max(1.0, float(np.abs(matrix).max()))
    image = axis.imshow(
        matrix,
        cmap="RdBu_r",
        norm=TwoSlopeNorm(vmin=-extent, vcenter=0.0, vmax=extent),
        aspect="auto",
    )
    axis.set_xticks(np.arange(len(metric_names)), metric_names, rotation=35, ha="right")
    axis.set_yticks(np.arange(len(row_labels)), row_labels)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            value = matrix[row, col]
            colour = "white" if abs(value) > 0.58 * extent else "#0f172a"
            axis.text(col, row, f"{value:+.1f}", ha="center", va="center", fontsize=7.2, color=colour)
    axis.set_title("(d) Paired mean gain over E0 (pp)", loc="left", fontweight="bold")
    colourbar = fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    colourbar.set_label("Percentage points")

    fig.subplots_adjust(wspace=0.36)
    _save(fig, "fig3_relative_metric_profiles_multiseed")


def write_tables(rows, index, thresholds, auroc):
    metrics = tuple(METRIC_LABELS)
    fixed_rows = []
    gain_rows = []
    for stage in STAGES:
        for threshold in FIXED_THRESHOLDS:
            for metric in metrics:
                values = _values(index, stage, threshold, metric, auroc)
                fixed_rows.append(
                    {
                        "stage": stage,
                        "threshold": threshold,
                        "metric": metric,
                        "n_seeds": len(values),
                        "mean": float(values.mean()),
                        "sample_sd": float(values.std(ddof=1)),
                        **{f"seed_{seed}": float(value) for seed, value in zip(SEEDS, values)},
                    }
                )
                if stage != "baseline":
                    delta = _paired_delta(index, stage, metric, threshold, auroc)
                    gain_rows.append(
                        {
                            "stage": stage,
                            "reference": "baseline",
                            "threshold": threshold,
                            "metric": metric,
                            "n_pairs": len(delta),
                            "paired_delta_mean": float(delta.mean()),
                            "paired_delta_sample_sd": float(delta.std(ddof=1)),
                            "positive_pairs": int((delta > 0).sum()),
                            "negative_pairs": int((delta < 0).sum()),
                            "ties": int((delta == 0).sum()),
                            **{f"seed_{seed}_delta": float(value) for seed, value in zip(SEEDS, delta)},
                        }
                    )

    for filename, output_rows in (
        ("fixed_threshold_summary.csv", fixed_rows),
        ("paired_gain_summary.csv", gain_rows),
    ):
        with (REPORTS / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(output_rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(output_rows)
    return fixed_rows, gain_rows


def _format(mean, sd):
    return f"{mean:.2f} ± {sd:.2f}"


def write_readme(fixed_rows, gain_rows):
    lookup = {(r["stage"], r["threshold"], r["metric"]): r for r in fixed_rows}
    gains = {(r["stage"], r["threshold"], r["metric"]): r for r in gain_rows}
    table = []
    for metric in ("G-mIoU@1", "Rej-F1", "negative_recall", "positive_recall", "AUROC"):
        row = [METRIC_LABELS[metric]]
        for stage in STAGES:
            item = lookup[(stage, 0.4, metric)]
            row.append(_format(item["mean"], item["sample_sd"]))
        table.append(row)

    g1_a = gains[("task_a", 0.4, "G-mIoU@1")]
    g1_m = gains[("minneg", 0.4, "G-mIoU@1")]
    nacc_m = gains[("minneg", 0.4, "negative_recall")]
    generated = datetime.now().astimezone().isoformat(timespec="seconds")
    protocol_path = REPORTS / "EVALUATION_PROTOCOL.json"
    checkpoint_note = ""
    if protocol_path.exists():
        protocol = json.loads(protocol_path.read_text())
        selected = protocol.get("selected_epoch_by_seed", {})
        selected_text = ", ".join(
            f"seed {seed}: epoch {epoch}" for seed, epoch in sorted(selected.items())
        )
        metric = protocol.get("selection_metric", "unknown metric")
        checkpoint_note = (
            f"A3 Test uses checkpoints selected strictly by Val {metric} ({selected_text}). "
            "The official Test split was evaluated only after each checkpoint had been frozen."
        )
    lines = [
        "# Four-seed threshold analysis",
        "",
        f"Generated: `{generated}`.",
        "",
        "All curves use the official Test split and thresholds from 0.00 to 1.00 in 0.01 increments. "
        "Lines and bars are the mean across paired seeds 2024–2027; ribbons and error bars are the sample standard deviation (n=4). "
        "Individual seed points are retained at the fixed operating points.",
        "",
        checkpoint_note,
        "" if checkpoint_note else "",
        "## 1. G-mIoU threshold dynamics",
        "",
        '<p align="center"><img src="assets/fig1_gmiou_threshold_dynamics_multiseed.png" width="100%" alt="Four-seed G-mIoU threshold dynamics"></p>',
        "",
        "The middle panel reports same-seed paired deltas, rather than subtracting two independently aggregated means. "
        f"At τ=0.4, Task A changes G-mIoU@1 by {g1_a['paired_delta_mean']:+.2f} ± {g1_a['paired_delta_sample_sd']:.2f} pp; "
        f"A3 changes it by {g1_m['paired_delta_mean']:+.2f} ± {g1_m['paired_delta_sample_sd']:.2f} pp.",
        "",
        "## 2. Rejection trade-off",
        "",
        '<p align="center"><img src="assets/fig2_rejection_metrics_tradeoff_multiseed.png" width="100%" alt="Four-seed rejection trade-off"></p>',
        "",
        "Thin trajectories in panel (a) are individual seeds; bold trajectories are four-seed means. "
        f"At τ=0.4, A3 changes negative recall by {nacc_m['paired_delta_mean']:+.2f} ± {nacc_m['paired_delta_sample_sd']:.2f} pp relative to same-seed E0.",
        "",
        "## 3. Relative metric profiles",
        "",
        '<p align="center"><img src="assets/fig3_relative_metric_profiles_multiseed.png" width="100%" alt="Four-seed relative metric profiles"></p>',
        "",
        "Radar curves show the cross-seed mean with a sample-SD band. The heatmap reports paired mean changes in percentage points; it is descriptive, not a significance test.",
        "",
        "## Fixed threshold τ=0.4",
        "",
        "| Metric | E0 Baseline | Task A | min neg (A3) |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(f"| {metric} | {e0} | {task_a} | {minneg} |" for metric, e0, task_a, minneg in table)
    lines += [
        "",
        "Values are mean ± sample SD (%). AUROC is threshold-independent and is repeated here only to keep the profile table self-contained.",
        "",
        "## Reproducible artifacts",
        "",
        "- `threshold_sweep_per_seed.csv`: every method × seed × threshold observation.",
        "- `threshold_sweep_summary.csv`: method-level mean and sample SD at every threshold.",
        "- `fixed_threshold_summary.csv`: 0.4/0.5/0.6 values with all four seed columns.",
        "- `paired_gain_summary.csv`: same-seed deltas against E0, including win/loss/tie counts.",
        "- `figures/`: PNG, PDF, and SVG exports.",
        "- `assets/`: README-sized PNG copies.",
        "- `../multiseed_figures.py`: data-driven regeneration script.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        "python multiseed_figures.py",
        "```",
    ]
    (REPORTS / "README.md").write_text("\n".join(lines) + "\n")


def main():
    source = REPORTS / "threshold_sweep_per_seed.csv"
    if not source.exists():
        raise FileNotFoundError(f"Threshold sweep is not complete: {source}")
    rows = _load_csv(source)
    present = {(row["stage"], int(row["seed"])) for row in rows}
    missing = [(stage, seed) for stage in STAGES for seed in SEEDS if (stage, seed) not in present]
    if missing:
        raise RuntimeError(f"Incomplete paired sweep; missing {missing}")
    thresholds = np.asarray(sorted({float(row["threshold"]) for row in rows}), dtype=float)
    expected = np.round(np.linspace(0.0, 1.0, 101), 2)
    if not np.array_equal(thresholds, expected):
        raise RuntimeError("Expected the complete 0.00–1.00 threshold grid at 0.01 intervals")

    auroc = _load_auroc()
    index = _index(rows)
    figure_gmiou(index, thresholds, auroc)
    figure_rejection(index, thresholds, auroc)
    figure_profiles(index, auroc)
    write_tables(rows, index, thresholds, auroc)

    manifest = {
        "generated": datetime.now().astimezone().isoformat(),
        "seeds": list(SEEDS),
        "thresholds": {"start": 0.0, "stop": 1.0, "step": 0.01, "count": 101},
        "uncertainty": "sample standard deviation across four paired seeds",
        "paired_reference": "same-seed E0",
        "figures": [
            "fig1_gmiou_threshold_dynamics_multiseed",
            "fig2_rejection_metrics_tradeoff_multiseed",
            "fig3_relative_metric_profiles_multiseed",
        ],
    }
    (REPORTS / "FIGURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
