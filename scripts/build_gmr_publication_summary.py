#!/usr/bin/env python3
"""Build the joint README, tables and figures from frozen experiment outputs."""
import collections
import copy
import csv
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs/gmr_baseline_summary_20261011'
ASSETS = ROOT / 'assets/gmr_baseline_summary_20261011'
CHARADES = Path('experiments/agy_test/publication_review_20261011/charades_cg')
DATASETS = [
    ('Clean v3', Path('experiments/agy_test/v3_release_baselines_20261009'),
     Path('data/release/semantic_existence_v3_release'), 'MACRO'),
    ('Balanced v3', Path('experiments/agy_test/v3_balanced_baselines_20261010'),
     Path('data/release/semantic_existence_v3_balanced'), 'MACRO'),
    ('Charades-CG v2', CHARADES,
     Path('data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2'), 'C3_CG'),
]
BACKBONES = ('moment', 'qd', 'flash')
NAMES = {'moment': 'Moment-DETR-GMR', 'qd': 'QD-DETR-GMR', 'flash': 'FlashVTG-GMR'}
SHORT = {'moment': 'Moment-DETR', 'qd': 'QD-DETR', 'flash': 'FlashVTG'}
METRICS = [('auc', 'AUROC', 'gap'), ('rej_f1', 'Rej-F1', 'rej_f1_gap_pp'),
           ('gmiou1', 'G-mIoU@1', 'gmiou1_gap_pp')]
COLORS = ('#0072B2', '#D55E00', '#009E73')
plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_results():
    all_rows, counts, inventory = [], [], []
    for label, experiment, dataset, aggregate in DATASETS:
        if label == 'Charades-CG v2':
            evaluation = ROOT / experiment / 'docs/reports/charades_cg_gmr_baselines_20261011'
        else:
            evaluation = ROOT / experiment / 'evaluation'
        rows = read_json(evaluation / 'degradation_metrics.json')
        absolute = read_json(evaluation / 'bootstrap.json')
        subset = read_json(evaluation / 'degradation_bootstrap.json')
        status_path = (evaluation if label == 'Charades-CG v2' else ROOT / experiment) / 'FINAL_EVALUATION_STATUS.json'
        status = read_json(status_path)
        if status.get('complete') is not True:
            raise ValueError(f'Incomplete experiment: {label}')
        inventory.append({'dataset': label, 'experiment': str(experiment),
                          'release': str(dataset), 'evaluation': str(evaluation.relative_to(ROOT)),
                          'completed_settings': sum(r['split'] != 'MACRO' for r in rows),
                          'summary_split': aggregate, 'status': status})
        for row in rows:
            row = copy.deepcopy(row)
            bb, split = row['backbone'], row['split']
            if label == 'Charades-CG v2':
                abs_ci = subset[bb]['absolute']
                sub_ci = subset[bb]['subset']
            else:
                abs_ci = absolute[f'{split}|{bb}']
                sub_ci = subset['intervals'][f'{split}|{bb}']
            out = {'dataset': label, 'split': split, 'backbone': bb, 'method': 'Baseline',
                   'threshold': row.get('threshold')}
            for key in ['seen_auc', 'unseen_auc', 'rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1']:
                out[key] = row[key]
                out[key + '_ci_low'], out[key + '_ci_high'] = abs_ci[key]
            out['auroc_gap_pp'] = 100 * row['gap']
            out['auroc_gap_pp_ci_low'], out['auroc_gap_pp_ci_high'] = [100*x for x in abs_ci['gap']]
            for key in ['seen_rej_f1', 'unseen_rej_f1', 'rej_f1_gap_pp',
                        'seen_gmiou1', 'unseen_gmiou1', 'gmiou1_gap_pp']:
                out[key] = row[key]
                out[key + '_ci_low'], out[key + '_ci_high'] = sub_ci[key]['ci95']
            for prefix in ('seen', 'unseen'):
                out[prefix + '_positive_n'] = row[prefix + '_positive_n']
                out[prefix + '_negative_n'] = row.get(prefix + '_negative_n',
                    row.get(prefix + '_n', 0) - row[prefix + '_positive_n'])
            for metric in ('auroc', 'rej_f1', 'gmiou1'):
                for comparison in ('unseen_net_gain', 'seen_change', 'gap_reduction'):
                    out[metric + '_' + comparison] = None
            all_rows.append(out)
        for folder in sorted((ROOT / dataset / 'splits').iterdir()):
            if not folder.is_dir():
                continue
            for part in (('train', 'val_seen', 'test') if label == 'Charades-CG v2' else ('train', 'val', 'test')):
                path = folder / (part + '.jsonl')
                cnt = collections.Counter()
                vids = set()
                with path.open() as stream:
                    for line in stream:
                        if line.strip():
                            record = json.loads(line)
                            cnt[record['partition']] += 1
                            vids.add(record['vid'])
                counts.append({'dataset': label, 'split': folder.name, 'partition': part,
                               **{p: cnt[p] for p in ('S+', 'S-', 'U+', 'U-')},
                               'total': sum(cnt.values()), 'videos': len(vids)})
    return all_rows, counts, inventory


def save_figure(fig, name):
    for suffix in ('svg', 'pdf', 'png'):
        fig.savefig(ASSETS / f'{name}.{suffix}', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_composition(counts):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    for ax, (label, _, _, _) in zip(axes, DATASETS):
        rows = [r for r in counts if r['dataset'] == label and r['partition'] == 'test']
        base = np.zeros(len(rows))
        for p, color, hatch in zip(('S+', 'S-', 'U+', 'U-'),
                                   ('#0072B2', '#56B4E9', '#D55E00', '#E69F00'), ('', '//', '', '//')):
            values = np.array([r[p] for r in rows])
            ax.barh(range(len(rows)), values, left=base, color=color, hatch=hatch,
                    edgecolor='white', label=p)
            for i, value in enumerate(values):
                if value > 900:
                    ax.text(base[i] + value/2, i, str(value), ha='center', va='center',
                            fontsize=8, color='white' if p in ('S+', 'U+') else '#202020')
            base += values
        ax.set(yticks=range(len(rows)), yticklabels=[r['split'] for r in rows],
               title=label, xlabel='Test video-query pairs', xlim=(0, 12000))
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=.15)
        ax.set_axisbelow(True)
    axes[0].legend(ncol=4, loc='lower left', bbox_to_anchor=(0, 1.10), frameon=False)
    fig.suptitle('Test composition by release and split', y=1.05, fontsize=15)
    fig.text(.5, -.015, 'S / U: Seen / Unseen; + / -: present / absent construction label. '
             'Balanced v3 is balanced overall, not necessarily within Seen and Unseen.',
             ha='center', fontsize=9)
    fig.tight_layout()
    save_figure(fig, 'dataset_composition')


def plot_performance(rows):
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for i, (label, _, _, aggregate) in enumerate(DATASETS):
        subset = [next(r for r in rows if r['dataset'] == label and r['split'] == aggregate
                       and r['backbone'] == bb) for bb in BACKBONES]
        for j, (key, title, _) in enumerate(METRICS):
            ax = axes[i, j]
            for delta, prefix, color, marker in ((-.14, 'seen', '#0072B2', 'o'),
                                                  (.14, 'unseen', '#D55E00', 's')):
                metric = prefix + '_' + key
                values = np.array([r[metric] for r in subset])
                lo = np.array([r[metric + '_ci_low'] for r in subset])
                hi = np.array([r[metric + '_ci_high'] for r in subset])
                ax.errorbar(np.arange(3)+delta, values, yerr=[values-lo, hi-values],
                            fmt=marker, color=color, label=prefix.capitalize(), capsize=4, ms=6)
                for x, value in zip(np.arange(3)+delta, values):
                    ax.annotate(f'{value:.3f}' if key == 'auc' else f'{value:.1f}', (x, value),
                                xytext=(0, 13 if prefix == 'seen' else -19),
                                textcoords='offset points', ha='center', fontsize=8)
            ax.set(xticks=np.arange(3), xticklabels=[SHORT[b] for b in BACKBONES],
                   ylim=(0, 1 if key == 'auc' else 100), xlim=(-.6, 2.6),
                   ylabel='AUROC (0–1)' if key == 'auc' else f'{title} (%)',
                   title=f'{label} | {"5-split macro" if aggregate == "MACRO" else aggregate}')
            ax.grid(axis='y', alpha=.18)
    axes[0, 0].legend(frameon=False, ncol=2, fontsize=9, loc='upper center')
    fig.suptitle('Seen / Unseen performance under frozen Seen-validation choices', fontsize=15)
    fig.text(.5, .002, '95% video-cluster bootstrap CI; 2,000 draws; seed 3407. '
             'Each release has its own test distribution; rows are not paired method comparisons.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .025, 1, .97))
    save_figure(fig, 'seen_unseen_performance')


def plot_gaps(rows):
    fig, axes = plt.subplots(3, 3, figsize=(14, 11.5),
                             gridspec_kw={'height_ratios': [2.3, 2.3, 1]})
    for i, (label, _, _, aggregate) in enumerate(DATASETS):
        subset = [r for r in rows if r['dataset'] == label]
        order = ['A1_v3', 'A2_v3', 'A3_v3', 'C1_v3', 'C2_v3', 'MACRO'] if aggregate == 'MACRO' else ['C3_CG']
        subset = sorted(subset, key=lambda r: (order.index(r['split']), BACKBONES.index(r['backbone'])))
        for j, (_, title, source_key) in enumerate(METRICS):
            ax = axes[i, j]
            gap = 'auroc_gap_pp' if source_key == 'gap' else source_key
            for y, row in enumerate(subset):
                b = BACKBONES.index(row['backbone'])
                val, lo, hi = row[gap], row[gap+'_ci_low'], row[gap+'_ci_high']
                ax.errorbar(val, y, xerr=[[val-lo], [hi-val]], fmt=('o', 's', '^')[b],
                            color=COLORS[b], ms=4, capsize=2, lw=1.1)
            ax.axvline(0, color='#555555', linestyle='--', lw=.9)
            ax.set(title=f'{label} | {title}', xlabel='Seen − Unseen (pp)',
                   yticks=range(len(subset)), ylim=(len(subset)-.4, -.6))
            ax.set_yticklabels([f'{r["split"].replace("_v3", "")} / {SHORT[r["backbone"]]}'
                                for r in subset] if j == 0 else [], fontsize=8)
            ax.grid(axis='x', alpha=.18)
    fig.suptitle('Signed generalization gaps: each split and backbone', fontsize=15)
    fig.text(.5, .003, '95% joint video-cluster bootstrap CI; 2,000 draws; frozen checkpoints and thresholds. '
             'Negative gaps are retained. Rej-F1 and G-mIoU depend on class proportions.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .03, 1, .97))
    save_figure(fig, 'generalization_gaps')


def combine_svg(sources, name, columns=1):
    """Combine the original vector elements; namespace every SVG identifier."""
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    width = 1320
    cell_width = width / columns
    cells = []
    for i, (label, path) in enumerate(sources):
        svg = ET.parse(path).getroot()
        view = svg.get('viewBox')
        if view:
            _, _, w, h = map(float, view.split())
        else:
            w = float(re.sub(r'[^0-9.]', '', svg.get('width')))
            h = float(re.sub(r'[^0-9.]', '', svg.get('height')))
            svg.set('viewBox', f'0 0 {w} {h}')
        ids = {el.get('id'): f'{name}_{i}_{el.get("id")}' for el in svg.iter() if el.get('id')}
        for el in svg.iter():
            for attr, value in list(el.attrib.items()):
                if attr == 'id':
                    el.set(attr, ids[value])
                else:
                    for original, replacement in ids.items():
                        value = value.replace(f'url(#{original})', f'url(#{replacement})')
                        if value == '#' + original:
                            value = '#' + replacement
                    el.set(attr, value)
            # Cairo selects the first font without per-glyph fallback. Put CJK
            # first for Chinese text so the PNG/PDF exports keep readable glyphs.
            if el.tag == f'{{{ns}}}text' and re.search(r'[\u3400-\u9fff]', ''.join(el.itertext())):
                style = el.get('style', '')
                style = re.sub(r'font-family\s*:[^;]+',
                               "font-family: 'Noto Sans CJK SC', 'DejaVu Sans'", style)
                el.set('style', style)
                el.set('font-family', 'Noto Sans CJK SC, DejaVu Sans, sans-serif')
        content_height = h * (cell_width - 24) / w
        cells.append((label, svg, content_height))
    row_heights = [max(c[2] for c in cells[i:i+columns]) + 55 for i in range(0, len(cells), columns)]
    root = ET.Element(f'{{{ns}}}svg', {'width': str(width), 'height': str(sum(row_heights)),
                      'viewBox': f'0 0 {width} {sum(row_heights)}', 'role': 'img'})
    ET.SubElement(root, f'{{{ns}}}title').text = name.replace('_', ' ')
    ET.SubElement(root, f'{{{ns}}}rect', {'width': '100%', 'height': '100%', 'fill': 'white'})
    for i, (label, svg, height) in enumerate(cells):
        x, y = (i % columns)*cell_width, sum(row_heights[:i//columns])
        ET.SubElement(root, f'{{{ns}}}text', {'x': str(x+14), 'y': str(y+28),
                      'font-family': 'DejaVu Sans, sans-serif', 'font-size': '22',
                      'font-weight': 'bold', 'fill': '#1e293b'}).text = label
        svg.attrib.update({'x': str(x+12), 'y': str(y+40),
                           'width': str(cell_width-24), 'height': str(height)})
        root.append(svg)
    ET.ElementTree(root).write(ASSETS / f'{name}.svg', encoding='utf-8', xml_declaration=True)


def fmt(value, auc=False):
    return f'{value:.4f}' if auc else f'{value:.2f}'


def tables(rows, counts):
    lines = ['# 全部划分、backbone 与 95% CI', '',
             'AUROC 为 0–1；Rej-F1 / G-mIoU@1 为 %；Gap 为 Seen − Unseen（pp）。区间来自已有冻结输出，未重新训练或重采样。', '']
    for label, _, _, _ in DATASETS:
        lines += [f'## {label}', '', '| Split | Backbone | Metric | Seen [95% CI] | Unseen [95% CI] | Gap pp [95% CI] |',
                  '|---|---|---|---:|---:|---:|']
        for row in [r for r in rows if r['dataset'] == label]:
            for key, title, source_gap in METRICS:
                seen, unseen = 'seen_'+key, 'unseen_'+key
                gap = 'auroc_gap_pp' if source_gap == 'gap' else source_gap
                cell = lambda k: f'{fmt(row[k], key == "auc")} [{fmt(row[k+"_ci_low"], key == "auc")}, {fmt(row[k+"_ci_high"], key == "auc")}]'
                lines.append(f'| {row["split"]} | {NAMES[row["backbone"]]} | {title} | {cell(seen)} | {cell(unseen)} | '
                             f'{row[gap]:+.2f} [{row[gap+"_ci_low"]:+.2f}, {row[gap+"_ci_high"]:+.2f}] |')
        lines += ['', '| Split | Backbone | Overall Rej-F1 [CI] | RR [CI] | S+ FRR [CI] | U+ FRR [CI] | Overall G-mIoU@1 [CI] |',
                  '|---|---|---:|---:|---:|---:|---:|']
        for row in [r for r in rows if r['dataset'] == label]:
            cells = [f'{row[k]:.2f} [{row[k+"_ci_low"]:.2f}, {row[k+"_ci_high"]:.2f}]'
                     for k in ('rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1')]
            lines.append(f'| {row["split"]} | {NAMES[row["backbone"]]} | ' + ' | '.join(cells) + ' |')
        lines += ['']
    lines += ['独立 baseline 的 Unseen Net Gain / Seen Change / Gap Reduction 对三项指标均为 N/A；没有同划分同 backbone 的新方法比较。', '',
              'MACRO 为五组等权均值，CI 使用共同视频宇宙上的对应抽样；样本数不求和为独立样本。单种子区间不覆盖训练种子随机性。', '']
    (REPORT / 'RESULTS_WITH_CI.md').write_text('\n'.join(lines))
    lines = ['# 各版本各划分样本数', '', '| Dataset | Split | Partition | S+ | S− | U+ | U− | Total | Videos |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in counts:
        lines.append('| ' + ' | '.join(str(v) for v in r.values()) + ' |')
    lines += ['', '不同划分重复使用相同视频与查询；不得将五组行数相加解释为独立视频/查询数。val 为完整归档验证集，选模与定阈值只使用 val_seen。', '']
    (REPORT / 'DATASET_COUNTS.md').write_text('\n'.join(lines))


def write_readme(rows, counts, inventory):
    summary = [next(r for r in rows if r['dataset'] == label and r['split'] == agg and r['backbone'] == bb)
               for label, _, _, agg in DATASETS for bb in BACKBONES]
    metric_lines, overall_lines, count_lines, index_lines = [], [], [], []
    for row in summary:
        cells = []
        for key, _, source_gap in METRICS:
            gap = 'auroc_gap_pp' if source_gap == 'gap' else source_gap
            cells.append(f'{fmt(row["seen_"+key], key=="auc")} → {fmt(row["unseen_"+key], key=="auc")} ({row[gap]:+.2f})')
        metric_lines.append(f'| {row["dataset"]} / {row["split"]} | {NAMES[row["backbone"]]} | ' + ' | '.join(cells) + ' |')
        overall_lines.append(f'| {row["dataset"]} / {row["split"]} | {NAMES[row["backbone"]]} | ' +
                             ' | '.join(f'{row[k]:.2f}%' for k in ('rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1')) + ' |')
    for r in counts:
        if r['partition'] == 'test':
            count_lines.append('| ' + ' | '.join(str(r[k]) for k in ('dataset', 'split', 'S+', 'S-', 'U+', 'U-', 'total')) + ' |')
    for item in inventory:
        index_lines.append(f'| {item["dataset"]} | [{Path(item["experiment"]).name}]({item["experiment"]}/README.md) | '
                           f'[{Path(item["release"]).name}]({item["release"]}/README.md) | {item["completed_settings"]}/{item["completed_settings"]} |')
    text = '''# GMR 三组基准实验汇总

本分支汇总 Clean Semantic Existence v3、Balanced v3 与 Charades-CG-GMR v2 的数据、方法源码、运行脚本和冻结结果，更新于 **2026-10-11**。两个 v3 项目各完成五划分 × 三 backbone（15/15）；Charades-CG v2 完成 C3_CG × 三 backbone（3/3），共 **33 个已完成评测设置**。本次仅整理已有实验，未新增训练、调参或方法实验。

## 项目与数据入口

| 项目 | 实验 README | 对应数据集 | 完成设置 |
|---|---|---|---:|
INDEX

方法包含 **Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR**。各项目的 `native_source/` 或 `source_snapshot/native_source/` 保留实际使用的 `models/`、`training/`、`configs/` 和 `eval/`，以各自 `SOURCE_MANIFEST.json` 为准。

## 数据版本、构建方式与划分

**Clean v3**：完成语义审计后保留 15,034 个正例 qid 与 2,869 个不同负例 qid，排除隔离与剔除样本。A1/A2/A3 分别留出放置/拿取、饮用/倾倒、跑步/行走；C1 留出坐×床/椅/沙发，C2 留出打开/关闭×箱/柜。完整查询若含已断言的留出事件便不进入训练。审计未逐视频确认事件缺席。

**Balanced v3**：保留 Clean v3 原始行，补充跨视频伪负例。用归一化 CLIP 文本向量，对目标视频全部正描述取最大余弦相似度，按查询选排名最低 50% 的候选视频，再执行标注冲突过滤与配额采样，使每个完整 split 正负 1:1；Seen/Unseen 内部仍可能不平衡。新增负例未经视频缺席核验，不能将低文本相似度当作真实缺席证明。

**Charades-CG v2**：官方 Test-Trivial 为 Seen，Novel-Composition 为 Unseen；只含 C3_CG。机械剔除 2,119 条非法/越界正例窗口而不截断，再构造同 split 跨视频负例。两类测试正描述共同进入候选池；S−/U− 在联合池重新采样。Train 与 Seen validation 和 v1 逐字节相同，测试使用全量 v2 重新推理。训练为 6,342 正 + 6,342 负，Seen validation 为 684 正 + 684 负，测试为 11,348 行。负例均为构造标签，未经逐视频缺席确认；Unseen 指下游未见组合，不代表预训练从未见过相关概念。

![三套数据的原始构建图合并](assets/gmr_baseline_summary_20261011/construction_pipelines.svg)

*图 1：三套数据具有不同来源与负例构造过程。按项目合并原始矢量管线；最低 50% 指视频排名比例，非余弦阈值 0.5。*

<details>
<summary>五类语义留出：合并原有 A1–C2 示意图</summary>

![五类划分原图合并](assets/gmr_baseline_summary_20261011/semantic_splits.svg)

该图保留 Clean v3 的原始定义、真实查询示例和统计；Balanced v3 沿用相同语义定义，但补充负例后的数量见下表。

</details>

| 数据集 | Test split | S+ | S− | U+ | U− | 总行数 |
|---|---|---:|---:|---:|---:|---:|
COUNTS

![三版本数据组成合并](assets/gmr_baseline_summary_20261011/dataset_composition.svg)

*图 2：Balanced v3 的完整测试集与 Charades-CG v2 正负平衡，Balanced 的 Seen/Unseen 子集仍有比例差异。图中 S/U 为 Seen/Unseen，+/− 为存在/缺席构造标签；全部 train/val/test 计数见 [DATASET_COUNTS](docs/gmr_baseline_summary_20261011/DATASET_COUNTS.md)。五划分共享视频与查询，不能把行数相加当作独立样本数。*

## 统一训练和评测协议

| 项目 | 固定设置 |
|---|---|
| 特征 | CLIP 文本，CLIP + SlowFast 视频；精确查询 SHA-256 核验复用特征 |
| 训练 | S+/S− only；seed 3407；从头训练，最多 100 epochs；max_es_cnt=26（连续 27 次无改善早停） |
| Checkpoint | Moment/QD：Seen validation MR-full-mAP；Flash：Seen validation R1@0.5 与 R1@0.7 均值 |
| 阈值 | 完整 Seen validation 的 5–95 分位数、91 个候选，最大化 Balanced Accuracy，并列取最早；score ≥ threshold 接受 |
| 分数 | Moment/QD 原生四位 sigmoid；Flash 原生六位 logit，避免三位概率饱和并列 |
| 定位 | 原生输出第一个合法窗口；不因窗口终点超过标注时长改选后续窗口 |
| 不确定性 | 2,000 次 video-cluster bootstrap，seed 3407，冻结 checkpoint 与阈值；Seen/Unseen 共享视频联合重采样 |
| 宏平均 | 仅 Clean/Balanced 的五组全部完成后作等权 MACRO；共同视频宇宙配对抽样；C3_CG 单独报告 |

Charades-CG v2 **复用原 C3_CG 的冻结 checkpoint、Seen-validation 原生预测及阈值**，只重新推理 v2 测试；其训练/验证与 v1 相同。CI 反映固定模型下的视频抽样不确定性，不代表跨训练种子波动。

AUROC 为存在分数的排序能力。Actual Rej-F1 将拒绝作为正决策，`2TN/(2TN+FP+FN)`；TN 为正确拒绝缺席，FP 为错误接受缺席，FN 为错误拒绝存在。G-mIoU@1 接受查询时使用原生 top-1 的集合 IoU；拒绝负例得 1，拒绝正例得 0，再对全部样本平均。**Gap = Seen − Unseen**，统一用 pp；AUROC 差值乘 100，负 Gap 保留为 Unseen 点估计更高。

## 主要结果

下表各单元格为 **Seen → Unseen（Gap pp）**。AUROC 为 0–1；Rej-F1、G-mIoU@1 为百分数。Clean/Balanced 为完整五划分等权宏平均，Charades-CG 为单划分。

| 数据 / 汇总范围 | Backbone | AUROC | Rej-F1 (%) | G-mIoU@1 (%) |
|---|---|---:|---:|---:|
METRICS

![Seen Unseen 三指标合并](assets/gmr_baseline_summary_20261011/seen_unseen_performance.svg)

*图 3：三套数据中，多数模型的 Unseen AUROC 点估计低于 Seen。每行对应独立数据版本，每列对应一项指标；圆点/方点分别为 Seen/Unseen，误差线为视频聚类 bootstrap 95% CI。不同版本不构成同测试集方法比较。*

![全部划分泛化差距合并](assets/gmr_baseline_summary_20261011/generalization_gaps.svg)

*图 4：泛化差距随划分、模型和指标而改变；负 Gap 原样保留。展示各 split/backbone 与五组 MACRO 的 95% CI，虚线为零。区间含零时不将点估计方向解读为明确退化或改善。*

**完整结果与 CI**：[逐划分、逐 backbone 的三项 Seen/Unseen、Gap 及 overall 表](docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md) · [CSV](docs/gmr_baseline_summary_20261011/metrics.csv) · [JSON](docs/gmr_baseline_summary_20261011/metrics.json)。所有汇总均读取未舍入的冻结 JSON。

| 数据 / 汇总范围 | Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 |
|---|---|---:|---:|---:|---:|---:|
OVERALL

**结果解读**：Clean v3 的三模型宏平均 AUROC Gap 为 18.96–20.76 pp；Balanced v3 为 3.52–10.98 pp，但其负例构造、训练分布和测试组成均改变，不能称为同测试集方法净增益。Balanced QD 的 Unseen AUROC 仅 0.5093，却有负的 Rej-F1/G-mIoU Gap；应结合其 U+ FRR 71.86% 阅读。Charades-CG 的 Moment/Flash 三项 Gap CI 均高于零；QD 三项 Gap CI 均含零，其 AUROC 接近随机排序。

Rej-F1 与 G-mIoU 受正负比例影响；高正确拒绝率可以抬高端到端数值，负 Gap 也不直接等价于正例定位提升。在 Charades-CG 每个子集正负 1:1 下，一律拒绝的公式参照为 Rej-F1=66.67%、G-mIoU=50%、正例 FRR=100%（恒定分数 AUROC=0.5）。该参照仅是确定性公式结果。

独立 baseline 的 **Unseen Net Gain、Seen Change、Gap Reduction 对三项指标均未定义（N/A）**。未来方法须与同版本、同 split、同 backbone baseline 进行成对比较并报告 paired bootstrap CI；不把跨版本差值当作方法增益，本包也未检验 backbone 之间的成对显著性。

## 源码、脚本和冻结结果

| 内容 | 位置 |
|---|---|
| 数据制作 / 校验 | [scripts](scripts/)；各数据集 `construction_protocol.json`、`validation_report.json`、清单和 provenance |
| Clean / Balanced 实际模型源码与配置 | 各实验 `native_source/{models,training,configs,eval}/` 与 `SOURCE_MANIFEST.json` |
| Clean / Balanced 训练和推理 | 各实验 `run_baselines.py`、`common.py`、`launch_native.sh`；原训练配置保留于 `groups/*/runs/` |
| Clean / Balanced 冻结输出 | `groups/*/evaluation/*/{predictions.npz,FROZEN_CALIBRATION.json,bootstrap_draws.npz,metrics.json,bootstrap.json}`；`frozen_checkpoints/` 保留权重哈希与原验证预测；`runs/*/test/` 保留原生测试窗口 |
| Clean / Balanced 补充 bootstrap | `evaluation/degradation_cache/`、`degradation_bootstrap.json`，以及原始 Markdown/CSV/JSON |
| Charades-CG 自含审阅包 | [README](experiments/agy_test/publication_review_20261011/charades_cg/README.md)；包内 `docs/reports/charades_cg_gmr_baselines_20261011/{frozen,source_snapshot}/` |
| Charades-CG 原训练与 v2 执行脚本 | [原训练](experiments/agy_test/charades_cg_baselines_20261010/) · [v2 重评估](experiments/agy_test/charades_cg_v2_evaluation_20261011/)；实际 native 源码见审阅包快照 |
| 图表 | [合并图](assets/gmr_baseline_summary_20261011/)；原图与绘制代码保留于 `assets/semantic_existence_v3/` 和 Charades-CG 包内 assets |
| 本次发布元数据 | [PACKAGING](docs/gmr_baseline_summary_20261011/PACKAGING.json) · [PUBLICATION_MANIFEST](docs/gmr_baseline_summary_20261011/PUBLICATION_MANIFEST.json) · [实验完成记录](docs/gmr_baseline_summary_20261011/EXPERIMENTS.json) |

发布范围包含标注、方法/训练/评估源码、配置、脚本、冻结预测、校准与 bootstrap 产物。遵循仓库约定，视频、特征数组、模型权重和凭据不进入提交；权重以原始 SHA-256 清单追溯。Balanced 的超大 `master/negative_added.jsonl` 使用无损 gzip 存储，还原后逐字节匹配原校验值。日志归档为 `.log.gz`。

## 使用与复现

从仓库根目录还原超大标注并校验发布文件：

```bash
python scripts/restore_gmr_publication.py
```

汇总与重绘只读取已保存结果，不需要视频、特征或权重：

```bash
python -m pip install -r requirements-publication.txt
python scripts/build_gmr_publication_summary.py
```

重绘直接合并原始 SVG 元素，并从冻结指标/标注生成数据组成、性能与 Gap 图；导出 SVG/PDF/PNG，原始矢量图可单独查看。

训练依赖见 `requirements.txt`、`requirements-flash-vtg.txt`；数据构建另见 `requirements-dataset.txt`。原始 `run_baselines.py` / `common.py` 是执行时源码记录，包含本机解释器、视频目录及历史特征清单路径；在其他机器运行须先按 README 和 `PROTOCOL.json` 配置路径并准备外部特征、冻结权重或新训练目录。`launch_native.sh` 支持 `V3_NATIVE_REPO`、`DATA_ROOT`、`FEATURE_ROOT`、`VIDEO_ROOT`、`RUN_ROOT`、`TRAIN_GPU`、`GMR_PYTHON` 和 `FLASH_PYTHON`；应使用全新 RUN_ROOT，以免覆盖已有实验。Charades 原训练脚本所用 native 源码在审阅包中，需对应设置其路径。

已有 `RELEASE_VALIDATION`、`LOCAL_VERIFICATION` 和独立验收记录保留为历史证据。本次整理未重新运行训练或实验验证；还原脚本执行发布级 SHA-256 完整性校验。完整重建语义审计或 CLIP 排名还需要原始审计工作材料、外部向量缓存等未发布输入，不能仅凭无权重发布包完成。
'''
    for key, value in [('INDEX', index_lines), ('COUNTS', count_lines), ('METRICS', metric_lines), ('OVERALL', overall_lines)]:
        text = text.replace('\n'+key+'\n', '\n'+'\n'.join(value)+'\n')
    (ROOT / 'README.md').write_text(text)


def main():
    REPORT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    rows, counts, inventory = load_results()
    write_json(REPORT / 'metrics.json', rows)
    write_csv(REPORT / 'metrics.csv', rows)
    write_json(REPORT / 'dataset_counts.json', counts)
    write_csv(REPORT / 'dataset_counts.csv', counts)
    write_json(REPORT / 'EXPERIMENTS.json', inventory)
    tables(rows, counts)
    plot_composition(counts)
    plot_performance(rows)
    plot_gaps(rows)
    combine_svg([
        ('Clean v3', ROOT / 'assets/semantic_existence_v3/clean_release_pipeline.svg'),
        ('Balanced v3', ROOT / 'assets/semantic_existence_v3/balanced_pipeline.svg'),
        ('Charades-CG v2', ROOT / CHARADES / 'assets/charades_cg_gmr/construction_pipeline.svg'),
    ], 'construction_pipelines')
    combine_svg([(group, ROOT / f'assets/semantic_existence_v3/split_figures/{group}.svg')
                 for group in ('A1_v3', 'A2_v3', 'A3_v3', 'C1_v3', 'C2_v3')], 'semantic_splits', columns=2)
    try:
        import cairosvg
    except ImportError:
        print('SVG composites saved; install cairosvg for PDF/PNG composite exports.')
    else:
        for name in ('construction_pipelines', 'semantic_splits'):
            data = (ASSETS / f'{name}.svg').read_bytes()
            cairosvg.svg2pdf(bytestring=data, write_to=str(ASSETS / f'{name}.pdf'))
            cairosvg.svg2png(bytestring=data, write_to=str(ASSETS / f'{name}.png'), output_width=2000)
    write_readme(rows, counts, inventory)
    print(f'Saved {len(rows)} setting/macro rows, {len(counts)} split counts and 5 grouped figures.')


if __name__ == '__main__':
    main()
