"""Figure 3: A3 Enhancement: Batch-wise Semantic Similarity Hard-Negative Contrastive Mining
Created according to plot-is-all-you-need scientific figure design principles.
Deliverables:
- figures/fig3_a3_hard_negative.png (300 DPI)
- figures/fig3_a3_hard_negative.pdf (Vector)
- figures/fig3_a3_hard_negative.py (Reproducible source)
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Styling consistent with plot-is-all-you-need & IEEE/Nature guidelines
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "mathtext.fontset": "cm",
    "pdf.fonttype": 42,
    "axes.linewidth": 0.9,
    "font.size": 8.5
})

# Color Palette
C_NAVY = "#0f172a"
C_BLUE = "#1e3a8a"
C_LIGHT_BLUE = "#dbeafe"
C_BORDER_BLUE = "#3b82f6"

C_TEAL = "#0d9488"
C_LIGHT_TEAL = "#ccfbf1"
C_BORDER_TEAL = "#14b8a6"

C_PURPLE = "#6b21a8"
C_LIGHT_PURPLE = "#f3e8ff"
C_BORDER_PURPLE = "#a855f7"

C_GREEN = "#15803d"
C_LIGHT_GREEN = "#dcfce7"
C_BORDER_GREEN = "#22c55e"

C_RED = "#b91c1c"
C_LIGHT_RED = "#fee2e2"
C_BORDER_RED = "#ef4444"

C_AMBER = "#b45309"
C_LIGHT_AMBER = "#fef3c7"
C_BORDER_AMBER = "#f59e0b"

C_GRAY_BG = "#f8fafc"
C_BORDER_GRAY = "#94a3b8"


def add_box(ax, x, y, w, h, boxstyle="round,pad=0.015,rounding_size=0.025", 
            facecolor="#ffffff", edgecolor="#94a3b8", linewidth=1.2, zorder=2, alpha=1.0):
    box = FancyBboxPatch((x, y), w, h, boxstyle=boxstyle,
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=linewidth, zorder=zorder, alpha=alpha)
    ax.add_patch(box)
    return box


def add_arrow(ax, p1, p2, color="#64748b", linewidth=1.8, arrowstyle="-|>", 
              mutation_scale=12, linestyle="solid", zorder=3, connectionstyle="arc3,rad=0"):
    arrow = FancyArrowPatch(p1, p2, color=color, linewidth=linewidth,
                            arrowstyle=arrowstyle, mutation_scale=mutation_scale,
                            linestyle=linestyle, zorder=zorder, connectionstyle=connectionstyle)
    ax.add_patch(arrow)
    return arrow


def generate_figure_3():
    fig = plt.figure(figsize=(14.2, 8.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    # Grid Layout: Top (a) Similarity Mining & (b) Dual Forward Architecture
    # Bottom: (c) Negative Rejection Performance & (d) Comprehensive Benchmark Radar/Grouped Bar
    ax_arch = fig.add_axes([0.02, 0.48, 0.96, 0.48])
    ax_arch.set_xlim(0, 1)
    ax_arch.set_ylim(0, 1)
    ax_arch.axis("off")

    ax_rej = fig.add_axes([0.06, 0.08, 0.42, 0.33])
    ax_radar = fig.add_axes([0.55, 0.08, 0.41, 0.33])

    # --------------------------------------------------------------------------
    # PANEL (a) & (b): SIMILARITY MINING ENGINE & CONTRASTIVE PATHS
    # --------------------------------------------------------------------------
    ax_arch.text(0.01, 0.97, "(a) Batch-wise Semantic Similarity Hard-Negative Mining & Dual Contrastive Grounding",
                 fontsize=11.5, fontweight="bold", color=C_NAVY, ha="left", va="center")

    # 1. Mini-Batch Query Stream (Left)
    add_box(ax_arch, 0.01, 0.06, 0.22, 0.87, facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.4)
    ax_arch.text(0.12, 0.88, "Mini-Batch $(B=8)$ Queries", ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_NAVY)

    # Pairs list in mini-batch
    queries = [
        ("Pair 1", '"Direct free kick near penalty box"'),
        ("Pair 2", '"Corner kick crossed into box"'),
        ("Pair 3", '"Header on target by striker"'),
        ("Pair 4", '"Goal kick by goalkeeper"')
    ]
    for i, (p_title, q_text) in enumerate(queries):
        yo = 0.70 - i * 0.15
        add_box(ax_arch, 0.025, yo, 0.19, 0.12, facecolor="#ffffff", edgecolor="#cbd5e1")
        ax_arch.text(0.12, yo + 0.075, f"{p_title}: $(V_{i+1}, T_{i+1})$", ha="center", va="center", fontsize=8, fontweight="bold", color=C_NAVY)
        ax_arch.text(0.12, yo + 0.035, q_text, ha="center", va="center", fontsize=6.8, color=C_BLUE if i == 0 else (C_RED if i == 1 else "#64748b"))

    # 2. Similarity Matrix Engine (Center Left)
    add_box(ax_arch, 0.25, 0.06, 0.29, 0.87, facecolor="#faf5ff", edgecolor=C_BORDER_PURPLE, linewidth=1.5)
    ax_arch.text(0.395, 0.88, "Semantic Similarity Matrix", ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_PURPLE)

    # Text L2 Normalization
    add_box(ax_arch, 0.27, 0.73, 0.25, 0.10, facecolor="#ffffff", edgecolor=C_BORDER_PURPLE)
    ax_arch.text(0.395, 0.795, "L2-Normalized Embedding", ha="center", va="center", fontsize=8, fontweight="bold", color=C_NAVY)
    ax_arch.text(0.395, 0.755, r"$\hat{T}_i = \mathrm{Normalize}(\mathrm{Pool}(T_i)) \in \mathbb{R}^{256}$", ha="center", va="center", fontsize=7.5, color=C_PURPLE)
    add_arrow(ax_arch, (0.23, 0.77), (0.27, 0.77), color=C_BORDER_PURPLE)

    # Similarity Matrix Heatmap Visualization
    add_box(ax_arch, 0.27, 0.35, 0.25, 0.35, facecolor="#ffffff", edgecolor=C_BORDER_PURPLE)
    ax_arch.text(0.395, 0.66, r"Cosine Matrix: $S_{ij} = \hat{T}_i^\top \hat{T}_j \quad (S_{ii} = -\infty)$",
                 ha="center", va="center", fontsize=7.5, fontweight="bold", color=C_NAVY)

    # Render a 4x4 mini heatmap inside
    matrix_vals = [
        ["$-\\infty$", "0.89", "0.42", "0.31"],
        ["0.89", "$-\\infty$", "0.55", "0.28"],
        ["0.42", "0.55", "$-\\infty$", "0.36"],
        ["0.31", "0.28", "0.36", "$-\\infty$"]
    ]
    for r in range(4):
        for c in range(4):
            is_diag = (r == c)
            is_argmax = (r == 0 and c == 1)
            cell_col = "#e2e8f0" if is_diag else ("#fda4af" if is_argmax else "#f3e8ff")
            edge_col = "#ef4444" if is_argmax else "#c084fc"
            add_box(ax_arch, 0.285 + c * 0.054, 0.58 - r * 0.054, 0.050, 0.046,
                    boxstyle="round,pad=0.005,rounding_size=0.01",
                    facecolor=cell_col, edgecolor=edge_col, linewidth=1.0 if is_argmax else 0.6)
            ax_arch.text(0.310 + c * 0.054, 0.603 - r * 0.054, matrix_vals[r][c],
                         ha="center", va="center", fontsize=6.5,
                         fontweight="bold" if is_argmax else "normal",
                         color=C_RED if is_argmax else C_NAVY)

    # Argmax Selection Callout
    add_box(ax_arch, 0.27, 0.10, 0.25, 0.21, facecolor=C_LIGHT_RED, edgecolor=C_BORDER_RED, linewidth=1.4)
    ax_arch.text(0.395, 0.26, "Hardest In-Batch Distractor", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_RED)
    ax_arch.text(0.395, 0.20, r"$j^* = \operatorname{argmax}_{j \neq i} S_{ij}$" "\n" r"(Highest Semantic Confusion)",
                 ha="center", va="center", fontsize=8, color=C_NAVY)
    ax_arch.text(0.395, 0.135, 'Pair $(V_1, T_2)$: "Free kick" vs "Corner kick"',
                 ha="center", va="center", fontsize=7.2, fontweight="bold", color=C_RED)
    add_arrow(ax_arch, (0.395, 0.35), (0.395, 0.31), color=C_BORDER_RED, linewidth=1.8)

    # 3. Dual Contrastive Forward Paths (Right)
    add_box(ax_arch, 0.56, 0.06, 0.43, 0.87, facecolor="#f8fafc", edgecolor="#94a3b8", linewidth=1.5)
    ax_arch.text(0.775, 0.88, "Dual-Stream Contrastive Forward & Supervision",
                 ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_NAVY)

    # 3.1 Path A: Positive Grounding Forward
    add_box(ax_arch, 0.58, 0.51, 0.39, 0.33, facecolor=C_LIGHT_GREEN, edgecolor=C_BORDER_GREEN, linewidth=1.4)
    ax_arch.text(0.775, 0.80, "Path A: Standard Positive Grounding Forward", ha="center", va="center", fontsize=9, fontweight="bold", color=C_GREEN)
    ax_arch.text(0.775, 0.74, "Input: Matched Video & Query $(V_i, T_i)$", ha="center", va="center", fontsize=7.8, color=C_NAVY)

    add_box(ax_arch, 0.60, 0.54, 0.35, 0.16, facecolor="#ffffff", edgecolor=C_BORDER_GREEN)
    ax_arch.text(0.775, 0.64, r"Positive Existence Loss ($\mathcal{L}_{exist}$)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_GREEN)
    ax_arch.text(0.775, 0.58, r"$\mathcal{L}_{exist} = \mathrm{BCE}(\sigma(\hat{y}_i^+), 1.0) \to$ Pull toward 1.0",
                 ha="center", va="center", fontsize=8, color=C_NAVY)

    add_arrow(ax_arch, (0.23, 0.73), (0.58, 0.73), color=C_BORDER_GREEN, linewidth=1.8)

    # 3.2 Path B: Hard Negative Contrastive Forward
    add_box(ax_arch, 0.58, 0.10, 0.39, 0.37, facecolor=C_LIGHT_RED, edgecolor=C_BORDER_RED, linewidth=1.4)
    ax_arch.text(0.775, 0.42, "Path B: Hard-Negative Contrastive Penalty", ha="center", va="center", fontsize=9, fontweight="bold", color=C_RED)
    ax_arch.text(0.775, 0.36, r"Input: Video $V_i$ with Distractor Query $T_{j^*}$", ha="center", va="center", fontsize=7.8, color=C_NAVY)

    add_box(ax_arch, 0.60, 0.13, 0.35, 0.19, facecolor="#ffffff", edgecolor=C_BORDER_RED)
    ax_arch.text(0.775, 0.26, r"Hard Negative Loss ($\mathcal{L}_{hard}$)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_RED)
    ax_arch.text(0.775, 0.20, r"$\mathcal{L}_{hard} = \mathrm{BCE}(\sigma(\hat{y}_i^-), 0.0) \to$ Push toward 0.0",
                 ha="center", va="center", fontsize=8, color=C_RED)
    ax_arch.text(0.775, 0.155, r"Loss Weight $\lambda_{hard} = 0.5$", ha="center", va="center", fontsize=7.2, color="#64748b")

    add_arrow(ax_arch, (0.52, 0.20), (0.58, 0.20), color=C_BORDER_RED, linewidth=1.8)

    # --------------------------------------------------------------------------
    # PANEL (c): NEGATIVE REJECTION ACCURACY & FALSE-POSITIVE SUPPRESSION
    # --------------------------------------------------------------------------
    gates = ["Gate @ 0.4", "Gate @ 0.5", "Val-Calibrated"]
    x = np.arange(len(gates))
    w_bar = 0.26

    # Real experimental numbers from E0, Task A, and A3
    n_acc_e0 = [46.34, 75.00, 84.95]
    n_acc_ta = [65.65, 78.46, 92.07]
    n_acc_a3 = [78.05, 93.09, 98.98]

    b_e0 = ax_rej.bar(x - w_bar, n_acc_e0, w_bar, color="#94a3b8", label="E0 Baseline", edgecolor="#475569", lw=0.8)
    b_ta = ax_rej.bar(x, n_acc_ta, w_bar, color=C_BLUE, label="Task A (Decoupled)", edgecolor=C_NAVY, lw=0.8)
    b_a3 = ax_rej.bar(x + w_bar, n_acc_a3, w_bar, color=C_RED, label="A3 (Hard-Neg Mining)", edgecolor=C_NAVY, lw=0.8)

    # Add numeric labels
    for rects, col in [(b_e0, "#475569"), (b_ta, C_BLUE), (b_a3, C_RED)]:
        for r in rects:
            h = r.get_height()
            ax_rej.text(r.get_x() + r.get_width()/2., h + 1.2, f"{h:.1f}%",
                        ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=col)

    ax_rej.set_title("(b) Negative Sample Rejection Accuracy (N-acc)", loc="left", fontweight="bold", fontsize=9, pad=4)
    ax_rej.set_xticks(x)
    ax_rej.set_xticklabels(gates, fontsize=8)
    ax_rej.set_ylabel("True Negative Rejection Rate (%)")
    ax_rej.set_ylim(0, 110)
    ax_rej.legend(fontsize=7, frameon=False, loc="upper left")
    ax_rej.spines[["top", "right"]].set_visible(False)
    ax_rej.grid(True, linestyle=":", alpha=0.4, color="#94a3b8", axis="y")

    # --------------------------------------------------------------------------
    # PANEL (d): COMPREHENSIVE BENCHMARK COMPARISON (Grouped Bar)
    # --------------------------------------------------------------------------
    metrics = ["Loc mAP", "AUROC", "G-mIoU@0.4", "G-mIoU@0.5", "Rej-F1@0.4", "Plur-BA"]
    x_m = np.arange(len(metrics))
    w_m = 0.26

    # E0, Task A, A3
    m_e0 = [26.14, 74.27, 34.66, 46.19, 54.16, 50.00]  # E0 had no plurality model (chance 50%)
    m_ta = [26.18, 73.19, 42.42, 47.41, 64.28, 65.29]
    m_a3 = [26.18, 75.03, 47.62, 53.39, 70.52, 70.65]

    ax_radar.bar(x_m - w_m, m_e0, w_m, color="#94a3b8", label="E0 Baseline", edgecolor="#475569", lw=0.8)
    ax_radar.bar(x_m, m_ta, w_m, color=C_BLUE, label="Task A", edgecolor=C_NAVY, lw=0.8)
    b_top = ax_radar.bar(x_m + w_m, m_a3, w_m, color=C_GREEN, label="A3 Hard-Negative", edgecolor=C_NAVY, lw=0.8)

    # Highlight A3 gains
    for i, r in enumerate(b_top):
        h = r.get_height()
        gain = h - m_e0[i]
        gain_str = f"+{gain:.1f}" if gain > 0 and i > 0 else ""
        ax_radar.text(r.get_x() + r.get_width()/2., h + 1.2, f"{h:.1f}%",
                      ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=C_GREEN)
        if gain_str:
            ax_radar.text(r.get_x() + r.get_width()/2., h + 6.0, f"({gain_str})",
                          ha="center", va="bottom", fontsize=5.8, color=C_GREEN)

    ax_radar.set_title("(c) Overall Evaluation on Official Test Split (N=1,036)", loc="left", fontweight="bold", fontsize=9, pad=4)
    ax_radar.set_xticks(x_m)
    ax_radar.set_xticklabels(metrics, fontsize=7.5)
    ax_radar.set_ylabel("Metric Score (%)")
    ax_radar.set_ylim(0, 88)
    ax_radar.legend(fontsize=7, frameon=False, loc="upper left")
    ax_radar.spines[["top", "right"]].set_visible(False)
    ax_radar.grid(True, linestyle=":", alpha=0.4, color="#94a3b8", axis="y")

    # Save deliverables
    out_png = Path("figures/fig3_a3_hard_negative.png")
    out_pdf = Path("figures/fig3_a3_hard_negative.pdf")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    # Also update assets/
    fig.savefig("assets/a3_hard_negative_architecture.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_png} and {out_pdf} successfully!")


if __name__ == "__main__":
    generate_figure_3()
