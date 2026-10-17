"""Validation-only evaluation and immutable-localizer checks."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, roc_auc_score
from torch.utils.data import DataLoader

from training.flash_vtg_gmr.dataset import start_end_collate
from training.flash_vtg_gmr.inference import compute_mr_results, post_processing_mr_nms
from models.flash_vtg_gmr.standalone_eval.eval import eval_submission
from eval.metrics import compute_G_mIoU, compute_gmr_cls, prepare_submission_for_gmiou


def _stable_localizer_payload(rows):
    payload = []
    for row in rows:
        windows = row.get('pred_relevant_windows_pre_exist')
        if windows is None:
            raise AssertionError('pred_relevant_windows_pre_exist is required for the safety check')
        payload.append([row['qid'], [[round(float(v), 6) for v in window] for window in windows]])
    return payload


def localizer_fingerprint(rows):
    raw = json.dumps(_stable_localizer_payload(rows), separators=(',', ':'), sort_keys=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def assert_localizer_invariant(rows, reference_path, tol=1e-6):
    reference = [json.loads(line) for line in Path(reference_path).read_text().splitlines() if line.strip()]
    got_payload = _stable_localizer_payload(rows)
    ref_payload = _stable_localizer_payload(reference)
    if len(got_payload) != len(ref_payload):
        raise AssertionError('localizer output count changed')
    if got_payload != ref_payload:
        for index, (got, ref) in enumerate(zip(got_payload, ref_payload)):
            if got[0] != ref[0]:
                raise AssertionError(f'qid mismatch at row {index}: {got[0]} vs {ref[0]}')
            got_w = np.array(got[1])
            ref_w = np.array(ref[1])
            if got_w.shape != ref_w.shape or not np.allclose(got_w, ref_w, atol=tol):
                raise AssertionError(f'localizer output changed at row {index}, qid={got[0]}')
    return localizer_fingerprint(rows)


@torch.no_grad()
def predictions(model, dataset, opt, capture_diagnostics=False):
    captured = []
    internals = []

    def collect(_module, _args, output):
        logits = output['pred_exist_logits'].detach().cpu().double().reshape(-1)
        multi = output['pred_multi_logits'].detach().cpu().double()
        count = output.get('pred_count_logits')
        count = count.detach().cpu().double() if count is not None else None
        for index, value in enumerate(logits.tolist()):
            row = {
                'pred_exist_logit_raw': value,
                'pred_multi_logits_raw': multi[index].tolist(),
            }
            if count is not None:
                row['pred_count_logits_raw'] = count[index].tolist()
            captured.append(row)
            if capture_diagnostics:
                internals.append({
                    'video_units': output['diagnostic_video_units'][index].detach().cpu().float().numpy(),
                    'video_valid': output['diagnostic_video_valid'][index].detach().cpu().bool().numpy(),
                    'readout_states': output['diagnostic_readout_states'][index].detach().cpu().float().numpy(),
                    'video_attention': output['diagnostic_video_attention'][index].detach().cpu().float().numpy(),
                    'native_exist_input': output['diagnostic_native_exist_input'][index].detach().cpu().float().numpy(),
                    'text_memory': output['diagnostic_text_memory'][index].detach().cpu().float().numpy(),
                    'text_valid': output['diagnostic_text_valid'][index].detach().cpu().bool().numpy(),
                    'video_memories': output['diagnostic_video_memories'][index].detach().cpu().float().numpy(),
                })

    handle = model.register_forward_hook(collect)
    try:
        loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0, collate_fn=start_end_collate)
        pre, _ = compute_mr_results(model, loader, opt, None, None, None)
    finally:
        handle.remove()
    assert len(captured) == len(pre) == len(dataset)
    for prediction, extra in zip(pre, captured):
        prediction.update(extra)
    post = post_processing_mr_nms(
        copy.deepcopy(pre), opt.nms_thd, opt.max_before_nms, opt.max_after_nms, opt.nms_type
    )
    return (pre, post, internals) if capture_diagnostics else (pre, post)


def _threshold_metrics(predictions_list, ground_truth, threshold):
    effective = float(np.nextafter(threshold, -np.inf))
    classification = next(iter(compute_gmr_cls(predictions_list, ground_truth, (effective,))['per_threshold'].values()))
    gated, _ = prepare_submission_for_gmiou(predictions_list, effective, 10)
    values = compute_G_mIoU(gated, ground_truth, (1, 3, 5))
    values.update(classification)
    lookup = {row['qid']: row for row in predictions_list}
    labels = np.array([bool(row['relevant_windows']) for row in ground_truth])
    scores = np.array([lookup[row['qid']]['pred_exist_score'] for row in ground_truth])
    guess = scores >= threshold
    values.update(
        threshold=float(threshold),
        negative_recall=100.0 * float((~guess[~labels]).mean()),
        positive_recall=100.0 * float(guess[labels].mean()),
        balanced_accuracy=50.0 * float(guess[labels].mean() + (~guess[~labels]).mean()),
    )
    return values


def validate(pre, post, ground_truth, opt, reference_path=None):
    fingerprint = None
    if reference_path is not None:
        fingerprint = assert_localizer_invariant(pre, reference_path)
    native = eval_submission(
        copy.deepcopy(pre), ground_truth, verbose=False, match_number=True,
        full_only=opt.eval_full_only, mr_only=opt.mr_only,
    )
    raw_pre = copy.deepcopy(pre)
    for row in raw_pre:
        row['pred_relevant_windows'] = copy.deepcopy(row['pred_relevant_windows_pre_exist'])
    raw_native = eval_submission(
        raw_pre, ground_truth, verbose=False, match_number=True,
        full_only=opt.eval_full_only, mr_only=opt.mr_only,
    )
    lookup = {row['qid']: row for row in post}
    labels = np.array([bool(row['relevant_windows']) for row in ground_truth])
    scores = np.array([lookup[row['qid']]['pred_exist_score'] for row in ground_truth])
    raw_logits = np.array([lookup[row['qid']]['pred_exist_logit_raw'] for row in ground_truth])
    candidates = np.unique(scores)
    balanced = np.array([
        0.5 * ((scores[labels] >= threshold).mean() + (scores[~labels] < threshold).mean())
        for threshold in candidates
    ])
    threshold = float(candidates[int(balanced.argmax())])
    report = {
        'native_pre_nms': native['brief'],
        'raw_localizer_pre_exist': raw_native['brief'],
        'localizer_fingerprint': fingerprint,
        'localizer_matches_e0': True,
        'AUROC': 100.0 * float(roc_auc_score(labels, raw_logits)),
        'gate_04': _threshold_metrics(post, ground_truth, 0.4),
        'fixed_05': _threshold_metrics(post, ground_truth, 0.5),
        'val_BA_threshold': _threshold_metrics(post, ground_truth, threshold),
        'counts': {'total': len(labels), 'positive': int(labels.sum()), 'negative': int((~labels).sum())},
    }

    positive_gt = [row for row in ground_truth if row['relevant_windows']]
    plural_labels = np.array([len(row['relevant_windows']) >= 2 for row in positive_gt])
    multi_logits = np.array([lookup[row['qid']]['pred_multi_logits_raw'] for row in positive_gt])
    shifted = multi_logits - multi_logits.max(1, keepdims=True)
    multi_prob = np.exp(shifted) / np.exp(shifted).sum(1, keepdims=True)
    multi_guess = multi_logits.argmax(1)
    report['plurality'] = {
        'balanced_accuracy': 100.0 * float(balanced_accuracy_score(plural_labels, multi_guess)),
        'AUROC': 100.0 * float(roc_auc_score(plural_labels, multi_prob[:, 1])),
        'confusion': confusion_matrix(plural_labels, multi_guess, labels=[0, 1]).tolist(),
    }
    if all('pred_count_logits_raw' in lookup[row['qid']] for row in ground_truth):
        count_labels = np.array([min(3, len(row['relevant_windows'])) for row in ground_truth])
        count_guess = np.array([
            int(np.argmax(lookup[row['qid']]['pred_count_logits_raw'])) for row in ground_truth
        ])
        report['cardinality'] = {
            'macro_f1': 100.0 * float(f1_score(count_labels, count_guess, average='macro')),
            'accuracy': 100.0 * float((count_labels == count_guess).mean()),
            'confusion_0_1_2_3plus': confusion_matrix(count_labels, count_guess, labels=[0, 1, 2, 3]).tolist(),
        }
    return report
