#!/usr/bin/env python3
"""
Reproducibility Suite for Decomposed Directional Verifier (DDV).

Usage:
  # 1. Instant Verification (re-evaluate existing checkpoints in ~5 seconds):
  python reproduce.py --mode eval

  # 2. Full End-to-End Retraining & Evaluation (~3 minutes on 2x RTX 3090):
  python reproduce.py --mode train

  # 3. Complete Ground-Zero Pipeline (Data Prep -> Train -> Eval -> Bootstrap -> Report):
  python reproduce.py --mode all
"""
from __future__ import annotations
import sys
import os
import argparse
import json
import time
from pathlib import Path
import numpy as np
import torch

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[2]

sys.path.insert(0, str(BASE_DIR))
from model import DecomposedDirectionalVerifier
import prepare_data
import train_and_eval
import generate_report

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def check_environment():
    print("=" * 80)
    print("           ENVIRONMENT & PREREQUISITES VERIFICATION            ")
    print("=" * 80)
    print(f"Python version : {sys.version.split()[0]}")
    print(f"PyTorch version: {torch.__version__}")
    cuda_avail = torch.cuda.is_available()
    print(f"CUDA Available : {cuda_avail}")
    if cuda_avail:
        n_gpus = torch.cuda.device_count()
        print(f"GPU Count      : {n_gpus}")
        for i in range(n_gpus):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("  WARNING: No GPU detected, will run on CPU (slower).")
        n_gpus = 0
    print("=" * 80 + "\n")
    return n_gpus

def evaluate_existing_checkpoints(n_boot: int = 2000):
    print("=" * 80)
    print("      EVALUATING EXISTING DDV CHECKPOINTS (INSTANT VERIFICATION)        ")
    print("=" * 80)
    t0 = time.time()
    
    from sklearn.metrics import roc_auc_score, f1_score
    from train_and_eval import (
        rank_transform,
        choose_val_seen_threshold,
        compute_matched_pair_acc,
        prepare_submission_for_gmiou,
        _compute_set_iou_score,
        run_paired_video_cluster_bootstrap,
        KS,
        CACHE_DIR,
        RUNS_DIR,
        RELEASE_DIR,
        SUBMISSION_DIR,
    )
    
    ordered_results = []
    for split in SPLITS:
        split_dir = RUNS_DIR / split
        ckpt_path = split_dir / "best_model.pt"
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Missing checkpoint: {ckpt_path}. Run with --mode train first.")
            
        feat_dir = CACHE_DIR / split
        tr_d = np.load(feat_dir / "train.npz")
        val_d = np.load(feat_dir / "val.npz")
        te_d = np.load(feat_dir / "test.npz")
        
        X_tr = tr_d["X"]
        X_val, y_val = val_d["X"], val_d["labels"]
        X_te, y_te, parts_te = te_d["X"], te_d["labels"], te_d["partitions"]
        qids_te, vids_te = te_d["qids"], te_d["vids"]
        base_te_scores = te_d["base_scores"]
        
        is_s_te = (parts_te == "S+") | (parts_te == "S-")
        is_u_te = (parts_te == "U+") | (parts_te == "U-")
        
        # Rank transform
        r_val = rank_transform(X_tr, X_val)
        r_te = rank_transform(X_tr, X_te)
        
        t_val = torch.tensor(r_val, dtype=torch.float32)
        t_te = torch.tensor(r_te, dtype=torch.float32)
        
        # Load model
        alpha_min = 0.35
        alpha_max = 0.60 if split == "A3" else 0.55
        model = DecomposedDirectionalVerifier(
            split=split,
            hidden_dim=32,
            alpha_min=alpha_min,
            alpha_max=alpha_max,
        )
        model.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        model.eval()
        
        with torch.no_grad():
            v_scores = model(t_val).numpy()
            seen_threshold = choose_val_seen_threshold(v_scores, y_val)
            val_seen_auc = float(roc_auc_score(y_val, v_scores))
            te_scores = model(t_te).numpy()
            
        b1_seen_auc = float(roc_auc_score(y_te[is_s_te], base_te_scores[is_s_te]))
        b1_unseen_auc = float(roc_auc_score(y_te[is_u_te], base_te_scores[is_u_te]))
        b1_gap = b1_seen_auc - b1_unseen_auc
        
        # Base 2
        qd_sub_file = SUBMISSION_DIR / split / "qd/test/qd_detr_gmr_test_submission.jsonl"
        qd_sub = [json.loads(l) for l in qd_sub_file.read_text().splitlines() if l.strip()]
        qd_map = {str(p["qid"]): float(p.get("pred_exist_score", 0.0)) for p in qd_sub}
        base2_scores = np.array([qd_map[str(q)] for q in qids_te], dtype=np.float32)
        b2_seen_auc = float(roc_auc_score(y_te[is_s_te], base2_scores[is_s_te]))
        b2_unseen_auc = float(roc_auc_score(y_te[is_u_te], base2_scores[is_u_te]))
        b2_gap = b2_seen_auc - b2_unseen_auc
        
        ddv_seen_auc = float(roc_auc_score(y_te[is_s_te], te_scores[is_s_te]))
        ddv_unseen_auc = float(roc_auc_score(y_te[is_u_te], te_scores[is_u_te]))
        ddv_gap = ddv_seen_auc - ddv_unseen_auc
        
        pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
        base_pair_acc = compute_matched_pair_acc(qids_te, base_te_scores, pairs_file)
        ddv_pair_acc = compute_matched_pair_acc(qids_te, te_scores, pairs_file)
        
        u_pos_mask = (parts_te == "U+")
        u_neg_mask = (parts_te == "U-")
        u_preds = (te_scores >= seen_threshold)
        u_pos_frr = float((~u_preds[u_pos_mask]).mean() * 100.0)
        u_neg_rr = float((~u_preds[u_neg_mask]).mean() * 100.0)
        rej_pred_u = (~u_preds).astype(int)
        rej_gt_u = (y_te[is_u_te] == 0).astype(int)
        rej_f1 = float(f1_score(rej_gt_u, rej_pred_u[is_u_te], average="binary") * 100.0)
        
        gt_file = RELEASE_DIR / split / "test.jsonl"
        gt_list = [json.loads(l) for l in gt_file.read_text().splitlines() if l.strip()]
        qd_pred_map = {str(p["qid"]): p for p in qd_sub}
        raw_sub = [{
            "qid": str(q),
            "pred_exist_score": float(te_scores[i] >= seen_threshold),
            "pred_relevant_windows": qd_pred_map[str(q)]["pred_relevant_windows"]
        } for i, q in enumerate(qids_te)]
        gated_sub, _ = prepare_submission_for_gmiou(raw_sub, cls_threshold=0.5, max_pred_windows=10)
        gmiou_vals = np.zeros((len(qids_te), 3))
        for i, x in enumerate(gt_list):
            for m_idx, k in enumerate(KS):
                gmiou_vals[i, m_idx] = _compute_set_iou_score([w[:2] for w in gated_sub[i]["pred_relevant_windows"][:k]], x["relevant_windows"])
        gmiou_seen = [float(gmiou_vals[is_s_te, m_idx].mean() * 100.0) for m_idx in range(3)]
        gmiou_unseen = [float(gmiou_vals[is_u_te, m_idx].mean() * 100.0) for m_idx in range(3)]
        
        ordered_results.append({
            "split": split,
            "val_seen_auc": val_seen_auc,
            "seen_threshold": seen_threshold,
            "base1_seen_auc": b1_seen_auc,
            "base1_unseen_auc": b1_unseen_auc,
            "base1_gap": b1_gap,
            "base2_seen_auc": b2_seen_auc,
            "base2_unseen_auc": b2_unseen_auc,
            "base2_gap": b2_gap,
            "base_pair_acc": base_pair_acc,
            "ddv_seen_auc": ddv_seen_auc,
            "ddv_unseen_auc": ddv_unseen_auc,
            "ddv_gap": ddv_gap,
            "ddv_pair_acc": ddv_pair_acc,
            "gain1_seen": ddv_seen_auc - b1_seen_auc,
            "gain1_unseen": ddv_unseen_auc - b1_unseen_auc,
            "gap_red1": b1_gap - ddv_gap,
            "gain2_seen": ddv_seen_auc - b2_seen_auc,
            "gain2_unseen": ddv_unseen_auc - b2_unseen_auc,
            "gap_red2": b2_gap - ddv_gap,
            "pair_gain": ddv_pair_acc - base_pair_acc,
            "u_pos_frr": u_pos_frr,
            "u_neg_rr": u_neg_rr,
            "rej_f1": rej_f1,
            "gmiou_seen": gmiou_seen,
            "gmiou_unseen": gmiou_unseen,
            "qids": list(qids_te),
            "vids": list(vids_te),
            "partitions": parts_te,
            "labels": y_te,
            "base_hq_scores": base_te_scores,
            "base_rel_scores": base2_scores,
            "ddv_scores": te_scores,
        })
        print(f"[{split}] Eval done: Seen={ddv_seen_auc:.4f}, Unseen={ddv_unseen_auc:.4f}, PairAcc={ddv_pair_acc:.4f}")
        
    bootstrap_results = run_paired_video_cluster_bootstrap(ordered_results, n_boot=n_boot)
    print_results_table(ordered_results, bootstrap_results)

def print_results_table(ordered_results, bootstrap_results):
    b1_seen = np.mean([r["base1_seen_auc"] for r in ordered_results])
    b1_unseen = np.mean([r["base1_unseen_auc"] for r in ordered_results])
    b1_gap = np.mean([r["base1_gap"] for r in ordered_results])
    b1_pair = np.mean([r["base_pair_acc"] for r in ordered_results])
    
    b2_seen = np.mean([r["base2_seen_auc"] for r in ordered_results])
    b2_unseen = np.mean([r["base2_unseen_auc"] for r in ordered_results])
    b2_gap = np.mean([r["base2_gap"] for r in ordered_results])
    
    ddv_seen = np.mean([r["ddv_seen_auc"] for r in ordered_results])
    ddv_unseen = np.mean([r["ddv_unseen_auc"] for r in ordered_results])
    ddv_gap = np.mean([r["ddv_gap"] for r in ordered_results])
    ddv_pair = np.mean([r["ddv_pair_acc"] for r in ordered_results])
    
    print("\n" + "=" * 92)
    print("                       FINAL BENCHMARK REPRODUCTION TABLE                       ")
    print("=" * 92)
    print(f"{'Split':<10} | {'Base1 Unseen':<12} | {'Base2 Unseen':<12} | {'DDV Unseen':<12} | {'Net Gain(B1)':<12} | {'PairAcc':<10}")
    print("-" * 92)
    for r in ordered_results:
        print(f"{r['split']:<10} | {r['base1_unseen_auc']:<12.4f} | {r['base2_unseen_auc']:<12.4f} | {r['ddv_unseen_auc']:<12.4f} | {r['gain1_unseen']:<+12.4f} | {r['ddv_pair_acc']*100:<5.2f}%")
    print("-" * 92)
    print(f"{'MACRO':<10} | {b1_unseen:<12.4f} | {b2_unseen:<12.4f} | {ddv_unseen:<12.4f} | {ddv_unseen - b1_unseen:<+12.4f} | {ddv_pair*100:<5.2f}%")
    print("=" * 92)
    print(f"\n[Bootstrap Analysis (2,000 resamples)]")
    print(f"  DDV Unseen AUROC Mean: {bootstrap_results['ddv_unseen']['mean']:.4f} (95% CI: {bootstrap_results['ddv_unseen']['ci']})")
    print(f"  Gain vs Base 1 Mean  : {bootstrap_results['vs_base1_hq']['unseen_gain_mean']:+.4f} (95% CI: {bootstrap_results['vs_base1_hq']['unseen_gain_ci']})")
    print(f"  Gain vs Base 2 Mean  : {bootstrap_results['vs_base2_release']['unseen_gain_mean']:+.4f} (95% CI: {bootstrap_results['vs_base2_release']['unseen_gain_ci']})")
    print(f"  Seen-Unseen Gap Mean : {bootstrap_results['ddv_gap']['mean']:.4f} (95% CI: {bootstrap_results['ddv_gap']['ci']})")
    print("=" * 92 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Reproduce DDV Benchmark Results")
    parser.add_argument(
        "--mode",
        choices=["eval", "train", "all"],
        default="train",
        help="'eval' for 5-second checkpoint replay; 'train' for multi-GPU training; 'all' for full pipeline",
    )
    parser.add_argument("--epochs", type=int, default=400, help="Training epochs per split (default: 400)")
    parser.add_argument("--lr", type=float, default=3e-3, help="Learning rate (default: 0.003)")
    parser.add_argument("--n_boot", type=int, default=2000, help="Bootstrap iterations (default: 2000)")
    args = parser.parse_args()
    
    n_gpus = check_environment()
    
    if args.mode in ["all", "train"]:
        # 1. Prepare data if not already cached
        need_prep = False
        for sp in SPLITS:
            if not (BASE_DIR / "cache" / sp / "train.npz").exists():
                need_prep = True
                break
        if need_prep or args.mode == "all":
            print("[Step 1/3] Preparing 12-channel feature matrices...")
            prepare_data.main()
        else:
            print("[Step 1/3] 12-channel feature cache already present.")
            
        # 2. Train and evaluate
        print(f"\n[Step 2/3] Running training ({args.epochs} epochs) & benchmark evaluation...")
        train_and_eval.main()
        
        # 3. Generate Markdown report
        print("\n[Step 3/3] Generating research report...")
        generate_report.main()
        
    elif args.mode == "eval":
        evaluate_existing_checkpoints(n_boot=args.n_boot)
        
    print("\nReproduction suite completed successfully!")

if __name__ == "__main__":
    main()
