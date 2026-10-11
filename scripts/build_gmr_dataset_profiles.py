#!/usr/bin/env python3
"""Render four dataset information figures from frozen construction/count data."""
import json
from pathlib import Path

import render_gmr_construction_figures as drawing

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/gmr_baseline_summary_20261011/reader'
BLUE, ORANGE, INK = '#0072B2', '#B95000', '#243746'
MUTED, LINE = '#526572', '#DCE4EA'

CHARADES_SEMANTICS = [
    ('A1', '物理放置 / 拿取'),
    ('A2', '饮用 / 倾倒'),
    ('A3', '跑步 / 行走'),
    ('C1', '坐 × 床 / 椅子 / 沙发'),
    ('C2', '打开或关闭 × 箱子 / 柜子'),
]

PROFILES = [
    dict(dataset='Clean v3', name='dataset_clean_v3', title='Clean v3｜同视频语义改写',
         subtitle='Charades 室内活动 · 同时测试未见动作与未见动作–对象组合',
         source=['正例：Charades 原始查询与时间窗。',
                 '审核后样本池：15,034 正例 + 2,869 负例。'],
         negative_label='视频固定   →   修改动作 / 对象',
         negative=['沿用早期反事实候选，逐句审核完整事件。',
                   '排除语义重合、歧义及构造错误的候选。',
                   '保留的负例标为缺席，时间窗为空。'],
         semantics=CHARADES_SEMANTICS,
         semantic_note='整句中任一已断言发生的事件命中规则 → Unseen',
         footer='文本语义审核不能证明视频中缺席；五组复用样本，不能相加作为独立数据。',
         source_path='data/release/semantic_existence_v3_release/README.md'),
    dict(dataset='Balanced v3', name='dataset_balanced_v3', title='Balanced v3｜保留 Clean，跨视频补负例',
         subtitle='沿用 Clean 的正例和五组 Unseen 语义 · 每个完整划分正负 1:1',
         source=['Clean 的原始正负样本与语义身份全部保留。',
                 '每组 Test 再增加 2,295 个跨视频伪负例。'],
         negative_label='真实查询不变   →   配给另一视频',
         negative=['同组、同 train/val/test 内，用 CLIP 排名。',
                   '每视频取描述最高相似度，从最低一半采样。',
                   '排除原视频、同句、重复和语义冲突，再补齐。'],
         semantics=CHARADES_SEMANTICS,
         semantic_note='新增负例继承查询的 S/U 身份；Train 只补 S−',
         footer='新增负例借鉴 Moment of Untruth §3.3；整体 1:1 不等于 Seen、Unseen 各自 1:1。',
         source_path='data/release/semantic_existence_v3_balanced/README.md'),
    dict(dataset='Charades-CG v2', name='dataset_charades_cg_v2', title='Charades-CG v2｜官方组合泛化 + 跨视频负例',
         subtitle='保留官方 Test-Trivial / Novel-Composition 身份 · 独立单划分 C3_CG',
         source=['正例：官方 Train 与两个测试子集。',
                 '异常、越界时间窗直接删除；不包含 Novel-Word。'],
         negative_label='每个正例查询   →   一个跨视频负例',
         negative=['同划分内，CLIP 比较查询与视频全部正描述。',
                   '每视频取最高相似度，从最低一半随机采样。',
                   '排除原视频及同句；两个 Test 共用候选池。'],
         semantics=[('训练', '官方 Train → Seen'),
                    ('Seen', '官方 Test-Trivial'),
                    ('Unseen', '官方 Novel-Composition')],
         semantic_note='S/U 身份继承官方；没有改成 A1–C2 规则',
         footer='负例借鉴 Moment of Untruth §3.3；Seen Test、Unseen Test 各自正负 1:1。',
         source_path='data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/README.md'),
    dict(dataset='Soccer-GMR v1', name='dataset_soccer_v1', title='Soccer｜既有足球标注，重新组织语义划分',
         subtitle='WorldCup 2022 · 动作泛化与动作–球队组合泛化 · 图中为实际实验输入',
         source=['正负例均来自已有 WorldCup 2022 标注。',
                 '剔除矛盾、重复、正负冲突和时间越界样本。'],
         negative_label='沿用源负例   →   本次不生成新负例',
         negative=['原查询、存在标签和正例时间窗保持不变。',
                   '4 个片段缺完整特征，关联 37 条查询移除。',
                   '其中 Test 移除 13 条：2,246 → 2,233。'],
         semantics=[('A1', '盘带 dribble'), ('A2', '射门 shot'),
                    ('A3', '拦截 interception'),
                    ('C1', '封堵 / 解围 × 指定球队'),
                    ('C2', '盘带 / 拦截 × 指定球队')],
         semantic_note='C1/C2：每个动作 8 支球队，按训练支持量选取',
         footer='C1/C2 训练删去相关泛指球队查询，测试泛指仍属 Seen；原发布未改动。',
         source_path='data/release/soccer_gmr_unseen_v1/README.md'),
]


def figure(profile, counts):
    dataset = profile['dataset']
    test = [r for r in counts if r['dataset'] == dataset and r['partition'] == 'test']
    positives = {r['S+'] + r['U+'] for r in test}
    negatives = {r['S-'] + r['U-'] for r in test}
    assert len(positives) == len(negatives) == 1
    positive, negative = next(iter(positives)), next(iter(negatives))
    assert (ROOT / profile['source_path']).exists()
    f = drawing.Figure(profile['name'], 920, profile['title'], profile['subtitle'])
    cards = [
        (30, 'Unseen 语义划分', '5 组' if len(test) == 5 else '1 组 · C3_CG', INK, '#F4F7FA'),
        (420, '每组 Test 正例 · 事件存在', f'{positive:,}', BLUE, '#EDF6FC'),
        (810, '每组 Test 负例 · 标注缺席', f'{negative:,}', ORANGE, '#FFF3E8'),
    ]
    for x, label, value, color, fill in cards:
        f.rect(x, 105, 360, 91, fill, LINE, radius=8)
        f.text(x + 18, 135, label, 20, MUTED)
        f.text(x + 18, 177, value, 31, color, 'bold')

    f.panel(30, 220, 550, 109, '样本来源', INK)
    f.lines(48, 292, profile['source'], 21, step=27)
    # Keep the source text below the panel divider while preserving whitespace.
    f.panel(30, 345, 550, 200, '负例设计', ORANGE)
    f.rect(48, 411, 514, 38, '#FFF3E8', '#FFF3E8')
    f.text(305, 437, profile['negative_label'], 22, ORANGE, 'bold', 'middle')
    f.lines(48, 479, profile['negative'], 21, step=27)

    f.panel(620, 220, 550, 325, '哪些查询属于 Unseen？', BLUE)
    if dataset == 'Charades-CG v2':
        for i, (label, description) in enumerate(profile['semantics']):
            y = 311 + 61 * i
            color = ORANGE if label == 'Unseen' else BLUE
            f.rect(640, y - 26, 510, 43, '#F4F7FA', '#F4F7FA')
            f.text(652, y + 3, label, 23, color, 'bold')
            f.text(753, y + 3, description, 22)
    else:
        for i, (label, description) in enumerate(profile['semantics']):
            y = 308 + 43 * i
            f.text(642, y, label, 23, BLUE, 'bold')
            f.text(714, y, description, 22)
            if i < 4:
                f.line(642, y + 14, 1148, y + 14, LINE)
    f.text(640, 525, profile['semantic_note'], 19, MUTED)

    table_height = 275 if len(test) == 5 else 150
    f.panel(30, 565, 1140, table_height, '实际使用的样本数 · 单位：视频–查询配对', INK)
    test_videos = {r['videos'] for r in test}
    assert len(test_videos) == 1
    f.text(1148, 601, f'每组 Test：{next(iter(test_videos)):,} 个视频 / 片段',
           19, MUTED, anchor='end')
    headings = [('划分', 82), ('Train', 258), ('Seen Val', 429),
                ('Test S+', 606), ('Test S−', 773), ('Test U+', 939), ('Test U−', 1104)]
    for label, x in headings:
        color = BLUE if ' S' in label else ORANGE if ' U' in label else MUTED
        f.text(x, 646, label, 21, color, 'bold', 'middle')
    for i, row in enumerate(test):
        group = row['split']
        train = next(r for r in counts if r['dataset'] == dataset and r['split'] == group and r['partition'] == 'train')
        val = next(r for r in counts if r['dataset'] == dataset and r['split'] == group and r['partition'] in ('val', 'val_seen'))
        assert train['U+'] == train['U-'] == 0
        values = [group.split('_')[0] if group != 'C3_CG' else group,
                  f"{train['total']:,}", f"{val['S+'] + val['S-']:,}"]
        values.extend(f"{row[part]:,}" for part in ('S+', 'S-', 'U+', 'U-'))
        y = 684 + i * 33
        if i % 2 == 0:
            f.rect(43, y - 25, 1114, 32, '#F4F7FA', '#F4F7FA', radius=2)
        for value, (_, x) in zip(values, headings):
            f.text(x, y, value, 22, INK, anchor='middle')

    if len(test) == 1:
        # The single CG split has enough room for a visual 2x2 explanation.
        for x, label, p, n, color in (
                (30, 'Seen Test · Test-Trivial', test[0]['S+'], test[0]['S-'], BLUE),
                (620, 'Unseen Test · Novel-Composition', test[0]['U+'], test[0]['U-'], ORANGE)):
            f.rect(x, 737, 550, 103, '#F4F7FA', LINE)
            f.text(x + 18, 771, label, 22, color, 'bold')
            f.text(x + 18, 815, f'{p:,} 正例 + {n:,} 负例 = {p+n:,} 条', 25)

    f.text(30, 869, 'S = Seen，U = Unseen；+ 有时间窗，− 空时间窗。训练与选模只用 Seen。', 21, MUTED)
    f.text(30, 901, profile['footer'], 20, MUTED)
    f.save()


def main():
    drawing.ASSETS = ASSETS
    counts = json.loads((ROOT / 'docs/gmr_baseline_summary_20261011/dataset_counts.json').read_text())
    for profile in PROFILES:
        figure(profile, counts)
    print('Four dataset profiles rendered from frozen sample counts.')


if __name__ == '__main__':
    main()
