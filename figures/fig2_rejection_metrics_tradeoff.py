"""Figure 2: Rejection Dynamics & Negative Recall (N-acc) Escalation across Fixed Thresholds
Evaluated on Official Test Split (N=1,036: 544 Positives + 492 Negatives)
Comparing:
1. E0 Baseline
2. Task A (Two-Stage Decoupled Fine-Tuning)
3. min neg (A3 Similarity Hard-Negative Contrastive Mining)
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Plot-is-all-you-need aesthetic styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "mathtext.fontset": "cm",
    "pdf.fonttype": 42,
    "axes.linewidth": 1.0,
    "font.size": 8.5
})

# Academic color palette
C_NAVY = "#0f172a"
C_E0 = "#64748b"         # Slate Grey for Baseline
C_TASKA = "#2563eb"      # Vibrant Royal Blue for Task A
C_MINNEG = "#dc2626"     # Crimson Red for min neg (A3)
C_GREEN = "#16a34a"      # Forest Green
C_LIGHT_MINNEG = "#fee2e2"

# Real evaluation data across thresholds tau in [0.2, 0.8]
taus = np.array([0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8])

# N-acc (Rej-R, % of true negatives successfully rejected)
nacc_e0 = np.array([1.42, 4.88, 14.84, 29.88, 46.34, 63.82, 75.00, 81.71, 84.96, 87.80, 90.45, 92.68, 95.53])
nacc_ta = np.array([4.47, 14.02, 29.88, 52.64, 65.65, 72.97, 78.46, 84.35, 88.82, 91.67, 93.70, 94.92, 96.95])
nacc_minneg = np.array([21.14, 32.72, 46.75, 63.41, 78.25, 88.41, 93.09, 96.54, 99.39, 100.0, 100.0, 100.0, 100.0])

# Pos-Recall (% of true positives retained)
posrec_e0 = np.array([96.14, 93.93, 89.34, 84.01, 77.57, 68.38, 59.01, 55.33, 52.39, 49.08, 47.06, 45.40, 44.49])
posrec_ta = np.array([88.97, 83.46, 76.84, 69.85, 64.52, 60.11, 56.25, 52.39, 49.26, 46.69, 44.49, 42.83, 40.81])
posrec_minneg = np.array([84.01, 78.12, 72.43, 66.73, 60.29, 53.31, 46.32, 43.75, 41.54, 39.89, 38.60, 36.95, 33.64])

# Rej-F1
rejf1_e0 = np.array([2.79, 9.21, 24.83, 41.76, 54.16, 63.69, 68.08, 70.53, 71.51, 71.88, 72.83, 73.61, 74.31])
rejf1_ta = np.array([8.48, 23.55, 41.00, 57.11, 64.09, 67.17, 69.18, 71.24, 72.53, 73.63, 73.82, 73.78, 74.07])
rejf1_minneg = np.array([32.86, 44.23, 54.50, 63.87, 70.45, 73.05, 73.75, 74.28, 75.29, 75.00, 74.89, 74.38, 70.94])

# Fixed threshold indices [4, 6, 8]
idx_fixed = [4, 6, 8]
fixed_th = [0.4, 0.5, 0.6]


def generate_figure_2():
    fig = plt.figure(figsize=(14.2, 5.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    # Three panels: (a) N-acc vs Pos-Recall Tradeoff Frontier, (b) Rej-F1 Curves, (c) Relative Rejection Gains Delta
    ax_a = fig.add_axes([0.06, 0.15, 0.28, 0.74])
    ax_b = fig.add_axes([0.40, 0.15, 0.26, 0.74])
    ax_c = fig.add_axes([0.72, 0.15, 0.25, 0.74])

    # --------------------------------------------------------------------------
    # PANEL (a): N-acc vs Pos-Recall Tradeoff Frontier
    # --------------------------------------------------------------------------
    ax_a.plot(nacc_minneg, posrec_minneg, color=C_MINNEG, lw=2.2, marker="o", ms=4.5, label="min neg (A3)", zorder=4)
    ax_a.plot(nacc_ta, posrec_ta, color=C_TASKA, lw=1.8, marker="s", ms=4, label="Task A", zorder=3)
    ax_a.plot(nacc_e0, posrec_e0, color=C_E0, lw=1.6, ls="--", marker="^", ms=4, label="E0 Baseline", zorder=2)

    # Highlight operating points at 0.4, 0.5, 0.6
    for i in idx_fixed:
        # min neg annotations
        ax_a.scatter(nacc_minneg[i], posrec_minneg[i], s=55, color=C_MINNEG, edgecolor="#ffffff", lw=1.2, zorder=5)
        ax_a.text(nacc_minneg[i] - 1.5, posrec_minneg[i] + 2.0, f"$\\tau={taus[i]:.1f}$",
                  ha="right", va="bottom", fontsize=7.2, fontweight="bold", color=C_MINNEG)

    ax_a.set_title("(a) N-acc vs Pos-Recall Pareto Frontier", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_a.set_xlabel("Negative Rejection Rate N-acc (%)")
    ax_a.set_ylabel("Positive Event Recall (%)")
    ax_a.set_xlim(-2, 105)
    ax_a.set_ylim(30, 102)
    ax_a.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="lower left")
    ax_a.spines[["top", "right"]].set_visible(False)
    ax_a.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")

    # --------------------------------------------------------------------------
    # PANEL (b): Rejection F1 Score across tau in [0.2, 0.8]
    # --------------------------------------------------------------------------
    ax_b.plot(taus, rejf1_minneg, color=C_MINNEG, lw=2.2, marker="o", ms=4.5, label="min neg (A3)", zorder=4)
    ax_b.plot(taus, rejf1_ta, color=C_TASKA, lw=1.8, marker="s", ms=4, label="Task A", zorder=3)
    ax_b.plot(taus, rejf1_e0, color=C_E0, lw=1.6, ls="--", marker="^", ms=4, label="E0 Baseline", zorder=2)

    for th in fixed_th:
        ax_b.axvline(th, color="#cbd5e1", lw=1.0, ls=":", zorder=1)

    ax_b.fill_between(taus, rejf1_e0, rejf1_minneg, color=C_LIGHT_MINNEG, alpha=0.45, label="min neg Gain vs E0")

    ax_b.set_title(r"(b) Rejection F1 (Rej-F1) vs $\tau$", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_b.set_xlabel(r"Confidence Decision Threshold $\tau$")
    ax_b.set_ylabel("Rej-F1 Score (%)")
    ax_b.set_xlim(0.18, 0.82)
    ax_b.set_ylim(0, 80)
    ax_b.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="lower right")
    ax_b.spines[["top", "right"]].set_visible(False)
    ax_b.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")

    # --------------------------------------------------------------------------
    # PANEL (c): Relative Rejection Gains at Fixed Thresholds (0.4, 0.5, 0.6)
    # --------------------------------------------------------------------------
    x = np.arange(len(fixed_th))
    w = 0.35

    delta_nacc_ta = nacc_ta[idx_fixed] - nacc_e0[idx_fixed]
    delta_nacc_minneg = nacc_minneg[idx_fixed] - nacc_e0[idx_fixed]

    b1 = ax_c.bar(x - w/2, delta_nacc_ta, w, color=C_TASKA, label=r"$\Delta$ N-acc (Task A)", edgecolor=C_NAVY, lw=0.8)
    b2 = ax_c.bar(x + w/2, delta_nacc_minneg, w, color=C_MINNEG, label=r"$\Delta$ N-acc (min neg)", edgecolor=C_NAVY, lw=0.8)

    for r in b1:
        h = r.get_height()
        ax_c.text(r.get_x() + r.get_width()/2., h + 0.8, f"+{h:.1f}", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=C_TASKA)
    for r in b2:
        h = r.get_height()
        ax_c.text(r.get_x() + r.get_width()/2., h + 0.8, f"+{h:.1f}", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=C_MINNEG)

    ax_c.set_title(r"(c) Relative N-acc Gain $\Delta$ over E0", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels([r"$\tau = 0.4$", r"$\tau = 0.5$", r"$\tau = 0.6$"], fontsize=8.5)
    ax_c.set_ylabel(r"N-acc Improvement $\Delta$ (pp)")
    ax_c.set_ylim(0, 38)
    ax_c.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="upper right")
    ax_c.spines[["top", "right"]].set_visible(False)
    ax_c.grid(True, linestyle=":", alpha=0.4, color="#94a3b8", axis="y")

    # Output paths
    out_png = Path("figures/fig2_rejection_metrics_tradeoff.png")
    out_pdf = Path("figures/fig2_rejection_metrics_tradeoff.pdf")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig("assets/fig2_rejection_metrics_tradeoff.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_png} and {out_pdf} successfully!")


if __name__ == "__main__":
    generate_figure_2()
