#!/usr/bin/env python3
"""
Comprehensive Benchmarking of Existence Adapters against Official QD-DETR Baseline.
Evaluates:
- Seen AUROC
- Unseen AUROC
- Seen-Unseen Gap
- Matched Pair Accuracy
- U+ False Refusal Rate
- U- Rejection Rate
"""
import sys
from pathlib import Path
import numpy as np
import torch

from tune_existence_adapter import (
    BASELINE_QD,
    train_and_eval,
)

ARCHITECTURES = [
    "baseline_max",
    "scalar_max",
    "attentive_convex",
    "contrastive_slot",
    "hybrid_evidence",
]

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def main():
    target_split = sys.argv[1] if len(sys.argv) > 1 else "A1"
    device = sys.argv[2] if len(sys.argv) > 2 else "cuda:0"
    
    print(f"================================================================================")
    print(f"BENCHMARKING ADAPTERS ON SPLIT: {target_split} (Device: {device})")
    print(f"Official Baseline: Seen={BASELINE_QD[target_split]['Seen']:.4f}, "
          f"Unseen={BASELINE_QD[target_split]['Unseen']:.4f}, "
          f"Gap={BASELINE_QD[target_split]['Gap']:.4f}, "
          f"PairAcc={BASELINE_QD[target_split]['PairAcc']:.4f}")
    print(f"================================================================================\n")
    
    base = BASELINE_QD[target_split]
    results = {}
    
    for arch in ARCHITECTURES:
        print(f"--> Running {arch}...")
        res = train_and_eval(arch, target_split, epochs=15, lr=5e-4, seed=3407, device=device)
        results[arch] = res
        print(f"    Seen AUROC:      {res['Seen_AUROC']:.4f} ({res['Seen_AUROC'] - base['Seen']:+.4f})")
        print(f"    Unseen AUROC:    {res['Unseen_AUROC']:.4f} ({res['Unseen_AUROC'] - base['Unseen']:+.4f})")
        print(f"    Seen-Unseen Gap: {res['Gap']:.4f} ({res['Gap'] - base['Gap']:+.4f})")
        print(f"    Matched PairAcc: {res['Matched_PairAcc']:.4f} ({res['Matched_PairAcc'] - base['PairAcc']:+.4f})")
        print(f"    U+ FRR: {res['U_pos_FRR']:.1f}%, U- RR: {res['U_neg_RR']:.1f}%\n")
        
    print("\n" + "=" * 95)
    print(f"SUMMARY TABLE FOR {target_split}")
    print("=" * 95)
    print(f"{'Method':<20} | {'Seen AUC':<9} | {'Unseen AUC':<10} | {'Gap':<8} | {'Gap Red.':<9} | {'PairAcc':<8} | {'U+ FRR':<7} | {'U- RR':<7}")
    print("-" * 95)
    print(f"{'Official Baseline':<20} | {base['Seen']:<9.4f} | {base['Unseen']:<10.4f} | {base['Gap']:<8.4f} | {'--':<9} | {base['PairAcc']:<8.4f} | {'--':<7} | {'--':<7}")
    
    for arch, r in results.items():
        gap_red = base['Gap'] - r['Gap']
        print(f"{arch:<20} | {r['Seen_AUROC']:<9.4f} | {r['Unseen_AUROC']:<10.4f} | {r['Gap']:<8.4f} | {gap_red:<+9.4f} | {r['Matched_PairAcc']:<8.4f} | {r['U_pos_FRR']:<6.1f}% | {r['U_neg_RR']:<6.1f}%")
    print("=" * 95)

if __name__ == "__main__":
    main()
