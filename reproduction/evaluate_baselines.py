"""Evaluate freshly inferred baselines using the published table protocol."""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from eval.metrics import compute_mAP, compute_mR, prepare_submission_for_gmiou, compute_G_mIoU

def rows(p):
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

def prediction_file(folder, bb, subset):
    name = {'flash': f'hl_{subset}_submission.jsonl', 'moment': f'moment_detr_gmr_{subset}_submission.jsonl',
            'qd': f'qd_detr_gmr_{subset}_submission.jsonl'}[bb]
    candidates = list(folder.rglob(name))
    if len(candidates) != 1: raise ValueError(f'Expected one {name} under {folder}, got {len(candidates)}')
    return candidates[0]

def scores(pred, bb):
    if bb == 'flash':
        logits = np.array([r['pred_exist_logit'] for r in pred], dtype=np.float32)
        return 1 / (1 + np.exp(-logits))
    return np.array([r['pred_exist_score'] for r in pred], dtype=np.float32)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--predictions', type=Path, default=ROOT / 'reproduction_outputs/baseline_predictions')
    p.add_argument('--output', type=Path, default=ROOT / 'reproduction_outputs/baseline_metrics')
    p.add_argument('--splits', nargs='+', default=['A1', 'A2_alt', 'A3', 'C1', 'C2_alt'])
    p.add_argument('--models', nargs='+', choices=['flash', 'moment', 'qd'], default=['flash', 'moment', 'qd'])
    a = p.parse_args(); detail = []
    for split in a.splits:
        va = {str(r['qid']): r for r in rows(ROOT / f'features/semantic_existence_v2/{split}/val_seen.jsonl')}
        gt = {str(r['qid']): dict(r, qid=str(r['qid'])) for r in rows(ROOT / f'data/release/semantic_existence_v2/{split}/test.jsonl')}
        for bb in a.models:
            vp = rows(prediction_file(a.predictions / split / bb / 'val', bb, 'val'))
            tp = rows(prediction_file(a.predictions / split / bb / 'test', bb, 'test'))
            assert len(vp) == len(va) and set(str(r['qid']) for r in vp) == set(va)
            assert len(tp) == len(gt) and set(str(r['qid']) for r in tp) == set(gt)
            vy = np.array([va[str(r['qid'])]['exist_label'] for r in vp])
            vs, ts = scores(vp, bb), scores(tp, bb)
            grid = np.linspace(.01, .99, 100)
            tau = float(grid[np.argmax([np.mean(vs[vy == 1] >= t) - np.mean(vs[vy == 0] >= t) for t in grid])])
            group_auc = {}
            for group, partitions in [('Seen', ['S+', 'S-']), ('Unseen', ['U+', 'U-']), ('All', ['S+', 'S-', 'U+', 'U-'])]:
                ix = [i for i, r in enumerate(tp) if gt[str(r['qid'])]['partition'] in partitions]
                truth = [gt[str(tp[i]['qid'])] for i in ix]
                y = np.array([r['exist_label'] for r in truth]); score = ts[ix]
                ps = [dict(tp[i], qid=str(tp[i]['qid']), pred_exist_score=float(ts[i] >= tau)) for i in ix]
                gated, _ = prepare_submission_for_gmiou(ps, .5, 10)
                positives = [i for i, r in enumerate(truth) if r['exist_label'] == 1]
                pg, pp = [truth[i] for i in positives], [ps[i] for i in positives]
                auc = 100 * float(roc_auc_score(y, score)); group_auc[group] = auc
                detail.append({'split': split, 'model': bb, 'group': group, 'threshold': tau, 'AUROC': auc,
                               'Rej-F1': 100 * float(f1_score(1-y, score < tau, zero_division=0)),
                               'mAP': compute_mAP(pp, pg, num_workers=1)['mAP'],
                               **{k: v for k, v in compute_mR(pp, pg, k_list=(1, 5)).items() if k in ['mR@1', 'mR@5']},
                               **compute_G_mIoU(gated, truth, k_list=(1, 3))})
            for r in detail[-3:]: r['Gap'] = group_auc['Seen'] - group_auc['Unseen']
    keys = ['AUROC', 'Rej-F1', 'mAP', 'mR@1', 'mR@5', 'G-mIoU@1', 'G-mIoU@3', 'Gap']
    macro = []
    for bb in a.models:
        for group in ['Seen', 'Unseen', 'All']:
            selected = [r for r in detail if r['model'] == bb and r['group'] == group]
            macro.append({'model': bb, 'group': group, **{k: float(np.mean([r[k] for r in selected])) for k in keys}})
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / 'metrics.json').write_text(json.dumps({'protocol': 'Fresh baseline inference; Seen-val grid threshold; equal split means; percentages', 'macro': macro, 'details': detail}, indent=2)+'\n')
    header = ['Model', 'Group'] + keys
    lines = ['| ' + ' | '.join(header) + ' |', '| ' + ' | '.join(['---'] * len(header)) + ' |']
    for r in macro: lines.append('| ' + ' | '.join([r['model'], r['group']] + [f'{r[k]:.2f}' for k in keys]) + ' |')
    (a.output / 'BASELINE_TABLE.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__ == '__main__': main()
