#!/usr/bin/env python3
"""Render five split explanations from frozen, unaugmented v3 test JSONL files."""
import argparse
import json
import hashlib
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

GROUPS = {
    'A1_v3': ('物理放置 / 拿取', ['物理放置', '物理拿取', '同时放置与拿取'],
              'person puts a box on the closet shelf.',
              'person take the laptop.'),
    'A2_v3': ('饮用 / 倾倒', ['饮用', '倾倒'],
              'person drinking from a cup.',
              'person drink a cup of coffee.'),
    'A3_v3': ('跑步 / 行走', ['跑步', '行走'],
              'person runs up the stairs.',
              'a person walks into the laundry room.'),
    'C1_v3': ('坐 × 床 / 椅子 / 沙发', ['坐在床上', '坐在椅子上', '坐在沙发上'],
              'a person sits in a chair.',
              'person sit on the sofa.'),
    'C2_v3': ('打开 / 关闭 × 箱子 / 柜子', ['打开箱子', '关闭箱子', '打开柜子', '关闭柜子'],
              'person opens a box.',
              'one person closes a box of shoes.'),
}


def category(group, row):
    events = row['events']
    if group.startswith('A'):
        mapping = {'A1_v3': {'physical_place': '物理放置', 'physical_take': '物理拿取'},
                   'A2_v3': {'drink': '饮用', 'pour': '倾倒'},
                   'A3_v3': {'run': '跑步', 'walk': '行走'}}[group]
        found = {mapping[e['action_family']] for e in events if e['action_family'] in mapping}
        if group == 'A1_v3' and len(found) == 2:
            return '同时放置与拿取'
        assert len(found) == 1, (group, row['qid'], found)
        return found.pop()
    found = set()
    for e in events:
        action, obj = e['action_family'], e.get('anchor_object', '')
        if group == 'C1_v3' and action == 'sit':
            for word, label in [('bed', '坐在床上'), ('chair', '坐在椅子上'),
                                ('couch', '坐在沙发上'), ('sofa', '坐在沙发上')]:
                if word in obj:
                    found.add(label)
        elif group == 'C2_v3' and action in ('open', 'close'):
            for word, label in [('box', '箱子'), ('cabinet', '柜子')]:
                if word in obj:
                    found.add(('打开' if action == 'open' else '关闭') + label)
    assert len(found) == 1, (group, row['qid'], found)
    return found.pop()


def render(group, rows, output):
    title, categories, positive, negative = GROUPS[group]
    counts = Counter(r['partition'] for r in rows)
    detail = {p: Counter(category(group, r) for r in rows if r['partition'] == p)
              for p in ('U+', 'U-')}
    assert sum(counts.values()) == 4611
    for query, part in [(positive, 'U+'), (negative, 'U-')]:
        assert any(r['query'] == query and r['partition'] == part for r in rows)
    neg = next(r for r in rows if r['query'] == negative and r['partition'] == 'U-')
    fig = plt.figure(figsize=(12, 7), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    def text(x, y, s, size=14, color='#263445', weight='normal', **kw):
        return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                       va='center', **kw)
    def box(x, y, w, h, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.012',
                                   facecolor=color, edgecolor='#DCE2E8', linewidth=.8))
    text(.04, .95, group.replace('_v3', '') + '  |  ' + title, 22, weight='bold')
    text(.04, .90, '未补充版 semantic_existence_v3_release · 完整 Test：4,611 条视频–查询配对', 13)
    box(.04, .76, .92, .095, '#F2F5F8')
    rule = '训练排除：包含上述任一已断言事件的完整查询；训练仅使用 Seen 正例 / 负例。'
    if group.startswith('C'):
        rule = '训练排除：包含上述已断言动作与对象组合的完整查询；其余组合按规则归为 Seen。'
    text(.06, .82, 'Unseen 的语义：' + title, 15, weight='bold')
    text(.06, .78, rule, 12)
    for x, name, p, n, color in [(.04, 'Seen', counts['S+'], counts['S-'], '#EFF5FC'),
                                (.28, 'Unseen', counts['U+'], counts['U-'], '#FFF4E8')]:
        box(x, .48, .215, .235, color)
        text(x+.015, .675, name, 18, weight='bold')
        text(x+.015, .62, f'正例  {p:,}', 17)
        text(x+.015, .57, f'负例  {n:,}', 17)
        text(x+.015, .515, f'合计  {p+n:,} 条', 14)
    text(.55, .69, 'Unseen 查询的语义分布', 16, weight='bold')
    text(.55, .645, '语义类别', 13, weight='bold')
    text(.825, .645, 'U+', 13, weight='bold', ha='center')
    text(.925, .645, 'U−', 13, weight='bold', ha='center')
    for i, label in enumerate(categories):
        y = .60 - i*.039
        text(.55, y, label, 13)
        text(.825, y, str(detail['U+'][label]), 14, ha='center')
        text(.925, y, str(detail['U-'][label]), 14, ha='center')
    ax.plot([.04, .96], [.445, .445], color='#DCE2E8', lw=.8)
    text(.04, .405, '实际查询示例（均来自本组 Test）', 15, weight='bold')
    text(.04, .355, 'U+  ' + positive, 14)
    text(.04, .31, 'U−  ' + negative, 14)
    text(.04, .265, '负例来源原句：' + neg['source_query'], 12, color='#596677')
    text(.04, .205, '正例有 GT 时间段；负例时间段为空。Unseen 由查询语义决定，存在 / 缺席由配对标签决定。', 12)
    box(.04, .075, .92, .085, '#F2F5F8')
    text(.06, .128, '退化评估：同一模型、同一冻结阈值，分别评估 Seen 与 Unseen，差距 = Seen − Unseen。', 12)
    text(.06, .09, '分别报告 AUROC、Rej-F1、G-mIoU@1；后两项差距也受两个子集正负比例影响。', 12)
    note = {'C1_v3': '对象归一：sofa / couch 均为沙发；电脑椅、床沿等按对应对象归类。',
            'C2_v3': '对象范围：包含文本明确关联柜子的柜门、抽屉；普通门或抽屉不自动归入。'}.get(group,
            '动作按完整句子的语义归类，不只匹配单词；同一句话可对应不同视频。')
    text(.04, .035, note, 11, color='#596677')
    for extension in ('svg', 'pdf', 'png'):
        fig.savefig(output / f'{group}.{extension}', dpi=180, facecolor='white')
    plt.close(fig)
    return {'group': group, 'counts': dict(counts), 'unseen_semantics': {p: dict(c) for p, c in detail.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, default=Path(__file__).resolve().parents[3] / 'data/release/semantic_existence_v3_release')
    args = parser.parse_args()
    plt.rcParams.update({'font.family': 'Noto Sans CJK JP', 'svg.fonttype': 'none', 'pdf.fonttype': 42})
    output = Path(__file__).resolve().parent
    summary = []
    for group in GROUPS:
        rows = [json.loads(line) for line in (args.release / 'splits' / group / 'test.jsonl').read_text().splitlines()]
        entry = render(group, rows, output)
        entry['test_sha256'] = hashlib.sha256((args.release / 'splits' / group / 'test.jsonl').read_bytes()).hexdigest()
        summary.append(entry)
    (output / 'counts.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')

if __name__ == '__main__':
    main()
