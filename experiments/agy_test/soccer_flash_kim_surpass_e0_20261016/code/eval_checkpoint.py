"""Standalone evaluator to evaluate any checkpoint against official Test set and compare with E0."""
import argparse
import sys
from pathlib import Path
import torch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
sys.path.insert(0, str(ROOT / 'baseline_source'))

from environment import options, make_dataset, read_json, write_json
from models.flash_vtg_gmr.model import build_model1
from model import RetrievalModel
from validation import predictions, validate

E0_TEST = {
    'mAP': 26.14,
    'AUROC': 74.27,
    'G-mIoU@1_04': 34.66,
    'G-mIoU@1_05': 46.19,
    'G-mIoU@3_04': 28.24,
    'Rej-F1@0.4': 54.16,
    'N-acc@0.4': 46.34,
    'PositiveRecall@0.4': 77.94
}

def evaluate_checkpoint(ckpt_path, job_config, device='cuda'):
    opt = options(job_config, device)
    base, _ = build_model1(opt)
    model = RetrievalModel(base, job_config).to(device)
    
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    model.load_state_dict(ckpt['model'])
    model.eval()

    test_ds = make_dataset(opt, 'test')
    pre_test, post_test = predictions(model, test_ds, opt)
    report = validate(pre_test, post_test, test_ds.data, opt)

    loc = report['positive_localization']
    brief = {
        'epoch': ckpt.get('epoch', -1),
        'best_val_mAP': ckpt.get('best', -1),
        'test_mAP': loc['mAP'],
        'test_mR@1': loc['mR@1'],
        'test_mR@5': loc['mR@5'],
        'test_AUROC': report['AUROC'],
        'test_AUROC_raw': report['AUROC_raw'],
        'test_GmIoU1_04': report['gate_04']['G-mIoU@1'],
        'test_GmIoU1_05': report['fixed_05']['G-mIoU@1'],
        'test_GmIoU1_calib': report['own_val_BA_threshold']['G-mIoU@1'],
        'test_RejF1_04': report['gate_04']['Rej-F1'],
        'test_Nacc_04': report['gate_04']['negative_recall'],
        'test_PosRecall_04': report['gate_04']['positive_recall']
    }

    print("\n" + "=" * 70)
    print(f"EVALUATION OF: {ckpt_path}")
    print("=" * 70)
    print(f"{'Metric':<22} | {'Baseline E0':<12} | {'Current Model':<14} | {'Diff':<10}")
    print("-" * 70)
    diff_map = brief['test_mAP'] - E0_TEST['mAP']
    diff_auroc = brief['test_AUROC'] - E0_TEST['AUROC']
    diff_gm04 = brief['test_GmIoU1_04'] - E0_TEST['G-mIoU@1_04']
    diff_gm05 = brief['test_GmIoU1_05'] - E0_TEST['G-mIoU@1_05']
    diff_rej = brief['test_RejF1_04'] - E0_TEST['Rej-F1@0.4']
    diff_nacc = brief['test_Nacc_04'] - E0_TEST['N-acc@0.4']

    print(f"{'mAP (Localization)':<22} | {E0_TEST['mAP']:<12.2f} | {brief['test_mAP']:<14.2f} | {diff_map:+6.2f}%")
    print(f"{'AUROC (Existence)':<22} | {E0_TEST['AUROC']:<12.2f} | {brief['test_AUROC']:<14.2f} | {diff_auroc:+6.2f}%")
    print(f"{'G-mIoU@1 (gate=0.4)':<22} | {E0_TEST['G-mIoU@1_04']:<12.2f} | {brief['test_GmIoU1_04']:<14.2f} | {diff_gm04:+6.2f}%")
    print(f"{'G-mIoU@1 (gate=0.5)':<22} | {E0_TEST['G-mIoU@1_05']:<12.2f} | {brief['test_GmIoU1_05']:<14.2f} | {diff_gm05:+6.2f}%")
    print(f"{'G-mIoU@1 (calibrated)':<22} | {'—':<12} | {brief['test_GmIoU1_calib']:<14.2f} | —")
    print(f"{'Rej-F1 @ 0.4':<22} | {E0_TEST['Rej-F1@0.4']:<12.2f} | {brief['test_RejF1_04']:<14.2f} | {diff_rej:+6.2f}%")
    print(f"{'N-acc @ 0.4':<22} | {E0_TEST['N-acc@0.4']:<12.2f} | {brief['test_Nacc_04']:<14.2f} | {diff_nacc:+6.2f}%")
    print("=" * 70)
    return brief, report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', required=True)
    parser.add_argument('--variant', default='E2M')
    parser.add_argument('--multi_source', default='text')
    parser.add_argument('--scale', type=float, default=0.25)
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--plurality-gating', action='store_true', default=True)
    args = parser.parse_args()
    
    cfg = {
        'variant': args.variant,
        'multi_source': args.multi_source,
        'feature_grad_scale': args.scale,
        'use_plurality_gating': args.plurality_gating,
        'epochs': 60, 'seed': 2024, 'lr': 3e-5, 'grad_clip': 0.1, 'wd': 1e-4
    }
    evaluate_checkpoint(args.ckpt, cfg, args.device)
