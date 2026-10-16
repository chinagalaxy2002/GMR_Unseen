"""Validation and metric evaluation supporting official GMR benchmarks, plurality gating, and calibrated thresholding."""
import copy
import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, confusion_matrix

from training.flash_vtg_gmr.dataset import start_end_collate
from training.flash_vtg_gmr.inference import compute_mr_results, post_processing_mr_nms
from models.flash_vtg_gmr.standalone_eval.eval import eval_submission
from eval.eval_main import evaluate_gmr
from eval.metrics import compute_gmr_cls, prepare_submission_for_gmiou, compute_G_mIoU

def apply_plurality_gating(predictions_list):
    """Scheme B: Plurality-Conditioned Dynamic Filtering.
    When plurality prediction indicates single event (p_multi < 0.45),
    suppress lower-confidence secondary windows to eliminate false-positive clutter.
    When multi-event (p_multi >= 0.45), retain multiple non-overlapping windows.
    """
    gated = []
    for p in predictions_list:
        p_c = copy.deepcopy(p)
        if 'pred_multi_logits_raw' in p:
            logits = p['pred_multi_logits_raw']
            p_multi = float(np.exp(logits[1]) / (np.exp(logits[0]) + np.exp(logits[1])))
            p_c['pred_multi_prob'] = p_multi
            windows = p_c.get('pred_relevant_windows', [])
            if p_multi < 0.45 and len(windows) > 1:
                p_c['pred_relevant_windows'] = windows[:1]
        gated.append(p_c)
    return gated

@torch.no_grad()
def predictions(model, data, opt):
    captured = []
    def collect(module, args, out):
        z = out['pred_exist_logits'].detach().cpu().double().reshape(-1).tolist()
        multi = out.get('pred_multi_logits')
        for i, v in enumerate(z):
            row = {'pred_exist_logit_raw': v}
            if multi is not None:
                row['pred_multi_logits_raw'] = multi[i].detach().cpu().double().tolist()
            captured.append(row)

    handle = model.register_forward_hook(collect)
    try:
        loader = DataLoader(data, batch_size=1, shuffle=False, num_workers=0, collate_fn=start_end_collate)
        pre, _ = compute_mr_results(model, loader, opt, None, None, None)
    finally:
        handle.remove()

    assert len(captured) == len(pre) == len(data)
    assert [p['qid'] for p in pre] == [r['qid'] for r in data.data]
    for p, c in zip(pre, captured):
        p.update(c)
    post = post_processing_mr_nms(copy.deepcopy(pre), opt.nms_thd, opt.max_before_nms, opt.max_after_nms, opt.nms_type)
    
    if getattr(opt, 'use_plurality_gating', False):
        post = apply_plurality_gating(post)
        
    return pre, post

def threshold_metrics(pred, gt, threshold):
    effective = float(np.nextafter(threshold, -np.inf))
    cls = next(iter(compute_gmr_cls(pred, gt, (effective,))['per_threshold'].values()))
    gated, _ = prepare_submission_for_gmiou(pred, effective, 10)
    values = compute_G_mIoU(gated, gt, (1, 3, 5))
    values.update(cls)
    lookup = {p['qid']: p for p in pred}
    y = np.array([bool(g['relevant_windows']) for g in gt])
    s = np.array([lookup[g['qid']]['pred_exist_score'] for g in gt])
    a = s >= threshold
    values.update(
        threshold=threshold,
        positive_if='p >= threshold',
        negative_recall=100.0 * float((~a[~y]).mean()),
        positive_recall=100.0 * float(a[y].mean()),
        balanced_accuracy=50.0 * float(a[y].mean() + (~a[~y]).mean())
    )
    return values

def validate(pre, post, gt, opt):
    native = eval_submission(copy.deepcopy(pre), gt, verbose=False, match_number=True, full_only=opt.eval_full_only, mr_only=opt.mr_only)
    
    # Official benchmark gate at 0.4
    eff_04 = float(np.nextafter(0.4, -np.inf))
    metrics_04 = evaluate_gmr(copy.deepcopy(post), gt, k_list=(1, 3, 5), max_pred_windows=10,
                              cls_thresholds=(eff_04,), gmiou_cls_threshold=eff_04, map_num_workers=0, verbose=False)
    
    lookup = {p['qid']: p for p in post}
    y = np.array([bool(g['relevant_windows']) for g in gt])
    s = np.array([lookup[g['qid']]['pred_exist_score'] for g in gt])
    candidates = np.unique(s)
    
    # Calibrated threshold on Val (maximizing Balanced Accuracy)
    ba = np.array([0.5 * ((s[y] >= t).mean() + (s[~y] < t).mean()) for t in candidates])
    t_opt = float(candidates[int(ba.argmax())])
    
    raw = np.array([lookup[g['qid']]['pred_exist_logit_raw'] for g in gt])
    report = {
        'native_pre_nms': native['brief'],
        'positive_localization': {k: v for k, v in metrics_04['brief'].items() if k.startswith(('mAP', 'mR', 'mIoU'))},
        'AUROC': metrics_04['brief']['AUROC'],
        'AUROC_raw': 100.0 * float(roc_auc_score(y, raw)),
        'gate_04': threshold_metrics(post, gt, 0.4),
        'fixed_05': threshold_metrics(post, gt, 0.5),
        'own_val_BA_threshold': threshold_metrics(post, gt, t_opt),
        'counts': {'total': len(gt), 'positive': int(y.sum()), 'negative': int((~y).sum())}
    }
    
    # Plurality metrics if head active
    if all('pred_multi_logits_raw' in lookup[g['qid']] for g in gt):
        pgt = [g for g in gt if g['relevant_windows']]
        labels = np.array([len(g['relevant_windows']) >= 2 for g in pgt])
        z = np.array([lookup[g['qid']]['pred_multi_logits_raw'] for g in pgt])
        v = z - z.max(1, keepdims=True)
        prob = np.exp(v) / np.exp(v).sum(1, keepdims=True)
        guess = z.argmax(1)
        report['plurality'] = {
            'scope': 'GT positives only',
            'n': len(labels),
            'accuracy': 100.0 * float((guess == labels).mean()),
            'balanced_accuracy': 100.0 * float(balanced_accuracy_score(labels, guess)),
            'AUROC': 100.0 * float(roc_auc_score(labels, prob[:, 1])) if len(np.unique(labels)) == 2 else None,
            'confusion': confusion_matrix(labels, guess, labels=[0, 1]).tolist()
        }
    return report

def evaluate_on_test(model, opt, run_dir):
    """Full official Test set evaluation on 1,036 samples with predictions saved."""
    from environment import make_dataset, write_rows, write_json
    test_ds = make_dataset(opt, 'test')
    pre_test, post_test = predictions(model, test_ds, opt)
    test_report = validate(pre_test, post_test, test_ds.data, opt)
    write_json(run_dir / 'test_metrics.json', test_report)
    write_rows(run_dir / 'test_predictions.jsonl', post_test)
    write_rows(run_dir / 'test_predictions_pre_nms.jsonl', pre_test)
    return test_report
