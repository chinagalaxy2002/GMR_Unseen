"""Re-evaluate original frozen C3_CG baselines on v2 without training or tuning."""
import csv
import datetime
import fcntl
import importlib.util
import json
import shutil
import subprocess
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from sklearn.metrics import roc_auc_score

from common import ROOT, REPO, RELEASE, NATIVE, PRIOR, BACKBONES, GMR, NUMERICAL, VIDEO, environment, read_rows, save_json, digest

sys.path.insert(0, str(NATIVE))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

LOCK = threading.Lock()
STATUS = {}
KEYS = ('seen_auc', 'unseen_auc', 'gap', 'rej_f1', 'rr', 's_frr', 'u_frr', 'gmiou1')


def update(bb, **fields):
    with LOCK:
        STATUS[bb] = {**STATUS.get(bb, {}), **fields}
        save_json(ROOT / 'QUEUE_STATUS.json', {'updated': datetime.datetime.now().isoformat(), 'jobs': STATUS})


def metrics(y, p, sc, threshold, iou, weights):
    accept = sc >= threshold
    def mean(values, mask):
        return float(np.dot(weights[mask], values[mask]) / weights[mask].sum()) if weights[mask].sum() else float('nan')
    def auc(mask):
        mask = mask & (weights > 0)
        return float(roc_auc_score(y[mask], sc[mask], sample_weight=weights[mask])) if len(np.unique(y[mask])) == 2 else float('nan')
    sa, ua = auc(np.char.startswith(p, 'S')), auc(np.char.startswith(p, 'U'))
    tn = weights[(y == 0) & ~accept].sum()
    fp = weights[(y == 0) & accept].sum()
    fn = weights[(y == 1) & ~accept].sum()
    return dict(seen_auc=sa, unseen_auc=ua, gap=sa - ua,
                rej_f1=100 * 2 * tn / (2 * tn + fp + fn),
                rr=100 * np.dot(weights, ~accept) / weights.sum(),
                s_frr=100 * mean(~accept, p == 'S+'), u_frr=100 * mean(~accept, p == 'U+'),
                gmiou1=100 * np.dot(weights, np.where(accept, iou, y == 0)) / weights.sum())


def evaluate(bb, val_path, pred_path):
    task = ROOT / 'groups/C3_CG'
    release = task / 'release/C3_CG'
    prior_folder = PRIOR / 'groups/C3_CG/evaluation' / bb
    calibration = json.loads((prior_folder / 'FROZEN_CALIBRATION.json').read_text())
    assert digest(release / 'val_seen.jsonl') == calibration['validation_sha256']
    assert digest(val_path) == calibration['prediction_sha256']
    threshold = calibration['threshold']
    out = task / 'evaluation' / bb
    out.mkdir(parents=True, exist_ok=True)
    # Exact frozen copy: no threshold selection or checkpoint selection on v2 test.
    shutil.copy2(prior_folder / 'FROZEN_CALIBRATION.json', out / 'FROZEN_CALIBRATION.json')
    rows = read_rows(release / 'test.jsonl')
    native = read_rows(pred_path)
    pred = {str(r['qid']): r for r in native}
    assert len(native) == len(pred) == len(rows)
    assert set(pred) == {str(r['qid']) for r in rows}
    for row in rows:
        r = pred[str(row['qid'])]
        assert r['vid'] == row['vid'], (row['qid'], r['vid'], row['vid'])
    y = np.array([r['exist_label'] for r in rows])
    p = np.array([r['partition'] for r in rows])
    vids = np.array([r['vid'] for r in rows])
    sc = np.array([pred[str(r['qid'])]['pred_exist_logit' if bb == 'flash' else 'pred_exist_score'] for r in rows], np.float32)
    assert np.isfinite(sc).all()
    iou = np.array([_compute_set_iou_score(
        [w[:2] for w in _clean_pred_windows(pred[str(r['qid'])]['pred_relevant_windows'], max_pred_windows=1)],
        r['relevant_windows']) for r in rows])
    point = metrics(y, p, sc, threshold, iou, np.ones(len(y)))
    np.savez_compressed(out / 'predictions.npz', qids=np.array([str(r['qid']) for r in rows]),
                        vids=vids, labels=y, partitions=p, scores=sc, threshold=threshold, accept_iou=iou)
    videos, vi = np.unique(vids, return_inverse=True)
    rng = np.random.RandomState(3407)
    draws = []
    for _ in range(2000):
        weights = np.bincount(rng.randint(len(videos), size=len(videos)), minlength=len(videos))[vi]
        draws.append(list(metrics(y, p, sc, threshold, iou, weights).values()))
    draws = np.array(draws)
    valid = np.isfinite(draws).all(axis=1)
    assert valid.all()
    np.savez_compressed(out / 'bootstrap_draws.npz', draws=draws, valid=valid, videos=videos, keys=np.array(KEYS))
    save_json(out / 'bootstrap.json', dict(seed=3407, requested_draws=2000, valid_draws=int(valid.sum()),
        unit='joint target-video cluster across Seen and Unseen',
        absolute={k: np.percentile(draws[:, i], [2.5, 97.5]).tolist() for i, k in enumerate(KEYS)}))
    save_json(out / 'metrics.json', dict(split='C3_CG', backbone=bb, method='Baseline', threshold=threshold, **point))
    spec = importlib.util.spec_from_file_location('gmr_summary', REPO / 'scripts/summarize_gmr_degradation.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    subset_point, ci, subset_draws, subset_videos, counts = module.summarize(out / 'predictions.npz', 2000, 3407)
    assert np.array_equal(videos, subset_videos)
    save_json(out / 'subset_metrics.json', dict(point=subset_point, ci=ci, counts=counts))
    np.savez_compressed(out / 'subset_bootstrap_draws.npz', draws=subset_draws, videos=subset_videos, keys=np.array(module.KEYS))


def report():
    records, intervals = [], {}
    for bb in BACKBONES:
        folder = ROOT / 'groups/C3_CG/evaluation' / bb
        base = json.loads((folder / 'metrics.json').read_text())
        detail = json.loads((folder / 'subset_metrics.json').read_text())
        counts = detail['counts']
        records.append(dict(**base, **detail['point'],
            seen_positive_n=counts['S']['positive'], seen_negative_n=counts['S']['negative'],
            unseen_positive_n=counts['U']['positive'], unseen_negative_n=counts['U']['negative'],
            unseen_net_gain=None, seen_change=None, gap_reduction=None))
        intervals[bb] = dict(absolute=json.loads((folder / 'bootstrap.json').read_text())['absolute'], subset=detail['ci'])
    out = ROOT / 'evaluation'
    out.mkdir(exist_ok=True)
    for name in ('metrics.json', 'degradation_metrics.json'):
        save_json(out / name, records)
    for name in ('bootstrap.json', 'degradation_bootstrap.json'):
        save_json(out / name, intervals)
    for name in ('metrics.csv', 'degradation_metrics.csv'):
        with (out / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    lines = ['# C3_CG v2: frozen baseline Seen/Unseen re-evaluation', '',
             'Completed: 3/3. Same original checkpoint and Seen-validation threshold; no training or test tuning.', '',
             '| Backbone | Seen AUROC | Unseen AUROC | Gap (pp) | Seen Rej-F1 (%) | Unseen Rej-F1 (%) | Gap (pp) | Seen G-mIoU@1 (%) | Unseen G-mIoU@1 (%) | Gap (pp) |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['backbone']} | {r['seen_auc']:.4f} | {r['unseen_auc']:.4f} | {100*r['gap']:+.2f} | {r['seen_rej_f1']:.2f} | {r['unseen_rej_f1']:.2f} | {r['rej_f1_gap_pp']:+.2f} | {r['seen_gmiou1']:.2f} | {r['unseen_gmiou1']:.2f} | {r['gmiou1_gap_pp']:+.2f} |")
    lines += ['', 'Gap = Seen − Unseen; negative gaps retained. 2,000 joint target-video-cluster bootstrap draws, seed 3407. Full absolute/subset/gap CIs are in bootstrap.json and per-backbone draws. Standalone relative method gains are undefined; no five-split macro. F1/G-mIoU depend on class proportions. Negative labels are constructed, not video-confirmed.', '']
    for name in ('STANDARD_EVALUATION.md', 'GENERALIZATION_DROP_COMPARISON.md'):
        (out / name).write_text('\n'.join(lines))


def job(bb, gpu):
    task = ROOT / 'groups/C3_CG'
    prior_frozen = PRIOR / 'groups/C3_CG/frozen_checkpoints' / bb
    manifest = json.loads((prior_frozen / 'MANIFEST.json').read_text())
    for name, expected in manifest.items():
        assert digest(prior_frozen / name) == expected
    frozen = task / 'frozen_checkpoints' / bb
    frozen.parent.mkdir(parents=True, exist_ok=True)
    if not frozen.exists():
        frozen.symlink_to(prior_frozen, target_is_directory=True)
    run = task / 'runs' / bb
    output = run / 'test'
    output.mkdir(parents=True, exist_ok=True)
    common_args = ['--eval_path', str(task / 'release/C3_CG/test.jsonl'),
                   '--t_feat_dir', str(task / 'features/C3_CG/clip_text')]
    if bb == 'flash':
        val = frozen / 'best_charadesSTA_val_preds.jsonl'
        cmd = [NUMERICAL, '-m', 'training.flash_vtg_gmr.inference', 'configs/flash_vtg_gmr/model.py',
               '--resume', str(frozen / 'model_best.ckpt'), '--eval_split_name', 'test',
               '--eval_results_dir', str(output), '--device', '0', '--nms_thd', '-1', *common_args]
        pred = output / 'hl_test_submission.jsonl'
    else:
        val = frozen / 'best_charades_semantic_existence_val_preds.jsonl'
        cmd = [GMR, f'training/{"qd" if bb == "qd" else "moment"}_detr_gmr/evaluate.py',
               '--dataset', 'charades_semantic_existence', '--model_path', str(frozen / 'best.ckpt'),
               '--split', 'test', *common_args, '--v_feat_dirs', str(VIDEO / 'vid_clip'), str(VIDEO / 'vid_slowfast'),
               '--results_dir', str(output), '--device', 'cuda' if bb == 'moment' else 'cuda:0']
        pred = output / (bb + '_detr_gmr_test_submission.jsonl')
    save_json(run / 'INFERENCE_COMMAND.json', dict(command=cmd, cwd=str(NATIVE), gpu=gpu,
        test_sha256=digest(task / 'release/C3_CG/test.jsonl'), prior_checkpoint_manifest=manifest))
    update(bb, stage='inference', gpu=gpu, started=datetime.datetime.now().isoformat())
    if not (run / 'INFERENCE_COMPLETE.json').exists():
        with (run / 'inference.log').open('w') as stream:
            subprocess.run(cmd, cwd=NATIVE, env=environment(gpu), stdout=stream, stderr=subprocess.STDOUT, check=True)
        assert len(read_rows(pred)) == 11348
        save_json(run / 'INFERENCE_COMPLETE.json', dict(prediction_sha256=digest(pred), rows=11348))
    else:
        assert digest(pred) == json.loads((run / 'INFERENCE_COMPLETE.json').read_text())['prediction_sha256']
    update(bb, stage='bootstrap')
    evaluate(bb, val, pred)
    update(bb, stage='complete', finished=datetime.datetime.now().isoformat())


def main():
    from prepare_experiment import prepare
    prepare()
    for name in ('train.jsonl', 'val_seen.jsonl'):
        assert digest(ROOT / 'groups/C3_CG/release/C3_CG' / name) == digest(PRIOR / 'groups/C3_CG/release/C3_CG' / name)
    protocol = json.loads((PRIOR / 'PROTOCOL.json').read_text())
    protocol.update(dataset=str(RELEASE), evaluation_revision='v2 Seen+Unseen test',
        training_performed=False, checkpoint_reused_from=str(PRIOR), threshold_reselected=False,
        bootstrap_unit='joint target-video clusters, shared Seen/Unseen videos resampled together')
    save_json(ROOT / 'PROTOCOL.json', protocol)
    for name in ('REFERENCE_PARITY.json',):
        shutil.copy2(PRIOR / name, ROOT / name)
    errors = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {bb: pool.submit(job, bb, {'moment': 0, 'qd': 1, 'flash': 0}[bb]) for bb in BACKBONES}
        for bb, future in futures.items():
            try:
                future.result()
            except Exception:
                errors.append(bb)
                update(bb, stage='failed', error=traceback.format_exc())
    finished = datetime.datetime.now().isoformat()
    save_json(ROOT / 'PIPELINE_EXIT.json', dict(complete=3 - len(errors), failed=len(errors), finished=finished))
    save_json(ROOT / 'FINAL_EVALUATION_STATUS.json', dict(complete=not errors, finished=finished,
        score_readout='Moment/QD native sigmoid; Flash native logit', dataset=str(RELEASE), training_performed=False))
    if errors:
        raise RuntimeError('Inference/evaluation failed: ' + ', '.join(errors))
    report()


if __name__ == '__main__':
    with (ROOT / 'queue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
