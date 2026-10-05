#!/usr/bin/env python3
"""
Training and Evaluation Pipeline for Aligned Calibration Verifier (AC-Verifier).

Minimum Experimental Matrix Implementation:
- P0: Independent Detector Adapter Control (answers: is gain from detector adaptation?).
- P1: Aligned Reference-Centered CLIP Verifier (answers: does reference-centered CLIP improve unseen rejection?).
- Diagnostic Controls: Visual Permutation, Text-Only Zeroing, Matched PairAcc.
- Strict Protocol: Trained ONLY on Seen data (S+/S-), val-selected ONLY on Seen validation.
- 2,000-iteration Paired Video Cluster Bootstrap across all 5 splits.
"""
import sys
import os
import json
import random
import time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
FEATURES_DIR = BASE_DIR / "aligned_features"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
AUDIT_DIR = REPO_ROOT / "experiments/agy_test/audit_20261005"
RUNS_DIR = BASE_DIR / "runs"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(AUDIT_DIR))
sys.path.insert(0, str(BASE_DIR))

from audit_results import prepared_auc
from model import DetectorAdapter, AlignedCalibrationVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_matched_pair_acc(qids, scores, pairs_file):
    if not pairs_file.exists():
        return 0.5
    pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
    qid_to_score = dict(zip([str(q) for q in qids], scores))
    accs = []
    for p in pairs:
        pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
        if pq in qid_to_score and nq in qid_to_score:
            sp, sn = qid_to_score[pq], qid_to_score[nq]
            accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    return float(np.mean(accs)) if accs else 0.5

def choose_val_seen_threshold(scores, labels):
    thresholds = np.unique(scores)
    if len(thresholds) > 1000:
        thresholds = np.quantile(scores, np.linspace(0, 1, 1000))
    pos = (labels == 1)
    neg = (labels == 0)
    best_bal, best_th = -1.0, float(thresholds[0])
    for th in thresholds:
        pred = (scores >= th)
        bal = 0.5 * (float(pred[pos].mean()) + float((~pred[neg]).mean()))
        if bal > best_bal:
            best_bal = bal
            best_th = float(th)
    return best_th

def to_tensor_dict(d, device):
    return {
        "orig_logits": torch.tensor(d["orig_logits"], dtype=torch.float32, device=device),
        "fg_max": torch.tensor(d["fg_max"], dtype=torch.float32, device=device),
        "h_pool": torch.tensor(d["h_pool"], dtype=torch.float32, device=device),
        "sim_cand_sent": torch.tensor(d["sim_cand_sent"], dtype=torch.float32, device=device),
        "sim_glob_sent": torch.tensor(d["sim_glob_sent"], dtype=torch.float32, device=device),
        "labels": torch.tensor(d["labels"], dtype=torch.float32, device=device),
    }

def train_and_eval_split(split: str, device: torch.device, epochs=30, lr=1e-3, seed=3407):
    set_seed(seed)
    split_out_dir = RUNS_DIR / split
    split_out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{split}] Loading aligned features...")
    tr_d = np.load(FEATURES_DIR / split / "train.npz")
    val_d = np.load(FEATURES_DIR / split / "val.npz")
    te_d = np.load(FEATURES_DIR / split / "test.npz")
    
    tr_t = to_tensor_dict(tr_d, device)
    val_t = to_tensor_dict(val_d, device)
    te_t = to_tensor_dict(te_d, device)
    
    val_seen_mask = (val_d["partitions"] == "S+") | (val_d["partitions"] == "S-")
    val_seen_labels = val_d["labels"][val_seen_mask]
    
    te_seen_mask = (te_d["partitions"] == "S+") | (te_d["partitions"] == "S-")
    te_unseen_mask = (te_d["partitions"] == "U+") | (te_d["partitions"] == "U-")
    te_labels = te_d["labels"]
    te_qids = te_d["qids"]
    te_vids = te_d["vids"]
    te_parts = te_d["partitions"]
    te_types = te_d["construction_types"]
    
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    
    # 0. Baseline metrics
    base_logits = te_d["orig_logits"]
    base_seen_auc = float(roc_auc_score(te_labels[te_seen_mask], base_logits[te_seen_mask]))
    base_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], base_logits[te_unseen_mask]))
    base_gap = base_seen_auc - base_unseen_auc
    base_pair_acc = compute_matched_pair_acc(te_qids, base_logits, pairs_file)
    
    pos_idx = torch.where(tr_t["labels"] == 1)[0]
    neg_idx = torch.where(tr_t["labels"] == 0)[0]
    pos_weight = torch.tensor([(len(neg_idx)) / len(pos_idx)], device=device)
    bce_loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    
    # 1. Train P0 Control: Detector Adapter
    print(f"[{split}] Training P0 Control (Detector Adapter)...")
    p0_model = DetectorAdapter().to(device)
    p0_opt = optim.AdamW(p0_model.parameters(), lr=lr, weight_decay=1e-4)
    best_p0_val_auc = -1.0
    best_p0_state = None
    
    for epoch in range(1, epochs + 1):
        p0_model.train()
        p0_opt.zero_grad()
        s_det = p0_model(tr_t["orig_logits"], tr_t["fg_max"], tr_t["h_pool"])
        loss = bce_loss_fn(s_det, tr_t["labels"])
        loss.backward()
        p0_opt.step()
        
        p0_model.eval()
        with torch.no_grad():
            v_det = p0_model(val_t["orig_logits"], val_t["fg_max"], val_t["h_pool"])[val_seen_mask].cpu().numpy()
            v_auc = float(roc_auc_score(val_seen_labels, v_det))
            if v_auc > best_p0_val_auc:
                best_p0_val_auc = v_auc
                best_p0_state = {k: v.cpu().clone() for k, v in p0_model.state_dict().items()}
                
    p0_model.load_state_dict(best_p0_state)
    p0_model.eval()
    with torch.no_grad():
        p0_test_logits = p0_model(te_t["orig_logits"], te_t["fg_max"], te_t["h_pool"]).cpu().numpy()
    p0_seen_auc = float(roc_auc_score(te_labels[te_seen_mask], p0_test_logits[te_seen_mask]))
    p0_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], p0_test_logits[te_unseen_mask]))
    p0_pair_acc = compute_matched_pair_acc(te_qids, p0_test_logits, pairs_file)
    
    # 2. Train P1 Verifier: Aligned Calibration Verifier (with Reference Centering)
    print(f"[{split}] Training P1 Verifier (Aligned Calibration Verifier)...")
    model = AlignedCalibrationVerifier().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    best_val_auc = -1.0
    best_epoch = -1
    best_state = None
    
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        out = model(tr_t)
        loss = bce_loss_fn(out["s_exist"], tr_t["labels"])
        loss.backward()
        optimizer.step()
        
        model.eval()
        with torch.no_grad():
            val_out = model(val_t)
            val_scores = val_out["s_exist"][val_seen_mask].cpu().numpy()
            val_auc = float(roc_auc_score(val_seen_labels, val_scores))
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_epoch = epoch
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    model.eval()
    
    # Threshold selection strictly on Seen validation
    with torch.no_grad():
        val_out = model(val_t)
        val_scores = val_out["s_exist"][val_seen_mask].cpu().numpy()
        th = choose_val_seen_threshold(val_scores, val_seen_labels)
        
    # Evaluate P1 on Test
    with torch.no_grad():
        te_out = model(te_t)
        test_logits = te_out["s_exist"].cpu().numpy()
        
    seen_auc = float(roc_auc_score(te_labels[te_seen_mask], test_logits[te_seen_mask]))
    unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], test_logits[te_unseen_mask]))
    gap = seen_auc - unseen_auc
    pair_acc = compute_matched_pair_acc(te_qids, test_logits, pairs_file)
    
    pos_u = (te_parts == "U+")
    neg_u = (te_parts == "U-")
    u_pos_frr = float((test_logits[pos_u] < th).mean() * 100.0)
    u_neg_rr = float((test_logits[neg_u] < th).mean() * 100.0)
    
    # 3. Diagnostic Controls
    # Visual Permutation Control (shuffling video similarities)
    rng_perm = np.random.default_rng(seed)
    perm_idx = rng_perm.permutation(len(te_labels))
    te_t_perm = {k: v.clone() for k, v in te_t.items()}
    te_t_perm["sim_cand_sent"] = te_t["sim_cand_sent"][perm_idx]
    te_t_perm["sim_glob_sent"] = te_t["sim_glob_sent"][perm_idx]
    with torch.no_grad():
        perm_out = model(te_t_perm)
        perm_logits = perm_out["s_exist"].cpu().numpy()
    perm_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], perm_logits[te_unseen_mask]))
    perm_pair_acc = compute_matched_pair_acc(te_qids, perm_logits, pairs_file)
    
    # Text-Only Control (zeroed visual similarities)
    te_t_zero = {k: v.clone() for k, v in te_t.items()}
    te_t_zero["sim_cand_sent"] = torch.zeros_like(te_t["sim_cand_sent"])
    te_t_zero["sim_glob_sent"] = torch.zeros_like(te_t["sim_glob_sent"])
    with torch.no_grad():
        zero_out = model(te_t_zero)
        zero_logits = zero_out["s_exist"].cpu().numpy()
    zero_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], zero_logits[te_unseen_mask]))
    zero_pair_acc = compute_matched_pair_acc(te_qids, zero_logits, pairs_file)
    
    metrics = {
        "split": split,
        "best_epoch": best_epoch,
        "threshold": float(th),
        "Seen_AUROC": seen_auc,
        "Unseen_AUROC": unseen_auc,
        "Gap": gap,
        "Matched_PairAcc": pair_acc,
        "U_pos_FRR": u_pos_frr,
        "U_neg_RR": u_neg_rr,
        "delta_seen": seen_auc - base_seen_auc,
        "delta_unseen": unseen_auc - base_unseen_auc,
        "gap_reduction": base_gap - gap,
        "baseline_fresh": {
            "Seen_AUROC": base_seen_auc,
            "Unseen_AUROC": base_unseen_auc,
            "Gap": base_gap,
            "Matched_PairAcc": base_pair_acc,
        },
        "p0_detector_adapter": {
            "Seen_AUROC": p0_seen_auc,
            "Unseen_AUROC": p0_unseen_auc,
            "Gap": p0_seen_auc - p0_unseen_auc,
            "Matched_PairAcc": p0_pair_acc,
            "delta_unseen": p0_unseen_auc - base_unseen_auc,
        },
        "visual_permutation_control": {
            "Unseen_AUROC": perm_unseen_auc,
            "Matched_PairAcc": perm_pair_acc,
        },
        "text_only_control": {
            "Unseen_AUROC": zero_unseen_auc,
            "Matched_PairAcc": zero_pair_acc,
        }
    }
    
    # Save checkpoint
    torch.save({
        "split": split,
        "best_epoch": best_epoch,
        "threshold": float(th),
        "state_dict": best_state,
        "metrics": metrics,
    }, split_out_dir / "ac_verifier_checkpoint.pt")
    
    with (split_out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"[{split}] Results:")
    print(f"  Baseline:  Seen={base_seen_auc:.4f}, Unseen={base_unseen_auc:.4f}, Gap={base_gap:.4f}, PairAcc={base_pair_acc:.4f}")
    print(f"  P0 DetAdp: Seen={p0_seen_auc:.4f}, Unseen={p0_unseen_auc:.4f}, DeltaU={p0_unseen_auc-base_unseen_auc:+.4f}, PairAcc={p0_pair_acc:.4f}")
    print(f"  P1 AC-Ver: Seen={seen_auc:.4f}, Unseen={unseen_auc:.4f}, DeltaU={unseen_auc-base_unseen_auc:+.4f}, GapRed={base_gap-gap:+.4f}, PairAcc={pair_acc:.4f}")
    print(f"  Controls:  Permuted Unseen={perm_unseen_auc:.4f}, TextOnly Unseen={zero_unseen_auc:.4f}")
    
    return metrics, {
        "y": te_labels,
        "parts": te_parts,
        "vids": te_vids,
        "original": base_logits,
        "p0": p0_test_logits,
        "final": test_logits,
    }

def run_cluster_bootstrap(boot_data, n_repeats=2000, seed=20261005):
    all_vids = sorted(set(np.concatenate([x["vids"] for x in boot_data.values()])))
    vmap = {v: i for i, v in enumerate(all_vids)}
    
    funcs = []
    for d in boot_data.values():
        vi = np.array([vmap[v] for v in d["vids"]])
        group = []
        for parts in [["S+", "S-"], ["U+", "U-"]]:
            mask = np.isin(d["parts"], parts)
            group.append([prepared_auc(d["y"][mask], d[k][mask], vi[mask]) for k in ["original", "final"]])
        funcs.append(group)
        
    rng = np.random.default_rng(seed)
    deltas = np.empty((n_repeats, len(SPLITS), 3))
    for b in range(n_repeats):
        counts = np.bincount(rng.integers(len(all_vids), size=len(all_vids)), minlength=len(all_vids)).astype(float)
        for i, group in enumerate(funcs):
            ds, du = [f[1](counts) - f[0](counts) for f in group]
            deltas[b, i] = [ds, du, du - ds]
            
    names = ["delta_seen", "delta_unseen", "gap_reduction"]
    ci = lambda arr: {names[j]: [float(np.nanquantile(arr[:, j], 0.025)), float(np.nanquantile(arr[:, j], 0.975))] for j in range(3)}
    
    per_split = {s: ci(deltas[:, i]) for i, s in enumerate(SPLITS)}
    macro = ci(np.nanmean(deltas, axis=1))
    return {
        "repeats": n_repeats,
        "seed": seed,
        "video_clusters": len(all_vids),
        "per_split": per_split,
        "macro": macro,
    }

def main():
    print("=" * 80)
    print("Aligned Calibration Verifier (AC-Verifier) Benchmarking Across 5 Splits")
    print("Strict Seen-Only Training & Threshold Selection | P0 vs P1 Evaluation")
    print("=" * 80)
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Execution device:", device)
    
    split_metrics = {}
    boot_data = {}
    
    for split in SPLITS:
        m, bd = train_and_eval_split(split, device=device, epochs=30, lr=1e-3, seed=3407)
        split_metrics[split] = m
        boot_data[split] = bd
        
    print("\nRunning 2,000-iteration Paired Video Cluster Bootstrap...")
    bootstrap_results = run_cluster_bootstrap(boot_data, n_repeats=2000, seed=20261005)
    
    macro_summary = {
        "Seen_AUROC": float(np.mean([m["Seen_AUROC"] for m in split_metrics.values()])),
        "Unseen_AUROC": float(np.mean([m["Unseen_AUROC"] for m in split_metrics.values()])),
        "Gap": float(np.mean([m["Gap"] for m in split_metrics.values()])),
        "Matched_PairAcc": float(np.mean([m["Matched_PairAcc"] for m in split_metrics.values()])),
        "U_pos_FRR": float(np.mean([m["U_pos_FRR"] for m in split_metrics.values()])),
        "U_neg_RR": float(np.mean([m["U_neg_RR"] for m in split_metrics.values()])),
        "delta_seen": float(np.mean([m["delta_seen"] for m in split_metrics.values()])),
        "delta_unseen": float(np.mean([m["delta_unseen"] for m in split_metrics.values()])),
        "gap_reduction": float(np.mean([m["gap_reduction"] for m in split_metrics.values()])),
        "baseline_macro_fresh": {
            "Seen_AUROC": float(np.mean([m["baseline_fresh"]["Seen_AUROC"] for m in split_metrics.values()])),
            "Unseen_AUROC": float(np.mean([m["baseline_fresh"]["Unseen_AUROC"] for m in split_metrics.values()])),
            "Gap": float(np.mean([m["baseline_fresh"]["Gap"] for m in split_metrics.values()])),
            "Matched_PairAcc": float(np.mean([m["baseline_fresh"]["Matched_PairAcc"] for m in split_metrics.values()])),
        },
        "p0_detector_adapter_macro": {
            "Seen_AUROC": float(np.mean([m["p0_detector_adapter"]["Seen_AUROC"] for m in split_metrics.values()])),
            "Unseen_AUROC": float(np.mean([m["p0_detector_adapter"]["Unseen_AUROC"] for m in split_metrics.values()])),
            "Gap": float(np.mean([m["p0_detector_adapter"]["Gap"] for m in split_metrics.values()])),
            "Matched_PairAcc": float(np.mean([m["p0_detector_adapter"]["Matched_PairAcc"] for m in split_metrics.values()])),
            "delta_unseen": float(np.mean([m["p0_detector_adapter"]["delta_unseen"] for m in split_metrics.values()])),
        },
        "visual_permutation_control": {
            "Unseen_AUROC": float(np.mean([m["visual_permutation_control"]["Unseen_AUROC"] for m in split_metrics.values()])),
            "Matched_PairAcc": float(np.mean([m["visual_permutation_control"]["Matched_PairAcc"] for m in split_metrics.values()])),
        },
        "text_only_control": {
            "Unseen_AUROC": float(np.mean([m["text_only_control"]["Unseen_AUROC"] for m in split_metrics.values()])),
            "Matched_PairAcc": float(np.mean([m["text_only_control"]["Matched_PairAcc"] for m in split_metrics.values()])),
        }
    }
    
    benchmark_summary = {
        "model_name": "Aligned_Calibration_Verifier",
        "macro_summary": macro_summary,
        "bootstrap_95ci": bootstrap_results["macro"],
        "splits": split_metrics,
        "per_split_bootstrap": bootstrap_results["per_split"],
    }
    
    summary_file = BASE_DIR / "benchmark_summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)
        
    print("\n" + "=" * 90)
    print("5-SPLIT BENCHMARK SUMMARY (Baseline vs P0 Control vs P1 AC-Verifier):")
    print("=" * 90)
    print(f"Baseline Fresh: Seen={macro_summary['baseline_macro_fresh']['Seen_AUROC']:.4f}, Unseen={macro_summary['baseline_macro_fresh']['Unseen_AUROC']:.4f}, Gap={macro_summary['baseline_macro_fresh']['Gap']:.4f}, PairAcc={macro_summary['baseline_macro_fresh']['Matched_PairAcc']:.4f}")
    print(f"P0 Det Adapter: Seen={macro_summary['p0_detector_adapter_macro']['Seen_AUROC']:.4f}, Unseen={macro_summary['p0_detector_adapter_macro']['Unseen_AUROC']:.4f}, DeltaU={macro_summary['p0_detector_adapter_macro']['delta_unseen']:+.4f}, Gap={macro_summary['p0_detector_adapter_macro']['Gap']:.4f}, PairAcc={macro_summary['p0_detector_adapter_macro']['Matched_PairAcc']:.4f}")
    print(f"P1 AC-Verifier: Seen={macro_summary['Seen_AUROC']:.4f} ({macro_summary['delta_seen']:+.4f}), Unseen={macro_summary['Unseen_AUROC']:.4f} ({macro_summary['delta_unseen']:+.4f}), Gap={macro_summary['Gap']:.4f} (Reduct={macro_summary['gap_reduction']:+.4f}), PairAcc={macro_summary['Matched_PairAcc']:.4f}")
    print(f"Bootstrap 95% CI: Delta Unseen = {bootstrap_results['macro']['delta_unseen']}, Gap Reduct = {bootstrap_results['macro']['gap_reduction']}")
    print(f"Controls:       Permuted Unseen={macro_summary['visual_permutation_control']['Unseen_AUROC']:.4f}, TextOnly Unseen={macro_summary['text_only_control']['Unseen_AUROC']:.4f}")
    print(f"\nResults saved to {summary_file}")

if __name__ == "__main__":
    main()
