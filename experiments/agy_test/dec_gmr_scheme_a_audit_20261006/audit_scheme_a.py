"""Read-only Scheme A replay and ranking diagnostics; never overwrites experiment outputs."""
from pathlib import Path
import importlib.util
import json
import hashlib
import numpy as np
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'experiments/agy_test/detr_decoder_gmr'
spec = importlib.util.spec_from_file_location('scheme_a_original', BASE / 'evaluate_dec_gmr.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def cdf(reference, values):
    reference = np.sort(reference)
    return (np.searchsorted(reference, values, 'left') + np.searchsorted(reference, values, 'right')) / (2 * len(reference))

def aucs(score, data):
    s = np.isin(data['partitions'], ['S+', 'S-'])
    u = np.isin(data['partitions'], ['U+', 'U-'])
    seen = float(roc_auc_score(data['labels'][s], score[s]))
    unseen = float(roc_auc_score(data['labels'][u], score[u]))
    return {'seen': seen, 'unseen': unseen, 'gap': seen - unseen}

def main():
    details = []
    manifest = {}
    def record(p):
        manifest[str(p.relative_to(ROOT))] = {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'resolved_path': str(p.resolve())}
        return p
    record(BASE / 'evaluate_dec_gmr.py')
    record(BASE / 'benchmark_summary.json')
    reported = json.loads((BASE / 'benchmark_summary.json').read_text())['macro_summary']
    for split in original.SPLITS:
        tr = np.load(record(BASE / 'cache' / split / 'train.npz'))
        te = np.load(record(BASE / 'cache' / split / 'test.npz'))
        saved = np.load(record(BASE / 'runs' / split / 'predictions.npz'))
        train_gt = {str(r['qid']): r for r in rows(record(ROOT / 'data/release/semantic_existence_v2' / split / 'train.jsonl'))}
        test_rows = rows(record(ROOT / 'data/release/semantic_existence_v2' / split / 'test.jsonl'))
        test_gt = {str(r['qid']): r for r in test_rows}
        assert list(map(str, te['qids'])) == [str(r['qid']) for r in test_rows]
        assert all(int(y) == test_gt[str(q)]['exist_label'] and str(v) == test_gt[str(q)]['vid'] for q, y, v in zip(te['qids'], te['labels'], te['vids']))
        assert all(train_gt[str(q)]['partition'] in ['S+', 'S-'] for q in tr['qids'])
        assert all(np.array_equal(te[k], saved[k]) for k in ['qids', 'vids', 'labels', 'partitions'])
        ev = original.route_query_evidence([test_gt[str(q)]['query'].lower() for q in te['qids']], te['X'])
        ev_tr = original.route_query_evidence([train_gt[str(q)]['query'].lower() for q in tr['qids']], tr['X'])
        n = len(ev)
        er = np.argsort(np.argsort(ev)) / n
        ea = (rankdata(ev, method='average') - 1) / n
        et = cdf(ev_tr, ev)
        perm = np.random.RandomState(3407).permutation(n)
        inv = np.argsort(perm)
        ep = (np.argsort(np.argsort(ev[perm])) / n)[inv]
        for bb, (_, col) in original.BACKBONES.items():
            det = te['X'][:, col]
            dr = np.argsort(np.argsort(det)) / n
            da = (rankdata(det, method='average') - 1) / n
            scores = {
                'baseline': det,
                'original': dr ** .65 * er ** .85,
                'test_average_ties': da ** .65 * ea ** .85,
                'train_reference_cdf': cdf(tr['X'][:, col], det) ** .65 * et ** .85,
                'original_shuffled_order': ((np.argsort(np.argsort(det[perm])) / n)[inv]) ** .65 * ep ** .85,
            }
            replay = float(np.max(abs(scores['original'] - saved['pred_dec_' + bb])))
            assert replay < 1e-12, (split, bb, replay)
            details.append({'split': split, 'backbone': bb, 'replay_error': replay,
                            'max_order_change': float(np.max(abs(scores['original'] - scores['original_shuffled_order']))),
                            'detector_unique_fraction': len(np.unique(det)) / n,
                            'metrics': {name: aucs(score, te) for name, score in scores.items()}})
        print('Checked', split, flush=True)
    macro = {}
    for bb in original.BACKBONES:
        subset = [r for r in details if r['backbone'] == bb]
        macro[bb] = {name: {key: float(np.mean([r['metrics'][name][key] for r in subset])) for key in ['seen', 'unseen', 'gap']}
                     for name in subset[0]['metrics']}
        for name, values in macro[bb].items():
            base = macro[bb]['baseline']
            values.update(unseen_gain=values['unseen'] - base['unseen'], seen_change=values['seen'] - base['seen'], gap_reduction=base['gap'] - values['gap'])
        for key, field in [('seen', 'dec_seen'), ('unseen', 'dec_unseen'), ('gap', 'dec_gap')]:
            assert abs(macro[bb]['original'][key] - reported[bb][field]) < 1e-12
    result = {'protocol': 'Frozen replay; no retraining, no original outputs overwritten. Alternative ranking results are diagnostics on shared cached evidence; no new bootstrap CIs.',
              'numpy_version': np.__version__, 'macro': macro, 'details': details, 'max_replay_error': max(r['replay_error'] for r in details)}
    (OUT / 'audit_metrics.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'input_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'macro': macro, 'max_replay_error': result['max_replay_error']}, indent=2))

if __name__ == '__main__': main()
