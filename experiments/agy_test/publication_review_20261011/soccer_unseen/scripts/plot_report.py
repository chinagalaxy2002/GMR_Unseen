#!/usr/bin/env python3
"""Redraw Soccer report figures from frozen machine-readable metrics."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs/reports/soccer_unseen_baselines_20261011'
OUTPUT = ROOT / 'assets/soccer_gmr_unseen_v1'
GROUPS = tuple(f'{g}_soccer' for g in ('A1', 'A2', 'A3', 'C1', 'C2'))
BACKBONES = ('moment', 'qd', 'flash')
NAMES = ('Moment-DETR', 'QD-DETR', 'FlashVTG')
COLORS = ('#0072B2', '#D55E00', '#009E73')
MARKERS = ('o', 's', '^')
METRICS = ('AUROC', 'Rej-F1', 'G-mIoU@1')
families = ['DejaVu Sans']
for path in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
             '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'):
    if Path(path).exists():
        font_manager.fontManager.addfont(path)
        family = font_manager.FontProperties(fname=path).get_name()
        if family not in families:
            families.append(family)
plt.rcParams.update({'font.family': families,
    'font.size': 11, 'axes.labelsize': 11, 'axes.titlesize': 12, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
    'axes.spines.top': False, 'axes.spines.right': False})


def read(name):
    return json.loads((REPORT / name).read_text())


def save(fig, name):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for ext in ('svg', 'pdf', 'png'):
        fig.savefig(OUTPUT / f'{name}.{ext}', bbox_inches='tight', facecolor='white', dpi=180)
    plt.close(fig)


def performance(rows):
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.7))
    for ax, title in zip(axes, METRICS):
        selected = [next(r for r in rows if r['split'] == 'MACRO' and r['backbone'] == b and r['metric'] == title) for b in BACKBONES]
        for offset, prefix, color, hatch in ((-.18, 'seen', '#0072B2', ''), (.18, 'unseen', '#E69F00', '//')):
            values = np.array([r[prefix] for r in selected])
            lo = np.array([r[prefix + '_ci_low'] for r in selected])
            hi = np.array([r[prefix + '_ci_high'] for r in selected])
            x = np.arange(3) + offset
            ax.bar(x, values, .33, color=color, hatch=hatch, edgecolor='white', label=prefix.capitalize())
            ax.errorbar(x, values, yerr=[values - lo, hi - values], fmt='none', ecolor='#333333', capsize=3, lw=1)
            for xx, value, top in zip(x, values, hi):
                ax.text(xx, top + (.018 if title == 'AUROC' else 2), f'{value:.3f}' if title == 'AUROC' else f'{value:.1f}', ha='center', fontsize=10)
        ax.set(xticks=range(3), xticklabels=NAMES, ylim=(0, 1 if title == 'AUROC' else 100), title=title,
               ylabel='Score (0–1)' if title == 'AUROC' else 'Score (%)')
        ax.tick_params(axis='x', rotation=15, labelsize=10)
        ax.grid(axis='y', alpha=.18)
        ax.set_axisbelow(True)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=10, ncol=2, loc='upper center', bbox_to_anchor=(.5, .93))
    fig.suptitle('Soccer: AUROC decreases on Unseen semantics', fontsize=14)
    fig.text(.5, .015, 'Five-split equal-weight macro; 95% video-clip bootstrap CI (2,000 draws, seed 3407).\nFrozen Seen-validation checkpoint and threshold; F1 / G-mIoU depend on class proportions.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .11, 1, .87))
    save(fig, 'macro_performance')


def gaps(rows):
    fig, axes = plt.subplots(1, 3, figsize=(12, 8.5), sharey=True)
    pairs = [(g, b) for g in GROUPS + ('MACRO',) for b in BACKBONES]
    labels = [g.replace('_soccer', '') + ' / ' + NAMES[BACKBONES.index(b)] for g, b in pairs]
    for ax, title in zip(axes, METRICS):
        for i, (g, b) in enumerate(pairs):
            r = next(r for r in rows if r['split'] == g and r['backbone'] == b and r['metric'] == title)
            ax.errorbar(r['gap_pp'], i, xerr=[[r['gap_pp'] - r['gap_pp_ci_low']], [r['gap_pp_ci_high'] - r['gap_pp']]],
                marker=MARKERS[BACKBONES.index(b)], color=COLORS[BACKBONES.index(b)], lw=1.3, capsize=3)
        ax.axvline(0, color='#555555', ls='--', lw=1)
        for y in (2.5, 5.5, 8.5, 11.5, 14.5):
            ax.axhline(y, color='#dddddd', lw=.7)
        ax.set(title=title, xlabel='Seen − Unseen (pp)', xlim=(-30, 38), yticks=range(len(labels)))
        ax.grid(axis='x', alpha=.18)
    axes[0].set_yticklabels(labels, fontsize=11)
    axes[0].invert_yaxis()
    fig.suptitle('Soccer: ranking gaps and rejection-weighted gaps differ', fontsize=14)
    fig.text(.5, .012, 'Positive: Unseen lower; negative: Unseen higher. All five splits completed.\n95% paired video-clip bootstrap CI; 2,000 draws; F1 / G-mIoU depend on class proportions.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .07, 1, .95))
    save(fig, 'degradation_by_split')


def composition():
    counts = read('EXPERIMENT_DATA_COUNTS.json')
    fig, ax = plt.subplots(figsize=(8.3, 4.7))
    left = np.zeros(5)
    for part, color, hatch in zip(('S+', 'S-', 'U+', 'U-'), ('#0072B2', '#56B4E9', '#D55E00', '#E69F00'), ('', '//', '', '//')):
        values = np.array([counts[g]['counts']['test'][part] for g in GROUPS])
        ax.barh(range(5), values, left=left, color=color, hatch=hatch, edgecolor='white', label=part.replace('-', '−'))
        for y, start, n in zip(range(5), left, values):
            ax.text(start + n / 2, y, str(n), ha='center', va='center', fontsize=10, color='white' if part in ('S+', 'U+') else 'black')
        left += values
    ax.set(yticks=range(5), yticklabels=[g.replace('_soccer', '') for g in GROUPS], xlabel='Video–query pairs',
           xlim=(0, 2233), title='Soccer: actual Test has 936 positive and 1,297 negative queries')
    ax.invert_yaxis()
    ax.legend(ncol=4, frameon=False, loc='upper center', bbox_to_anchor=(.5, -.16))
    fig.text(.5, .01, 'S / U = Seen / Unseen; + / − = present / source-labeled absent.\n2,233 shared Test qids per split; 13 excluded for missing video features.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .09, 1, 1))
    save(fig, 'dataset_composition')


def frr():
    records = read('degradation_metrics.json')
    absolute = read('bootstrap.json')
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for i, bb in enumerate(BACKBONES):
        values = np.array([next(r for r in records if r['split'] == g and r['backbone'] == bb)['u_frr'] for g in GROUPS])
        limits = np.array([absolute[g + '|' + bb]['u_frr'] for g in GROUPS])
        x = np.arange(5) + (i - 1) * .24
        ax.bar(x, values, .23, color=COLORS[i], hatch=('', '//', '..')[i], label=NAMES[i])
        ax.errorbar(x, values, yerr=[values - limits[:, 0], limits[:, 1] - values], fmt='none', color='#333333', capsize=2, lw=1)
        for xx, value, top in zip(x, values, limits[:, 1]):
            ax.text(xx, top + 1.5, f'{value:.1f}', ha='center', fontsize=10)
    ax.set(xticks=range(5), xticklabels=[g.replace('_soccer', '') for g in GROUPS], ylim=(0, 115), yticks=range(0, 101, 20),
           ylabel='U+ false rejection rate (%)', title='Soccer: QD rejects 72 of 73 Unseen positive queries in C2')
    ax.legend(ncol=3, frameon=False, loc='upper left', bbox_to_anchor=(0, 1.02), fontsize=10)
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)
    fig.text(.5, .015, '95% video-clip bootstrap CI; 2,000 draws; seed 3407.\nHigh rejection-weighted scores must be read alongside positive false rejections.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .10, 1, 1))
    save(fig, 'unseen_false_rejection')


def pipeline():
    fig, ax = plt.subplots(figsize=(11.5, 2.6))
    ax.set(xlim=(0, 11.5), ylim=(0, 2.5))
    ax.axis('off')
    nodes = [('已有足球标注', '仅 WorldCup 2022\n沿用正负标签与时间窗'),
             ('剔除异常', '去掉冲突、重复、越界\n保留 18,005 条'),
             ('五组 Unseen 语义', 'A：动作 / C：动作×球队\n训练仅保留 Seen'),
             ('统一特征与输入', 'CLIP + SlowFast\n排除失败的 37 条查询'),
             ('训练与评测', 'Seen Val 冻结选择\nTest 分测 Seen / Unseen')]
    for i, (title, body) in enumerate(nodes):
        x = .1 + i * 2.3
        ax.add_patch(FancyBboxPatch((x, .8), 2.08, 1.15, boxstyle='round,pad=0.04,rounding_size=0.08',
            facecolor=('#e9f2f8' if i < 3 else '#fff3d9'), edgecolor='#9eabb5', lw=1))
        ax.text(x + 1.04, 1.67, title, ha='center', va='center', fontsize=11, fontweight='bold')
        ax.text(x + 1.04, 1.18, body, ha='center', va='center', fontsize=10, linespacing=1.6)
        if i < 4:
            ax.annotate('', (x + 2.28, 1.38), (x + 2.1, 1.38), arrowprops={'arrowstyle': '->', 'color': '#526879', 'lw': 1.4})
    ax.text(5.75, .35, '保留源数据；实验副本一致过滤。原有负例直接沿用，本次没有新增伪负例。', ha='center', fontsize=11)
    save(fig, 'construction_pipeline')


if __name__ == '__main__':
    performance(read('ALL_METRICS_WITH_CI.json'))
    gaps(read('ALL_METRICS_WITH_CI.json'))
    composition()
    frr()
    pipeline()
    print('Saved 5 figures as SVG / PDF / PNG:', OUTPUT)
