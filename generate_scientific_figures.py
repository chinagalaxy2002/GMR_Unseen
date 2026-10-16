"""Generate publication-grade scientific research illustrations for:
1. Baseline E0 (End-to-end joint architecture & gradient entanglement bottleneck)
2. Task A (Two-stage decoupled fine-tuning with frozen localizer and text plurality)
3. A3 Enhancement (Batch-wise semantic similarity hard-negative contrastive mining)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set global styles
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'cm'

# Color Palette (Nature / IEEE / Modern CVPR style)
C_NAVY = '#0f172a'
C_DARK_BLUE = '#1e3a8a'
C_BLUE = '#2563eb'
C_LIGHT_BLUE = '#dbeafe'
C_BORDER_BLUE = '#3b82f6'

C_TEAL = '#0d9488'
C_LIGHT_TEAL = '#ccfbf1'
C_BORDER_TEAL = '#14b8a6'

C_PURPLE = '#7c3aed'
C_LIGHT_PURPLE = '#ede9fe'
C_BORDER_PURPLE = '#8b5cf6'

C_GREEN = '#15803d'
C_LIGHT_GREEN = '#dcfce7'
C_BORDER_GREEN = '#22c55e'

C_RED = '#b91c1c'
C_LIGHT_RED = '#fee2e2'
C_BORDER_RED = '#ef4444'

C_AMBER = '#b45309'
C_LIGHT_AMBER = '#fef3c7'
C_BORDER_AMBER = '#f59e0b'

C_GRAY_BG = '#f8fafc'
C_GRAY_BOX = '#f1f5f9'
C_GRAY_BORDER = '#94a3b8'
C_TEXT_DARK = '#1e293b'
C_TEXT_MUTED = '#64748b'


def add_box(ax, x, y, w, h, boxstyle="round,pad=0.02,rounding_size=0.03", 
            facecolor='#ffffff', edgecolor='#94a3b8', linewidth=1.5, zorder=2, alpha=1.0):
    box = FancyBboxPatch((x, y), w, h, boxstyle=boxstyle,
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=linewidth, zorder=zorder, alpha=alpha)
    ax.add_patch(box)
    return box


def add_arrow(ax, p1, p2, color='#64748b', linewidth=2.0, arrowstyle='-|>', 
              mutation_scale=15, linestyle='solid', zorder=3, connectionstyle="arc3,rad=0"):
    arrow = FancyArrowPatch(p1, p2, color=color, linewidth=linewidth,
                            arrowstyle=arrowstyle, mutation_scale=mutation_scale,
                            linestyle=linestyle, zorder=zorder, connectionstyle=connectionstyle)
    ax.add_patch(arrow)
    return arrow


def draw_tensor_stack(ax, x, y, w, h, depth=3, offset=0.015, facecolor='#dbeafe', edgecolor='#2563eb', label=""):
    for i in range(depth - 1, -1, -1):
        ox = x + i * offset
        oy = y + i * offset
        rect = FancyBboxPatch((ox, oy), w, h, boxstyle="round,pad=0.005,rounding_size=0.01",
                              facecolor=facecolor, edgecolor=edgecolor, linewidth=1.2, zorder=2+i)
        ax.add_patch(rect)
    if label:
        ax.text(x + w/2 + (depth-1)*offset/2, y + h/2 + (depth-1)*offset/2, label,
                ha='center', va='center', fontsize=9, fontweight='bold', color=C_TEXT_DARK, zorder=10)


# ==============================================================================
# FIGURE 1: E0 BASELINE ARCHITECTURE & GRADIENT ENTANGLEMENT
# ==============================================================================
def generate_figure_1():
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main Title & Subtitle Banner
    ax.text(0.5, 0.965, "E0 Baseline: End-to-End Joint Architecture & The Gradient Entanglement Bottleneck",
            ha='center', va='center', fontsize=16, fontweight='bold', color=C_NAVY)
    ax.text(0.5, 0.932, "Shared Cross-Modal Temporal Transformer with Entangled Optimization Objectives for Localization and Existence",
            ha='center', va='center', fontsize=11, color=C_TEXT_MUTED)

    # 1. INPUT PANEL (Left)
    add_box(ax, 0.02, 0.12, 0.20, 0.77, facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5)
    ax.text(0.12, 0.86, "Multi-Modal Inputs", ha='center', va='center', fontsize=12, fontweight='bold', color=C_NAVY)

    # Video Feature Tube
    draw_tensor_stack(ax, 0.04, 0.60, 0.16, 0.18, depth=4, offset=0.012, 
                      facecolor=C_LIGHT_BLUE, edgecolor=C_BORDER_BLUE, label="Video Features\n$V \\in \\mathbb{R}^{L_v \\times D_v}$")
    ax.text(0.12, 0.55, "SlowFast (2048d) + CLIP-ViT (512d)\n$L_v = 150$ temporal clips", 
            ha='center', va='center', fontsize=8.5, color=C_TEXT_MUTED)

    # Text Feature Tube
    draw_tensor_stack(ax, 0.04, 0.28, 0.16, 0.18, depth=3, offset=0.012, 
                      facecolor=C_LIGHT_TEAL, edgecolor=C_BORDER_TEAL, label="Text Query\n$T \\in \\mathbb{R}^{L_t \\times D_t}$")
    ax.text(0.12, 0.23, "CLIP-Text Encoder\n$L_t \\leq 30$ tokens (512d)", 
            ha='center', va='center', fontsize=8.5, color=C_TEXT_MUTED)

    # 2. SHARED BACKBONE PANEL (Center)
    add_box(ax, 0.27, 0.12, 0.38, 0.77, facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.5)
    ax.text(0.46, 0.86, "Shared FlashVTG-GMR Backbone (Jointly Trained)", ha='center', va='center', fontsize=12, fontweight='bold', color=C_NAVY)

    # Projections
    add_box(ax, 0.30, 0.65, 0.13, 0.10, facecolor=C_LIGHT_BLUE, edgecolor=C_BORDER_BLUE)
    ax.text(0.365, 0.70, "Video Projection\nLinear $\\mathbb{R}^{D_v \\to 256}$", ha='center', va='center', fontsize=9, fontweight='bold', color=C_NAVY)

    add_box(ax, 0.30, 0.33, 0.13, 0.10, facecolor=C_LIGHT_TEAL, edgecolor=C_BORDER_TEAL)
    ax.text(0.365, 0.38, "Text Projection\nLinear $\\mathbb{R}^{D_t \\to 256}$", ha='center', va='center', fontsize=9, fontweight='bold', color=C_NAVY)

    add_arrow(ax, (0.22, 0.70), (0.30, 0.70), color=C_BORDER_BLUE)
    add_arrow(ax, (0.22, 0.38), (0.30, 0.38), color=C_BORDER_TEAL)

    # Cross-Attention & Transformer Encoder Stack
    add_box(ax, 0.47, 0.28, 0.16, 0.48, boxstyle="round,pad=0.02,rounding_size=0.04", 
            facecolor='#ede9fe', edgecolor=C_BORDER_PURPLE, linewidth=2.0)
    ax.text(0.55, 0.71, "Temporal Cross-Encoder", ha='center', va='center', fontsize=10.5, fontweight='bold', color=C_PURPLE)

    # Sub-blocks inside Transformer
    add_box(ax, 0.49, 0.58, 0.12, 0.08, facecolor='#ffffff', edgecolor=C_PURPLE, linewidth=1.0)
    ax.text(0.55, 0.62, "Cross-Attention\n(Video $\\leftrightarrow$ Text)", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_box(ax, 0.49, 0.46, 0.12, 0.08, facecolor='#ffffff', edgecolor=C_PURPLE, linewidth=1.0)
    ax.text(0.55, 0.50, "Self-Attention\n(Temporal Context)", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_box(ax, 0.49, 0.34, 0.12, 0.08, facecolor='#ffffff', edgecolor=C_PURPLE, linewidth=1.0)
    ax.text(0.55, 0.38, "Feed-Forward\nNorm & Residuals", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_arrow(ax, (0.43, 0.70), (0.47, 0.64), color=C_BORDER_BLUE)
    add_arrow(ax, (0.43, 0.38), (0.47, 0.40), color=C_BORDER_TEAL)

    # 3. TASK HEADS PANEL (Right)
    # 3.1 Localization Branch (Top Right)
    add_box(ax, 0.69, 0.53, 0.29, 0.36, facecolor=C_LIGHT_GREEN, edgecolor=C_BORDER_GREEN, linewidth=1.8)
    ax.text(0.835, 0.85, "Task 1: Positive Localization Head", ha='center', va='center', fontsize=11, fontweight='bold', color=C_GREEN)

    add_box(ax, 0.71, 0.68, 0.25, 0.12, facecolor='#ffffff', edgecolor=C_BORDER_GREEN)
    ax.text(0.835, 0.74, "Span Boundary & Saliency MLP\n$\\hat{s}_i, \\hat{e}_i = \\mathrm{Regressor}(H_i), \\quad q_i = \\mathrm{Score}(H_i)$", 
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_NAVY)

    add_box(ax, 0.71, 0.56, 0.25, 0.09, facecolor='#ffffff', edgecolor=C_BORDER_GREEN)
    ax.text(0.835, 0.605, "Localization Loss: $\\mathcal{L}_{loc} = \\mathcal{L}_{L1} + \\mathcal{L}_{GIoU} + \\mathcal{L}_{sal}$", 
            ha='center', va='center', fontsize=9, fontweight='bold', color=C_GREEN)

    add_arrow(ax, (0.63, 0.62), (0.69, 0.72), color=C_BORDER_PURPLE, linewidth=2.5)

    # 3.2 Existence Branch (Bottom Right)
    add_box(ax, 0.69, 0.12, 0.29, 0.36, facecolor=C_LIGHT_AMBER, edgecolor=C_BORDER_AMBER, linewidth=1.8)
    ax.text(0.835, 0.44, "Task 2: Event Existence Head", ha='center', va='center', fontsize=11, fontweight='bold', color=C_AMBER)

    add_box(ax, 0.71, 0.27, 0.25, 0.12, facecolor='#ffffff', edgecolor=C_BORDER_AMBER)
    ax.text(0.835, 0.33, "Global Temporal Pooling + MLP\n$h_{cls} = \\mathrm{GAP}(H), \\quad \\hat{y}_{exist} = \\mathbf{w}^\\top h_{cls} + b$", 
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_NAVY)

    add_box(ax, 0.71, 0.15, 0.25, 0.09, facecolor='#ffffff', edgecolor=C_BORDER_AMBER)
    ax.text(0.835, 0.195, "Existence Loss: $\\mathcal{L}_{exist} = \\mathrm{BCE}(\\sigma(\\hat{y}_{exist}), y_{exist})$", 
            ha='center', va='center', fontsize=9, fontweight='bold', color=C_AMBER)

    add_arrow(ax, (0.63, 0.40), (0.69, 0.32), color=C_BORDER_PURPLE, linewidth=2.5)

    # 4. CONFLICT OVERLAY CALLOUT (Bottom Center-Right)
    add_arrow(ax, (0.71, 0.58), (0.62, 0.54), color=C_BORDER_RED, linestyle='dashed', linewidth=2.0)
    add_arrow(ax, (0.71, 0.20), (0.62, 0.38), color=C_BORDER_RED, linestyle='dashed', linewidth=2.0)

    # Warning Box
    add_box(ax, 0.29, 0.02, 0.67, 0.08, facecolor=C_LIGHT_RED, edgecolor=C_BORDER_RED, linewidth=1.8)
    ax.text(0.625, 0.06, r"Gradient Entanglement Bottleneck: Backpropagating $\mathcal{L}_{exist}$ gradients distort shared representations," "\n" r"corrupting temporal boundary sharpness required by $\mathcal{L}_{loc}$, causing positive localization precision to degrade!",
            ha='center', va='center', fontsize=9, fontweight='bold', color=C_RED)

    plt.savefig('assets/e0_baseline_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated assets/e0_baseline_architecture.png successfully!")


# ==============================================================================
# FIGURE 2: TASK A TWO-STAGE DECOUPLED FINE-TUNING & PLURALITY
# ==============================================================================
def generate_figure_2():
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main Title & Subtitle Banner
    ax.text(0.5, 0.965, "Task A: Two-Stage Decoupled Fine-Tuning with Frozen Localizer & Text Plurality",
            ha='center', va='center', fontsize=16, fontweight='bold', color=C_NAVY)
    ax.text(0.5, 0.932, "Freeze E0 Backbone to Guarantee Zero Localization Degradation + Decoupled Event Head & Text Plurality Supervision",
            ha='center', va='center', fontsize=11, color=C_TEXT_MUTED)

    # STAGE 1: FROZEN LOCALIZER (Left Half)
    add_box(ax, 0.02, 0.12, 0.38, 0.77, facecolor='#f1f5f9', edgecolor=C_GRAY_BORDER, linewidth=2.0)
    # Frozen Badge
    add_box(ax, 0.04, 0.82, 0.34, 0.055, facecolor='#e2e8f0', edgecolor='#64748b', linewidth=1.2)
    ax.text(0.21, 0.847, "STAGE 1: E0 Localizer (100% FROZEN, requires_grad=False)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#334155')

    # Video & Text Inputs
    draw_tensor_stack(ax, 0.04, 0.60, 0.11, 0.16, depth=3, offset=0.008, 
                      facecolor=C_LIGHT_BLUE, edgecolor=C_BORDER_BLUE, label="Video $V$")
    draw_tensor_stack(ax, 0.04, 0.36, 0.11, 0.16, depth=3, offset=0.008, 
                      facecolor=C_LIGHT_TEAL, edgecolor=C_BORDER_TEAL, label="Query $T$")

    # Frozen Transformer Block
    add_box(ax, 0.19, 0.36, 0.19, 0.40, facecolor='#e2e8f0', edgecolor='#64748b', linewidth=1.5)
    ax.text(0.285, 0.71, "Frozen Transformer\n& Cross-Attention", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1e293b')
    ax.text(0.285, 0.62, "Weights locked at\nconverged E0 checkpoint", ha='center', va='center', fontsize=8, color=C_TEXT_MUTED)

    add_arrow(ax, (0.155, 0.68), (0.19, 0.68), color=C_BORDER_BLUE)
    add_arrow(ax, (0.155, 0.44), (0.19, 0.44), color=C_BORDER_TEAL)

    # Locked Candidate Box
    add_box(ax, 0.20, 0.15, 0.18, 0.16, facecolor=C_LIGHT_GREEN, edgecolor=C_BORDER_GREEN, linewidth=1.5)
    ax.text(0.29, 0.25, "[Preserved] Localization Candidates", ha='center', va='center', fontsize=9, fontweight='bold', color=C_GREEN)
    ax.text(0.29, 0.19, r"Invariant Fingerprint:" "\n" r"$mAP = 26.18\%$ (Zero Drift)", ha='center', va='center', fontsize=8.5, color=C_NAVY)
    add_arrow(ax, (0.285, 0.36), (0.285, 0.31), color=C_GREEN, linewidth=2.0)

    # GRADIENT BARRIER (Center)
    add_box(ax, 0.42, 0.28, 0.07, 0.50, boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor='#f3e8ff', edgecolor=C_BORDER_PURPLE, linewidth=2.0)
    ax.text(0.455, 0.72, "[STOP GRAD]\nGradient\nBarrier", ha='center', va='center', fontsize=8.5, fontweight='bold', color=C_PURPLE)
    ax.text(0.455, 0.48, r"$\mathrm{detach}(\cdot)$" "\n\n" r"$\partial \mathcal{L} / \partial \theta_{loc} = 0$", 
            ha='center', va='center', fontsize=9, fontweight='bold', color=C_PURPLE)

    add_arrow(ax, (0.38, 0.58), (0.42, 0.58), color=C_BORDER_PURPLE, linewidth=2.5)

    # STAGE 2: DECOUPLED EVENT HEAD & PLURALITY (Right Half)
    add_box(ax, 0.51, 0.12, 0.47, 0.77, facecolor='#fffbeb', edgecolor=C_BORDER_AMBER, linewidth=2.0)
    # Trainable Badge
    add_box(ax, 0.53, 0.82, 0.43, 0.055, facecolor='#fef3c7', edgecolor=C_AMBER, linewidth=1.2)
    ax.text(0.745, 0.847, "STAGE 2: Decoupled Multi-Task Adaptation (Active Tuning)", 
            ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_AMBER)

    # 2.1 Decoupled Event Query Head
    add_box(ax, 0.53, 0.48, 0.25, 0.31, facecolor='#ffffff', edgecolor=C_BORDER_AMBER, linewidth=1.5)
    ax.text(0.655, 0.75, "Decoupled Event Head", ha='center', va='center', fontsize=10, fontweight='bold', color=C_NAVY)
    ax.text(0.655, 0.69, "Multi-level Evidence Cross-Attention\n$Q_{evt} \\leftrightarrow \\mathrm{detach}(H_{vid})$", 
            ha='center', va='center', fontsize=8.5, color=C_TEXT_MUTED)

    add_box(ax, 0.54, 0.50, 0.23, 0.13, facecolor=C_LIGHT_AMBER, edgecolor=C_BORDER_AMBER)
    ax.text(0.655, 0.58, "Existence Logit: $\\hat{y}_{exist}$", ha='center', va='center', fontsize=9, fontweight='bold', color=C_AMBER)
    ax.text(0.655, 0.53, "$\\mathcal{L}_{exist} = \\mathrm{BCE}(\\sigma(\\hat{y}_{exist}), y_{exist})$", 
            ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_arrow(ax, (0.49, 0.58), (0.53, 0.65), color=C_BORDER_AMBER, linewidth=2.0)

    # 2.2 Text Plurality Classifier Head
    add_box(ax, 0.53, 0.15, 0.25, 0.30, facecolor='#ffffff', edgecolor='#0284c7', linewidth=1.5)
    ax.text(0.655, 0.41, "Text Plurality Modeling", ha='center', va='center', fontsize=10, fontweight='bold', color='#0284c7')
    ax.text(0.655, 0.35, "Kim-style Plurality Classifier on $e_0$\n$p_{multi} = \\mathrm{Softmax}(\\mathrm{MLP}(e_0))$", 
            ha='center', va='center', fontsize=8.5, color=C_TEXT_MUTED)

    add_box(ax, 0.54, 0.17, 0.23, 0.13, facecolor='#e0f2fe', edgecolor='#0284c7')
    ax.text(0.655, 0.25, "Plurality AUROC: 83.51%", ha='center', va='center', fontsize=9, fontweight='bold', color='#0284c7')
    ax.text(0.655, 0.20, "$\\mathcal{L}_{multi} = \\mathrm{CE}(p_{multi}, y_{multi})$", 
            ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_arrow(ax, (0.155, 0.40), (0.53, 0.30), color='#0284c7', linewidth=1.5, connectionstyle="arc3,rad=-0.2")

    # 2.3 Joint Inference & Gating (Far Right)
    add_box(ax, 0.80, 0.24, 0.16, 0.45, boxstyle="round,pad=0.015,rounding_size=0.03", 
            facecolor='#f0fdf4', edgecolor=C_BORDER_GREEN, linewidth=2.0)
    ax.text(0.88, 0.64, "Inference Gating\n& Rejection", ha='center', va='center', fontsize=10, fontweight='bold', color=C_GREEN)
    ax.text(0.88, 0.52, "Gate: $P(exist) \\geq 0.4$\n\nIf $P < 0.4 \\to \\emptyset$\n(Reject true negatives)\n\nIf $P \\geq 0.4 \\to$ Retain\nLocked Window", 
            ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_box(ax, 0.81, 0.26, 0.14, 0.12, facecolor=C_LIGHT_GREEN, edgecolor=C_BORDER_GREEN)
    ax.text(0.88, 0.34, "G-mIoU@0.4", ha='center', va='center', fontsize=8.5, color=C_NAVY)
    ax.text(0.88, 0.29, "42.42%", ha='center', va='center', fontsize=12, fontweight='bold', color=C_GREEN)
    ax.text(0.88, 0.26, "(+7.76 pp vs E0)", ha='center', va='center', fontsize=8, color=C_GREEN)

    add_arrow(ax, (0.77, 0.58), (0.80, 0.55), color=C_BORDER_AMBER, linewidth=2.0)
    add_arrow(ax, (0.38, 0.22), (0.80, 0.42), color=C_BORDER_GREEN, linewidth=2.0, connectionstyle="arc3,rad=-0.15")

    # Bottom summary tag
    ax.text(0.5, 0.05, "Key Property: Decoupled design guarantees zero localization degradation while unlocking +7.76 pp higher rejection performance.",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1e3a8a')

    plt.savefig('assets/task_a_twostage_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated assets/task_a_twostage_architecture.png successfully!")


# ==============================================================================
# FIGURE 3: A3 HARD-NEGATIVE CONTRASTIVE MINING ARCHITECTURE
# ==============================================================================
def generate_figure_3():
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main Title & Subtitle Banner
    ax.text(0.5, 0.965, "A3 Enhancement: Batch-wise Semantic Similarity Hard-Negative Contrastive Mining",
            ha='center', va='center', fontsize=16, fontweight='bold', color=C_NAVY)
    ax.text(0.5, 0.932, "Mining Closest In-Batch Semantic Distractors to Suppress False-Positive Fallacies and Elevate Rejection Boundaries",
            ha='center', va='center', fontsize=11, color=C_TEXT_MUTED)

    # 1. BATCH INPUTS (Far Left)
    add_box(ax, 0.02, 0.12, 0.19, 0.77, facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5)
    ax.text(0.115, 0.86, "Mini-Batch $(B=8)$", ha='center', va='center', fontsize=11, fontweight='bold', color=C_NAVY)

    # Stack of batch pairs
    for b in range(4):
        yo = 0.68 - b * 0.14
        add_box(ax, 0.035, yo, 0.16, 0.11, facecolor='#ffffff', edgecolor='#94a3b8')
        ax.text(0.115, yo + 0.07, f"Pair {b+1}: $(V_{b+1}, T_{b+1})$", ha='center', va='center', fontsize=9, fontweight='bold', color=C_NAVY)
        if b == 0:
            ax.text(0.115, yo + 0.03, '"Free kick near penalty box"', ha='center', va='center', fontsize=7.5, color=C_BLUE)
        elif b == 1:
            ax.text(0.115, yo + 0.03, '"Direct corner kick to box"', ha='center', va='center', fontsize=7.5, color=C_RED)
        elif b == 2:
            ax.text(0.115, yo + 0.03, '"Header on target by striker"', ha='center', va='center', fontsize=7.5, color=C_TEXT_MUTED)
        else:
            ax.text(0.115, yo + 0.03, '"...", "... (Soccer Queries)"', ha='center', va='center', fontsize=7.5, color=C_TEXT_MUTED)

    # 2. HARD NEGATIVE MINING ENGINE (Center Left)
    add_box(ax, 0.23, 0.12, 0.32, 0.77, facecolor='#faf5ff', edgecolor=C_BORDER_PURPLE, linewidth=1.8)
    ax.text(0.39, 0.86, "Semantic Hard Negative Mining", ha='center', va='center', fontsize=11, fontweight='bold', color=C_PURPLE)

    # Text L2 Normalization
    add_box(ax, 0.25, 0.70, 0.28, 0.11, facecolor='#ffffff', edgecolor=C_BORDER_PURPLE)
    ax.text(0.39, 0.77, "L2-Normalized Query Embeddings", ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.text(0.39, 0.73, "$\\hat{T}_i = \\mathrm{Normalize}(\\mathrm{Pool}(T_i)) \\in \\mathbb{R}^{256}$", ha='center', va='center', fontsize=8.5, color=C_PURPLE)

    add_arrow(ax, (0.195, 0.73), (0.25, 0.73), color=C_BORDER_PURPLE)

    # Similarity Matrix Heatmap Representation
    add_box(ax, 0.25, 0.38, 0.28, 0.29, facecolor='#ffffff', edgecolor=C_BORDER_PURPLE)
    ax.text(0.39, 0.63, "Batch-wise Similarity Matrix", ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_NAVY)
    ax.text(0.39, 0.58, "$S_{ij} = \\hat{T}_i^\\top \\hat{T}_j, \\quad S_{ii} = -\\infty$", ha='center', va='center', fontsize=9, fontweight='bold', color=C_PURPLE)

    # Visual mini-grid of heatmap
    for r in range(3):
        for c in range(3):
            val_col = '#cbd5e1' if r == c else ('#fda4af' if (r==0 and c==1) else '#f3e8ff')
            txt = "$-\\infty$" if r == c else ("0.91" if (r==0 and c==1) else f"0.{45+r*12+c*8}")
            add_box(ax, 0.29 + c*0.065, 0.49 - r*0.045, 0.06, 0.04, facecolor=val_col, edgecolor='#a855f7', linewidth=0.8)
            ax.text(0.32 + c*0.065, 0.51 - r*0.045, txt, ha='center', va='center', fontsize=7.5, color=C_NAVY)

    # Argmax Selection Box
    add_box(ax, 0.25, 0.16, 0.28, 0.18, facecolor=C_LIGHT_RED, edgecolor=C_BORDER_RED, linewidth=1.5)
    ax.text(0.39, 0.29, "Hardest Negative Selection", ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_RED)
    ax.text(0.39, 0.24, "$j^* = \\mathrm{argmax}_{j \\neq i} S_{ij}$", ha='center', va='center', fontsize=11, fontweight='bold', color=C_RED)
    ax.text(0.39, 0.19, "Pair $(V_1, T_2)$: Video 1 vs 'Direct corner kick'", ha='center', va='center', fontsize=8, color=C_NAVY)

    add_arrow(ax, (0.39, 0.38), (0.39, 0.34), color=C_BORDER_RED, linewidth=2.0)

    # 3. DUAL CONTRASTIVE FORWARD PATHS (Right)
    add_box(ax, 0.57, 0.12, 0.41, 0.77, facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.8)
    ax.text(0.775, 0.86, "Dual Contrastive Paths & Supervision", ha='center', va='center', fontsize=11, fontweight='bold', color=C_NAVY)

    # 3.1 Path 1: Positive Grounding Forward
    add_box(ax, 0.59, 0.52, 0.37, 0.30, facecolor=C_LIGHT_GREEN, edgecolor=C_BORDER_GREEN, linewidth=1.5)
    ax.text(0.775, 0.78, "Path A: Standard Positive Grounding", ha='center', va='center', fontsize=10, fontweight='bold', color=C_GREEN)
    ax.text(0.775, 0.72, "Input: Matched Video & Query $(V_i, T_i)$", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_box(ax, 0.61, 0.55, 0.33, 0.12, facecolor='#ffffff', edgecolor=C_BORDER_GREEN)
    ax.text(0.775, 0.63, "Positive Existence Loss ($\\mathcal{L}_{exist}$)", ha='center', va='center', fontsize=9, fontweight='bold', color=C_GREEN)
    ax.text(0.775, 0.58, "$\\mathcal{L}_{exist} = \\mathrm{BCE}(\\sigma(\\hat{y}_i^+), 1.0) \\to$ Pull towards 1.0", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_arrow(ax, (0.195, 0.70), (0.59, 0.70), color=C_BORDER_GREEN, linewidth=2.0)

    # 3.2 Path 2: Hard-Negative Contrastive Forward
    add_box(ax, 0.59, 0.16, 0.37, 0.32, facecolor=C_LIGHT_RED, edgecolor=C_BORDER_RED, linewidth=1.5)
    ax.text(0.775, 0.44, "Path B: Hard-Negative Contrastive Grounding", ha='center', va='center', fontsize=10, fontweight='bold', color=C_RED)
    ax.text(0.775, 0.38, "Input: Video $V_i$ with Hard Distractor $T_{j^*}$", ha='center', va='center', fontsize=8.5, color=C_NAVY)

    add_box(ax, 0.61, 0.19, 0.33, 0.15, facecolor='#ffffff', edgecolor=C_BORDER_RED)
    ax.text(0.775, 0.29, "Hard Negative Penalty Loss ($\\mathcal{L}_{hard}$)", ha='center', va='center', fontsize=9, fontweight='bold', color=C_RED)
    ax.text(0.775, 0.24, "$\\mathcal{L}_{hard} = \\mathrm{BCE}(\\sigma(\\hat{y}_i^-), 0.0) \\to$ Push towards 0.0", ha='center', va='center', fontsize=8.5, color=C_RED)
    ax.text(0.775, 0.21, "Loss Weight $\\lambda_{hard} = 0.5$", ha='center', va='center', fontsize=8, color=C_TEXT_MUTED)

    add_arrow(ax, (0.53, 0.24), (0.59, 0.24), color=C_BORDER_RED, linewidth=2.0)

    # Bottom Objective Banner
    add_box(ax, 0.23, 0.02, 0.75, 0.08, facecolor=C_LIGHT_AMBER, edgecolor=C_BORDER_AMBER, linewidth=1.5)
    ax.text(0.605, 0.06, r"Total Objective: $\mathcal{L}_{total} = \mathcal{L}_{exist} + 0.1 \mathcal{L}_{multi} + 0.5 \mathcal{L}_{hard}$  $\rightarrow$ Test AUROC: 75.03% | G-mIoU@0.4: 47.62% (+12.96 pp) | N-acc: 93.09%",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color=C_NAVY)

    plt.savefig('assets/a3_hard_negative_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated assets/a3_hard_negative_architecture.png successfully!")


if __name__ == '__main__':
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
