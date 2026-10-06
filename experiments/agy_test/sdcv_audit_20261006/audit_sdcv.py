"""Read-only replay of SDCV artifacts, with independent metrics and video bootstrap.

Original experiments are never modified. CPU inference; no retraining.
Run with /home/guoxiangyu/miniconda3/envs/univtg/bin/python.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
import json
import hashlib
from collections import Counter
import numpy as np
import torch
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'experiments/agy_test/semantic_directional_calibrated_verifier'
PREV = ROOT / 'experiments/agy_test/ddv_audit_20261006'
AC = ROOT / 'experiments/agy_test/aligned_calibration_verifier/aligned_features'
SPLITS = ['A1', 'A2_alt', 'A3', 'C1', 'C2_alt']
MANIFEST = {}

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

sys.path.insert(0, str(ROOT))
helper = module('ddv_audit_helpers', PREV / 'audit_ddv.py')
model = module('sdcv_model_replay', BASE / 'model.py')
torch.set_num_threads(2)

def record(path):
    path = path.absolute()
    MANIFEST[str(path.relative_to(ROOT))] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    return path

def load(path):
    with np.load(record(path)) as z:
        return {k: z[k] for k in z.files if k != 'q_proj_sent'}

def rows(path):
    return [json.loads(line) for line in record(path).read_text().splitlines() if line.strip()]

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def ci(x):
    return {'mean': float(np.mean(x)), 'ci95': np.quantile(x, [.025, .975]).tolist()}

def main():
    out = {'protocol': {'inference': 'CPU frozen checkpoints; original files read only; no retraining', 'bootstrap': '2000 shared-video clusters, RandomState(3407)', 'feature_audit': 'All 15 subset identity/label joins; 30 deterministic endpoint-feature checks per subset'}, 'splits': {}, 'subsets': {}, 'macro': {}}
    banks = {}
    clip_cache = {}
    for split in SPLITS:
        tr, val, te = [load(BASE / 'cache' / split / (sub + '.npz')) for sub in ['train', 'val', 'test']]
        for sub, d in [('train', tr), ('val', val), ('test', te)]:
            prev = load(ROOT / 'experiments/agy_test/decomposed_directional_verifier/cache' / split / (sub + '.npz'))
            a = load(AC / split / (sub + '.npz'))
            amap = {str(q): i for i, q in enumerate(a['qids'])}
            ai = np.array([amap[str(q)] for q in d['qids']])
            assert all(np.array_equal(d[k], prev[k]) for k in ['qids', 'vids', 'labels'])
            assert np.array_equal(d['vids'], a['vids'][ai]) and np.array_equal(d['labels'], a['labels'][ai])
            prefix_error = float(np.abs(d['X'][:, :12] - prev['X']).max())
            assert prefix_error == 0
            gt = rows(ROOT / 'data/release/semantic_existence_v2' / split / (sub + '.jsonl'))
            gm = {str(g['qid']): g for g in gt}
            assert len(set(d['qids'])) == len(d['qids'])
            assert all(int(gm[str(q)]['exist_label']) == int(y) for q, y in zip(d['qids'], d['labels']))
            assert all(str(gm[str(q)]['vid']) == str(v) for q, v in zip(d['qids'], d['vids']))
            parts = Counter(gm[str(q)]['partition'] for q in d['qids'])
            if sub in ['train', 'val']:
                assert set(parts) <= {'S+', 'S-'}
            errors, missing = [], 0
            for i in np.linspace(0, len(d['qids']) - 1, 30, dtype=int):
                v = str(d['vids'][i])
                if v not in clip_cache:
                    f = ROOT / 'features/charades_semantic_existence/clip' / (v + '.npz')
                    if not f.exists():
                        clip_cache[v] = None
                    else:
                        c = np.load(record(f))['features'].astype(np.float32)
                        clip_cache[v] = c / (np.linalg.norm(c, axis=-1, keepdims=True) + 1e-8)
                c = clip_cache[v]
                if c is None:
                    missing += 1
                    continue
                ix = ai[i]
                start, end = [max(0, min(len(c)-1, int(round(t * (len(c)-1))))) for t in a['best_spans'][ix]]
                recomputed = [np.dot(c[end], a[k][ix]) - np.dot(c[start], a[k][ix]) for k in ['q_proj_act', 'q_proj_obj']]
                errors.append(float(np.abs(d['X'][i, 12:14] - recomputed).max()))
            assert max(errors, default=0) < 1e-6
            neg = [gm[str(q)] for q, y in zip(d['qids'], d['labels']) if y == 0]
            out['subsets'][split + '/' + sub] = {'n': len(d['qids']), 'partitions': dict(parts), 'prefix_12d_max_error': prefix_error, 'signed_checks': len(errors), 'signed_max_error': max(errors, default=0), 'missing_clip_in_checks': missing, 'negative_construction_types': dict(Counter(g.get('construction_type', 'missing') for g in neg))}
        saved = load(BASE / 'runs' / split / 'predictions.npz')
        prev = load(PREV / split / 'audit_predictions.npz')
        assert all(np.array_equal(te[k], saved[k]) and np.array_equal(te[k], prev[k]) for k in ['qids', 'vids', 'labels', 'partitions'])
        index = {str(q): i for i, q in enumerate(te['qids'])}
        pairs = np.array([[index[str(p['positive_qid'])], index[str(p['negative_qid'])]] for p in rows(ROOT / 'data/release/semantic_existence_v2' / split / 'matched_u_pairs.jsonl')])
        rva, rte = helper.rank(tr['X'], val['X']), helper.rank(tr['X'], te['X'])
        scores, replay, params = {}, {}, {}
        vs = None
        for name, constructor, file, key in [('sdcv', lambda: model.SemanticDirectionalCalibratedVerifier(alpha_max=.60 if split == 'A3' else .55), 'best_model.pt', 'sdcv_scores'), ('det_mlp', model.DetectorOnlyMLP, 'best_det_mlp.pt', 'det_mlp_scores'), ('mm_mlp', model.MultimodalOnlyMLP, 'best_mm_mlp.pt', 'mm_mlp_scores')]:
            m = constructor().eval()
            m.load_state_dict(torch.load(record(BASE / 'runs' / split / file), map_location='cpu'))
            params[name] = sum(p.numel() for p in m.parameters())
            with torch.no_grad():
                scores[name] = m(torch.tensor(rte)).numpy()
                if name == 'sdcv':
                    vs = m(torch.tensor(rva)).numpy()
            replay[name] = float(np.abs(scores[name] - saved[key]).max())
            assert replay[name] < 1e-6
        for name in ['hq_qd', 'release_qd', 'flash_logit', 'ddv', 'rank_mean', 'rank_median']:
            scores[name] = prev[name]
        th = helper.threshold(vs, val['labels'])
        assert abs(th - float(saved['threshold'])) < 1e-6
        mu, sd = float(vs.mean()), float(vs.std() + 1e-8)
        zth = (th - mu) / sd
        tm, ts = float(scores['sdcv'].mean()), float(scores['sdcv'].std() + 1e-8)
        trans_th = tm + ts * zth
        raw = scores['sdcv'] >= th
        seenfixed = (scores['sdcv'] - mu) / sd >= zth
        assert np.array_equal(raw, seenfixed)
        trans = (scores['sdcv'] - tm) / ts >= zth
        half_change = []
        for mask in [np.arange(len(raw)) % 2 == 0, np.arange(len(raw)) % 2 == 1]:
            ss = scores['sdcv'][mask]
            pred = (ss - float(ss.mean())) / float(ss.std() + 1e-8) >= zth
            half_change.append(float(np.mean(pred != trans[mask])))
        met = {n: helper.metrics(s, te, pairs, th if n == 'sdcv' else None) for n, s in scores.items()}
        met['sdcv_transductive'] = helper.metrics(scores['sdcv'], te, pairs, trans_th)
        um = np.isin(te['partitions'], ['U+', 'U-'])
        signed = {n: {'unseen': float(roc_auc_score(te['labels'][um], s[um])), 'pair_acc': helper.pairacc(s, pairs)} for n, s in [('delta_act', te['X'][:, 12]), ('delta_obj', te['X'][:, 13]), ('abs_delta_act', abs(te['X'][:, 12]))]}
        gt = rows(ROOT / 'data/release/semantic_existence_v2' / split / 'test.jsonl')
        qd = rows(ROOT / 'results/semantic_existence/multi_split_v2' / split / 'qd/test/qd_detr_gmr_test_submission.jsonl')
        qmap = {str(p['qid']): p for p in qd}
        graw, _ = helper.gmiou(scores['sdcv'], th, te, gt, qmap, 'pred_relevant_windows')
        gtrans, _ = helper.gmiou(scores['sdcv'], trans_th, te, gt, qmap, 'pred_relevant_windows')
        out['splits'][split] = {'params': params, 'replay_max_error': replay, 'metrics': met, 'direction_only_diagnostic': signed, 'calibration': {'seen_threshold': th, 'val_mean': mu, 'val_std': sd, 'test_mean': tm, 'test_std': ts, 'z_threshold': zth, 'test_adapted_threshold': trans_th, 'seen_fixed_z_changed_decisions': int(np.sum(raw != seenfixed)), 'half_batch_changed_fractions': half_change}, 'official_gmiou': {'raw': graw, 'transductive': gtrans}}
        banks[split] = (te, scores)
        np.savez_compressed(OUT / (split + '_replay.npz'), qids=te['qids'], vids=te['vids'], labels=te['labels'], partitions=te['partitions'], **scores)
        print(split, 'replay', replay, 'SDCV', met['sdcv'], flush=True)
    for name in out['splits']['A1']['metrics']:
        ms = [out['splits'][s]['metrics'][name] for s in SPLITS]
        out['macro'][name] = {k: float(np.mean([m[k] for m in ms])) for k in ms[0] if k != 'threshold'}
        out['macro'][name]['action_unseen'] = float(np.mean([m['unseen'] for m in ms[:3]]))
        out['macro'][name]['composition_unseen'] = float(np.mean([m['unseen'] for m in ms[3:]]))
    write('audit_metrics.json', out)
    names = list(banks['A1'][1])
    videos = sorted(set.union(*[set(d['vids']) for d, _ in banks.values()]))
    vm = {v: i for i, v in enumerate(videos)}
    funcs = []
    for split in SPLITS:
        d, scores = banks[split]
        vi = np.array([vm[v] for v in d['vids']])
        groups = []
        for parts in [['S+', 'S-'], ['U+', 'U-']]:
            mask = np.isin(d['partitions'], parts)
            groups.append([helper.weighted_auc(d['labels'][mask], scores[n][mask], vi[mask]) for n in names])
        funcs.append(groups)
    draws = np.empty((2000, 5, 2, len(names)))
    rng = np.random.RandomState(3407)
    for b in range(2000):
        counts = np.bincount(rng.choice(len(videos), len(videos), replace=True), minlength=len(videos))
        for j in range(5):
            for g in range(2):
                draws[b, j, g] = [f(counts) for f in funcs[j][g]]
        if (b+1) % 500 == 0:
            print('bootstrap', b+1, flush=True)
    macro = draws.mean(1)
    si = names.index('sdcv')
    bs = {'n': 2000, 'unique_videos': len(videos), 'sdcv_seen': ci(macro[:, 0, si]), 'sdcv_unseen': ci(macro[:, 1, si]), 'comparisons': {}, 'splits': {}}
    for name in names:
        if name == 'sdcv':
            continue
        ni = names.index(name)
        bs['comparisons']['sdcv_minus_' + name] = {'unseen': ci(macro[:, 1, si] - macro[:, 1, ni]), 'seen': ci(macro[:, 0, si] - macro[:, 0, ni]), 'gap_reduction': ci((macro[:, 0, ni] - macro[:, 1, ni]) - (macro[:, 0, si] - macro[:, 1, si])), 'action_unseen': ci((draws[:, :3, 1, si] - draws[:, :3, 1, ni]).mean(1))}
    qi = names.index('hq_qd')
    for j, split in enumerate(SPLITS):
        bs['splits'][split] = {'unseen_gain_hq': ci(draws[:, j, 1, si] - draws[:, j, 1, qi]), 'gap_reduction_hq': ci((draws[:, j, 0, qi] - draws[:, j, 1, qi]) - (draws[:, j, 0, si] - draws[:, j, 1, si]))}
    np.savez_compressed(OUT / 'bootstrap_draws.npz', auc=draws, names=names, splits=SPLITS)
    write('bootstrap.json', bs)
    for file in ['model.py', 'prepare_data.py', 'train_and_eval.py', 'generate_audit_report.py', 'benchmark_summary.json', 'SDCV_AUDIT_REPORT.md']:
        record(BASE / file)
    record(PREV / 'audit_ddv.py')
    record(Path(__file__))
    write('input_manifest.json', MANIFEST)
    print('DONE', json.dumps(out['macro']['sdcv']), flush=True)

if __name__ == '__main__':
    main()
