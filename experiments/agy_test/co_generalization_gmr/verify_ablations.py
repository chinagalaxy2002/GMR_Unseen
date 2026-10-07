#!/usr/bin/env python3
"""Replay the four existing ablations without overwriting their archived JSON.

Use --repo-root to validate another restored repository's input assets.
Writes only this verification's audit JSON and replay log to --output-dir.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import sys
import os
import sklearn
import scipy

import numpy as np

HERE = Path(__file__).resolve().parent
SPLITS = ['A1', 'A2_alt', 'A3', 'C1', 'C2_alt']


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=HERE.parents[2])
    parser.add_argument('--output-dir', type=Path, default=HERE.parents[2] / 'docs/cog/ablation_audit')
    parser.add_argument('--atol', type=float, default=1e-6)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source = HERE / 'ablation_and_mechanism_study.py'
    archive = HERE / 'ablation_results.json'
    spec = importlib.util.spec_from_file_location('cog_archived_ablations', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = args.repo_root.resolve()
    module.BASE_CACHE = module.ROOT / 'experiments/agy_test/detr_decoder_gmr/cache'
    started = time.time()
    log_path = args.output_dir / 'replay.log'
    with log_path.open('w') as log, contextlib.redirect_stdout(log):
        data = module.load_all_split_data()
        # Original loops repeatedly decompress NPZ arrays for each query.
        # Materialize identical arrays once; preserve every numerical operation.
        for split_data in data.values():
            for subset in ('tr', 'val', 'te'):
                archive_handle = split_data[subset]
                split_data[subset] = {key: archive_handle[key] for key in archive_handle.files}
                archive_handle.close()
        alignment = []
        for split in SPLITS:
            for role, cache_key in [('train', 'tr'), ('val', 'val'), ('test', 'te')]:
                cache = data[split][cache_key]
                rows = module.rows(module.ROOT / f'data/release/semantic_existence_v2/{split}/{role}.jsonl')
                if role == 'val':
                    rows = [r for r in rows if r['partition'] in ('S+', 'S-')]
                qids = [str(r['qid']) for r in rows]
                labels = [int(r['exist_label']) for r in rows]
                assert np.array_equal(cache['qids'].astype(str), qids), (split, role, 'qid order')
                assert np.array_equal(cache['labels'], labels), (split, role, 'labels')
                if 'partitions' in cache:
                    assert np.array_equal(cache['partitions'].astype(str), [r['partition'] for r in rows]), (split, role, 'partitions')
                if role in ('train', 'val'):
                    assert all(r['partition'] in ('S+', 'S-') for r in rows), (split, role, 'unseen partition')
                if role == 'test':
                    for backbone, pred in data[split]['bb_pred_rows'].items():
                        assert all(q in pred for q in qids), (split, backbone, 'missing submission qid')
                alignment.append({'split': split, 'subset': role, 'rows': len(rows), 'qid_label_aligned': True, 'cached_partitions_checked': 'partitions' in cache})
        funcs = {
            'exp1_threshold_decoupling': module.run_threshold_decoupling,
            'exp2_fusion_weight_sweep': module.run_fusion_weight_sweep,
            'exp3_evidence_weight_ablations': module.run_evidence_weight_ablations,
            'exp4_routing_rule_ablations': module.run_routing_rule_ablations,
        }
        replay = {key: fn(data) for key, fn in funcs.items()}
    replay = json.loads(json.dumps(replay))  # normalize numeric weight keys to JSON strings
    expected = json.loads(archive.read_text())
    differences = []
    comparisons = 0
    max_error = 0.0

    def compare(a, b, path=''):
        nonlocal comparisons, max_error
        if isinstance(a, dict):
            assert set(a) == set(b), ('keys', path)
            for key in a:
                compare(a[key], b[key], path + '/' + key)
        elif isinstance(a, list):
            assert len(a) == len(b), ('length', path)
            for index, (x, y) in enumerate(zip(a, b)):
                compare(x, y, path + '/' + str(index))
        else:
            assert np.isfinite(a) and np.isfinite(b), ('nonfinite', path)
            error = abs(float(a) - float(b))
            comparisons += 1
            max_error = max(max_error, error)
            if error > args.atol:
                differences.append({'path': path, 'archived': a, 'replayed': b, 'absolute_error': error})

    compare(expected, replay)
    # The fitted logistic control is not reproducible from the archived artifacts.
    # Publish only the other, exactly checked variants as verified results.
    verified = json.loads(json.dumps(expected))
    for backbone in verified['exp3_evidence_weight_ablations']:
        del verified['exp3_evidence_weight_ablations'][backbone]['learned_val_logistic']
    fixed_differences = [d for d in differences if '/learned_val_logistic/' not in d['path']]
    verified_count = comparisons - 3 * 5 * 6
    (args.output_dir / 'verified_ablation_results.json').write_text(json.dumps(verified, indent=2) + '\n')
    (args.output_dir / 'replayed_ablation_results.json').write_text(json.dumps(replay, indent=2) + '\n')
    result = {
        'verification': 'independent invocation of all four archived ablation functions; no training or edits to source input assets',
        'status': 'PASS' if not differences else ('PARTIAL' if not fixed_differences else 'FAIL'),
        'verified_fixed_variants': {'status': 'PASS' if not fixed_differences else 'FAIL', 'metric_comparisons': verified_count, 'max_absolute_error': max((d['absolute_error'] for d in fixed_differences), default=0.0), 'excluded_variant': 'learned_val_logistic (90 metrics)'},
        'environment': {'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': scipy.__version__, 'sklearn': sklearn.__version__, 'OPENBLAS_NUM_THREADS': os.environ.get('OPENBLAS_NUM_THREADS'), 'OMP_NUM_THREADS': os.environ.get('OMP_NUM_THREADS')},
        'units': 'percentage points for all compared metrics',
        'tolerance': args.atol, 'metric_comparisons': comparisons,
        'max_absolute_error': max_error, 'differences': differences,
        'input_alignment': alignment,
        'script_sha256': sha256(source), 'archived_results_sha256': sha256(archive),
        'elapsed_seconds': round(time.time() - started, 3),
        'input_loading': 'NPZ arrays materialized once in memory to avoid repeated decompression; experiment functions unchanged',
        'limits': [
            'Logistic regression control differs from archived values; verified output excludes this fitted control.',
            'Replays the same metric implementation; does not prove annotation correctness or causal mechanism.',
            'Does not rerun the 2000-draw bootstrap or establish significance of new ablation differences.',
            'Seen-partition checks do not certify semantic holdout purity; known A3 multi-action and routing issues remain.',
        ],
    }
    (args.output_dir / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'metric_comparisons', 'max_absolute_error', 'elapsed_seconds']}))
    if differences:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
