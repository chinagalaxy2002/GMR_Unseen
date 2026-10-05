#!/usr/bin/env python3
"""
Explore optimal calibration and fusion of existing backbone signals:
- orig_logits (GMR existence head output)
- fg_max (DETR slot maximum foreground probability)
- cos_disp (slot cosine disparity from mean slot)
- slot_max_dev (slot maximum L2 deviation from mean slot)
- slot_var (mean slot variance)

Evaluates on all 5 splits: Seen AUROC, Unseen AUROC, Gap, Matched PairAcc.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

REPO = Path(__file__).resolve().parents[3]
HQ_DIR = REPO / "experiments/agy_test/cache/hq"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

from diagnose_signals import eval_scores, compute_signals

def evaluate_fusion_rule(rule_fn, name=""):
    seen_list, unseen_list, gap_list, pair_list = [], [], [], []
    per_split = {}
    for split in SPLITS:
        val_data = np.load(HQ_DIR / split / "val.npz")
        test_data = np.load(HQ_DIR / split / "test.npz")
        val_sig = compute_signals(val_data)
        test_sig = compute_signals(test_data)
        
        v_scores = rule_fn(val_sig, val_data)
        t_scores = rule_fn(test_sig, test_data)
        
        res = eval_scores(split, v_scores, t_scores)
        seen_list.append(res["Seen"])
        unseen_list.append(res["Unseen"])
        gap_list.append(res["Gap"])
        pair_list.append(res["PairAcc"])
        per_split[split] = res
        
    m_seen = np.mean(seen_list)
    m_unseen = np.mean(unseen_list)
    m_gap = np.mean(gap_list)
    m_pair = np.mean(pair_list)
    
    print(f"{name:<45} | Seen: {m_seen:.4f} | Unseen: {m_unseen:.4f} | Gap: {m_gap:.4f} (Red: {0.2332 - m_gap:+.4f}) | PairAcc: {m_pair:.4f}")
    return {"mean_seen": m_seen, "mean_unseen": m_unseen, "mean_gap": m_gap, "mean_pair": m_pair, "per_split": per_split}

def main():
    print("========================================================================================================")
    print("SEARCHING OPTIMAL FUSION RULES ACROSS 5 SPLITS")
    print("Baseline Target: Seen=0.7476, Unseen=0.5144, Gap=0.2332, PairAcc=0.5294")
    print("Goal: Reduce Gap significantly ('AUROC降低的少一些'), higher Unseen AUROC")
    print("========================================================================================================\n")
    
    # 0. Raw Baseline
    evaluate_fusion_rule(lambda s, d: s["orig_logits"], "0. Raw GMR orig_logits Baseline")
    
    # 1. Percentile / Rank Fusion
    for w_disp in [0.2, 0.4, 0.6, 0.8, 1.0]:
        def rank_fuse(s, d, w=w_disp):
            r_orig = rankdata(s["orig_logits"]) / len(s["orig_logits"])
            r_disp = rankdata(s["cos_disp"]) / len(s["cos_disp"])
            return r_orig + w * r_disp
        evaluate_fusion_rule(rank_fuse, f"Rank(orig) + {w_disp}*Rank(cos_disp)")
        
    for w_disp in [0.2, 0.4, 0.6, 0.8, 1.0]:
        def rank_fuse2(s, d, w=w_disp):
            r_orig = rankdata(s["orig_logits"]) / len(s["orig_logits"])
            r_dev = rankdata(s["slot_max_dev"]) / len(s["slot_max_dev"])
            return r_orig + w * r_dev
        evaluate_fusion_rule(rank_fuse2, f"Rank(orig) + {w_disp}*Rank(slot_max_dev)")
        
    # 2. Multiplicative Rank Fusion: Rank(orig) * Rank(cos_disp)
    for p in [0.25, 0.5, 1.0, 1.5]:
        def rank_mult(s, d, power=p):
            r_orig = rankdata(s["orig_logits"]) / len(s["orig_logits"])
            r_disp = rankdata(s["cos_disp"]) / len(s["cos_disp"])
            return (r_orig ** 1.0) * (r_disp ** power)
        evaluate_fusion_rule(rank_mult, f"Rank(orig) * Rank(cos_disp)^{p}")
        
    # 3. Standardized Linear Combination
    for c_disp in [0.3, 0.5, 0.8, 1.0, 1.5]:
        def std_lin(s, d, c=c_disp):
            z_orig = (s["orig_logits"] - np.mean(s["orig_logits"])) / (np.std(s["orig_logits"]) + 1e-6)
            z_disp = (s["cos_disp"] - np.mean(s["cos_disp"])) / (np.std(s["cos_disp"]) + 1e-6)
            return z_orig + c * z_disp
        evaluate_fusion_rule(std_lin, f"Std(orig) + {c_disp}*Std(cos_disp)")
        
    for c_dev in [0.3, 0.5, 0.8, 1.0, 1.5]:
        def std_lin_dev(s, d, c=c_dev):
            z_orig = (s["orig_logits"] - np.mean(s["orig_logits"])) / (np.std(s["orig_logits"]) + 1e-6)
            z_dev = (s["slot_max_dev"] - np.mean(s["slot_max_dev"])) / (np.std(s["slot_max_dev"]) + 1e-6)
            return z_orig + c * z_dev
        evaluate_fusion_rule(std_lin_dev, f"Std(orig) + {c_dev}*Std(slot_max_dev)")
        
    # 4. Tri-Modal: orig + cos_disp + fg_max
    for c_disp, c_fg in [(0.5, 0.3), (0.8, 0.5), (1.0, 0.5), (1.2, 0.6)]:
        def std_tri(s, d, cd=c_disp, cf=c_fg):
            z_orig = (s["orig_logits"] - np.mean(s["orig_logits"])) / (np.std(s["orig_logits"]) + 1e-6)
            z_disp = (s["cos_disp"] - np.mean(s["cos_disp"])) / (np.std(s["cos_disp"]) + 1e-6)
            z_fg = (s["fg_max"] - np.mean(s["fg_max"])) / (np.std(s["fg_max"]) + 1e-6)
            return z_orig + cd * z_disp + cf * z_fg
        evaluate_fusion_rule(std_tri, f"Std(orig) + {c_disp}*Std(cos_disp) + {c_fg}*Std(fg)")

if __name__ == "__main__":
    main()
