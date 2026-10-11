"""Independently verify frozen C3_CG v2 evaluation without importing its driver.

Read-only toward inputs; writes this experiment's independent JSON conclusion.
No training, threshold selection, semantic review, or video-presence claim.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PRIOR = ROOT.parent / 'charades_cg_baselines_20261010'
RELEASE = REPO / 'data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2'
BACKBONES = ('moment', 'qd', 'flash')
MAIN_KEYS = ('seen_auc', 'unseen_auc', 'gap', 'rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1')
SUBSET_KEYS = ('seen_rej_f1', 'unseen_rej_f1', 'rej_f1_gap_pp', 'seen_gmiou1', 'unseen_gmiou1', 'gmiou1_gap_pp')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def first_valid_window(prediction):
    for candidate in prediction.get('pred_relevant_windows', []):
        if not isinstance(candidate, (list, tuple)) or len(candidate) < 2:
            continue
        try:
            start, end = float(candidate[0]), float(candidate[1])
            score = float(candidate[2]) if len(candidate) > 2 else 1.0
        except (ValueError, TypeError):
            continue
        assert np.isfinite([start, end, score]).all()
        if end > start:
            return (start, end)
    return None


def top_one_set_iou(prediction, ground_truth):
    window = first_valid_window(prediction)
    truth = ground_truth['relevant_windows']
    if window is None:
        return float(not truth)
    if not truth:
        return 0.0
    # Released positives have exactly one original source window. Independently
    # compute intersection / union rather than importing native metric helpers.
    assert len(truth) == 1
    start, end = window
    a, b = map(float, truth[0])
    intersection = max(0.0, min(end, b) - max(start, a))
    union = (end - start) + (b - a) - intersection
    return intersection / union if union > 0 else 0.0


def weighted_auc(labels, scores, weights):
    # Mann-Whitney probability, with half-credit for tied positive/negative
    # scores. This is independent of the driver's sklearn ROC implementation.
    order = np.argsort(scores, kind='stable')
    score = scores[order]
    label = labels[order]
    weight = weights[order]
    starts = np.r_[0, np.flatnonzero(score[1:] != score[:-1]) + 1]
    pos = np.add.reduceat(weight * (label == 1), starts)
    neg = np.add.reduceat(weight * (label == 0), starts)
    return float(np.dot(pos, np.cumsum(neg) - 0.5 * neg) / (pos.sum() * neg.sum()))


def readout(labels, partitions, scores, threshold, iou, weights):
    accept = scores >= threshold
    seen = np.char.startswith(partitions, 'S')
    unseen = ~seen

    def subset(mask):
        tn = weights[mask & (labels == 0) & ~accept].sum()
        fp = weights[mask & (labels == 0) & accept].sum()
        fn = weights[mask & (labels == 1) & ~accept].sum()
        rejection_f1 = 200 * tn / (2 * tn + fp + fn)
        values = np.where(accept, iou, labels == 0)
        generalized_iou = 100 * np.dot(weights[mask], values[mask]) / weights[mask].sum()
        return rejection_f1, generalized_iou

    sa = weighted_auc(labels[seen], scores[seen], weights[seen])
    ua = weighted_auc(labels[unseen], scores[unseen], weights[unseen])
    sf, sg = subset(seen)
    uf, ug = subset(unseen)
    overall_f, overall_g = subset(np.ones(len(labels), dtype=bool))
    positive_seen = partitions == 'S+'
    positive_unseen = partitions == 'U+'
    main = [sa, ua, sa - ua, overall_f,
            100 * weights[~accept].sum() / weights.sum(),
            100 * weights[positive_seen & ~accept].sum() / weights[positive_seen].sum(),
            100 * weights[positive_unseen & ~accept].sum() / weights[positive_unseen].sum(), overall_g]
    detail = [sf, uf, sf - uf, sg, ug, sg - ug]
    return np.array(main), np.array(detail)


def verify_inputs():
    frozen = ROOT / 'groups/C3_CG/release/C3_CG'
    parts = {name: rows(frozen / (name + '.jsonl')) for name in ('train', 'val_seen', 'test')}
    videos = {name: {r['vid'] for r in rr} for name, rr in parts.items()}
    for a, b in (('train', 'val_seen'), ('train', 'test'), ('val_seen', 'test')):
        assert not videos[a] & videos[b]
    for name, rr in parts.items():
        assert digest(frozen / (name + '.jsonl')) == digest(RELEASE / 'splits/C3_CG' / (name + '.jsonl'))
        assert len({r['qid'] for r in rr}) == len(rr)
        if name != 'test':
            assert all(r['partition'] in ('S+', 'S-') for r in rr)
            assert digest(frozen / (name + '.jsonl')) == digest(PRIOR / 'groups/C3_CG/release/C3_CG' / (name + '.jsonl'))
        for r in rr:
            assert bool(r['relevant_windows']) == bool(r['exist_label'])
            assert r['partition'][1:] == ('+' if r['exist_label'] else '-')
            if name == 'test':
                assert r['official_subset'] == ('test_trivial' if r['partition'][0] == 'S' else 'novel_composition')
    official_source = REPO / 'data/release/charades_cg_gmr_v1/source'
    source_files = {name: load(official_source / name) for name in ('train.json', 'test_trivial.json', 'novel_composition.json')}
    all_rows = [r for rr in parts.values() for r in rr]
    positives = {r['qid']: r for r in all_rows if r['exist_label'] == 1}
    for r in positives.values():
        filename, vid, index = r['source_qid'].split(':')
        original = source_files[filename][vid]
        index = int(index)
        assert r['qid'] == r['source_qid'] and r['vid'] == vid
        assert r['query'] == original['sentences'][index]
        assert r['relevant_windows'] == [original['timestamps'][index]]
        assert r['duration'] == original['duration']
        assert r['source_commit'] == '2372337e9166b8e26b83ce936a8474c6ae127290'
    for r in all_rows:
        if r['exist_label'] == 0:
            source = positives[r['source_qid']]
            assert r['query'] == source['query'] and r['source_vid'] == source['vid']
            assert r['vid'] != source['vid'] and r['relevant_windows'] == []
            assert r['partition'][0] == source['partition'][0]
            assert r['official_subset'] == source['official_subset'] and r['pair_id'] == source['pair_id']
    manifest = load(ROOT / 'TEXT_FEATURE_MANIFEST.json')
    features = {r['qid']: r for r in manifest}
    verified = {}
    previous = {m['query_sha256']: m for m in load(PRIOR / 'TEXT_FEATURE_MANIFEST.json')}
    for rr in parts.values():
        for r in rr:
            m = features[r['qid']]
            assert m['query_sha256'] == hashlib.sha256(r['query'].encode()).hexdigest()
            source = Path(m['source'])
            if source not in verified:
                verified[source] = digest(source)
            assert verified[source] == m['feature_sha256']
            assert (ROOT / 'features/clip_text' / f"qid{r['qid']}.npz").resolve() == source.resolve()
            if m['query_sha256'] in previous:
                assert m['feature_sha256'] == previous[m['query_sha256']]['feature_sha256']
    encoder = load(ROOT / 'TEXT_ENCODER.json')
    old_encoder = load(PRIOR / 'TEXT_ENCODER.json')
    for key in ('weights_sha256', 'clip_model_sha256', 'tokenizer_sha256', 'token_context', 'truncation'):
        assert encoder[key] == old_encoder[key]
    assert digest(encoder['weights_path']) == encoder['weights_sha256']
    assert digest(Path(encoder['clip_code_path']) / 'clip/model.py') == encoder['clip_model_sha256']
    assert digest(Path(encoder['clip_code_path']) / 'clip/simple_tokenizer.py') == encoder['tokenizer_sha256']
    for relative, expected in load(ROOT / 'SOURCE_MANIFEST.json').items():
        assert digest(PRIOR / 'native_source' / relative) == expected
    protocol = load(ROOT / 'PROTOCOL.json')
    assert protocol['training_performed'] is False and protocol['threshold_reselected'] is False
    summary = dict(status='PASS', counts={k: dict(Counter(r['partition'] for r in rr)) for k, rr in parts.items()},
                   video_counts={k: len(v) for k, v in videos.items()}, verified_unique_text_features=len(verified),
                   train_validation_byte_identical_to_prior=True, video_disjoint=True,
                   official_positive_source_query_video_window_and_negative_pair_mapping='PASS',
                   test_sha256=digest(frozen / 'test.jsonl'),
                   shared_seen_unseen_target_videos=len({r['vid'] for r in parts['test'] if r['partition'].startswith('S')} &
                                                      {r['vid'] for r in parts['test'] if r['partition'].startswith('U')}))
    return parts['test'], summary


def verify_backbone(backbone, truth):
    frozen = PRIOR / 'groups/C3_CG/frozen_checkpoints' / backbone
    for name, expected in load(frozen / 'MANIFEST.json').items():
        assert digest(frozen / name) == expected
    out = ROOT / 'groups/C3_CG/evaluation' / backbone
    calibration_path = PRIOR / 'groups/C3_CG/evaluation' / backbone / 'FROZEN_CALIBRATION.json'
    calibration = load(calibration_path)
    assert digest(out / 'FROZEN_CALIBRATION.json') == digest(calibration_path)
    assert calibration['validation_sha256'] == digest(ROOT / 'groups/C3_CG/release/C3_CG/val_seen.jsonl')
    validation_name = 'best_charadesSTA_val_preds.jsonl' if backbone == 'flash' else 'best_charades_semantic_existence_val_preds.jsonl'
    assert digest(frozen / validation_name) == calibration['prediction_sha256']
    filename = 'hl_test_submission.jsonl' if backbone == 'flash' else backbone + '_detr_gmr_test_submission.jsonl'
    native_path = ROOT / 'groups/C3_CG/runs' / backbone / 'test' / filename
    native = rows(native_path)
    predictions = {str(r['qid']): r for r in native}
    assert len(native) == len(predictions) == len(truth) == 11348
    assert set(predictions) == {str(r['qid']) for r in truth}
    for r in truth:
        prediction = predictions[str(r['qid'])]
        assert prediction['vid'] == r['vid'] and prediction['query'] == r['query']
    y = np.array([r['exist_label'] for r in truth])
    partitions = np.array([r['partition'] for r in truth])
    vids = np.array([r['vid'] for r in truth])
    score_key = 'pred_exist_logit' if backbone == 'flash' else 'pred_exist_score'
    scores = np.array([predictions[str(r['qid'])][score_key] for r in truth], dtype=np.float32)
    iou = np.array([top_one_set_iou(predictions[str(r['qid'])], r) for r in truth])
    assert np.isfinite(scores).all() and np.isfinite(iou).all()
    standardized = np.load(out / 'predictions.npz', allow_pickle=False)
    for key, value in [('qids', np.array([str(r['qid']) for r in truth])), ('labels', y),
                       ('partitions', partitions), ('vids', vids), ('scores', scores)]:
        assert np.array_equal(standardized[key], value), key
    np.testing.assert_allclose(standardized['accept_iou'], iou, rtol=0, atol=1e-12)
    assert float(standardized['threshold']) == calibration['threshold']
    point, subset_point = readout(y, partitions, scores, calibration['threshold'], iou, np.ones(len(y)))
    expected_point = load(out / 'metrics.json')
    expected_subset = load(out / 'subset_metrics.json')
    np.testing.assert_allclose(point, [expected_point[k] for k in MAIN_KEYS], rtol=0, atol=1e-10)
    np.testing.assert_allclose(subset_point, [expected_subset['point'][k] for k in SUBSET_KEYS], rtol=0, atol=1e-10)
    videos, inverse = np.unique(vids, return_inverse=True)
    main_saved = np.load(out / 'bootstrap_draws.npz', allow_pickle=False)
    subset_saved = np.load(out / 'subset_bootstrap_draws.npz', allow_pickle=False)
    assert np.array_equal(main_saved['videos'], videos) and np.array_equal(subset_saved['videos'], videos)
    assert list(main_saved['keys']) == list(MAIN_KEYS) and list(subset_saved['keys']) == list(SUBSET_KEYS)
    rng = np.random.RandomState(3407)
    main_draws, subset_draws = [], []
    for _ in range(2000):
        cluster_weights = np.bincount(rng.randint(0, len(videos), size=len(videos)), minlength=len(videos))
        main, detail = readout(y, partitions, scores, calibration['threshold'], iou, cluster_weights[inverse])
        main_draws.append(main)
        subset_draws.append(detail)
    main_draws, subset_draws = np.array(main_draws), np.array(subset_draws)
    assert np.isfinite(main_draws).all() and np.isfinite(subset_draws).all()
    assert main_saved['valid'].all() and len(main_saved['valid']) == 2000
    np.testing.assert_allclose(main_draws, main_saved['draws'], rtol=0, atol=1e-10)
    np.testing.assert_allclose(subset_draws, subset_saved['draws'], rtol=0, atol=1e-10)
    expected_ci = load(out / 'bootstrap.json')
    assert expected_ci['seed'] == 3407 and expected_ci['requested_draws'] == expected_ci['valid_draws'] == 2000
    for index, key in enumerate(MAIN_KEYS):
        np.testing.assert_allclose(np.percentile(main_draws[:, index], [2.5, 97.5]), expected_ci['absolute'][key], rtol=0, atol=1e-10)
    for index, key in enumerate(SUBSET_KEYS):
        np.testing.assert_allclose(np.percentile(subset_draws[:, index], [2.5, 97.5]), expected_subset['ci'][key]['ci95'], rtol=0, atol=1e-10)
        assert expected_subset['ci'][key]['valid_draws'] == 2000
    return dict(status='PASS', native_prediction_rows=len(native), native_prediction_sha256=digest(native_path),
                frozen_threshold=calibration['threshold'], checkpoint_manifest=load(frozen / 'MANIFEST.json'),
                point=dict(zip(MAIN_KEYS, map(float, point))), subset_point=dict(zip(SUBSET_KEYS, map(float, subset_point))),
                bootstrap_seed=3407, independently_recomputed_draws=2000, joint_video_clusters=len(videos),
                maximum_main_draw_error=float(np.max(np.abs(main_draws - main_saved['draws']))),
                maximum_subset_draw_error=float(np.max(np.abs(subset_draws - subset_saved['draws']))),
                all_absolute_and_gap_ci_match=True, qid_coverage_video_text_mapping='PASS')


def main():
    truth, data_summary = verify_inputs()
    results = {}
    for backbone in BACKBONES:
        print('Independent verification:', backbone, flush=True)
        results[backbone] = verify_backbone(backbone, truth)
    final_status = load(ROOT / 'FINAL_EVALUATION_STATUS.json')
    assert final_status['complete'] is True and final_status['training_performed'] is False
    pipeline_status = load(ROOT / 'PIPELINE_EXIT.json')
    assert pipeline_status['complete'] == 3 and pipeline_status['failed'] == 0
    for filename in ('metrics.json', 'degradation_metrics.json'):
        aggregate = load(ROOT / 'evaluation' / filename)
        assert len(aggregate) == 3 and {r['backbone'] for r in aggregate} == set(BACKBONES)
        for record in aggregate:
            assert record['split'] == 'C3_CG' and record['method'] == 'Baseline'
            expected = {**results[record['backbone']]['point'], **results[record['backbone']]['subset_point']}
            for key, value in expected.items():
                np.testing.assert_allclose(record[key], value, rtol=0, atol=1e-10)
            assert (record['seen_positive_n'], record['seen_negative_n'], record['unseen_positive_n'], record['unseen_negative_n']) == (2684, 2684, 2990, 2990)
            assert all(record[key] is None for key in ('unseen_net_gain', 'seen_change', 'gap_reduction'))
    for filename in ('metrics.csv', 'degradation_metrics.csv'):
        with (ROOT / 'evaluation' / filename).open() as stream:
            aggregate = list(csv.DictReader(stream))
        assert len(aggregate) == 3
        for record in aggregate:
            expected = {**results[record['backbone']]['point'], **results[record['backbone']]['subset_point']}
            for key, value in expected.items():
                np.testing.assert_allclose(float(record[key]), value, rtol=0, atol=1e-10)
    for filename in ('bootstrap.json', 'degradation_bootstrap.json'):
        aggregate = load(ROOT / 'evaluation' / filename)
        for backbone in BACKBONES:
            folder = ROOT / 'groups/C3_CG/evaluation' / backbone
            assert aggregate[backbone]['absolute'] == load(folder / 'bootstrap.json')['absolute']
            assert aggregate[backbone]['subset'] == load(folder / 'subset_metrics.json')['ci']
    report = dict(status='PASS', scope='Mechanical independent verification; no semantic or video audit',
                  verifier_sha256=digest(__file__), data=data_summary, backbones=results,
                  aggregate_json_csv_ci_and_final_status='PASS',
                  methodology='Independent Mann-Whitney AUROC with score ties; direct interval IoU; rejection-positive F1; all 2000 seed-3407 joint target-video bootstrap draws reconstructed.',
                  code_inspection=dict(no_training_or_retuning=True, test_labels_do_not_affect_model_predictions=True,
                                       original_native_source_and_feature_encoding_reused=True,
                                       note='Flash eval labels populate output metadata only; QD labels go to separate targets and not model inputs.'))
    output = ROOT / 'LOCAL_VERIFICATION_INDEPENDENT.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
