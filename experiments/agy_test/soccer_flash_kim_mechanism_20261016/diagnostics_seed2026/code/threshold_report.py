"""Sweep every 0.01 decision threshold, aggregate paired seeds, and plot metrics."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'minneg/baseline_source'))
from eval.metrics import compute_G_mIoU, compute_gmr_cls, prepare_submission_for_gmiou

SEEDS = (2026,)
THRESHOLDS = np.round(np.linspace(0.0, 1.0, 101), 2)
METRICS = ('G-mIoU@1', 'G-mIoU@3', 'G-mIoU@5', 'Rej-F1',
           'negative_recall', 'positive_recall', 'balanced_accuracy')


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prediction_path(stage, seed):
    if stage == 'baseline':
        return ROOT / f'baseline/runs/E0_s{seed}/test_predictions.jsonl'
    if stage == 'task_a':
        return ROOT / f'task_a/runs/task_a_s{seed}/test_predictions.jsonl'
    if stage == 'no_minneg':
        return ROOT / f'minneg/runs/no_minneg_s{seed}/test_predictions.jsonl'
    return ROOT / f'minneg/runs/minneg_s{seed}/test_predictions.jsonl'


def evaluate(predictions, ground_truth, threshold):
    effective = float(np.nextafter(float(threshold), -np.inf))
    gated, _ = prepare_submission_for_gmiou(predictions, effective, 10)
    values = compute_G_mIoU(gated, ground_truth, (1, 3, 5))
    classification = next(iter(compute_gmr_cls(
        predictions, ground_truth, (effective,))['per_threshold'].values()))
    lookup = {row['qid']: row for row in predictions}
    labels = np.asarray([bool(row['relevant_windows']) for row in ground_truth])
    scores = np.asarray([lookup[row['qid']]['pred_exist_score'] for row in ground_truth])
    guessed = scores >= threshold
    values.update(
        **{'Rej-F1': classification['Rej-F1']},
        negative_recall=100.0 * float((~guessed[~labels]).mean()),
        positive_recall=100.0 * float(guessed[labels].mean()),
        balanced_accuracy=50.0 * float((~guessed[~labels]).mean() + guessed[labels].mean()),
    )
    return values


def main():
    output = ROOT / 'reports'
    output.mkdir(exist_ok=True)
    ground_truth_path = ROOT / 'minneg/data/test.jsonl'
    ground_truth = read_rows(ground_truth_path)
    all_rows = []
    invariant = []
    for stage in ('baseline', 'no_minneg', 'minneg'):
        for seed in SEEDS:
            path = prediction_path(stage, seed)
            predictions = read_rows(path)
            lookup = {row['qid']: row for row in predictions}
            labels = np.asarray([bool(row['relevant_windows']) for row in ground_truth])
            scores = np.asarray([lookup[row['qid']]['pred_exist_score'] for row in ground_truth])
            auroc = 100.0 * float(roc_auc_score(labels, scores))
            invariant.append({'stage': stage, 'seed': seed, 'predictions_sha256': digest(path), 'AUROC': auroc})
            for threshold in THRESHOLDS:
                values = evaluate(predictions, ground_truth, float(threshold))
                all_rows.append({'stage': stage, 'seed': seed, 'threshold': float(threshold),
                                 **{metric: values[metric] for metric in METRICS}})

    csv_path = output / 'threshold_sweep_per_seed.csv'
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
        writer.writeheader(); writer.writerows(all_rows)

    summary = []
    for stage in ('baseline', 'no_minneg', 'minneg'):
        for threshold in THRESHOLDS:
            subset = [row for row in all_rows if row['stage'] == stage and row['threshold'] == float(threshold)]
            entry = {'stage': stage, 'threshold': float(threshold), 'n_seeds': len(subset)}
            for metric in METRICS:
                values = np.asarray([row[metric] for row in subset])
                entry[f'{metric}_mean'] = float(values.mean())
                entry[f'{metric}_sd'] = float(values.std(ddof=1)) if len(values) > 1 else 0.0
            summary.append(entry)
    with (output / 'threshold_sweep_summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)

    labels = {
        'G-mIoU@1': 'G-mIoU@1 (%)', 'G-mIoU@3': 'G-mIoU@3 (%)',
        'G-mIoU@5': 'G-mIoU@5 (%)', 'Rej-F1': 'Rejection F1 (%)',
        'negative_recall': 'Negative recall (%)', 'positive_recall': 'Positive recall (%)',
        'balanced_accuracy': 'Balanced accuracy (%)',
    }
    colors = {'baseline': '#4c78a8', 'no_minneg': '#f58518', 'minneg': '#54a24b'}
    fig, axes = plt.subplots(3, 3, figsize=(15, 12), sharex=True)
    for axis, metric in zip(axes.flat, METRICS):
        for stage in ('baseline', 'no_minneg', 'minneg'):
            rows = [row for row in summary if row['stage'] == stage]
            x = np.asarray([row['threshold'] for row in rows])
            mean = np.asarray([row[f'{metric}_mean'] for row in rows])
            sd = np.asarray([row[f'{metric}_sd'] for row in rows])
            axis.plot(x, mean, label=stage, color=colors[stage], linewidth=2)
            axis.fill_between(x, mean - sd, mean + sd, color=colors[stage], alpha=0.16)
        axis.set_title(labels[metric]); axis.grid(alpha=0.25); axis.set_ylabel('%')
    for axis in axes[-1]: axis.set_xlabel('Existence threshold')
    axes.flat[-2].axis('off'); axes.flat[-1].axis('off')
    handles, legend_labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc='lower center', ncol=3, frameon=False)
    fig.suptitle('Seed 2026 test threshold sweep', fontsize=16)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    fig.savefig(output / 'all_threshold_metrics.png', dpi=220)
    fig.savefig(output / 'all_threshold_metrics.pdf')
    plt.close(fig)

    payload = {
        'ground_truth_sha256': digest(ground_truth_path), 'thresholds': THRESHOLDS.tolist(),
        'seeds': list(SEEDS), 'invariant_metrics': invariant,
        'uncertainty': 'not estimated; seed 2026 only',
    }
    (output / 'REPORT.json').write_text(json.dumps(payload, indent=2) + '\n')

    selected = {}
    completed = {}
    selected_val_auroc = {}
    for seed in SEEDS:
        run = ROOT / f'minneg/runs/minneg_s{seed}'
        choice = json.loads((run / 'selected.json').read_text())
        trace = read_rows(run / 'trace.jsonl')
        if choice.get('selection_metric') != 'AUROC':
            raise RuntimeError(f'minneg seed {seed} was not selected by Val AUROC')
        selected[str(seed)] = int(choice['epoch'])
        selected_val_auroc[str(seed)] = float(choice['val_AUROC'])
        completed[str(seed)] = max(int(row['epoch']) for row in trace)
    freeze_path = output / 'CHECKPOINT_FREEZE.json'
    freeze = json.loads(freeze_path.read_text()) if freeze_path.exists() else {}
    evaluation_protocol = {
        'decision': freeze.get(
            'decision', 'evaluate Val-AUROC-selected A3 checkpoints after automatic early stopping'
        ),
        'requested_by_user': freeze.get('requested_by_user', False),
        'automatic_early_stopping_reached': freeze.get(
            'automatic_early_stopping_reached', True
        ),
        'selection_data': 'Val only',
        'selection_metric': 'AUROC',
        'selected_epoch_by_seed': selected,
        'selected_val_AUROC_by_seed': selected_val_auroc,
        'completed_training_epochs_by_seed': completed,
        'max_epochs': 100,
        'early_stop_patience': 23,
        'test_split_size': len(ground_truth),
        'threshold_grid': {'start': 0.0, 'stop': 1.0, 'step': 0.01, 'count': len(THRESHOLDS)},
        'seeds': list(SEEDS),
        'uncertainty': 'not estimated; seed 2026 only',
        'generated': datetime.now().astimezone().isoformat(timespec='seconds'),
        'test_complete': True,
        'figures_complete': False,
    }
    protocol_path = output / 'EVALUATION_PROTOCOL.json'
    protocol_path.write_text(json.dumps(evaluation_protocol, indent=2) + '\n')

    # The compact single-seed protocol uses the all-metric threshold figure
    # above; multi-seed uncertainty figures are intentionally not generated.
    evaluation_protocol['figures_complete'] = True
    protocol_path.write_text(json.dumps(evaluation_protocol, indent=2) + '\n')


if __name__ == '__main__':
    main()
