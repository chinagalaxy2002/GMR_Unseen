"""Evaluate MCEV checkpoint on official Test set and compute comprehensive metrics."""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

from environment import ROOT, E0_TEST_PREDICTIONS, make_dataset, options, read_json, write_json, write_rows
from model import MCEVModel
from validation import predictions, threshold_metrics, validate, assert_localizer_invariant
from models.flash_vtg_gmr.model import build_model1


def evaluate_test(run_name, device='cuda:0'):
    run_dir = ROOT / 'runs' / run_name
    config = read_json(run_dir / 'CONFIG.json')
    job = config['job']
    seed = config['seed']
    
    ckpt_path = run_dir / 'best.ckpt'
    assert ckpt_path.exists(), f"Missing checkpoint: {ckpt_path}"
    
    val_metrics = read_json(run_dir / 'validation_metrics.json')
    best_t_ba = val_metrics['best_t_ba']
    best_t_gmiou = val_metrics['best_t_gmiou']
    
    opt = options(job, device)
    base, _ = build_model1(opt)
    model = MCEVModel(base, job).to(device)
    
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    model.load_state_dict(ckpt['model'])
    model.eval()
    
    test_ds = make_dataset(opt, 'test')
    print(f"\n[TEST EVAL: {run_name}] Running inference on {len(test_ds)} Test samples...")
    pre_test, post_test = predictions(model, test_ds, opt)
    
    ref_test_path = E0_TEST_PREDICTIONS[seed]
    print(f"[TEST EVAL: {run_name}] Verifying localizer invariance against {ref_test_path.name}...")
    report = validate(pre_test, post_test, test_ds.data, opt, reference_path=ref_test_path)
    
    # Val-calibrated metrics applied to Test
    report['val_BA_calibrated'] = threshold_metrics(post_test, test_ds.data, best_t_ba)
    report['val_BA_calibrated']['threshold'] = best_t_ba
    report['val_G_calibrated'] = threshold_metrics(post_test, test_ds.data, best_t_gmiou)
    report['val_G_calibrated']['threshold'] = best_t_gmiou
    
    # Save test outputs
    write_json(run_dir / 'test_metrics.json', report)
    write_rows(run_dir / 'test_predictions.jsonl', post_test)
    write_rows(run_dir / 'test_predictions_pre_nms.jsonl', pre_test)
    
    print("\n" + "=" * 80)
    print(f"OFFICIAL TEST REPORT: {run_name} (Seed {seed})")
    print("=" * 80)
    print(f"Localizer Invariance to E0:  {report['localizer_matches_e0']} (Bitwise identical)")
    print(f"Test AUROC:                  {report['AUROC']:.2f}%")
    print(f"Fixed Gate 0.4 G-mIoU@1:     {report['gate_04']['G-mIoU@1']:.2f}% (NegRec: {report['gate_04']['negative_recall']:.1f}%, PosRec: {report['gate_04']['positive_recall']:.1f}%)")
    print(f"Fixed Gate 0.5 G-mIoU@1:     {report['fixed_05']['G-mIoU@1']:.2f}% (NegRec: {report['fixed_05']['negative_recall']:.1f}%, PosRec: {report['fixed_05']['positive_recall']:.1f}%)")
    print(f"Fixed Gate 0.6 G-mIoU@1:     {report['gate_06']['G-mIoU@1']:.2f}% (NegRec: {report['gate_06']['negative_recall']:.1f}%, PosRec: {report['gate_06']['positive_recall']:.1f}%)")
    print(f"Val-BA Calibrated G-mIoU@1:  {report['val_BA_calibrated']['G-mIoU@1']:.2f}% (at t={best_t_ba:.2f})")
    print(f"Val-G  Calibrated G-mIoU@1:  {report['val_G_calibrated']['G-mIoU@1']:.2f}% (at t={best_t_gmiou:.2f})")
    print(f"Test Max Achievable G-mIoU:  {report['max_gmiou_scan']:.2f}%")
    print(f"Rejection F1 @ 0.5:          {report['fixed_05']['Rej-F1']:.2f}%")
    if 'plurality' in report:
        print(f"Plurality Balanced Accuracy: {report['plurality']['balanced_accuracy']:.2f}%")
        print(f"Plurality AUROC:             {report['plurality']['AUROC']:.2f}%")
    print("=" * 80 + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()
    evaluate_test(args.run, args.device)


if __name__ == '__main__':
    main()
