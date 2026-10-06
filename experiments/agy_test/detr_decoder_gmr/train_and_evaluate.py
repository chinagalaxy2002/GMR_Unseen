#!/usr/bin/env python3
"""
DEC-GMR: Decoder-Evidential Conjunctive Verification Training & Evaluation Pipeline.

Evaluates standalone DETR-based models (Moment-DETR and FlashVTG) under the
Adaptive Conjunctive Gating algorithm to systematically solve the Unseen generalization drop.

Features:
1. Multi-GPU parallel training (GPU 0: A1, A2_alt, A3; GPU 1: C1, C2_alt).
2. 400 Epochs per model with Cosine Annealing.
3. Strictly zero label leakage (Seen-only validation model selection).
4. 2,000-iteration Paired Video Cluster Bootstrap for 95% Confidence Intervals.
5. Saves predictions and benchmark_summary.json.
"""
from __future__ import annotations
import sys
import os
import json
import random
import time
import multiprocessing as mp
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
RUNS_DIR = BASE_DIR / "runs"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"

sys.path.insert(0, str(BASE_DIR))
from model import ConjunctiveDecoderVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
MODELS = ["moment", "flash"] # Primary DETR and reference FlashVTG

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

def train_model(
    name: str,
    s_det_tr: torch.Tensor,
    mm_tr: torch.Tensor,
    y_tr_t: torch.Tensor,
    same_pairs_t: torch.Tensor,
    pos_idx: torch.Tensor,
    neg_idx: torch.Tensor,
    s_det_val: torch.Tensor,
    mm_val: torch.Tensor,
    y_val: np.ndarray,
    device: torch.device,
    epochs: int = 400,
    lr: float = 3e-3,
):
    model = ConjunctiveDecoderVerifier(hidden_dim=32).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    half_b = 128
    steps_per_epoch = 10
    best_val_auc = -1.0
    best_state = None
    
    for ep in range(1, epochs + 1):
        model.train()
        for step in range(steps_per_epoch):
            optimizer.zero_grad()
            
            # Intra-video counterfactual pairs (hard negatives)
            intra_idx = torch.randint(len(same_pairs_t), (half_b,), device=device)
            p_intra = same_pairs_t[intra_idx, 0]
            n_intra = same_pairs_t[intra_idx, 1]
            
            # Inter-video random pairs
            p_inter = pos_idx[torch.randint(len(pos_idx), (half_b,), device=device)]
            n_inter = neg_idx[torch.randint(len(neg_idx), (half_b,), device=device)]
            
            p_all = torch.cat([p_intra, p_inter])
            n_all = torch.cat([n_intra, n_inter])
            
            sp, sp_ev, b_det_p, b_ev_p = model(s_det_tr[p_all], mm_tr[p_all])
            sn, sn_ev, b_det_n, b_ev_n = model(s_det_tr[n_all], mm_tr[n_all])
            
            # 1. Soft Margin Ranking Loss
            loss_rank = F.softplus(-(sp - sn) / 0.15).mean()
            
            # 2. Evidential Grounding Ranking Loss
            loss_ev = F.softplus(-(sp_ev - sn_ev) / 0.15).mean()
            
            # 3. Calibration BCE Loss
            all_s_det = torch.cat([s_det_tr[p_all], s_det_tr[n_all]])
            all_mm = torch.cat([mm_tr[p_all], mm_tr[n_all]])
            all_y = torch.cat([torch.ones_like(sp), torch.zeros_like(sn)])
            s_all, _, _, _ = model(all_s_det, all_mm)
            loss_bce = F.binary_cross_entropy(torch.clamp(s_all, 1e-6, 1.0 - 1e-6), all_y)
            
            loss = loss_rank + 0.5 * loss_ev + 0.3 * loss_bce
            loss.backward()
            optimizer.step()
            
        scheduler.step()
        
        # Validate strictly on Seen validation
        model.eval()
        with torch.no_grad():
            v_scores, _, _, _ = model(s_det_val, mm_val)
            v_auc = float(roc_auc_score(y_val, v_scores.cpu().numpy()))
            if v_auc > best_val_auc:
                best_val_auc = v_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    model.eval()
    return model, best_val_auc

def process_split_worker(
    split: str,
    gpu_id: int,
    seed: int = 3407,
    epochs: int = 400,
    return_dict: dict | None = None,
):
    set_seed(seed)
    device = torch.device(f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu")
    split_dir = RUNS_DIR / split
    split_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[{split}] >>> Starting DEC-GMR Training on {device} (epochs={epochs})...", flush=True)
    t0 = time.time()
    
    # 1. Load Data
    feat_dir = CACHE_DIR / split
    tr_d = np.load(feat_dir / "train.npz")
    val_d = np.load(feat_dir / "val.npz")
    te_d = np.load(feat_dir / "test.npz")
    
    X_tr, y_tr, pairs_tr = tr_d["X"], tr_d["labels"], tr_d["same_vid_pairs"]
    X_val, y_val = val_d["X"], val_d["labels"]
    X_te, y_te, parts_te = te_d["X"], te_d["labels"], te_d["partitions"]
    qids_te, vids_te = te_d["qids"], te_d["vids"]
    
    is_s_te = (parts_te == "S+") | (parts_te == "S-")
    is_u_te = (parts_te == "U+") | (parts_te == "U-")
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    
    # Rank Transform
    r_tr = rank_transform(X_tr, X_tr)
    r_val = rank_transform(X_tr, X_val)
    r_te = rank_transform(X_tr, X_te)
    
    t_tr = torch.tensor(r_tr, dtype=torch.float32, device=device)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32, device=device)
    t_val = torch.tensor(r_val, dtype=torch.float32, device=device)
    t_te = torch.tensor(r_te, dtype=torch.float32, device=device)
    
    pos_idx = torch.where(y_tr_t == 1)[0]
    neg_idx = torch.where(y_tr_t == 0)[0]
    same_pairs_t = torch.tensor(pairs_tr, dtype=torch.long, device=device)
    
    # Standalone Baselines: Moment (col 1), Flash (col 0)
    col_map = {"moment": 1, "flash": 0}
    split_results = {}
    
    for bb in MODELS:
        c_idx = col_map[bb]
        s_tr_det = t_tr[:, c_idx]
        mm_tr = t_tr[:, 3:]
        
        s_val_det = t_val[:, c_idx]
        mm_val = t_val[:, 3:]
        
        s_te_det = t_te[:, c_idx]
        mm_te = t_te[:, 3:]
        
        # Standalone Baseline on Test:
        base_scores = r_te[:, c_idx]
        base_s_auc = float(roc_auc_score(y_te[is_s_te], base_scores[is_s_te]))
        base_u_auc = float(roc_auc_score(y_te[is_u_te], base_scores[is_u_te]))
        base_pa = compute_matched_pair_acc(qids_te, base_scores, pairs_file)
        
        # Train DEC-GMR Verifier:
        m, val_auc = train_model(
            f"{bb}_{split}", s_tr_det, mm_tr, y_tr_t, same_pairs_t, pos_idx, neg_idx,
            s_val_det, mm_val, y_val, device, epochs=epochs
        )
        
        # Test DEC-GMR:
        with torch.no_grad():
            dec_scores, s_ev, b_det, b_ev = m(s_te_det, mm_te)
            dec_scores = dec_scores.cpu().numpy()
            
        dec_s_auc = float(roc_auc_score(y_te[is_s_te], dec_scores[is_s_te]))
        dec_u_auc = float(roc_auc_score(y_te[is_u_te], dec_scores[is_u_te]))
        dec_pa = compute_matched_pair_acc(qids_te, dec_scores, pairs_file)
        
        torch.save(m.state_dict(), split_dir / f"dec_gmr_{bb}.pt")
        
        split_results[bb] = {
            "baseline": {
                "seen": base_s_auc,
                "unseen": base_u_auc,
                "gap": base_s_auc - base_u_auc,
                "pair_acc": base_pa,
            },
            "dec_gmr": {
                "seen": dec_s_auc,
                "unseen": dec_u_auc,
                "gap": dec_s_auc - dec_u_auc,
                "pair_acc": dec_pa,
                "val_auc": val_auc,
                "gain_unseen": dec_u_auc - base_u_auc,
                "gap_reduction": (base_s_auc - base_u_auc) - (dec_s_auc - dec_u_auc),
            },
            "predictions": dec_scores,
        }
        
        print(f"[{split} | {bb.upper()}] Base Unseen={base_u_auc:.4f} -> DEC-GMR Unseen={dec_u_auc:.4f} (Gain={dec_u_auc - base_u_auc:+.4f}, PairAcc={dec_pa:.4f})", flush=True)

    # Save predictions
    save_dict = {
        "qids": qids_te,
        "vids": vids_te,
        "partitions": parts_te,
        "labels": y_te,
    }
    for bb in MODELS:
        save_dict[f"pred_base_{bb}"] = r_te[:, col_map[bb]]
        save_dict[f"pred_dec_{bb}"] = split_results[bb]["predictions"]
    np.savez_compressed(split_dir / "predictions.npz", **save_dict)
    
    elapsed = time.time() - t0
    print(f"[{split}] Completed in {elapsed:.2f}s.", flush=True)
    
    res = {
        "split": split,
        "results": {bb: {k: v for k, v in split_results[bb].items() if k != "predictions"} for bb in MODELS},
        "qids": list(qids_te),
        "vids": list(vids_te),
        "partitions": parts_te,
        "labels": y_te,
        "pred_dec_moment": split_results["moment"]["predictions"],
        "pred_dec_flash": split_results["flash"]["predictions"],
        "pred_base_moment": r_te[:, col_map["moment"]],
        "pred_base_flash": r_te[:, col_map["flash"]],
    }
    if return_dict is not None:
        return_dict[split] = res
    return res

def run_paired_video_cluster_bootstrap(split_results, n_boot=2000, seed=3407):
    print(f"\n==================== RUNNING {n_boot}-ITERATION PAIRED VIDEO CLUSTER BOOTSTRAP ====================")
    set_seed(seed)
    shared_vids = sorted(list(set.union(*[set(r["vids"]) for r in split_results])))
    n_vids = len(shared_vids)
    
    vid_to_idx_per_split = []
    for r in split_results:
        v_map = {}
        for i, v in enumerate(r["vids"]):
            v_map.setdefault(v, []).append(i)
        vid_to_idx_per_split.append(v_map)
        
    boot_summary = {}
    for bb in MODELS:
        boot_u_dec = []
        boot_u_base = []
        boot_gain = []
        
        for b in range(n_boot):
            sample_vids = np.random.choice(shared_vids, size=n_vids, replace=True)
            split_dec = []
            split_base = []
            valid = True
            
            for s_idx, r in enumerate(split_results):
                v_map = vid_to_idx_per_split[s_idx]
                sub_indices = []
                for v in sample_vids:
                    if v in v_map:
                        sub_indices.extend(v_map[v])
                if not sub_indices:
                    valid = False
                    break
                    
                y_b = r["labels"][sub_indices]
                parts_b = r["partitions"][sub_indices]
                u_mask = (parts_b == "U+") | (parts_b == "U-")
                if len(np.unique(y_b[u_mask])) < 2:
                    valid = False
                    break
                    
                s_dec = r[f"pred_dec_{bb}"][sub_indices]
                s_base = r[f"pred_base_{bb}"][sub_indices]
                
                split_dec.append(roc_auc_score(y_b[u_mask], s_dec[u_mask]))
                split_base.append(roc_auc_score(y_b[u_mask], s_base[u_mask]))
                
            if not valid:
                continue
                
            m_dec = float(np.mean(split_dec))
            m_base = float(np.mean(split_base))
            boot_u_dec.append(m_dec)
            boot_u_base.append(m_base)
            boot_gain.append(m_dec - m_base)
            
        def ci_fmt(arr):
            lo, hi = np.percentile(arr, 2.5), np.percentile(arr, 97.5)
            sign = "+" if lo >= 0 else ""
            return f"[{sign}{lo:.4f}, +{hi:.4f}]"
            
        boot_summary[bb] = {
            "dec_mean": float(np.mean(boot_u_dec)),
            "dec_ci": ci_fmt(boot_u_dec),
            "base_mean": float(np.mean(boot_u_base)),
            "base_ci": ci_fmt(boot_u_base),
            "gain_mean": float(np.mean(boot_gain)),
            "gain_ci": ci_fmt(boot_gain),
        }
        print(f"[{bb.upper()}] Bootstrap Unseen: {boot_summary[bb]['dec_mean']:.4f} {boot_summary[bb]['dec_ci']} (Gain: {boot_summary[bb]['gain_mean']:+.4f} {boot_summary[bb]['gain_ci']})")
        
    return boot_summary

def main():
    print("================================================================================")
    print("      DEC-GMR: DECODER-EVIDENTIAL CONJUNCTIVE VERIFICATION BENCHMARK            ")
    print("================================================================================")
    t_start = time.time()
    
    gpu_map = {
        "A1": 0,
        "A2_alt": 0,
        "A3": 0,
        "C1": 1,
        "C2_alt": 1,
    }
    
    manager = mp.Manager()
    return_dict = manager.dict()
    processes = []
    
    for split in SPLITS:
        gpu_id = gpu_map[split]
        p = mp.Process(
            target=process_split_worker,
            args=(split, gpu_id, 3407, 400, return_dict),
        )
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    ordered_results = [return_dict[sp] for sp in SPLITS]
    
    # Compute Macro Averages
    macro_summary = {}
    for bb in MODELS:
        macro_summary[bb] = {
            "base_seen": float(np.mean([r["results"][bb]["baseline"]["seen"] for r in ordered_results])),
            "base_unseen": float(np.mean([r["results"][bb]["baseline"]["unseen"] for r in ordered_results])),
            "base_gap": float(np.mean([r["results"][bb]["baseline"]["gap"] for r in ordered_results])),
            "base_pair_acc": float(np.mean([r["results"][bb]["baseline"]["pair_acc"] for r in ordered_results])),
            "dec_seen": float(np.mean([r["results"][bb]["dec_gmr"]["seen"] for r in ordered_results])),
            "dec_unseen": float(np.mean([r["results"][bb]["dec_gmr"]["unseen"] for r in ordered_results])),
            "dec_gap": float(np.mean([r["results"][bb]["dec_gmr"]["gap"] for r in ordered_results])),
            "dec_pair_acc": float(np.mean([r["results"][bb]["dec_gmr"]["pair_acc"] for r in ordered_results])),
            "gain_unseen": float(np.mean([r["results"][bb]["dec_gmr"]["gain_unseen"] for r in ordered_results])),
            "gap_reduction": float(np.mean([r["results"][bb]["dec_gmr"]["gap_reduction"] for r in ordered_results])),
        }
        
    # Bootstrap
    bootstrap_summary = run_paired_video_cluster_bootstrap(ordered_results, n_boot=2000)
    
    # Save benchmark summary
    summary_out = {
        "macro_summary": macro_summary,
        "bootstrap": bootstrap_summary,
        "splits": [{
            "split": r["split"],
            "results": r["results"],
        } for r in ordered_results]
    }
    
    with open(BASE_DIR / "benchmark_summary.json", "w") as f:
        json.dump(summary_out, f, indent=2)
    print(f"\nBenchmark summary successfully saved to {BASE_DIR / 'benchmark_summary.json'}!")
    
    print("\n========================= FINAL MACRO PERFORMANCE BENCHMARK =========================")
    for bb in MODELS:
        m = macro_summary[bb]
        b = bootstrap_summary[bb]
        print(f"\nModel: {bb.upper()}")
        print(f"  Baseline : Seen={m['base_seen']:.4f}, Unseen={m['base_unseen']:.4f}, Gap={m['base_gap']:.4f}, PairAcc={m['base_pair_acc']:.4f}")
        print(f"  DEC-GMR  : Seen={m['dec_seen']:.4f}, Unseen={m['dec_unseen']:.4f}, Gap={m['dec_gap']:.4f}, PairAcc={m['dec_pair_acc']:.4f}")
        print(f"  NET GAIN : Unseen Gain={m['gain_unseen']:+.4f} (95% CI: {b['gain_ci']}), Gap Reduction={m['gap_reduction']:+.4f}")

    print(f"\nTotal pipeline completed in {time.time()-t_start:.2f}s.")

if __name__ == "__main__":
    main()
