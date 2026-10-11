#!/usr/bin/env python3
"""Create a concise research README and figures from frozen summary results."""
import html
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs/gmr_baseline_summary_20261011'
ASSETS = ROOT / 'assets/gmr_baseline_summary_20261011/reader'
DATASETS = ('Clean v3', 'Balanced v3', 'Charades-CG v2', 'Soccer-GMR v1')
TITLES = {'Clean v3': 'Clean v3', 'Balanced v3': 'Balanced v3',
          'Charades-CG v2': 'Charades-CG v2', 'Soccer-GMR v1': 'Soccer'}
BACKBONES = ('moment', 'qd', 'flash')
NAMES = {'moment': 'Moment-DETR-GMR', 'qd': 'QD-DETR-GMR', 'flash': 'FlashVTG-GMR'}
SHORT = {'moment': 'Moment', 'qd': 'QD', 'flash': 'Flash'}
COLORS = ('#0072B2', '#D55E00', '#009E73')
MARKERS = ('o', 's', '^')
METRICS = (('auc', 'AUROC', 'auroc_gap_pp'), ('rej_f1', 'Rej-F1', 'rej_f1_gap_pp'),
           ('gmiou1', 'G-mIoU@1', 'gmiou1_gap_pp'))
FAMILIES = ['DejaVu Sans']
for filename in ('NotoSansCJK-Regular.ttc', 'NotoSansCJK-Bold.ttc'):
    path = Path('/usr/share/fonts/opentype/noto') / filename
    if path.exists():
        font_manager.fontManager.addfont(str(path))
        family = font_manager.FontProperties(fname=str(path)).get_name()
        if family not in FAMILIES:
            FAMILIES.append(family)
plt.rcParams.update({'font.family': FAMILIES, 'font.size': 11, 'axes.labelsize': 11,
                     'svg.fonttype': 'none', 'pdf.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})


def read(name):
    return json.loads((REPORT / name).read_text())


def table(headers, records):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in records])


def save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    for extension in ('svg', 'pdf', 'png'):
        fig.savefig(ASSETS / f'{name}.{extension}', bbox_inches='tight', facecolor='white', dpi=180)
    plt.close(fig)


def overview():
    """Native vector layout: four short paths, then one shared evaluation rule."""
    from render_gmr_construction_figures import Figure
    import render_gmr_construction_figures as drawing
    drawing.ASSETS = ASSETS
    f = Figure('data_preparation', 570, '四套数据，回答同一个问题',
               '训练没见过的语义：事件是否发生？发生在哪里？')
    columns = [(30, 210, '数据'), (270, 240, '正例来源'), (540, 330, '负例：模型应拒绝'), (900, 270, 'Unseen 的语义')]
    for x, width, name in columns:
        f.text(x + 12, 127, name, 21, '#526572', 'bold')
    entries = [
        ('Clean v3', 'Charades 原句与时间窗', ['固定视频，改动作或对象', '语义审核后保留'], ['动作族', '动作 × 对象']),
        ('Balanced v3', '保留 Clean 全部正例', ['原句换视频，追加负例', '补齐每个划分正负 1:1'], ['沿用 Clean', '五组语义定义']),
        ('Charades-CG v2', '官方组合划分的正例', ['原句换视频', '每个正例对应一个负例'], ['官方未见组合', 'Novel-Composition']),
        ('Soccer', '已有世界杯正例标注', ['沿用源负例', '本次没有新增负例'], ['动作', '动作 × 球队']),
    ]
    for i, (label, source, negative, semantics) in enumerate(entries):
        y = 145 + i * 83
        f.rect(30, y, 1140, 72, '#F5F8FA', '#E4EAF0', radius=7)
        f.text(44, y + 43, label, 23, '#243746', 'bold')
        f.text(282, y + 43, source, 20)
        f.lines(552, y + 29, negative, 19, step=28)
        f.lines(912, y + 29, semantics, 19, step=28)
        for x in (519, 878):
            f.line(x, y + 36, x + 16, y + 36, '#8796A5', arrow=True)
    f.rect(30, 495, 1140, 47, '#EAF3F8', '#C4D9E6', radius=7)
    f.text(600, 527, '训练只用 Seen  →  Seen 验证选模型和阈值  →  Test 分别评测 Seen / Unseen',
           21, '#244961', 'bold', 'middle')
    f.save()


def composition(counts):
    fig, ax = plt.subplots(figsize=(8.8, 3.2))
    pairs = []
    for ds in DATASETS:
        test = [r for r in counts if r['dataset'] == ds and r['partition'] == 'test']
        totals = {(r['S+'] + r['U+'], r['S-'] + r['U-']) for r in test}
        assert len(totals) == 1
        pairs.append(next(iter(totals)))
    positive = np.array([p for p, _ in pairs])
    negative = np.array([n for _, n in pairs])
    share = 100 * positive / (positive + negative)
    ax.barh(range(4), share, .58, color='#0072B2', label='正例：应定位')
    ax.barh(range(4), 100 - share, .58, left=share, color='#E69F00', hatch='//', label='负例：应拒绝', edgecolor='white')
    for i, ((p, n), fraction) in enumerate(zip(pairs, share)):
        ax.text(fraction / 2, i, f'{p:,}', color='white', va='center', ha='center', fontsize=12)
        ax.text(fraction + (100 - fraction) / 2, i, f'{n:,}', va='center', ha='center', fontsize=12)
    ax.set(yticks=range(4), yticklabels=[TITLES[d] for d in DATASETS], xlim=(0, 100),
           xticks=(0, 25, 50, 75, 100), xticklabels=('0%', '25%', '50%', '75%', '100%'), xlabel='每个完整测试集的正负比例')
    ax.invert_yaxis()
    ax.legend(ncol=2, frameon=False, loc='lower left', bbox_to_anchor=(0, 1.02), fontsize=11)
    fig.tight_layout()
    save(fig, 'test_balance')


def gaps(summary):
    fig, axes = plt.subplots(1, 3, figsize=(10, 6.3), sharey=True)
    labels = [f'{TITLES[r["dataset"]]} / {SHORT[r["backbone"]]}' for r in summary]
    for ax, (_, title, key) in zip(axes, METRICS):
        for group in (0, 2):
            ax.axhspan(group * 3 - .5, group * 3 + 2.5, color='#F4F7FA', zorder=0)
        for i, r in enumerate(summary):
            b = BACKBONES.index(r['backbone'])
            value, lo, hi = r[key], r[key + '_ci_low'], r[key + '_ci_high']
            ax.errorbar(value, i, xerr=[[value - lo], [hi - value]], color=COLORS[b],
                        marker=MARKERS[b], capsize=3, lw=1.5, ms=6, zorder=3)
        for y in (2.5, 5.5, 8.5):
            ax.axhline(y, color='#D7DFE6', lw=.8)
        ax.axvline(0, color='#687887', ls='--', lw=1.1)
        ax.set(title=title, xlabel='Seen − Unseen（百分点）', yticks=range(len(summary)))
        ax.grid(axis='x', alpha=.15)
    axes[0].set_yticklabels(labels, fontsize=10.5)
    axes[0].set_ylim(len(summary) - .5, -.5)
    fig.tight_layout()
    save(fig, 'generalization_summary')


def write_readme(rows, counts, summary):
    data_table = []
    for ds in DATASETS:
        train = [r['total'] for r in counts if r['dataset'] == ds and r['partition'] == 'train']
        val = [r['S+'] + r['S-'] for r in counts if r['dataset'] == ds and r['partition'] in ('val', 'val_seen')]
        test = next(r for r in counts if r['dataset'] == ds and r['partition'] == 'test')
        def extent(values):
            return f'{min(values):,}' if min(values) == max(values) else f'{min(values):,}–{max(values):,}'
        data_table.append([TITLES[ds], extent(train), extent(val), f"{test['S+'] + test['U+']:,}",
                           f"{test['S-'] + test['U-']:,}", f"{test['total']:,}"])
    sizes = table(['数据', '训练数／组', 'Seen 验证数／组', '测试正例', '测试负例', '测试总数／组'], data_table)
    composition_rows = [[TITLES[ds], r['split'], r['S+'], r['S-'], r['U+'], r['U-']]
        for ds in DATASETS for r in counts if r['dataset'] == ds and r['partition'] == 'test']
    detailed_counts = table(['数据', '划分', 'S+', 'S−', 'U+', 'U−'], composition_rows)
    result_rows = []
    for r in summary:
        cells = [f"{r['seen_auc']:.4f} → {r['unseen_auc']:.4f}",
                 f"{r['seen_rej_f1']:.2f} → {r['unseen_rej_f1']:.2f}",
                 f"{r['seen_gmiou1']:.2f} → {r['unseen_gmiou1']:.2f}"]
        result_rows.append([TITLES[r['dataset']], NAMES[r['backbone']]] + cells)
    results = table(['数据', '模型', 'AUROC', 'Rej-F1（%）', 'G-mIoU@1（%）'], result_rows)
    overall = table(['数据', '模型', '整体 Rej-F1', '整体拒绝率', 'Seen 正例误拒率', 'Unseen 正例误拒率', '整体 G-mIoU@1'],
        [[TITLES[r['dataset']], SHORT[r['backbone']]] + [f'{r[k]:.2f}%' for k in ('rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1')]
        for r in summary])
    text = f'''# GMR 未见语义泛化评测

视频时刻检索根据一句查询，在视频中找出对应事件的时间段。然而，只考察事件存在时的定位表现，无法说明模型能否拒绝未发生的事件，也无法说明这两种能力能否推广到训练未见的语义。我们关注：**当查询中的动作或组合未进入下游训练时，模型还能判断事件是否发生，并在发生时准确定位吗？** 为此，我们整理了四套含正负查询的数据，用 Seen 样本训练和选模，分别衡量 Seen 与 Unseen 的存在判断、拒绝和端到端定位表现。实验显示，未见语义下的存在分数排序能力普遍下降；拒绝与定位分数还需结合正负比例和正例误拒率解释。

本页汇总 **四套数据、三个模型、48 个完成的评测设置**。模型为 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR。更新于 2026-10-11。

## 四套数据的详细实验结果

| 数据集 | 详细结果 README | 完成情况 |
| --- | --- | --- |
| Clean v3（未补充负例） | [数据与最终实验结果](experiments/agy_test/v3_release_baselines_20261009/README.md) | 五划分 × 三模型，15/15 |
| Balanced v3（补充跨视频负例） | [数据与最终实验结果](experiments/agy_test/v3_balanced_baselines_20261010/README.md) | 五划分 × 三模型，15/15 |
| Charades-CG v2（官方组合划分） | [数据制作与 Seen→Unseen 评测](experiments/agy_test/publication_review_20261011/charades_cg/README.md) | C3_CG × 三模型，3/3 |
| Soccer-GMR-Unseen v1 | [数据制作与泛化退化评测](experiments/agy_test/publication_review_20261011/soccer_unseen/README.md) | 五划分 × 三模型，15/15 |

各入口包含训练与评估协议、最终结果或其完整表格链接。三项指标的逐划分数值与置信区间另见[统一详细结果表](docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md)。

## 四套数据集

**一个样本是一对视频与查询**：正例有事件时间窗，负例的时间窗为空，模型应当拒绝。Seen/Unseen 则表示查询是否命中当前划分指定的 **Unseen 的语义**，与正负标签相互独立；因此 Test 同时包含 S+、S−、U+、U−，并非全部是 Unseen。

下面四张图分别说明**来源、负例设计、Unseen 的语义和实际样本数**。A 组测试动作泛化，C 组测试组合泛化；所有模型仅用 S+/S− 训练，并用 Seen 验证选择 checkpoint 和阈值。

### Clean v3：固定视频，修改查询

![Clean v3 数据集：来源、负例、Unseen 的语义与各组规模](assets/gmr_baseline_summary_20261011/reader/dataset_clean_v3.svg)

*Clean 通过修改动作或对象构造候选，再进行文本语义审核。五组规定不同的 Unseen 语义，共用视频分配与完整 Test 样本；训练排除命中 Unseen 语义的完整查询。[数据说明](data/release/semantic_existence_v3_release/README.md)*

### Balanced v3：保留原样本，跨视频补齐负例

![Balanced v3 数据集：原样本保留、跨视频增补与正负分布](assets/gmr_baseline_summary_20261011/reader/dataset_balanced_v3.svg)

*Balanced 完整保留 Clean，再追加跨视频伪负例，使每个完整 train/val/test 正负 1:1；Seen、Unseen 子集仍可能不平衡。[数据说明](data/release/semantic_existence_v3_balanced/README.md)*

### Charades-CG v2：保留官方未见组合，配对跨视频负例

![Charades-CG v2 数据集：官方组合身份、负例配对与 C3_CG 规模](assets/gmr_baseline_summary_20261011/reader/dataset_charades_cg_v2.svg)

*CG 沿用官方 Test-Trivial 为 Seen、Novel-Composition 为 Unseen，不套用 A1–C2 规则。每个正例构造一个跨视频负例，Seen Test 与 Unseen Test 各自正负 1:1。[数据说明](data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/README.md)*

Balanced 与 CG 的负例借鉴 [Moment of Untruth §3.3](https://arxiv.org/html/2502.08544v2#S3.SS3)：在同组、同 train/val/test 内，CLIP 比较查询与候选视频已有的正描述，每个视频取最高相似度，再从排名最低的一半视频中采样。排除原视频和含相同查询的视频；Balanced 另过滤重复与语义冲突。**低相似度不能证明事件缺席**，这些新增负例均未逐视频验证。

### Soccer：沿用已有正负例，构建动作与球队组合划分

![Soccer 数据集：来源标注、动作与球队组合、特征过滤后的规模](assets/gmr_baseline_summary_20261011/reader/dataset_soccer_v1.svg)

*Soccer 本次未生成新负例，沿用 WorldCup 2022 来源标签；图中列出特征过滤后真正进入实验的数量。C1/C2 每个动作指定 8 支球队，训练另删除相关动作的泛指球队查询，测试泛指查询仍为 Seen。[数据说明](data/release/soccer_gmr_unseen_v1/README.md) · [具体球队与复现记录](README_ENGINEERING.md)*

Unseen 指下游训练中的语义划分，不表示 CLIP/SlowFast 预训练从未接触这些概念。五组复用视频与查询，不能将组间数量相加作为独立数据量。

## 数据规模与分布

{sizes}

![完整测试集的正负分布](assets/gmr_baseline_summary_20261011/reader/test_balance.svg)

*条内为实际样本数；每条对应一个完整测试集。五组复用视频与查询，不能把五组行数相加当作独立样本。整体正负平衡也不保证 Seen、Unseen 各自平衡。*

Soccer 原发布每组 Test 有 2,246 条；4 个片段未得到完整特征，关联母池 37 条查询被排除，其中 Test 排除 13 条，实际测试 **2,233 条**。三个模型使用相同副本，原发布保留不变。

<details>
<summary>查看每组 Test 的 Seen / Unseen 正负数量</summary>

{detailed_counts}

</details>

## 实验结果

三个指标分别回答：**AUROC**——存在分数能否区分正负例；**Rej-F1**——是否正确拒绝缺席查询；**G-mIoU@1**——把拒绝与时间定位合起来，最终输出是否正确。

下表为 **Seen → Unseen**。Clean、Balanced、Soccer 各自取五划分等权平均；Charades-CG 为 C3_CG 单划分。各数据集独立汇总，分数不能直接当作跨数据集的方法收益。

{results}

![三项指标的 Seen 到 Unseen 差距](assets/gmr_baseline_summary_20261011/reader/generalization_summary.svg)

*Gap = Seen − Unseen，单位为百分点：右侧表示 Unseen 较低，左侧表示 Unseen 较高。误差线为 2,000 次视频簇 bootstrap 的 95% CI。Moment / QD / Flash 分别对应三个 backbone；图中汇总范围与上表相同。*

**存在判断的排序能力普遍下降。** Clean 三模型的 AUROC Gap 为 18.96–20.76 pp，Balanced 为 3.52–10.98 pp，Soccer 为 12.52–18.20 pp；这些宏平均区间均高于 0。Charades-CG 的 Moment、Flash 同样下降，QD 的 AUROC 接近 0.5，Gap 区间跨 0。

**拒绝和定位指标并不总是一起下降。** 负 Gap 按原符号保留。特别是 Rej-F1 和 G-mIoU 会受到测试子集正负比例影响，不能仅凭它们较高就认定泛化更好。

例如 Soccer C2/QD 的 73 条 Unseen 正例中，**72 条被误拒**，但 Unseen G-mIoU 仍为 65.09%：该子集还有 139 条负例，正确拒绝负例也会得到分数。Balanced QD 在 C1/C2 甚至拒绝全部 Unseen 正例。因此必须同时看存在判断、定位分数和正例误拒率。

<details>
<summary>查看整体拒绝、正例误拒和端到端定位结果</summary>

{overall}

拒绝率为全部测试查询中被拒绝的比例；正例误拒率为真实存在事件被拒绝的比例。汇总范围与主要结果表一致。

</details>

## 完整结果与阅读说明

[全部 48 个设置、逐划分指标与 95% CI](docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md) · [各划分完整样本数](docs/gmr_baseline_summary_20261011/DATASET_COUNTS.md) · [工程实验与复现记录](README_ENGINEERING.md)

[原分支 README：实验报告归档](README_EXPERIMENT_REPORT.md)原样保留发布前的详细报告；[工程实验版](README_ENGINEERING.md)包含本次集成的四套数据与 Soccer 实验记录。

本次使用单个训练种子，checkpoint 与阈值只由 Seen 验证确定。置信区间反映固定模型的视频抽样不确定性；Soccer 按片段聚类，不能据此声称整场比赛独立。负例没有逐视频确认缺席，结果以当前构造／来源标签为准。

这些实验均为独立 baseline；Unseen Net Gain、Seen Change、Gap Reduction 需要同版本、同划分、同 backbone 的新方法对照，本次不定义。

## 数据、训练测试与模型代码路径

[完整路径索引（Markdown）](docs/gmr_baseline_summary_20261011/DATA_CODE_PATHS.md)列出了四套数据的发布标注、逐组训练/验证/测试输入、三个 backbone 的训练与推理脚本、模型源码与配置、冻结预测和本机特征/权重目录。

| 数据 | 实际输入 | 训练总控 | 测试与评测总控 | 当前结果对应的模型源码 |
| --- | --- | --- | --- | --- |
| Clean v3 | [冻结标注](experiments/agy_test/v3_release_baselines_20261009/groups) | [run_baselines.py](experiments/agy_test/v3_release_baselines_20261009/run_baselines.py) | [run_baselines.py](experiments/agy_test/v3_release_baselines_20261009/run_baselines.py) / [最终评测](experiments/agy_test/v3_release_baselines_20261009/finalize_baselines.py) | [native_source/models](experiments/agy_test/v3_release_baselines_20261009/native_source/models) |
| Balanced v3 | [冻结标注](experiments/agy_test/v3_balanced_baselines_20261010/groups) | [run_baselines.py](experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py) | [run_baselines.py](experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py) | [native_source/models](experiments/agy_test/v3_balanced_baselines_20261010/native_source/models) |
| Charades-CG v2 | [C3_CG 标注](data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG) | [原 v1 训练](experiments/agy_test/charades_cg_baselines_20261010/run_baselines.py) | [v2 重新测试](experiments/agy_test/charades_cg_v2_evaluation_20261011/run_baselines.py) | [源码快照/models](experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models) |
| Soccer | [特征过滤后标注](data/experiment_inputs/soccer_unseen_baselines_20261011/splits) | [run_baselines.py](experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py) | [run_baselines.py](experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py) | [源码快照/models](experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models) |

三个 backbone 的具体 train.py、evaluate.py / inference.py、模型与 GMR 分支路径均在完整索引中逐项链接。CG v2 复用 v1 冻结模型和阈值；Soccer 脚本为本机实验的归档快照，运行目录与本机视频、特征和 checkpoint 路径见该索引。
'''
    (ROOT / 'README.md').write_text(text, encoding='utf-8')


def main():
    rows, counts = read('metrics.json'), read('dataset_counts.json')
    summary = [next(r for r in rows if r['dataset'] == ds and r['split'] == ('C3_CG' if ds == 'Charades-CG v2' else 'MACRO')
                    and r['backbone'] == bb) for ds in DATASETS for bb in BACKBONES]
    overview()
    from build_gmr_dataset_profiles import main as dataset_profiles
    dataset_profiles()
    composition(counts)
    gaps(summary)
    write_readme(rows, counts, summary)
    print('Reader README, four dataset profiles and summary figures generated from frozen results.')


if __name__ == '__main__':
    main()
