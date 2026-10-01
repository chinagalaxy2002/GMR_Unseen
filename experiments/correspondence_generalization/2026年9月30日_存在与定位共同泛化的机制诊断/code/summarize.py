"""Joint original-video bootstrap for three frozen holdout families."""
import collections
import argparse
import json
from pathlib import Path

import numpy as np
from phase2 import HERE, STAGE, dump, hit, rows, sha

FAMILIES = ('throw', 'open_close', 'sit')
RUNS = {'throw': HERE / 'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1'}
RUNS.update({f: STAGE / 'runs' / f'{f}_qd_gmr_baseline_s3407_attempt1' for f in FAMILIES[1:]})
METRICS = ('AUROC', 'raw_R1_05', 'gated_R1_05', 'FRR', 'RR', 'raw_correct_rejected_rate')


def pack(run, split):
    gtpath = run / ('views/pseudo.jsonl' if split == 'pseudo' else 'views/val_seen.jsonl')
    predpath = run / ('pseudo_predictions.jsonl' if split == 'pseudo' else 'best_seen_predictions.jsonl')
    rr = rows(gtpath)
    pp = {str(r['qid']): r for r in rows(predpath)}
    assert len(pp) == len(rr) and all(str(r['qid']) in pp for r in rr)
    threshold = json.loads((run / 'threshold_frozen.json').read_text())['threshold']
    y = np.array([r['exist_label'] for r in rr])
    score = np.array([pp[str(r['qid'])]['pred_exist_score'] for r in rr])
    raw = np.array([hit(pp[str(r['qid'])], r, 'pred_relevant_windows_pre_exist') if r['exist_label'] else False for r in rr])
    gated = np.array([hit(pp[str(r['qid'])], r, 'pred_relevant_windows') if r['exist_label'] else False for r in rr])
    return {'rows': rr, 'y': y, 'score': score, 'raw': raw, 'gated': gated,
            'reject': score < threshold, 'threshold': threshold,
            'hashes': {str(p): sha(p) for p in (gtpath, predpath, run / 'threshold_frozen.json')}}


def evaluate(d, weights):
    y = d['y']
    pos, neg = y == 1, y == 0
    p, n = weights[pos].sum(), weights[neg].sum()
    if p == 0 or n == 0:
        return None
    # Exact weighted rank AUC with .5 credit for equal stored scores.
    _, inv = np.unique(d['score'], return_inverse=True)
    wp = np.bincount(inv, weights=weights * pos)
    wn = np.bincount(inv, weights=weights * neg, minlength=len(wp))
    auc = np.dot(wp, np.cumsum(wn) - wn * .5) / (p * n)
    correct = weights[d['raw'] & pos].sum()
    return np.array([auc, correct / p, weights[d['gated'] & pos].sum() / p,
                     weights[d['reject'] & pos].sum() / p, weights[d['reject'] & neg].sum() / n,
                     weights[d['raw'] & pos & d['reject']].sum() / correct if correct else np.nan])


def interval(values, level):
    values = np.asarray(values)
    valid = values[np.isfinite(values)]
    return {'ci_level': level, 'ci': np.quantile(valid, [(1-level)/2, (1+level)/2]).tolist() if len(valid) else None,
            'valid_resamples': len(valid)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--closeout',action='store_true');args=parser.parse_args()
    if args.closeout:
        closeout=json.loads((STAGE/'closeout_state.json').read_text())
        assert closeout['state']=='diagnostics_completed_summary_pending'
        RUNS['sit']=STAGE/'diagnostics/sit/baseline/evaluation_bundle'
    else:
        queue = json.loads((STAGE / 'queue_state.json').read_text())
        assert queue['state'] == 'diagnostics_completed_decision_pending', queue['state']
    for path in ('diagnostics/BASELINE_METRICS.json','report/CROSS_FAMILY_COVERAGE.json','report/CONTROLLED_QUERY_SUMMARY.json','report/GRADIENT_SUMMARY.json'):
        assert not (STAGE/path).exists(), f'Refusing overwrite: {path}'
    data = {(f, s): pack(RUNS[f], s) for f in FAMILIES for s in ('pseudo', 'seen')}
    videos = sorted({r['vid'] for d in data.values() for r in d['rows']})
    vindex = {v: i for i, v in enumerate(videos)}
    indices = {k: np.array([vindex[r['vid']] for r in d['rows']]) for k, d in data.items()}
    controlled_pairs = {}
    controlled_points = {}
    controlled_samples = {f: [] for f in FAMILIES}
    for f in FAMILIES:
        control = json.loads((STAGE / 'diagnostics' / f / 'baseline/CONTROLLED_QUERY.json').read_text())
        scores = control['scores']
        byquery = collections.defaultdict(list)
        for r in data[f, 'pseudo']['rows']:
            if str(r['qid']) in scores:
                byquery[r['query']].append(r)
        pairs = []
        for rr in byquery.values():
            for a in rr:
                for b in rr:
                    if a['exist_label'] == 1 and b['exist_label'] == 0 and a['vid'] != b['vid']:
                        x, y = scores[str(a['qid'])], scores[str(b['qid'])]
                        pairs.append((float(x > y) + .5 * float(x == y), vindex[a['vid']], vindex[b['vid']]))
        assert len(pairs) == control['pairs']
        controlled_pairs[f] = np.asarray(pairs).reshape(-1, 3)
        controlled_points[f] = float(np.mean([p[0] for p in pairs])) if pairs else float('nan')
    rng = np.random.default_rng(3407)
    samples = {k: [] for k in data}
    points = {k: evaluate(d, np.ones(len(d['rows']))) for k, d in data.items()}
    for _ in range(1000):
        weight = np.bincount(rng.integers(0, len(videos), len(videos)), minlength=len(videos))
        for k, d in data.items():
            result = evaluate(d, weight[indices[k]])
            samples[k].append(result if result is not None else np.full(len(METRICS), np.nan))
        for f, pairs in controlled_pairs.items():
            endpoints = weight[pairs[:, 1].astype(int)] * weight[pairs[:, 2].astype(int)]
            controlled_samples[f].append(float(np.dot(pairs[:, 0], endpoints) / endpoints.sum()) if endpoints.sum() else float('nan'))
    result = {'state': 'completed', 'training_updates': 0, 'true_U_access': False,
              'seed': 3407, 'resamples': 1000, 'original_video_union': len(videos),
              'bootstrap': 'sample union of original videos once per replicate; reuse common multiplicities across all families and splits; equal family means',
              'intervals': 'baseline absolute uncertainty only, not paired candidate gains or seed stability',
              'source_sha256': sha(Path(__file__)), 'families': {}, 'equal_family_mean': {}}
    result['training_scope']='Saved seen-selected checkpoints; throw/open_close trained 100 epochs, sit stopped after 77 logged epochs. No new training; cross-family mean descriptive, not uniform completed-budget evidence.'
    coverage = {}
    for f in FAMILIES:
        result['families'][f] = {}
        coverage[f] = {}
        for split in ('pseudo', 'seen'):
            k = (f, split)
            d = data[k]
            sample = np.asarray(samples[k])
            result['families'][f][split] = {
                'metrics': {name: {'point': float(points[k][i]), **interval(sample[:, i], .975 if i < 2 else .95)} for i, name in enumerate(METRICS)},
                'threshold': d['threshold'], 'source_hashes': d['hashes'],
                'raw_correct_rejected_denominator': int((d['raw'] & (d['y'] == 1)).sum()),
            }
            rr = d['rows']
            byv = collections.defaultdict(set)
            for r in rr:
                byv[r['vid']].add(r['exist_label'])
            coverage[f][split] = {'rows': len(rr), 'positive': int(d['y'].sum()), 'negative': int((d['y']==0).sum()),
                                  'videos': len(byv), 'unique_query_strings': len({r['query'] for r in rr}),
                                  'mixed_label_videos': sum(len(v)==2 for v in byv.values())}
        controlled = json.loads((STAGE / 'diagnostics' / f / 'baseline/CONTROLLED_QUERY.json').read_text())
        coverage[f]['same_query_control'] = {k: controlled[k] for k in ('query_groups','rows','pairs','pairacc','video_endpoint_bootstrap_ci95')}
        increments = json.loads((STAGE / 'diagnostics' / f / 'baseline/VISUAL_INCREMENT.json').read_text())
        dump(STAGE / 'diagnostics' / f / 'baseline/SCORE_COMPARABILITY.json', {
            'state': 'completed', 'training_updates': 0, 'splits': increments,
            'limitations': 'Within/cross-video rank decomposition uses original queries and labels; differing compositions do not prove video bias. Identical string ranks before feature control are not a text tie control.',
        })
    for split in ('pseudo', 'seen'):
        point = np.mean([points[f, split] for f in FAMILIES], axis=0)
        sample = np.mean([np.asarray(samples[f, split]) for f in FAMILIES], axis=0)
        result['equal_family_mean'][split] = {name: {'point': float(point[i]), **interval(sample[:, i], .975 if i < 2 else .95)} for i, name in enumerate(METRICS)}
    overlap = {f'{a}:{b}': len({r['vid'] for r in data[a,'pseudo']['rows']} & {r['vid'] for r in data[b,'pseudo']['rows']}) for i,a in enumerate(FAMILIES) for b in FAMILIES[i+1:]}
    coverage['pseudo_video_overlap'] = overlap
    coverage['limitations'] = 'Families share original videos and annotation construction; not independent domains or trials. Annotated action plus lexical isolation is not complete conceptual isolation.'
    dump(STAGE / 'diagnostics/BASELINE_METRICS.json', result)
    dump(STAGE / 'report/CROSS_FAMILY_COVERAGE.json', coverage)
    control_mean_samples = np.mean([controlled_samples[f] for f in FAMILIES], axis=0)
    dump(STAGE / 'report/CONTROLLED_QUERY_SUMMARY.json', {
        'state': 'completed', 'seed': 3407, 'resamples': 1000, 'training_updates': 0,
        'families': {f: {'point': controlled_points[f], 'pairs': len(controlled_pairs[f]), **interval(controlled_samples[f], .95)} for f in FAMILIES},
        'equal_family_mean': {'point': float(np.mean(list(controlled_points.values()))), **interval(control_mean_samples, .95)},
        'bootstrap': 'same original-video union multiplicities as baseline metric summary; pair receives product of endpoint weights; each family weighted equally',
        'limitations': 'Sparse same-query support only, not whole-family accuracy; pair combinations and shared videos correlated; replicates without a valid family pair denominator are unavailable, not replaced by .5. Individual CONTROLLED_QUERY intervals sample each family endpoint set and may differ from this joint-union summary.',
    })
    gradient = {}
    for family, method in [(f,'baseline') for f in FAMILIES] + [('throw','adapter')]:
        checkpoints = {}
        for c in ('best','latest'):
            d = json.loads((STAGE / 'diagnostics' / family / method / f'GRADIENT_RELATIONS_{c}.json').read_text())
            assert d['training_updates'] == 0 and d['state'] == 'completed'
            blocks = {k: {key: value for key,value in v.items() if key in ('valid_batches','invalid_batches','median_cosine','negative_fraction')} for k,v in d['blocks'].items()}
            conflict = [k for k,v in blocks.items() if k.endswith('|loc') and v['median_cosine'] is not None and v['median_cosine'] < 0 and v['negative_fraction'] > .5]
            detail=json.loads((STAGE/'diagnostics'/family/method/'GRADIENT_DETAIL.json').read_text())['checkpoints'][c]
            checkpoints[c] = {'epoch_zero_based': d.get('checkpoint_epoch_zero_based',detail['checkpoint_epoch_zero_based']), 'checkpoint_sha256': d['checkpoint_sha256'],
                              'batches':len(d['qids']), 'sample_qids_sha256':sha_manifest(d['qids']), 'blocks':blocks,
                              'qualifying_loc_blocks':conflict, 'at_least_two_loc_blocks':len(conflict)>=2,
                              'saliency_loss_weight':d['loss_weights'].get('loss_saliency'),
                              'saliency_limit':'No active saliency objective when weight=0; missing saliency gradients do not indicate agreement.'}
        checkpoints['distinct_epochs'] = checkpoints['best']['epoch_zero_based'] != checkpoints['latest']['epoch_zero_based']
        details=json.loads((STAGE/'diagnostics'/family/method/'GRADIENT_DETAIL.json').read_text())['checkpoints']
        checkpoints['distinct_weights'] = details['best']['model_tensor_sha256'] != details['latest']['model_tensor_sha256']
        checkpoints['stable_within_family_loc_clue'] = checkpoints['distinct_epochs'] and checkpoints['distinct_weights'] and all(checkpoints[c]['at_least_two_loc_blocks'] for c in ('best','latest'))
        gradient[f'{family}/{method}'] = checkpoints
    dump(STAGE / 'report/GRADIENT_SUMMARY.json', gradient)
    print(json.dumps({'state':'completed','baseline_equal_family_mean':result['equal_family_mean'],'gradient_clue':{k:v['stable_within_family_loc_clue'] for k,v in gradient.items()}},indent=2))


def sha_manifest(value):
    import hashlib
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


if __name__ == '__main__':
    main()
