"""Figure 1: G-mIoU Retrieval Trajectories & Relative Performance Evolution across Operating Thresholds
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
C_LIGHT_MINNEG = "#fee2e2"
C_LIGHT_TASKA = "#dbeafe"

# Real evaluation data across thresholds tau in [0.2, 0.8]
taus = np.array([0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8])

# G-mIoU@1 across thresholds
gm1_e0 = np.array([15.36, 16.93, 21.44, 27.84, 34.66, 41.78, 46.12, 48.85, 50.24, 51.19, 52.17, 53.12, 54.07])
gm1_ta = np.array([16.77, 20.90, 27.48, 36.97, 42.39, 45.34, 47.41, 49.84, 51.54, 52.80, 53.51, 53.85, 54.46])
gm1_minneg = np.array([24.08, 28.81, 34.51, 41.36, 47.66, 51.65, 53.39, 54.39, 55.64, 55.69, 55.59, 55.15, 52.56])

# Fixed thresholds: 0.4, 0.5, 0.6
fixed_th = np.array([0.4, 0.5, 0.6])
# Indices in taus: [4, 6, 8]
idx_fixed = [4, 6, 8]

# G-mIoU@3 & @5 at fixed thresholds
gm3_e0 = np.array([28.24, 40.30, 44.51])
gm3_ta = np.array([36.40, 41.72, 45.87])
gm3_minneg = np.array([41.77, 47.75, 50.15])

gm5_e0 = np.array([25.85, 38.52, 42.93])
gm5_ta = np.array([34.42, 40.04, 44.46])
gm5_minneg = np.array([40.02, 46.41, 49.01])


def generate_figure_1():
    fig = plt.figure(figsize=(14.2, 5.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    # Three-panel layout: (a) Absolute Trajectories, (b) Relative Gain (Delta over E0), (c) Fixed Threshold Grouped Bar
    ax_a = fig.add_axes([0.06, 0.15, 0.28, 0.74])
    ax_b = fig.add_axes([0.40, 0.15, 0.26, 0.74])
    ax_c = fig.add_axes([0.72, 0.15, 0.25, 0.74])

    # --------------------------------------------------------------------------
    # PANEL (a): G-mIoU@1 Trajectories across tau in [0.2, 0.8]
    # --------------------------------------------------------------------------
    ax_a.plot(taus, gm1_minneg, color=C_MINNEG, lw=2.2, marker="o", ms=4.5, label="min neg (A3 Hard-Negative)", zorder=4)
    ax_a.plot(taus, gm1_ta, color=C_TASKA, lw=1.8, marker="s", ms=4, label="Task A (Decoupled)", zorder=3)
    ax_a.plot(taus, gm1_e0, color=C_E0, lw=1.6, ls="--", marker="^", ms=4, label="E0 Baseline", zorder=2)

    # Highlight vertical lines for fixed thresholds 0.4, 0.5, 0.6
    for th in fixed_th:
        ax_a.axvline(th, color="#cbd5e1", lw=1.0, ls=":", zorder=1)
        ax_a.text(th, 16.0, f"{th:.1f}", ha="center", va="bottom", fontsize=7.5, color="#64748b", fontweight="bold")

    # Fill area between min neg and E0
    ax_a.fill_between(taus, gm1_e0, gm1_minneg, color=C_LIGHT_MINNEG, alpha=0.45, label="min neg Gain vs E0")

    ax_a.set_title("(a) G-mIoU@1 vs Decision Threshold $\\tau$", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_a.set_xlabel(r"Confidence Decision Threshold $\tau$")
    ax_a.set_ylabel("G-mIoU@1 Score (%)")
    ax_a.set_xlim(0.18, 0.82)
    ax_a.set_ylim(14, 58)
    ax_a.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="upper left")
    ax_a.spines[["top", "right"]].set_visible(False)
    ax_a.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")

    # --------------------------------------------------------------------------
    # PANEL (b): Relative G-mIoU@1 Gain (Delta pp compared to E0 Baseline)
    # --------------------------------------------------------------------------
    delta_ta = gm1_ta - gm1_e0
    delta_minneg = gm1_minneg - gm1_e0

    ax_b.axhline(0, color=C_E0, lw=1.0, ls="--", label="E0 Baseline (0 pp ref)")
    ax_b.plot(taus, delta_minneg, color=C_MINNEG, lw=2.2, marker="o", ms=4.5, label=r"$\Delta$ min neg vs E0", zorder=4)
    ax_b.plot(taus, delta_ta, color=C_TASKA, lw=1.8, marker="s", ms=4, label=r"$\Delta$ Task A vs E0", zorder=3)

    # Annotate gains at 0.4, 0.5, 0.6
    for th, d_mn, d_t in zip(fixed_th, delta_minneg[idx_fixed], delta_ta[idx_fixed]):
        ax_b.plot([th, th], [0, d_mn], color="#cbd5e1", lw=1.0, ls=":", zorder=1)
        ax_b.text(th, d_mn + 0.6, f"+{d_mn:.1f}", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=C_MINNEG)

    ax_b.set_title(r"(b) Relative Gain $\Delta$ G-mIoU@1 over E0", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_b.set_xlabel(r"Confidence Decision Threshold $\tau$")
    ax_b.set_ylabel(r"Relative Gain $\Delta$ (pp)")
    ax_b.set_xlim(0.18, 0.82)
    ax_b.set_ylim(-1, 15)
    ax_b.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="upper right")
    ax_b.spines[["top", "right"]].set_visible(False)
    ax_b.grid(True, linestyle=":", alpha=0.4, color="#94a3b8")

    # --------------------------------------------------------------------------
    # PANEL (c): Grouped Bar Comparison at Fixed Thresholds (0.4, 0.5, 0.6)
    # --------------------------------------------------------------------------
    x = np.arange(len(fixed_th))
    w = 0.25

    b1 = ax_c.bar(x - w, gm1_e0[idx_fixed], w, color=C_E0, label="E0 Baseline", edgecolor="#334155", lw=0.8)
    b2 = ax_c.bar(x, gm1_ta[idx_fixed], w, color=C_TASKA, label="Task A", edgecolor=C_NAVY, lw=0.8)
    b3 = ax_c.bar(x + w, gm1_minneg[idx_fixed], w, color=C_MINNEG, label="min neg", edgecolor=C_NAVY, lw=0.8)

    # Label heights and relative boost
    for rects, col, is_minneg in [(b1, "#334155", False), (b2, C_TASKA, False), (b3, C_MINNEG, True)]:
        for i, r in enumerate(rects):
            h = r.get_height()
            ax_c.text(r.get_x() + r.get_width()/2., h + 0.8, f"{h:.1f}%",
                      ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=col)
            if is_minneg:
                gain = h - gm1_e0[idx_fixed][i]
                ax_c.text(r.get_x() + r.get_width()/2., h + 4.0, f"(+{gain:.1f})",
                          ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=C_MINNEG)

    ax_c.set_title("(c) G-mIoU@1 at $\\tau \\in \\{0.4, 0.5, 0.6\\}$", loc="left", fontweight="bold", fontsize=9.5, pad=6)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels([r"$\tau = 0.4$", r"$\tau = 0.5$", r"$\tau = 0.6$"], fontsize=8.5)
    ax_c.set_ylabel("G-mIoU@1 Score (%)")
    ax_c.set_ylim(0, 68)
    ax_c.legend(fontsize=7.2, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", loc="upper left")
    ax_c.spines[["top", "right"]].set_visible(False)
    ax_c.grid(True, linestyle=":", alpha=0.4, color="#94a3b8", axis="y")

    # Output paths
    Path("figures").mkdir(exist_ok=True)
    Path("assets").mkdir(exist_ok=True)

    out_png = Path("figures/fig1_gmiou_threshold_dynamics.png")
    out_pdf = Path("figures/fig1_gmiou_threshold_dynamics.pdf")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig("assets/fig1_gmiou_threshold_dynamics.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_png} and {out_pdf} successfully!")


if __name__ == "__main__":
    generate_figure_1()
