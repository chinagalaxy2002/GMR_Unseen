"""Evaluate a Task A Enhancement checkpoint on official Test set and verify against E0."""
import argparse
import sys
from pathlib import Path
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))

from environment import ROOT, make_dataset, options, read_json, write_json, write_rows
from diagnostics import save_final_diagnostics
from model import TaskAEnhancement
from validation import predictions, validate
from models.flash_vtg_gmr.model import build_model1


def evaluate_run(run_id, device='cuda:0', reference_predictions=None, smoke=False):
    run_dir = ROOT / ('tests/smoke' if smoke else 'runs') / run_id
    job = dict(read_json(run_dir / 'CONFIG.json')['identity']['job'])
    ckpt_path = run_dir / 'best.ckpt'
    assert ckpt_path.exists(), f"Checkpoint not found: {ckpt_path}"

    opt = options(job, device)
    base, _ = build_model1(opt)
    model = TaskAEnhancement(base, job).to(device)

    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    model.load_state_dict(ckpt['model'])
    model.eval()

    print(f"\n[EVAL] Loading Test dataset for {run_id}...")
    test_ds = make_dataset(opt, 'test', smoke=smoke)
    print(f"[EVAL] Running predictions on {len(test_ds)} test samples on {device}...")
    pre_test, post_test, diagnostic_internals = predictions(model, test_ds, opt, capture_diagnostics=True)

    ref_test = Path(reference_predictions).resolve()
    if not ref_test.exists():
        raise FileNotFoundError(f'missing same-seed Task A Test predictions: {ref_test}')
    print(f"[EVAL] Validating against reference E0 test predictions: {ref_test}...")
    report = validate(pre_test, post_test, test_ds.data, opt, reference_path=ref_test)
    frozen_threshold = read_json(run_dir / 'validation_metrics.json')['val_BA_threshold']['threshold']
    report['test_oracle_BA_threshold'] = report['val_BA_threshold']
    from validation import _threshold_metrics
    report['val_BA_threshold'] = _threshold_metrics(post_test, test_ds.data, frozen_threshold)
    report['val_BA_threshold']['threshold_source'] = 'frozen on Val'

    # Save test outputs
    test_metrics_path = run_dir / 'test_metrics.json'
    test_preds_path = run_dir / 'test_predictions.jsonl'
    test_pre_nms_path = run_dir / 'test_predictions_pre_nms.jsonl'

    write_json(test_metrics_path, report)
    write_rows(test_preds_path, post_test)
    write_rows(test_pre_nms_path, pre_test)
    save_final_diagnostics(run_dir, post_test, test_ds.data, diagnostic_internals, ckpt['epoch'],
                           opt.clip_length, getattr(opt, 'exist_pool', 'mean'), model)
    frozen = read_json(run_dir / 'selection/frozen.json')
    frozen.update(test_started=True, test_completed=True)
    write_json(run_dir / 'selection/frozen.json', frozen)

    print("\n" + "=" * 75)
    print(f"OFFICIAL TEST EVALUATION REPORT: {run_id}")
    print("=" * 75)
    print(f"Native Pre-NMS mAP:      {report['native_pre_nms']['MR-full-mAP']:.2f}%")
    print(f"Raw Localizer Pre-NMS:   {report['raw_localizer_pre_exist']['MR-full-mAP']:.2f}%")
    print(f"Localizer Matches E0:    {report['localizer_matches_e0']}")
    print(f"Test AUROC:              {report['AUROC']:.2f}%")
    print(f"Test G-mIoU@1 (gate=0.4):{report['gate_04']['G-mIoU@1']:.2f}%")
    print(f"Test G-mIoU@1 (gate=0.5):{report['fixed_05']['G-mIoU@1']:.2f}%")
    print(f"Test G-mIoU@1 (calib):   {report['val_BA_threshold']['G-mIoU@1']:.2f}%")
    print(f"Test Rej-F1 @ 0.4:       {report['gate_04']['Rej-F1']:.2f}%")
    print(f"Test N-acc @ 0.4:        {report['gate_04']['negative_recall']:.2f}%")
    print(f"Test PosRecall @ 0.4:    {report['gate_04']['positive_recall']:.2f}%")
    if 'plurality' in report:
        print(f"Plurality Balanced Acc:  {report['plurality']['balanced_accuracy']:.2f}%")
        print(f"Plurality AUROC:         {report['plurality']['AUROC']:.2f}%")
    print("=" * 75)
    print(f"Saved: {test_metrics_path}")
    print(f"Saved: {test_preds_path}")
    print(f"Saved: {test_pre_nms_path}")
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='A3_similarity_hardneg_s2024')
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--reference-predictions', required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    evaluate_run(args.run, args.device, args.reference_predictions, args.smoke)
