#!/usr/bin/env python3
"""Redraw v2 figures from this overlay's frozen JSON, without model weights."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for path in Path("/usr/share/fonts/opentype/noto").glob("NotoSansCJK-*.ttc"):
    font_manager.fontManager.addfont(str(path))
families = sorted({f.name for f in font_manager.fontManager.ttflist if "CJK" in f.name})
plt.rcParams.update({"font.family": ["DejaVu Sans"] + families[:1], "font.size": 10,
                     "svg.fonttype": "none", "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})
BACKBONES = ('moment', 'qd', 'flash')
SHORT = {'moment': 'Moment-DETR', 'qd': 'QD-DETR', 'flash': 'FlashVTG'}
METRICS = (('auc', 'AUROC'), ('rej_f1', 'Rej-F1'), ('gmiou1', 'G-mIoU@1'))
COLORS = ('#0072B2', '#D55E00', '#009E73')

def figure(fig, output, name):
    output.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(output / (name + "." + extension), dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_performance(full, output):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    for ax, (key, title) in zip(axes, METRICS):
        rr = [next(r for r in full if r["backbone"] == bb and r["metric"] == title) for bb in BACKBONES]
        for offset, prefix, color, hatch in ((-.18, "seen", "#0072B2", ""), (.18, "unseen", "#E69F00", "//")):
            values = np.array([r[prefix] for r in rr])
            lo, hi = [np.array([r[prefix + suffix] for r in rr]) for suffix in ("_ci_low", "_ci_high")]
            x = np.arange(3) + offset
            ax.bar(x, values, .33, color=color, edgecolor="white", hatch=hatch, label=prefix.capitalize())
            ax.errorbar(x, values, yerr=[np.maximum(0, values - lo), np.maximum(0, hi - values)],
                        fmt="none", ecolor="#333333", capsize=3, lw=1)
            for xx, value, top in zip(x, values, hi):
                ax.text(xx, top + (.017 if key == "auc" else 1.7), f"{value:.3f}" if key == "auc" else f"{value:.1f}", ha="center", fontsize=8.5)
        ax.set(xticks=np.arange(3), xticklabels=[SHORT[b] for b in BACKBONES],
               ylim=(0, 1 if key == "auc" else 100), title=title, ylabel="Score (0–1)" if key == "auc" else "Score (%)")
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
    axes[0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("Charades-CG-GMR v2: C3_CG Seen / Unseen test", fontsize=14)
    fig.text(.5, -.01, "95% video-cluster bootstrap CI; 2,000 joint draws; seed 3407.\n"
             "S+ = S− = 2,684; U+ = U− = 2,990; checkpoints and Seen-validation thresholds frozen.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .94))
    figure(fig, output, "seen_unseen_performance")


def plot_gaps(full, output):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
    for ax, (_, title) in zip(axes, METRICS):
        for i, bb in enumerate(BACKBONES):
            r = next(r for r in full if r["backbone"] == bb and r["metric"] == title)
            ax.errorbar(r["gap_pp"], i,
                        xerr=[[max(0, r["gap_pp"] - r["gap_pp_ci_low"])], [max(0, r["gap_pp_ci_high"] - r["gap_pp"])]],
                        marker=("o", "s", "^")[i], color=COLORS[i], capsize=4, lw=1.4)
            ax.annotate(f'{r["gap_pp"]:+.2f}', (r["gap_pp"], i), xytext=(0, -16), textcoords="offset points", ha="center", fontsize=9)
        ax.axvline(0, color="#555555", lw=1, linestyle="--")
        ax.set(title=title, xlabel="Seen − Unseen (pp)", yticks=range(3), ylim=(2.5, -.6))
        ax.grid(axis="x", alpha=.18)
        ax.margins(x=.22)
    axes[0].set_yticklabels([SHORT[b] for b in BACKBONES])
    fig.suptitle("Charades-CG-GMR v2: signed generalization gaps", fontsize=14)
    fig.text(.5, -.02, "95% CI from joint video-cluster draws, including videos shared by Seen and Unseen.\n"
             "Negative gaps denote higher Unseen point estimates; class proportions affect Rej-F1 and G-mIoU.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, .93))
    figure(fig, output, "generalization_gaps")


def plot_counts(counts, output):
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    splits = ("train", "val_seen", "test")
    left = np.zeros(3)
    for part, color, hatch in zip(("S+", "S-", "U+", "U-"), ("#0072B2", "#56B4E9", "#D55E00", "#E69F00"), ("", "//", "", "//")):
        values = np.array([counts["C3_CG"][s].get(part, 0) for s in splits])
        ax.barh(np.arange(3), values, left=left, color=color, edgecolor="white", hatch=hatch, label=part)
        for y, x, n in zip(range(3), left, values):
            if n:
                ax.text(x + n / 2, y, str(n), ha="center", va="center", fontsize=9, color="white" if part in ("S+", "U+") else "black")
        left += values
    ax.set(yticks=range(3), yticklabels=splits, xlabel="Video–query pairs", title="Charades-CG-GMR v2: all four test quadrants")
    ax.invert_yaxis()
    ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.16))
    fig.text(.5, -.035, "Train / calibration: S+/S− only. Test: official Test-Trivial (Seen) + Novel-Composition (Unseen).\n"
             "Both test subsets have a 1:1 positive / constructed-negative ratio.", ha="center", fontsize=9)
    fig.tight_layout()
    figure(fig, output, "dataset_composition")


def plot_pipeline(output):
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set(xlim=(0, 11), ylim=(0, 3.5))
    ax.axis("off")
    steps = [("官方 Charades-CG", "Train + Test-Trivial\n+ Novel-Composition"),
             ("机械清理与划分", "剔除 2,119 条异常窗口\n训练 / 验证保持不变"),
             ("联合 Test 换视频", "同视频全部 S/U 正描述\nCLIP 最低 50% 内采样"),
             ("同句正负配对", "Seen / Unseen 各自 1:1\n负例是构造标签")]
    for i, (title, body) in enumerate(steps):
        x = .15 + 2.75 * i
        ax.add_patch(FancyBboxPatch((x, 1.1), 2.35, 1.6, boxstyle="round,pad=.08", facecolor="#EEF5FA", edgecolor="#0072B2", lw=1.2))
        ax.text(x + 1.175, 2.3, title, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + 1.175, 1.65, body, ha="center", va="center", fontsize=9)
        if i < 3:
            ax.annotate("", xy=(x + 2.67, 1.9), xytext=(x + 2.43, 1.9), arrowprops={"arrowstyle": "->", "lw": 1.4})
    ax.text(5.5, 3.2, "Charades-CG-GMR v2：补回 Seen 测试与联合重配负例", ha="center", fontsize=14)
    ax.text(5.5, .5, "复用原 checkpoint 与 Seen-validation 阈值 → v2 重新推理 → 联合视频聚类 bootstrap", ha="center", fontsize=10.5)
    ax.text(5.5, .1, "Novel-Word 不进入主评估；低文本相似度不能确认实际视频缺席。", ha="center", fontsize=10, color="#8B3B13")
    figure(fig, output, "construction_pipeline")

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    report = root / 'docs/reports/charades_cg_gmr_baselines_20261011'
    output = Path(__file__).resolve().parent
    full = json.loads((report / "ALL_METRICS_WITH_CI.json").read_text())
    counts = json.loads((report / "LOCAL_VERIFICATION.json").read_text())["dataset_counts"]
    plot_performance(full, output)
    plot_gaps(full, output)
    plot_counts(counts, output)
    plot_pipeline(output)
    print("Redrawn 4 v2 figures as SVG/PDF/PNG")
