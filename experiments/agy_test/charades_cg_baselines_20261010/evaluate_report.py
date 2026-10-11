"""Report all three metrics without inventing a Seen test subset."""
import csv
import json
from pathlib import Path
import numpy as np
from common import ROOT, REPO, BACKBONES, read_rows, save_json

NAMES = {'moment': 'Moment-DETR-GMR', 'qd': 'QD-DETR-GMR', 'flash': 'FlashVTG-GMR'}


def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return None
    return value


def fmt(value, digits=2):
    return 'N/A' if value is None else f'{value:.{digits}f}'


def report():
    import importlib.util
    spec = importlib.util.spec_from_file_location('gmr_summary', REPO / 'scripts/summarize_gmr_degradation.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records, intervals = [], {}
    for bb in BACKBONES:
        folder = ROOT / 'groups/C3_CG/evaluation' / bb
        if not (folder / 'metrics.json').exists():
            continue
        base = json.loads((folder / 'metrics.json').read_text())
        cached = folder / 'subset_metrics.json'
        if cached.exists():
            detail = json.loads(cached.read_text())
        else:
            point, ci, draws, videos, counts = module.summarize(folder / 'predictions.npz', 2000, 3407)
            detail = clean(dict(point=point, ci=ci, counts=counts))
            save_json(cached, detail)
            np.savez_compressed(folder / 'subset_bootstrap_draws.npz', draws=draws,
                                videos=videos, keys=np.array(module.KEYS))
        counts = detail['counts']
        rec = clean(dict(**base, **detail['point'], seen_positive_n=counts['S']['positive'],
            seen_negative_n=counts['S']['negative'], unseen_positive_n=counts['U']['positive'],
            unseen_negative_n=counts['U']['negative'], unseen_net_gain=None,
            seen_change=None, gap_reduction=None))
        records.append(rec)
        absolute = json.loads((folder / 'bootstrap.json').read_text())['absolute']
        intervals[bb] = clean(dict(absolute=absolute, subset=detail['ci']))
    out = ROOT / 'evaluation'
    out.mkdir(exist_ok=True)
    save_json(out / 'metrics.json', records)
    save_json(out / 'degradation_metrics.json', records)
    save_json(out / 'bootstrap.json', intervals)
    save_json(out / 'degradation_bootstrap.json', intervals)
    if records:
        for name in ['metrics.csv', 'degradation_metrics.csv']:
            with (out / name).open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(records[0]))
                writer.writeheader()
                writer.writerows(records)
    lines = ['# C3_CG baseline evaluation', '', f'Completed settings: {len(records)}/3.', '',
        'Source test contains only U+ (2,990) and U− (2,990). Seen test metrics and Seen−Unseen gaps are N/A. '
        'Seen validation selects checkpoints and thresholds; its scores are not substituted for Seen test. '
        'Standalone baseline net gains/change/reduction are N/A. No five-split macro average applies.', '',
        '| Backbone | Seen AUROC | Unseen AUROC | Performance Gap | Unseen Net Gain | Unseen AUROC 95% CI | Seen Change | Gap Reduction |',
        '|---|---:|---:|---:|---:|---|---:|---:|']
    for r in records:
        ci = intervals[r['backbone']]['absolute']['unseen_auc']
        lines.append(f"| {NAMES[r['backbone']]} | N/A | {fmt(r['unseen_auc'],4)} | N/A | N/A | [{ci[0]:.4f}, {ci[1]:.4f}] | N/A | N/A |")
    lines += ['', '| Backbone | Overall Rej-F1 (%) | RR (%) | S+ FRR | U+ FRR (%) | Overall G-mIoU@1 (%) |',
        '|---|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {NAMES[r['backbone']]} | {fmt(r['rej_f1'])} | {fmt(r['rr'])} | N/A | {fmt(r['u_frr'])} | {fmt(r['gmiou1'])} |")
    lines += ['', '| Backbone | Seen Rej-F1 | Unseen Rej-F1 (%) | Rej-F1 Gap | Seen G-mIoU@1 | Unseen G-mIoU@1 (%) | G-mIoU Gap |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {NAMES[r['backbone']]} | N/A | {fmt(r['unseen_rej_f1'])} | N/A | N/A | {fmt(r['unseen_gmiou1'])} | N/A |")
    lines += ['', '| Backbone | Unseen Rej-F1 95% CI (%) | Unseen G-mIoU@1 95% CI (%) | U+ | U− |', '|---|---|---|---:|---:|']
    for r in records:
        cis = intervals[r['backbone']]['subset']
        a = cis['unseen_rej_f1']['ci95']; b = cis['unseen_gmiou1']['ci95']
        lines.append(f"| {NAMES[r['backbone']]} | [{a[0]:.2f}, {a[1]:.2f}] | [{b[0]:.2f}, {b[1]:.2f}] | {r['unseen_positive_n']} | {r['unseen_negative_n']} |")
    lines += ['', 'Seed 3407, 2,000 video-cluster bootstrap draws; frozen Seen-validation checkpoint and BA threshold. '
        'Moment/QD use native 4-decimal existence probabilities; Flash uses native 6-decimal logits. '
        'Rej-F1 treats rejection as positive. G-mIoU@1 uses each backbone’s native top-1 set IoU; '
        'rejected negatives score 1 and rejected positives score 0. F1/G-mIoU depend on class proportions. '
        'Negative labels are CLIP-reassigned construction labels, without video absence verification.', '']
    content = '\n'.join(lines)
    (out / 'STANDARD_EVALUATION.md').write_text(content)
    (out / 'GENERALIZATION_DROP_COMPARISON.md').write_text(content)


if __name__ == '__main__':
    report()
