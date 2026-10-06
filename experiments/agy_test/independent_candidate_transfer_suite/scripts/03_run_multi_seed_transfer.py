#!/usr/bin/env python3
"""
Task 3: Multi-Seed (3 Seeds) Cross-Backbone Transfer & Operational Rejection Benchmark.

Executes:
1. Multi-seed training (Seeds: 3407, 42, 2024) across 5 splits.
2. Parallelized across GPU 0 (A1, A2_alt, A3) and GPU 1 (C1, C2_alt).
3. Evaluates full 3x3 transfer matrix under TWO regimes:
   - Regime A: Target-Specific Candidates (End-to-End Grounding Transfer)
   - Regime B: Shared Candidates (Interface Score Transfer)
4. Evaluates operational rejection metrics:
   - Optimal threshold tau calibrated on Seen validation (Youden's J index)
   - Unseen Correct Rejection Rate (RR)
   - Seen False Rejection Rate (FRR)
   - Unseen Counterfactual Rejection F1 score (positive class is rejection of negative counterfactuals)
5. SAVES ALL CHECKPOINTS AND QUERY-LEVEL PREDICTIONS to runs/ for full replay auditability.
"""
from __future__ import annotations
import os
import sys
import json
import time
import random
import multiprocessing as mp
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[4]
BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "cache"
RUNS_DIR = BASE_DIR / "runs"
REPORTS_DIR = BASE_DIR / "reports"
RUNS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"

sys.path.insert(0, str(BASE_DIR))
from models.verifier_models import TargetCandidateVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
MODELS = ["flash", "moment", "qd"]
SEEDS = [3407, 42, 2024]

def set_seed(seed: int):
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

def rank_transform(X_ref, X_apply):
    res = np.zeros_like(X_apply)
    for c in range(X_apply.shape[1]):
        sorted_ref = np.sort(X_ref[:, c])
        res[:, c] = np.searchsorted(sorted_ref, X_apply[:, c]) / len(sorted_ref)
    return res

def compute_operational_rejection_metrics(y_val, val_scores, y_te, te_scores, parts_te):
    # Calibrate tau on Seen validation: maximize Youden's J index (TPR - FPR)
    thresholds = np.linspace(0.01, 0.99, 100)
    best_j = -1.0
    best_tau = 0.5
    for th in thresholds:
        pred_pos = (val_scores >= th).astype(int)
        tp = np.sum((pred_pos == 1) & (y_val == 1))
        fn = np.sum((pred_pos == 0) & (y_val == 1))
        tn = np.sum((pred_pos == 0) & (y_val == 0))
        fp = np.sum((pred_pos == 1) & (y_val == 0))
        tpr = tp / max(1, tp + fn)
        fpr = fp / max(1, fp + tn)
        j = tpr - fpr
        if j > best_j:
            best_j = j
            best_tau = float(th)
            
    is_s = (parts_te == "S+") | (parts_te == "S-")
    is_u = (parts_te == "U+") | (parts_te == "U-")
    
    # Seen False Rejection Rate (FRR: S+ rejected when score < tau)
    is_s_pos = (parts_te == "S+")
    s_frr = float(np.mean(te_scores[is_s_pos] < best_tau)) if np.sum(is_s_pos) > 0 else 0.0
    
    # Unseen Correct Rejection Rate (RR: U- rejected when score < tau)
    is_u_neg = (parts_te == "U-")
    u_rr = float(np.mean(te_scores[is_u_neg] < best_tau)) if np.sum(is_u_neg) > 0 else 0.0
    
    # Unseen False Rejection Rate (FRR: U+ rejected when score < tau)
    is_u_pos = (parts_te == "U+")
    u_frr = float(np.mean(te_scores[is_u_pos] < best_tau)) if np.sum(is_u_pos) > 0 else 0.0
    
    # F1 score for REJECTING NEGATIVE COUNTERFACTUALS:
    # Target task is detecting/rejecting negative queries (true negative counterfactual = U-, y == 0).
    # Prediction of rejection is (score < tau).
    pred_rej = (te_scores[is_u] < best_tau).astype(int)
    true_neg = (y_te[is_u] == 0).astype(int)
    
    tp_rej = int(np.sum((pred_rej == 1) & (true_neg == 1)))
    fp_rej = int(np.sum((pred_rej == 1) & (true_neg == 0)))
    fn_rej = int(np.sum((pred_rej == 0) & (true_neg == 1)))
    
    prec_rej = tp_rej / max(1, tp_rej + fp_rej)
    rec_rej = tp_rej / max(1, tp_rej + fn_rej) # equal to u_rr
    f1_rej = float(2 * prec_rej * rec_rej / max(1e-8, prec_rej + rec_rej))
    
    return {
        "calibrated_tau": best_tau,
        "seen_frr": s_frr,
        "unseen_rr": u_rr,
        "unseen_frr": u_frr,
        "rejection_f1": f1_rej,
    }

def train_single_source_verifier(
    t_tr: torch.Tensor,
    y_tr_t: torch.Tensor,
    same_pairs_t: torch.Tensor,
    pos_idx: torch.Tensor,
    neg_idx: torch.Tensor,
    t_val: torch.Tensor,
    y_val: np.ndarray,
    device: torch.device,
    epochs: int = 400,
):
    model = TargetCandidateVerifier(hidden_dim=32).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    half_b = 128
    best_val_auc = -1.0
    best_state = None
    
    s_det_tr, mm_tr = t_tr[:, 0], t_tr[:, 1:]
    s_det_val, mm_val = t_val[:, 0], t_val[:, 1:]
    
    for ep in range(1, epochs + 1):
        model.train()
        for _ in range(10):
            optimizer.zero_grad()
            intra_idx = torch.randint(len(same_pairs_t), (half_b,), device=device)
            p_intra, n_intra = same_pairs_t[intra_idx, 0], same_pairs_t[intra_idx, 1]
            p_inter = pos_idx[torch.randint(len(pos_idx), (half_b,), device=device)]
            n_inter = neg_idx[torch.randint(len(neg_idx), (half_b,), device=device)]
            p_all = torch.cat([p_intra, p_inter])
            n_all = torch.cat([n_intra, n_inter])
            
            sp = model(s_det_tr[p_all], mm_tr[p_all])
            sn = model(s_det_tr[n_all], mm_tr[n_all])
            loss_rank = F.softplus(-(sp - sn) / 0.15).mean()
            
            all_s = torch.cat([s_det_tr[p_all], s_det_tr[n_all]])
            all_mm = torch.cat([mm_tr[p_all], mm_tr[n_all]])
            all_y = torch.cat([torch.ones_like(sp), torch.zeros_like(sn)])
            s_calib = model(all_s, all_mm)
            loss_bce = F.binary_cross_entropy(torch.clamp(s_calib, 1e-6, 1.0 - 1e-6), all_y)
            
            (loss_rank + 0.4 * loss_bce).backward()
            optimizer.step()
        scheduler.step()
        
        model.eval()
        with torch.no_grad():
            v_scores = model(s_det_val, mm_val).cpu().numpy()
            v_auc = float(roc_auc_score(y_val, v_scores))
            if v_auc > best_val_auc:
                best_val_auc = v_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    model.eval()
    return model, best_val_auc

def process_split_seed(split: str, seed: int, gpu_id: int, regime: str = "target_specific"):
    set_seed(seed)
    device = torch.device(f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu")
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    
    split_run_dir = RUNS_DIR / regime / f"seed_{seed}" / split
    split_run_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load data for all models
    split_data = {}
    for m in MODELS:
        m_dir = CACHE_DIR / split / m
        tr_d = np.load(m_dir / "train.npz")
        val_d = np.load(m_dir / "val.npz")
        te_d = np.load(m_dir / "test.npz")
        
        X_tr, y_tr, pairs_tr = tr_d["X"], tr_d["labels"], tr_d["same_vid_pairs"]
        X_val, y_val = val_d["X"], val_d["labels"]
        X_te, y_te, parts_te, qids_te, vids_te = te_d["X"], te_d["labels"], te_d["partitions"], te_d["qids"], te_d["vids"]
        
        r_tr = rank_transform(X_tr, X_tr)
        r_val = rank_transform(X_tr, X_val)
        r_te = rank_transform(X_tr, X_te)
        
        split_data[m] = {
            "t_tr": torch.tensor(r_tr, dtype=torch.float32, device=device),
            "y_tr_t": torch.tensor(y_tr, dtype=torch.float32, device=device),
            "same_pairs_t": torch.tensor(pairs_tr, dtype=torch.long, device=device),
            "pos_idx": torch.where(torch.tensor(y_tr, device=device) == 1)[0],
            "neg_idx": torch.where(torch.tensor(y_tr, device=device) == 0)[0],
            "t_val": torch.tensor(r_val, dtype=torch.float32, device=device),
            "y_val": y_val,
            "t_te": torch.tensor(r_te, dtype=torch.float32, device=device),
            "y_te": y_te,
            "parts_te": parts_te,
            "qids_te": qids_te,
            "vids_te": vids_te,
            "raw_base_te": X_te[:, 0],
        }
        
    standalones = {}
    for m in MODELS:
        d = split_data[m]
        sc = d["raw_base_te"]
        y_te = d["y_te"]
        parts_te = d["parts_te"]
        is_s = (parts_te == "S+") | (parts_te == "S-")
        is_u = (parts_te == "U+") | (parts_te == "U-")
        s_auc = float(roc_auc_score(y_te[is_s], sc[is_s]))
        u_auc = float(roc_auc_score(y_te[is_u], sc[is_u]))
        pa = compute_matched_pair_acc(d["qids_te"], sc, pairs_file)
        standalones[m] = {"seen": s_auc, "unseen": u_auc, "gap": s_auc - u_auc, "pair_acc": pa}
        
    # 2. Train 3 Source Verifiers
    source_models = {}
    for src in MODELS:
        d = split_data[src]
        m, val_auc = train_single_source_verifier(
            d["t_tr"], d["y_tr_t"], d["same_pairs_t"], d["pos_idx"], d["neg_idx"],
            d["t_val"], d["y_val"], device, epochs=400
        )
        source_models[src] = m
        # Save trained checkpoint!
        torch.save(m.state_dict(), split_run_dir / f"verifier_src_{src}.pt")
        
    # 3. Evaluate 3x3 Transfer Matrix
    transfer_results = {}
    predictions = {}
    operational_results = {}
    
    for src in MODELS:
        transfer_results[src] = {}
        predictions[src] = {}
        operational_results[src] = {}
        m = source_models[src]
        
        for tgt in MODELS:
            d_tgt = split_data[tgt]
            s_det_te = d_tgt["t_te"][:, 0]
            
            if regime == "target_specific":
                mm_te = d_tgt["t_te"][:, 1:]
                s_det_val = d_tgt["t_val"][:, 0]
                mm_val = d_tgt["t_val"][:, 1:]
            else: # shared candidates from flash
                mm_te = split_data["flash"]["t_te"][:, 1:]
                s_det_val = d_tgt["t_val"][:, 0]
                mm_val = split_data["flash"]["t_val"][:, 1:]
                
            with torch.no_grad():
                te_pred = m(s_det_te, mm_te).cpu().numpy()
                val_pred = m(s_det_val, mm_val).cpu().numpy()
                
            y_te = d_tgt["y_te"]
            parts_te = d_tgt["parts_te"]
            is_s = (parts_te == "S+") | (parts_te == "S-")
            is_u = (parts_te == "U+") | (parts_te == "U-")
            
            s_auc = float(roc_auc_score(y_te[is_s], te_pred[is_s]))
            u_auc = float(roc_auc_score(y_te[is_u], te_pred[is_u]))
            pa = compute_matched_pair_acc(d_tgt["qids_te"], te_pred, pairs_file)
            gain = u_auc - standalones[tgt]["unseen"]
            
            op_metrics = compute_operational_rejection_metrics(
                d_tgt["y_val"], val_pred, y_te, te_pred, parts_te
            )
            
            transfer_results[src][tgt] = {
                "seen": s_auc,
                "unseen": u_auc,
                "gap": s_auc - u_auc,
                "pair_acc": pa,
                "gain_vs_target_base": gain,
            }
            predictions[src][tgt] = te_pred
            operational_results[src][tgt] = op_metrics
            
    # Save predictions file for auditability!
    pred_dict = {
        "qids": split_data["flash"]["qids_te"],
        "vids": split_data["flash"]["vids_te"],
        "labels": split_data["flash"]["y_te"],
        "partitions": split_data["flash"]["parts_te"],
    }
    for src in MODELS:
        for tgt in MODELS:
            pred_dict[f"pred_{src}_to_{tgt}"] = predictions[src][tgt]
    np.savez_compressed(split_run_dir / "transfer_predictions.npz", **pred_dict)
    
    return {
        "split": split,
        "seed": seed,
        "regime": regime,
        "standalones": standalones,
        "transfer_results": transfer_results,
        "operational_results": operational_results,
        "predictions": predictions,
        "labels": split_data["flash"]["y_te"],
        "partitions": split_data["flash"]["parts_te"],
        "vids": split_data["flash"]["vids_te"],
    }

def _process_split_worker(sp, sd, gid, reg, r_dict):
    r_dict[sp] = process_split_seed(sp, sd, gid, regime=reg)

def run_suite():
    print("================================================================================")
    print("      TASK 3: 3-SEED CROSS-BACKBONE TRANSFER & OPERATIONAL REJECTION BENCHMARK  ")
    print("================================================================================")
    t_start = time.time()
    
    regimes = ["target_specific", "shared"]
    suite_summary = {}
    
    for regime in regimes:
        print(f"\n{'='*70}\n>>> STARTING BENCHMARK REGIME: {regime.upper()}\n{'='*70}", flush=True)
        regime_results = {seed: [] for seed in SEEDS}
        
        for seed in SEEDS:
            print(f"\n--- Running Seed: {seed} ({regime}) ---", flush=True)
            manager = mp.Manager()
            return_dict = manager.dict()
            processes = []
            for split in SPLITS:
                gpu_id = 0 if split in ["A1", "A2_alt", "A3"] else 1
                p = mp.Process(target=_process_split_worker, args=(split, seed, gpu_id, regime, return_dict))
                processes.append(p)
                p.start()
            for p in processes:
                p.join()
            ordered_runs = [return_dict[sp] for sp in SPLITS]
            regime_results[seed] = ordered_runs
            for res in ordered_runs:
                sp = res["split"]
                tm = res["transfer_results"]
                print(f"[{sp}/seed{seed}] Diagonals: Flash={tm['flash']['flash']['unseen']:.4f}, Moment={tm['moment']['moment']['unseen']:.4f}, QD={tm['qd']['qd']['unseen']:.4f}", flush=True)
                
        # Aggregate Macro across seeds
        macro_seeds = []
        for seed in SEEDS:
            runs = regime_results[seed]
            macro_tm = {src: {tgt: {} for tgt in MODELS} for src in MODELS}
            macro_op = {src: {tgt: {} for tgt in MODELS} for src in MODELS}
            macro_base = {m: float(np.mean([r["standalones"][m]["unseen"] for r in runs])) for m in MODELS}
            
            for src in MODELS:
                for tgt in MODELS:
                    u_list = [r["transfer_results"][src][tgt]["unseen"] for r in runs]
                    g_list = [r["transfer_results"][src][tgt]["gain_vs_target_base"] for r in runs]
                    pa_list = [r["transfer_results"][src][tgt]["pair_acc"] for r in runs]
                    rr_list = [r["operational_results"][src][tgt]["unseen_rr"] for r in runs]
                    frr_list = [r["operational_results"][src][tgt]["seen_frr"] for r in runs]
                    u_frr_list = [r["operational_results"][src][tgt]["unseen_frr"] for r in runs]
                    f1_list = [r["operational_results"][src][tgt]["rejection_f1"] for r in runs]
                    
                    macro_tm[src][tgt] = {
                        "unseen": float(np.mean(u_list)),
                        "gain": float(np.mean(g_list)),
                        "pair_acc": float(np.mean(pa_list)),
                    }
                    macro_op[src][tgt] = {
                        "rr": float(np.mean(rr_list)),
                        "frr": float(np.mean(frr_list)),
                        "unseen_frr": float(np.mean(u_frr_list)),
                        "rejection_f1": float(np.mean(f1_list)),
                    }
            macro_seeds.append({
                "seed": seed,
                "macro_base": macro_base,
                "macro_tm": macro_tm,
                "macro_op": macro_op,
            })
            
        suite_summary[regime] = {
            "macro_seeds": macro_seeds,
            "raw_runs": [{
                "seed": r["seed"],
                "split": r["split"],
                "standalones": r["standalones"],
                "transfer_results": r["transfer_results"],
                "operational_results": r["operational_results"],
            } for s in SEEDS for r in regime_results[s]]
        }
        
    with open(REPORTS_DIR / "multi_seed_transfer_summary.json", "w") as f:
        json.dump(suite_summary, f, indent=2)
    print(f"\nSuite complete in {time.time()-t_start:.2f}s! Summary saved to {REPORTS_DIR / 'multi_seed_transfer_summary.json'}.")

if __name__ == "__main__":
    run_suite()
