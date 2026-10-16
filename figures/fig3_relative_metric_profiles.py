"""Figure 3: Multi-Metric Radar Profiles & Relative Gain Matrix across Fixed Thresholds (0.4, 0.5, 0.6)
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
    "font.size": 8.0
})

# Academic color palette
C_NAVY = "#0f172a"
C_E0 = "#64748b"         # Slate Grey
C_TASKA = "#2563eb"      # Royal Blue
C_MINNEG = "#dc2626"     # Crimson Red

# Categories for radar: 6 key indicators
categories = ["G-mIoU@1", "G-mIoU@3", "G-mIoU@5", "Rej-F1", "N-acc", "AUROC"]
N_cat = len(categories)
angles = [n / float(N_cat) * 2 * np.pi for n in range(N_cat)]
angles += angles[:1]

# Real data at tau = 0.4
data_04_e0 = [34.66, 28.24, 25.85, 54.16, 46.34, 74.27]
data_04_ta = [42.39, 36.40, 34.42, 64.09, 65.65, 73.19]
data_04_mn = [47.66, 41.77, 40.02, 70.45, 78.25, 75.03]

# Real data at tau = 0.5
data_05_e0 = [46.12, 40.30, 38.52, 68.08, 75.00, 74.27]
data_05_ta = [47.41, 41.72, 40.04, 69.18, 78.46, 73.19]
data_05_mn = [53.39, 47.75, 46.41, 73.75, 93.09, 75.03]

# Real data at tau = 0.6
data_06_e0 = [50.24, 44.51, 42.93, 71.51, 84.96, 74.27]
data_06_ta = [51.54, 45.87, 44.46, 72.53, 88.82, 73.19]
data_06_mn = [55.64, 50.15, 49.01, 75.29, 99.39, 75.03]


def plot_radar(ax, d_e0, d_ta, d_mn, title):
    d_e0_c = d_e0 + d_e0[:1]
    d_ta_c = d_ta + d_ta[:1]
    d_mn_c = d_mn + d_mn[:1]

    ax.plot(angles, d_mn_c, color=C_MINNEG, lw=1.8, marker="o", ms=3.5, label="min neg")
    ax.fill(angles, d_mn_c, color=C_MINNEG, alpha=0.12)

    ax.plot(angles, d_ta_c, color=C_TASKA, lw=1.5, marker="s", ms=3.0, label="Task A")
    ax.fill(angles, d_ta_c, color=C_TASKA, alpha=0.10)

    ax.plot(angles, d_e0_c, color=C_E0, lw=1.3, ls="--", marker="^", ms=3.0, label="E0")
    ax.fill(angles, d_e0_c, color=C_E0, alpha=0.06)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=7.2, fontweight="bold", color=C_NAVY)
    ax.set_ylim(15, 105)
    ax.set_yticks([30, 50, 70, 90])
    ax.set_yticklabels(["30", "50", "70", "90"], fontsize=6, color="#64748b")
    ax.set_title(title, loc="center", fontweight="bold", fontsize=8.5, pad=12)
    ax.grid(True, linestyle=":", alpha=0.5, color="#94a3b8")


def generate_figure_3():
    fig = plt.figure(figsize=(14.2, 5.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    # 4 panels: (a) Radar at 0.4, (b) Radar at 0.5, (c) Radar at 0.6, (d) Delta Heatmap Matrix
    ax_r1 = fig.add_subplot(1, 4, 1, polar=True)
    ax_r2 = fig.add_subplot(1, 4, 2, polar=True)
    ax_r3 = fig.add_subplot(1, 4, 3, polar=True)
    ax_mat = fig.add_axes([0.75, 0.16, 0.23, 0.70])

    plot_radar(ax_r1, data_04_e0, data_04_ta, data_04_mn, r"(a) Multi-Metric Radar ($\tau = 0.4$)")
    plot_radar(ax_r2, data_05_e0, data_05_ta, data_05_mn, r"(b) Multi-Metric Radar ($\tau = 0.5$)")
    plot_radar(ax_r3, data_06_e0, data_06_ta, data_06_mn, r"(c) Multi-Metric Radar ($\tau = 0.6$)")
    ax_r1.legend(loc="upper left", bbox_to_anchor=(-0.15, 1.15), fontsize=6.8, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1")

    # --------------------------------------------------------------------------
    # PANEL (d): Relative Metric Gains Matrix (Delta pp relative to E0)
    # --------------------------------------------------------------------------
    # Metrics: G-mIoU@1, G-mIoU@3, G-mIoU@5, Rej-F1, N-acc
    # Rows: [Task A @ 0.4, min neg @ 0.4, Task A @ 0.5, min neg @ 0.5, Task A @ 0.6, min neg @ 0.6]
    row_labels = [
        r"Task A ($\tau=0.4$)",
        r"min neg ($\tau=0.4$)",
        r"Task A ($\tau=0.5$)",
        r"min neg ($\tau=0.5$)",
        r"Task A ($\tau=0.6$)",
        r"min neg ($\tau=0.6$)"
    ]
    col_labels = ["G-m@1", "G-m@3", "G-m@5", "Rej-F1", "N-acc"]

    delta_matrix = np.array([
        [+7.73,  +8.16,  +8.57,  +9.93, +19.31],
        [+13.00, +13.53, +14.17, +16.29, +31.91],
        [+1.29,  +1.42,  +1.52,  +1.10,  +3.46],
        [+7.27,  +7.45,  +7.89,  +5.67, +18.09],
        [+1.30,  +1.36,  +1.53,  +1.02,  +3.86],
        [+5.40,  +5.64,  +6.08,  +3.78, +14.43]
    ])

    im = ax_mat.imshow(delta_matrix, cmap="Reds", vmin=0, vmax=35, aspect="auto")

    # Annotate numbers in cells
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            val = delta_matrix[i, j]
            txt = f"+{val:.1f}" if val > 0 else f"{val:.1f}"
            c_txt = "white" if val > 16.0 else C_NAVY
            ax_mat.text(j, i, txt, ha="center", va="center", fontsize=7.2, fontweight="bold", color=c_txt)

    ax_mat.set_xticks(range(len(col_labels)))
    ax_mat.set_xticklabels(col_labels, fontsize=7.2, fontweight="bold")
    ax_mat.set_yticks(range(len(row_labels)))
    ax_mat.set_yticklabels(row_labels, fontsize=7.2)
    ax_mat.set_title(r"(d) Relative Gain $\Delta$ Matrix (pp)", loc="center", fontweight="bold", fontsize=8.5, pad=8)

    # Colorbar
    cb = fig.colorbar(im, ax=ax_mat, orientation="horizontal", pad=0.14, shrink=0.85, aspect=18)
    cb.ax.tick_params(labelsize=6.5)
    cb.set_label(r"Gain $\Delta$ over E0 Baseline (pp)", fontsize=7)

    # Output paths
    out_png = Path("figures/fig3_relative_metric_profiles.png")
    out_pdf = Path("figures/fig3_relative_metric_profiles.pdf")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig("assets/fig3_relative_metric_profiles.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_png} and {out_pdf} successfully!")


if __name__ == "__main__":
    generate_figure_3()
