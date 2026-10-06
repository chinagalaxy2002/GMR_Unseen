#!/usr/bin/env python3
"""
Task 2: Fixed Fusion Prior vs. Trained Model & Directional Ablation Suite.

Evaluates across all 5 splits and specifically analyzes A3:
1. Standalone Detector Baseline
2. Fixed Prior (Untrained Random Initialization)
3. Full Trained Verifier
4. Directional Ablation: Unsigned (|delta| applied on RAW features BEFORE rank transform!)
5. Directional Ablation: No Direction (delta = 0 on RAW features)
6. Modality Ablation: Visual-Only (CLIP)
7. Modality Ablation: Kinetic-Only (SlowFast)

Saves all checkpoints and predictions to runs/ablation/ for full auditability.
"""
from __future__ import annotations
import os
import sys
import json
import time
import random
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

def rank_transform(X_ref, X_apply):
    res = np.zeros_like(X_apply)
    for c in range(X_apply.shape[1]):
        sorted_ref = np.sort(X_ref[:, c])
        res[:, c] = np.searchsorted(sorted_ref, X_apply[:, c]) / len(sorted_ref)
    return res

def train_and_eval_variant(
    split: str,
    target_model: str,
    ablation_mode: str,
    train_model: bool,
    device: torch.device,
    epochs: int = 400,
    seed: int = 3407,
):
    set_seed(seed)
    m_dir = CACHE_DIR / split / target_model
    tr_d = np.load(m_dir / "train.npz")
    val_d = np.load(m_dir / "val.npz")
    te_d = np.load(m_dir / "test.npz")
    
    X_tr, y_tr, pairs_tr = tr_d["X"], tr_d["labels"], tr_d["same_vid_pairs"]
    X_val, y_val = val_d["X"], val_d["labels"]
    X_te, y_te, parts_te, qids_te = te_d["X"], te_d["labels"], te_d["partitions"], te_d["qids"]
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    
    is_s = (parts_te == "S+") | (parts_te == "S-")
    is_u = (parts_te == "U+") | (parts_te == "U-")
    
    # Detector raw test score
    raw_det_te = X_te[:, 0]
    base_s_auc = float(roc_auc_score(y_te[is_s], raw_det_te[is_s]))
    base_u_auc = float(roc_auc_score(y_te[is_u], raw_det_te[is_u]))
    base_pa = compute_matched_pair_acc(qids_te, raw_det_te, pairs_file)
    
    if ablation_mode == "baseline":
        save_dir = RUNS_DIR / "ablation" / target_model / split / "baseline"
        save_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            save_dir / "predictions.npz",
            preds=raw_det_te,
            qids=qids_te,
            labels=y_te,
            partitions=parts_te,
        )
        return {
            "seen": base_s_auc,
            "unseen": base_u_auc,
            "gap": base_s_auc - base_u_auc,
            "pair_acc": base_pa,
            "gain_u": 0.0,
        }
        
    X_tr_in = X_tr.copy()
    X_val_in = X_val.copy()
    X_te_in = X_te.copy()
    
    # Apply ablation on RAW features BEFORE rank transform!
    # Indices 10 and 11 are d_act and d_obj
    if ablation_mode == "unsigned":
        X_tr_in[:, 10] = np.abs(X_tr_in[:, 10])
        X_tr_in[:, 11] = np.abs(X_tr_in[:, 11])
        X_val_in[:, 10] = np.abs(X_val_in[:, 10])
        X_val_in[:, 11] = np.abs(X_val_in[:, 11])
        X_te_in[:, 10] = np.abs(X_te_in[:, 10])
        X_te_in[:, 11] = np.abs(X_te_in[:, 11])
        model_abl_mode = "none"
    elif ablation_mode == "no_direction":
        X_tr_in[:, 10] = 0.0
        X_tr_in[:, 11] = 0.0
        X_val_in[:, 10] = 0.0
        X_val_in[:, 11] = 0.0
        X_te_in[:, 10] = 0.0
        X_te_in[:, 11] = 0.0
        model_abl_mode = "none"
    elif ablation_mode == "visual_only":
        model_abl_mode = "visual_only"
    elif ablation_mode == "kinetic_only":
        model_abl_mode = "kinetic_only"
    else:
        model_abl_mode = "none"
        
    # Rank normalization
    r_tr = rank_transform(X_tr_in, X_tr_in)
    r_val = rank_transform(X_tr_in, X_val_in)
    r_te = rank_transform(X_tr_in, X_te_in)
    
    t_tr = torch.tensor(r_tr, dtype=torch.float32, device=device)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32, device=device)
    t_val = torch.tensor(r_val, dtype=torch.float32, device=device)
    t_te = torch.tensor(r_te, dtype=torch.float32, device=device)
    
    pos_idx = torch.where(y_tr_t == 1)[0]
    neg_idx = torch.where(y_tr_t == 0)[0]
    same_pairs_t = torch.tensor(pairs_tr, dtype=torch.long, device=device)
    
    s_det_tr, mm_tr = t_tr[:, 0], t_tr[:, 1:]
    s_det_val, mm_val = t_val[:, 0], t_val[:, 1:]
    s_det_te, mm_te = t_te[:, 0], t_te[:, 1:]
    
    model = TargetCandidateVerifier(hidden_dim=32, ablation_mode=model_abl_mode).to(device)
    
    save_dir = RUNS_DIR / "ablation" / target_model / split / ablation_mode
    save_dir.mkdir(parents=True, exist_ok=True)
    
    if not train_model:
        model.eval()
        with torch.no_grad():
            preds = model(s_det_te, mm_te).cpu().numpy()
        s_auc = float(roc_auc_score(y_te[is_s], preds[is_s]))
        u_auc = float(roc_auc_score(y_te[is_u], preds[is_u]))
        pa = compute_matched_pair_acc(qids_te, preds, pairs_file)
        
        np.savez_compressed(
            save_dir / "predictions.npz",
            preds=preds,
            qids=qids_te,
            labels=y_te,
            partitions=parts_te,
        )
        return {
            "seen": s_auc,
            "unseen": u_auc,
            "gap": s_auc - u_auc,
            "pair_acc": pa,
            "gain_u": u_auc - base_u_auc,
        }
        
    optimizer = optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    best_val_auc = -1.0
    best_state = None
    half_b = 128
    
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
            
            all_s_det = torch.cat([s_det_tr[p_all], s_det_tr[n_all]])
            all_mm = torch.cat([mm_tr[p_all], mm_tr[n_all]])
            all_y = torch.cat([torch.ones_like(sp), torch.zeros_like(sn)])
            s_calib = model(all_s_det, all_mm)
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
    with torch.no_grad():
        te_scores = model(s_det_te, mm_te).cpu().numpy()
    s_auc = float(roc_auc_score(y_te[is_s], te_scores[is_s]))
    u_auc = float(roc_auc_score(y_te[is_u], te_scores[is_u]))
    pa = compute_matched_pair_acc(qids_te, te_scores, pairs_file)
    
    torch.save(model.state_dict(), save_dir / "verifier.pt")
    np.savez_compressed(
        save_dir / "predictions.npz",
        preds=te_scores,
        qids=qids_te,
        labels=y_te,
        partitions=parts_te,
    )
    
    return {
        "seen": s_auc,
        "unseen": u_auc,
        "gap": s_auc - u_auc,
        "pair_acc": pa,
        "gain_u": u_auc - base_u_auc,
    }

def main():
    print("================================================================================")
    print("      TASK 2: FIXED FUSION, DIRECTIONAL, AND MODALITY ABLATION BENCHMARK        ")
    print("================================================================================")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Running on device: {device}")
    
    variants = [
        ("Baseline (Detector Only)", "baseline", False),
        ("Fixed Prior (Untrained Init)", "none", False),
        ("Full Trained Verifier", "none", True),
        ("Ablation: Unsigned Direction (|delta|)", "unsigned", True),
        ("Ablation: No Direction (delta=0)", "no_direction", True),
        ("Ablation: Visual-Only (CLIP)", "visual_only", True),
        ("Ablation: Kinetic-Only (SlowFast)", "kinetic_only", True),
    ]
    
    results = {}
    
    print("\n>>> Evaluating FlashVTG Ablation Across All 5 Splits...")
    for v_name, abl_mode, train_flag in variants:
        t0 = time.time()
        split_res = []
        for split in SPLITS:
            r = train_and_eval_variant(split, "flash", abl_mode, train_flag, device, epochs=400)
            split_res.append(r)
        macro_u = float(np.mean([r["unseen"] for r in split_res]))
        macro_s = float(np.mean([r["seen"] for r in split_res]))
        macro_pa = float(np.mean([r["pair_acc"] for r in split_res]))
        macro_g = float(np.mean([r["gain_u"] for r in split_res]))
        print(f"  {v_name:40s} | Unseen: {macro_u:.4f} ({macro_g:+.4f}) | Seen: {macro_s:.4f} | PairAcc: {macro_pa:.4f} ({time.time()-t0:.1f}s)", flush=True)
        results[v_name] = {
            "macro_unseen": macro_u,
            "macro_seen": macro_s,
            "macro_pair_acc": macro_pa,
            "macro_gain_u": macro_g,
            "splits": {s: r for s, r in zip(SPLITS, split_res)}
        }
        
    print("\n>>> In-Depth Analysis on A3 Across All 3 Backbones:")
    a3_analysis = {}
    for model in MODELS:
        a3_analysis[model] = {}
        print(f"--- Backbone: {model.upper()} on A3 ---", flush=True)
        for v_name, abl_mode, train_flag in variants:
            r = train_and_eval_variant("A3", model, abl_mode, train_flag, device, epochs=400)
            a3_analysis[model][v_name] = r
            print(f"  {v_name:40s} | Unseen: {r['unseen']:.4f} ({r['gain_u']:+.4f}) | PairAcc: {r['pair_acc']:.4f}", flush=True)
            
    summary_data = {
        "macro_flash_ablation": results,
        "a3_deep_dive": a3_analysis,
    }
    
    with open(REPORTS_DIR / "ablation_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nAblation summary saved to {REPORTS_DIR / 'ablation_summary.json'}.")

if __name__ == "__main__":
    main()
