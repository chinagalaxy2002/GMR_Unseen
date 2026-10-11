#!/usr/bin/env python3
"""Draw construction explanations as editable SVG, PDF and PNG figures.

Examples and counts come from the publication's frozen annotations. Video
symbols identify records; they do not depict or synthesize video frames.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs/gmr_baseline_summary_20261011'
ASSETS = ROOT / 'assets/gmr_baseline_summary_20261011'
INK = '#243746'
MUTED = '#526572'
BLUE = '#0072B2'
ORANGE = '#B95000'
TEAL = '#00846A'
LINE = '#C7D1D8'
PALE_BLUE = '#EDF6FC'
PALE_ORANGE = '#FFF3E8'


def read_json(path):
    return json.loads(path.read_text())


class Figure:
    """Small vector drawing vocabulary with explicit coordinates and text."""

    def __init__(self, name, height, title, subtitle):
        self.name = name
        self.height = height
        self.items = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" '
            f'viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{html.escape(title)}</title>',
            f'<desc id="desc">{html.escape(subtitle)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker></defs>',
            '<rect width="1200" height="100%" fill="white"/>',
            '<g font-family="Noto Sans CJK SC, Noto Sans CJK JP, sans-serif">',
        ]
        self.text(30, 43, title, 28, weight='bold')
        self.text(30, 77, subtitle, 19, MUTED)

    def text(self, x, y, value, size=22, color=INK, weight='normal', anchor='start'):
        self.items.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(value))}</text>')

    def lines(self, x, y, values, size=21, color=INK, step=34):
        for i, value in enumerate(values):
            self.text(x, y + i * step, value, size, color)

    def rect(self, x, y, w, h, fill='white', stroke=LINE, radius=6, dashed=False):
        dash = ' stroke-dasharray="7 5"' if dashed else ''
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                          f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')

    def line(self, x1, y1, x2, y2, color=LINE, arrow=False, dashed=False):
        marker = ' marker-end="url(#arrow)"' if arrow else ''
        dash = ' stroke-dasharray="7 5"' if dashed else ''
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                          f'stroke="{color}" stroke-width="2"{marker}{dash}/>')

    def panel(self, x, y, w, h, label, color=INK, fill='white'):
        self.rect(x, y, w, h, fill)
        self.text(x + 20, y + 36, label, 23, color, 'bold')
        self.line(x + 20, y + 52, x + w - 20, y + 52)

    def video(self, x, y, vid, color=INK):
        self.rect(x, y, 142, 49, 'white', color, radius=3)
        for dx in (8, 125):
            for dy in (7, 20, 33):
                self.rect(x + dx, y + dy, 8, 7, color, color, radius=0)
        self.text(x + 71, y + 32, vid, 21, color, 'bold', 'middle')

    def timeline(self, x, y, width, record, color):
        duration = record['duration']
        self.rect(x, y, width, 12, '#EDF0F2', '#EDF0F2', radius=0)
        for start, end in record['relevant_windows']:
            self.rect(x + width * start / duration, y, width * (end - start) / duration,
                      12, color, color, radius=0)
        if not record['relevant_windows']:
            self.line(x, y + 6, x + width, y + 6, MUTED, dashed=True)
        self.text(x, y + 38, '0', 16, MUTED)
        self.text(x + width, y + 38, f'{duration:.1f} s', 16, MUTED, anchor='end')

    def save(self):
        import cairosvg
        ASSETS.mkdir(parents=True, exist_ok=True)
        data = ('\n'.join(self.items) + '\n</g></svg>\n').encode()
        (ASSETS / f'{self.name}.svg').write_bytes(data)
        cairosvg.svg2pdf(bytestring=data, write_to=str(ASSETS / f'{self.name}.pdf'))
        cairosvg.svg2png(bytestring=data, write_to=str(ASSETS / f'{self.name}.png'), output_width=1800)


def overview():
    f = Figure('construction_overview', 450, '从视频–查询配对到泛化评测',
               '同一个基准同时回答：事件是否存在？在哪里发生？训练未见语义是否仍能识别？')
    stages = [
        ('01  原始正例', ['视频 + 原始查询', '保留事件时间窗'], INK),
        ('02  构造负例', ['同视频改动作 / 对象', '或同查询换目标视频'], TEAL),
        ('03  确定语义身份', ['A1–A3：动作留出', 'C1–C2 / CG：组合'], ORANGE),
        ('04  训练与选模', ['训练：S+ / S−', '选模：Seen val'], BLUE),
        ('05  四分区测试', ['S+   S−   U+   U−', '存在判断 + 时间定位'], INK),
    ]
    for i, (title, lines, color) in enumerate(stages):
        x = 30 + 234 * i
        f.panel(x, 126, 204, 174, title, color)
        f.lines(x + 15, 216, lines, 18, step=34)
        if i < 4:
            f.line(x + 208, 212, x + 228, 212, MUTED, arrow=True)
    f.line(30, 337, 1170, 337)
    f.text(40, 382, '任务 A  事件存在判断', 23, TEAL, 'bold')
    f.text(40, 420, '存在 → 接受；缺席 → 拒绝', 21)
    f.text(430, 382, '任务 B  时间定位', 23, BLUE, 'bold')
    f.text(430, 420, '存在的事件 → 预测时间窗', 21)
    f.text(810, 382, '泛化轴  Seen → Unseen', 23, ORANGE, 'bold')
    f.text(810, 420, '动作或动作–对象组合留出', 21)
    return f


def negative_ideas(examples):
    e = examples[4]
    f = Figure('negative_construction_ideas', 600, '两种负样本构造：改变查询，或改变配对视频',
               'C2 冻结 Test 实例：open × box 为 Unseen；彩色字段标出变化发生在哪里。')
    f.panel(30, 112, 550, 390, '(a) Clean v3 · 固定视频，最小语义改写', BLUE, PALE_BLUE)
    f.panel(620, 112, 550, 390, '(b) Balanced v3 / CG v2 · 原句跨视频配对', TEAL)
    source, neg = e['clean_negative_source'], e['clean_unseen_negative']
    f.video(54, 192, source['vid'])
    f.text(219, 223, '同一目标视频', 22)
    f.text(54, 280, source['query'], 26, BLUE)
    f.text(54, 316, 'S+   [[18.7, 30.4]] 秒', 21, BLUE)
    f.line(313, 270, 313, 366, MUTED, arrow=True)
    f.text(335, 348, 'bag → box', 24, ORANGE, 'bold')
    f.text(54, 412, neg['query'], 26, ORANGE)
    f.text(54, 453, 'U−   []   语义审计后保留', 21, ORANGE)
    pos, neg = e['unseen_positive'], e['balanced_unseen_negative']
    f.text(644, 216, pos['query'], 26, ORANGE)
    f.text(644, 252, '查询文本与 Unseen 身份保持不变', 21)
    f.video(644, 291, pos['vid'], ORANGE)
    f.line(797, 316, 975, 316, MUTED, arrow=True)
    f.text(887, 299, '换目标视频', 20, TEAL, anchor='middle')
    f.video(995, 291, neg['vid'], TEAL)
    f.text(644, 381, 'U+  [[14.7, 21.2]] 秒', 21, ORANGE)
    f.text(995, 381, 'U−  []', 21, ORANGE)
    f.text(644, 430, 'CLIP 文本排名 → 低相似候选 → 采样', 22, TEAL)
    f.text(644, 468, '复用真实查询，重新构造视频–查询配对', 21)
    f.text(42, 548, '思路来源：本项目早期最小改写候选', 21, BLUE)
    f.text(630, 548, '思路来源：Moment of Untruth (WACV 2025)', 20, TEAL)
    f.text(630, 579, '§3.3  In-Domain negative sampling', 20, TEAL)
    return f


def sample_matrix(examples):
    e = examples[5]
    source_path = ROOT / e['source_file']
    seen_pos = e['seen_positive']
    with source_path.open() as stream:
        seen_neg = next(record for record in (json.loads(line) for line in stream)
                        if record['partition'] == 'S-' and
                        record.get('source_qid') == seen_pos['qid'])
    f = Figure('sample_partition_matrix', 660, 'S/U × +/−：语义身份与目标视频中的存在标签',
               'Charades-CG v2 真实配对：同行查询不变，换视频后由存在正例变为缺席负例。')
    f.text(340, 127, '存在 +  ·  保留原始时间窗', 23, TEAL, 'bold', 'middle')
    f.text(894, 127, '缺席 −  ·  relevant_windows = []', 23, MUTED, 'bold', 'middle')
    quartet = [('S+', seen_pos, BLUE, 60, 153), ('S−', seen_neg, BLUE, 645, 153),
               ('U+', e['unseen_positive'], ORANGE, 60, 395),
               ('U−', e['charades_unseen_negative'], ORANGE, 645, 395)]
    for label, record, color, x, y in quartet:
        f.rect(x, y, 500, 215, PALE_BLUE if label[0] == 'S' else PALE_ORANGE)
        f.text(x + 20, y + 36, label, 27, color, 'bold')
        f.text(x + 88, y + 36, 'Seen · 官方 Test-Trivial' if label[0] == 'S'
               else 'Unseen · 官方 Novel-Composition', 20, color)
        f.text(x + 20, y + 76, record['query'], 25)
        f.video(x + 20, y + 95, record['vid'], color)
        windows = record['relevant_windows']
        f.text(x + 183, y + 126, f'{windows} 秒' if windows else '[]  → 拒绝该配对', 20, color)
        f.timeline(x + 20, y + 160, 455, record, color)
    for y in (260, 502):
        f.line(570, y, 633, y, MUTED, arrow=True)
    f.text(600, 647, '横向：换目标视频，不改变查询的 S/U 身份；纵向：查询的语义类别不同。',
           21, MUTED, anchor='middle')
    return f, seen_neg


def clean_pipeline():
    f = Figure('clean_construction', 650, 'Clean v3：语义改写候选 → 审计发布池 → 五组语义留出',
               '先判断查询是否真的改变了事件语义，再按完整查询中的已发生事件确定 Seen / Unseen。')
    f.panel(30, 116, 340, 194, '01  原始正例与历史候选')
    f.lines(50, 205, ['Charades 原句 + 时间窗', '固定视频，改动作或对象', 'bag → box；run → walk'], 21)
    f.panel(430, 116, 340, 194, '02  逐 qid 语义审计', TEAL)
    f.lines(450, 205, ['对齐原始 GT 与事件结构', '筛除同义、蕴含、歧义', '以及与正例冲突的候选'], 21)
    f.panel(830, 116, 340, 194, '03  干净发布池', TEAL)
    f.text(855, 215, '15,034  正例 qid', 26, TEAL, 'bold')
    f.text(855, 266, '2,869    不同负例 qid', 25, MUTED, 'bold')
    f.line(378, 212, 418, 212, MUTED, arrow=True)
    f.line(778, 212, 818, 212, MUTED, arrow=True)
    f.panel(30, 356, 730, 198, '04  动作 / 组合规则 → S/U 身份', ORANGE, PALE_ORANGE)
    f.text(50, 443, '动作留出', 22, ORANGE, 'bold')
    f.text(180, 443, 'A1 拿取/放置   A2 饮用/倾倒   A3 跑步/行走', 21)
    f.text(50, 488, '组合留出', 22, ORANGE, 'bold')
    f.text(180, 488, 'C1 坐 × 床/椅/沙发   C2 开/关 × 箱/柜', 21)
    f.text(50, 531, '任一已发生事件命中留出规则 → 完整查询为 Unseen', 21, ORANGE)
    f.panel(830, 356, 340, 198, '05  固定且互斥的视频分配', BLUE, PALE_BLUE)
    f.lines(850, 442, ['Train：S+ / S−', '选模与阈值：val_seen', 'Val / Test 归档：四分区'], 21)
    f.line(1000, 312, 1000, 338, MUTED)
    f.line(1000, 338, 395, 338, MUTED)
    f.line(395, 338, 395, 352, MUTED, arrow=True)
    f.line(768, 455, 818, 455, MUTED, arrow=True)
    f.text(40, 610, 'C2 示例：open × bag → Seen；open × box → Unseen（open 动作仍可在 Seen 中出现）。',
           22, MUTED)
    return f


def balanced_pipeline(examples, counts):
    e = examples[4]
    old = next(r for r in counts if r['dataset'] == 'Clean v3' and r['split'] == 'C2_v3' and r['partition'] == 'test')
    new = next(r for r in counts if r['dataset'] == 'Balanced v3' and r['split'] == 'C2_v3' and r['partition'] == 'test')
    pos = old['S+'] + old['U+']
    neg = old['S-'] + old['U-']
    f = Figure('balanced_construction', 765, 'Balanced v3：保留原样本，按组补齐跨视频负例',
               '每个 group / split 独立操作；查询文本与原 S/U 身份继承自 donor 正例。')
    f.panel(30, 116, 340, 180, '01  保留 Clean v3')
    f.lines(50, 203, ['原 qid、查询、视频与窗口', '标签与 S/U 身份全部保留', '统计需要补充的负例数量'], 21)
    f.panel(430, 116, 340, 180, '02  原句 + 候选目标视频', ORANGE)
    f.lines(450, 203, ['“person open a box.”', 'Donor：FNBYE，身份 U+', '候选来自同 group / split'], 21)
    f.panel(830, 116, 340, 180, '03  CLIP 文本最大相似度', TEAL)
    f.lines(850, 203, ['查询 vs 视频的全部正描述', '每个目标视频取最高余弦值', 's(q,v) = max cos(q, caption)'], 20)
    f.line(378, 206, 418, 206, MUTED, arrow=True)
    f.line(778, 206, 818, 206, MUTED, arrow=True)
    f.panel(30, 346, 665, 202, '04  按视频分数排名，先取最低一半', TEAL)
    for i in range(10):
        x = 52 + i * 61
        f.rect(x, 445, 50, 47, '#DEF1EB' if i < 5 else '#EFF1F3', TEAL if i < 5 else LINE)
        f.text(x + 25, 477, i + 1, 22, TEAL if i < 5 else MUTED, anchor='middle')
    f.text(50, 425, '排名示意（10 个候选）', 19, MUTED)
    f.text(50, 532, '低相似 ←  排序  → 高相似；保留前 floor(N/2) 个视频', 20, TEAL)
    f.panel(755, 346, 415, 202, '05  过滤后采样，追加负例', TEAL)
    f.lines(775, 433, ['去重 / 相同描述 / 语义冲突检查', 'seed 3407 → FNBYE 换为 TCI7K', '“person open a box.” → U−，[]'], 21)
    f.line(1000, 298, 1000, 324, MUTED)
    f.line(1000, 324, 360, 324, MUTED)
    f.line(360, 324, 360, 342, MUTED, arrow=True)
    f.line(703, 449, 743, 449, MUTED, arrow=True)
    f.panel(30, 590, 1140, 140, '结果示例：C2 Test（完整 split 正负平衡）', BLUE, PALE_BLUE)
    f.text(50, 676, f'原 {pos:,} 正 + {neg:,} 负   +   新增 {pos-neg:,} 负   →   {pos:,} 正 + {new["S-"]+new["U-"]:,} 负',
           26, BLUE, 'bold')
    f.text(50, 713, 'Train 只增加 S−；Val / Test 的新增 S−、U− 配额按原 S+、U+ 比例分配。', 21)
    return f


def cg_pipeline(counts):
    f = Figure('charades_cg_construction', 720, 'Charades-CG v2：官方组合身份 → 联合测试池跨视频配对',
               'C3_CG 使用官方划分；每个正例原句配一个负例，Train / Val / Test 视频互斥。')
    sources = [('官方 Train', 'Seen 正例', BLUE), ('Test-Trivial', 'Seen Test 正例', BLUE),
               ('Novel-Composition', 'Unseen Test 正例', ORANGE)]
    for i, (name, kind, color) in enumerate(sources):
        x = 30 + 400 * i
        f.panel(x, 112, 340, 126, name, color)
        f.text(x + 20, 204, kind, 23, color)
        f.line(x + 170, 243, x + 170, 281, MUTED, arrow=True)
    f.rect(30, 288, 1140, 63, '#F4F7F9')
    f.text(600, 328, '统一时间窗清理：0 ≤ start < end ≤ duration；删除 2,119 条异常正例',
           24, INK, anchor='middle')
    f.line(200, 355, 200, 387, MUTED, arrow=True)
    f.line(800, 355, 800, 387, MUTED, arrow=True)
    train = next(r for r in counts if r['dataset'] == 'Charades-CG v2' and r['partition'] == 'train')
    val = next(r for r in counts if r['dataset'] == 'Charades-CG v2' and r['partition'] == 'val_seen')
    test = next(r for r in counts if r['dataset'] == 'Charades-CG v2' and r['partition'] == 'test')
    f.panel(30, 394, 340, 232, 'Train / Seen validation', BLUE, PALE_BLUE)
    f.lines(50, 483, ['按视频划分，seed 3407', f'Train  {train["S+"]:,} 正 + {train["S-"]:,} 负',
                      f'Val      {val["S+"]:,} 正 + {val["S-"]:,} 负', '与 v1 逐字节相同'], 21, step=37)
    f.panel(430, 394, 740, 232, 'Seen 与 Unseen 共用联合测试候选池', ORANGE, PALE_ORANGE)
    f.text(450, 482, 'Test-Trivial 视频 ∪ Novel-Composition 视频', 24, ORANGE, 'bold')
    f.text(450, 524, '两类正描述共同评分 → CLIP 最大余弦排名最低一半', 22)
    f.text(450, 563, '原句与 S/U 不变 → 换目标视频 → 每个正例对应一个负例', 22)
    f.text(450, 605, f'S+ / S− 各 {test["S+"]:,}；U+ / U− 各 {test["U+"]:,} → 共 {test["total"]:,} 条',
           25, ORANGE, 'bold')
    f.text(40, 682, '实际 U+ → U−：“person opens laptop.”  保持原句，目标视频 2ECXI → P5ANU，窗口变为 []。',
           22, MUTED)
    return f


def example_atlas(examples):
    f = Figure('semantic_example_atlas', 1430, '六个语义划分的真实例子：Seen / Unseen 与两种负例',
               '均来自冻结 Test 标注；英文保留原句，时间单位为秒。蓝色 Seen，橙色 Unseen。')
    rules = ['动作：物理放置 / 拿取', '动作：饮用 / 倾倒', '动作：跑步 / 行走',
             '组合：坐 × 床 / 椅 / 沙发', '组合：开 / 关 × 箱 / 柜', '官方组合：本例 open × laptop']
    for i, e in enumerate(examples):
        x = 30 + (i % 2) * 590
        y = 116 + (i // 2) * 430
        f.panel(x, y, 550, 406, f'{e["split"]}  |  {rules[i]}', ORANGE)
        for row, (label, key, color) in enumerate([('S+', 'seen_positive', BLUE), ('U+', 'unseen_positive', ORANGE)]):
            record = e[key]
            ry = y + 88 + row * 88
            f.text(x + 18, ry, label, 23, color, 'bold')
            f.text(x + 71, ry, record['query'], 23, color)
            f.text(x + 71, ry + 32, f'{record["vid"]}  ·  {record["relevant_windows"]} s', 19, MUTED)
        f.line(x + 18, y + 236, x + 530, y + 236)
        if 'clean_unseen_negative' in e:
            source, neg = e['clean_negative_source'], e['clean_unseen_negative']
            # Preserve the exact source and generated strings; split long text
            # into separate lines rather than silently paraphrasing annotations.
            f.text(x + 18, y + 267, f'Clean U−  ·  视频 {neg["vid"]} 不变', 20, MUTED, 'bold')
            f.text(x + 18, y + 299, source['query'] + ' →', 20)
            f.text(x + 18, y + 331, neg['query'] + '  []', 20, ORANGE)
            neg = e['balanced_unseen_negative']
            f.text(x + 18, y + 369, f'Balanced U−  ·  原 U+ 查询不变：{neg["source_vid"]} → {neg["vid"]}',
                   20, TEAL, 'bold')
            f.text(x + 18, y + 396, '换目标视频；relevant_windows = []', 18, MUTED)
        else:
            neg = e['charades_unseen_negative']
            f.text(x + 18, y + 274, '官方 Novel-Composition 决定 Unseen 身份', 21, ORANGE)
            f.text(x + 18, y + 321, 'CG U−  ·  person opens laptop.', 22, TEAL, 'bold')
            f.text(x + 18, y + 360, f'原句不变：{neg["source_vid"]} → {neg["vid"]}；[]', 22)
            f.text(x + 18, y + 396, '每个官方正例配一个跨视频负例', 19, MUTED)
    return f


def main():
    examples = read_json(REPORT / 'PIPELINE_EXAMPLES.json')['examples']
    counts = read_json(REPORT / 'dataset_counts.json')
    matrix, seen_negative = sample_matrix(examples)
    figures = [overview(), negative_ideas(examples), matrix, clean_pipeline(),
               balanced_pipeline(examples, counts), cg_pipeline(counts), example_atlas(examples)]
    for figure in figures:
        figure.save()
        print(f'Saved {figure.name}: SVG / PDF / PNG')
    provenance = {
        'generator': str(Path(__file__).relative_to(ROOT)),
        'examples': 'docs/gmr_baseline_summary_20261011/PIPELINE_EXAMPLES.json',
        'counts': 'docs/gmr_baseline_summary_20261011/dataset_counts.json',
        'clean_pool_counts': 'data/release/semantic_existence_v3_release/README.md',
        'negative_sampling_reference': 'https://arxiv.org/html/2502.08544v2#S3.SS3',
        'matrix_seen_negative': seen_negative,
        'rank_diagram': 'Schematic ranks 1–10 illustrate bottom-half selection; not measured CLIP scores.',
        'exports': {f.name: [f'assets/gmr_baseline_summary_20261011/{f.name}.{suffix}'
                             for suffix in ('svg', 'pdf', 'png')] for f in figures},
        'video_symbols': 'Video IDs with abstract filmstrip symbols; no generated video frames.',
    }
    (REPORT / 'CONSTRUCTION_FIGURES.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
