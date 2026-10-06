#!/usr/bin/env python3
"""
Cross-Backbone Transfer and Generalization Benchmark Suite.

Executes:
1. Training 3 specialized modular verifiers on Seen training data:
   - Verifier_Flash  (Source: FlashVTG + Multimodal)
   - Verifier_Moment (Source: Moment-DETR + Multimodal)
   - Verifier_QD     (Source: QD-DETR + Multimodal)
2. Evaluating full 3x3 Cross-Backbone Transfer Matrix on Unseen test set:
   - Self-Backbone Verification (Diagonal): Flash->Flash, Moment->Moment, QD->QD
   - Cross-Backbone Transfer (Off-Diagonal): Flash->Moment, Flash->QD, Moment->Flash, Moment->QD, QD->Flash, QD->Moment
3. Multi-GPU parallel execution:
   - GPU 0: Splits A1, A2_alt, A3 (3 concurrent tasks)
   - GPU 1: Splits C1, C2_alt     (2 concurrent tasks)
4. 400 Epochs per model with Cosine Annealing learning rate schedule.
5. Strictly zero label leakage (model selection on Seen validation).
6. 2,000-iteration Paired Video Cluster Bootstrap on all transfer cells.
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
REPORTS_DIR = BASE_DIR / "reports"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"

sys.path.insert(0, str(BASE_DIR))
from model import SingleBackboneVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = ["flash", "moment", "qd"]

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

def train_single_verifier(
    name: str,
    det_idx: int,
    t_tr: torch.Tensor,
    y_tr_t: torch.Tensor,
    same_pairs_t: torch.Tensor,
    pos_idx: torch.Tensor,
    neg_idx: torch.Tensor,
    t_val: torch.Tensor,
    y_val: np.ndarray,
    device: torch.device,
    epochs: int = 400,
    lr: float = 3e-3,
):
    model = SingleBackboneVerifier(hidden_dim=32).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    half_b = 128
    steps_per_epoch = 10
    best_val_auc = -1.0
    best_state = None
    
    # det_idx: 0 for flash, 1 for moment, 2 for qd
    # mm_feats: t_tr[:, 3:]
    s_det_tr = t_tr[:, det_idx]
    mm_tr = t_tr[:, 3:]
    
    s_det_val = t_val[:, det_idx]
    mm_val = t_val[:, 3:]
    
    for ep in range(1, epochs + 1):
        model.train()
        for step in range(steps_per_epoch):
            optimizer.zero_grad()
            
            # Intra-video counterfactual pairs
            intra_idx = torch.randint(len(same_pairs_t), (half_b,), device=device)
            p_intra = same_pairs_t[intra_idx, 0]
            n_intra = same_pairs_t[intra_idx, 1]
            
            # Inter-video random pairs
            p_inter = pos_idx[torch.randint(len(pos_idx), (half_b,), device=device)]
            n_inter = neg_idx[torch.randint(len(neg_idx), (half_b,), device=device)]
            
            p_all = torch.cat([p_intra, p_inter])
            n_all = torch.cat([n_intra, n_inter])
            
            sp = model(s_det_tr[p_all], mm_tr[p_all])
            sn = model(s_det_tr[n_all], mm_tr[n_all])
            
            loss_rank = F.softplus(-(sp - sn) / 0.15).mean()
            
            all_x_det = torch.cat([s_det_tr[p_all], s_det_tr[n_all]])
            all_x_mm = torch.cat([mm_tr[p_all], mm_tr[n_all]])
            all_y = torch.cat([torch.ones_like(sp), torch.zeros_like(sn)])
            s_calib = model(all_x_det, all_x_mm)
            loss_bce = F.binary_cross_entropy(torch.clamp(s_calib, 1e-6, 1.0 - 1e-6), all_y)
            
            loss = loss_rank + 0.4 * loss_bce
            loss.backward()
            optimizer.step()
            
        scheduler.step()
        
        # Validate strictly on Seen validation
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
    
    print(f"[{split}] >>> Starting Cross-Backbone Training on {device} (epochs={epochs})...", flush=True)
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
    
    # 2. Rank Transform
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
    
    # Standalone detector test scores (rank-normalized in [0, 1])
    s_fl_te = t_te[:, 0]
    s_mo_te = t_te[:, 1]
    s_qd_te = t_te[:, 2]
    mm_te = t_te[:, 3:]
    
    # Standalone raw baselines on test
    base_scores = {
        "flash": r_te[:, 0],
        "moment": r_te[:, 1],
        "qd": r_te[:, 2],
    }
    standalones = {}
    for bb in BACKBONES:
        sc = base_scores[bb]
        s_auc = float(roc_auc_score(y_te[is_s_te], sc[is_s_te]))
        u_auc = float(roc_auc_score(y_te[is_u_te], sc[is_u_te]))
        pa = compute_matched_pair_acc(qids_te, sc, pairs_file)
        standalones[bb] = {
            "seen": s_auc,
            "unseen": u_auc,
            "gap": s_auc - u_auc,
            "pair_acc": pa,
        }
        
    print(f"[{split}] Standalone Baselines: Flash={standalones['flash']['unseen']:.4f}, Moment={standalones['moment']['unseen']:.4f}, QD={standalones['qd']['unseen']:.4f}", flush=True)
    
    # 3. Train 3 Modular Verifiers
    models = {}
    val_aucs = {}
    
    det_map = {"flash": 0, "moment": 1, "qd": 2}
    for src_bb in BACKBONES:
        idx = det_map[src_bb]
        m, v_auc = train_single_verifier(
            src_bb, idx, t_tr, y_tr_t, same_pairs_t, pos_idx, neg_idx, t_val, y_val, device, epochs=epochs
        )
        models[src_bb] = m
        val_aucs[src_bb] = v_auc
        torch.save(m.state_dict(), split_dir / f"verifier_src_{src_bb}.pt")
        
    print(f"[{split}] All 3 verifiers trained. Val AUROCs: Flash={val_aucs['flash']:.4f}, Moment={val_aucs['moment']:.4f}, QD={val_aucs['qd']:.4f}", flush=True)
    
    # 4. Cross-Backbone Transfer Evaluation (3x3 Matrix)
    # Rows: source verifier, Columns: target backbone
    transfer_matrix = {}
    predictions_matrix = {}
    
    target_tensors = {
        "flash": s_fl_te,
        "moment": s_mo_te,
        "qd": s_qd_te,
    }
    
    for src in BACKBONES:
        m = models[src]
        transfer_matrix[src] = {}
        predictions_matrix[src] = {}
        for tgt in BACKBONES:
            tgt_s = target_tensors[tgt]
            with torch.no_grad():
                pred_scores = m(tgt_s, mm_te).cpu().numpy()
                
            s_auc = float(roc_auc_score(y_te[is_s_te], pred_scores[is_s_te]))
            u_auc = float(roc_auc_score(y_te[is_u_te], pred_scores[is_u_te]))
            pa = compute_matched_pair_acc(qids_te, pred_scores, pairs_file)
            
            tgt_base_u = standalones[tgt]["unseen"]
            gain_vs_tgt = u_auc - tgt_base_u
            
            transfer_matrix[src][tgt] = {
                "seen": s_auc,
                "unseen": u_auc,
                "gap": s_auc - u_auc,
                "pair_acc": pa,
                "gain_vs_target_base": gain_vs_tgt,
            }
            predictions_matrix[src][tgt] = pred_scores
            
    # Consensus Ensemble across the 3 transferred models
    # Average predictions of (Flash->tgt, Moment->tgt, QD->tgt) for each target
    ensemble_results = {}
    for tgt in BACKBONES:
        ens_pred = (
            predictions_matrix["flash"][tgt] +
            predictions_matrix["moment"][tgt] +
            predictions_matrix["qd"][tgt]
        ) / 3.0
        s_auc = float(roc_auc_score(y_te[is_s_te], ens_pred[is_s_te]))
        u_auc = float(roc_auc_score(y_te[is_u_te], ens_pred[is_u_te]))
        pa = compute_matched_pair_acc(qids_te, ens_pred, pairs_file)
        ensemble_results[tgt] = {
            "seen": s_auc,
            "unseen": u_auc,
            "gap": s_auc - u_auc,
            "pair_acc": pa,
            "gain_vs_base": u_auc - standalones[tgt]["unseen"],
        }
        
    elapsed = time.time() - t0
    print(f"[{split}] Cross-Evaluation Complete in {elapsed:.2f}s.", flush=True)
    print(f"  Diagonal (Self-Verified): Flash={transfer_matrix['flash']['flash']['unseen']:.4f}, Moment={transfer_matrix['moment']['moment']['unseen']:.4f}, QD={transfer_matrix['qd']['qd']['unseen']:.4f}", flush=True)
    print(f"  Off-Diagonal (Transfer) : Flash->Moment={transfer_matrix['flash']['moment']['unseen']:.4f}, Moment->Flash={transfer_matrix['moment']['flash']['unseen']:.4f}, QD->Moment={transfer_matrix['qd']['moment']['unseen']:.4f}", flush=True)
    
    # Save predictions
    save_dict = {
        "qids": qids_te,
        "vids": vids_te,
        "partitions": parts_te,
        "labels": y_te,
    }
    for src in BACKBONES:
        for tgt in BACKBONES:
            save_dict[f"pred_{src}_to_{tgt}"] = predictions_matrix[src][tgt]
    np.savez_compressed(split_dir / "transfer_predictions.npz", **save_dict)
    
    res = {
        "split": split,
        "standalones": standalones,
        "val_aucs": val_aucs,
        "transfer_matrix": transfer_matrix,
        "ensemble_results": ensemble_results,
        "qids": list(qids_te),
        "vids": list(vids_te),
        "partitions": parts_te,
        "labels": y_te,
        "predictions_matrix": predictions_matrix,
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
        
    boot_matrix_u = {src: {tgt: [] for tgt in BACKBONES} for src in BACKBONES}
    boot_matrix_gain = {src: {tgt: [] for tgt in BACKBONES} for src in BACKBONES}
    
    t0 = time.time()
    for b in range(n_boot):
        sample_vids = np.random.choice(shared_vids, size=n_vids, replace=True)
        
        split_u = {src: {tgt: [] for tgt in BACKBONES} for src in BACKBONES}
        split_base_u = {tgt: [] for tgt in BACKBONES}
        
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
                
            preds = r["predictions_matrix"]
            for tgt in BACKBONES:
                base_s = r["standalones"][tgt]["unseen"] # proxy
                
            for src in BACKBONES:
                for tgt in BACKBONES:
                    s_b = preds[src][tgt][sub_indices]
                    split_u[src][tgt].append(roc_auc_score(y_b[u_mask], s_b[u_mask]))
                    
        if not valid:
            continue
            
        for src in BACKBONES:
            for tgt in BACKBONES:
                boot_matrix_u[src][tgt].append(float(np.mean(split_u[src][tgt])))
                
    def ci_fmt(arr):
        lo, hi = np.percentile(arr, 2.5), np.percentile(arr, 97.5)
        sign = "+" if lo >= 0 else ""
        return f"[{sign}{lo:.4f}, +{hi:.4f}]"
        
    bootstrap_summary = {}
    for src in BACKBONES:
        bootstrap_summary[src] = {}
        for tgt in BACKBONES:
            arr = boot_matrix_u[src][tgt]
            bootstrap_summary[src][tgt] = {
                "mean": float(np.mean(arr)),
                "ci": ci_fmt(arr),
            }
            
    print(f"Bootstrap finished in {time.time()-t0:.2f}s ({len(boot_matrix_u['flash']['flash'])} valid resamples).")
    return bootstrap_summary

def main():
    print("================================================================================")
    print("      CROSS-BACKBONE TRANSFER AND GENERALIZATION BENCHMARK                      ")
    print("================================================================================")
    t_start = time.time()
    
    # Multi-GPU Mapping
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
    
    # 5. Compute Macro 3x3 Transfer Matrix
    macro_standalones = {}
    for bb in BACKBONES:
        macro_standalones[bb] = {
            "seen": float(np.mean([r["standalones"][bb]["seen"] for r in ordered_results])),
            "unseen": float(np.mean([r["standalones"][bb]["unseen"] for r in ordered_results])),
            "gap": float(np.mean([r["standalones"][bb]["gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["standalones"][bb]["pair_acc"] for r in ordered_results])),
        }
        
    macro_transfer_matrix = {}
    for src in BACKBONES:
        macro_transfer_matrix[src] = {}
        for tgt in BACKBONES:
            macro_transfer_matrix[src][tgt] = {
                "seen": float(np.mean([r["transfer_matrix"][src][tgt]["seen"] for r in ordered_results])),
                "unseen": float(np.mean([r["transfer_matrix"][src][tgt]["unseen"] for r in ordered_results])),
                "gap": float(np.mean([r["transfer_matrix"][src][tgt]["gap"] for r in ordered_results])),
                "pair_acc": float(np.mean([r["transfer_matrix"][src][tgt]["pair_acc"] for r in ordered_results])),
                "gain_vs_target_base": float(np.mean([r["transfer_matrix"][src][tgt]["gain_vs_target_base"] for r in ordered_results])),
            }
            
    macro_ensemble = {}
    for tgt in BACKBONES:
        macro_ensemble[tgt] = {
            "seen": float(np.mean([r["ensemble_results"][tgt]["seen"] for r in ordered_results])),
            "unseen": float(np.mean([r["ensemble_results"][tgt]["unseen"] for r in ordered_results])),
            "gap": float(np.mean([r["ensemble_results"][tgt]["gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["ensemble_results"][tgt]["pair_acc"] for r in ordered_results])),
            "gain_vs_base": float(np.mean([r["ensemble_results"][tgt]["gain_vs_base"] for r in ordered_results])),
        }
        
    # Bootstrap
    bootstrap_summary = run_paired_video_cluster_bootstrap(ordered_results, n_boot=2000)
    
    # Clean JSON summary
    summary_out = {
        "macro_standalones": macro_standalones,
        "macro_transfer_matrix": macro_transfer_matrix,
        "macro_ensemble": macro_ensemble,
        "bootstrap": bootstrap_summary,
        "splits": [{
            "split": r["split"],
            "standalones": r["standalones"],
            "transfer_matrix": r["transfer_matrix"],
            "ensemble_results": r["ensemble_results"],
        } for r in ordered_results]
    }
    
    with open(BASE_DIR / "benchmark_summary.json", "w") as f:
        json.dump(summary_out, f, indent=2)
    print(f"\nBenchmark summary successfully saved to {BASE_DIR / 'benchmark_summary.json'}!")
    
    print("\n========================= 3x3 MACRO CROSS-BACKBONE TRANSFER MATRIX =========================")
    print(f"Standalone Baselines: FlashVTG={macro_standalones['flash']['unseen']:.4f}, Moment-DETR={macro_standalones['moment']['unseen']:.4f}, QD-DETR={macro_standalones['qd']['unseen']:.4f}\n")
    print(f"{'Source Verifier':20s} | {'Target Flash':15s} | {'Target Moment':15s} | {'Target QD-DETR':15s}")
    print("-" * 75)
    for src in BACKBONES:
        row_str = f"Trained on {src.upper():9s} | "
        for tgt in BACKBONES:
            u = macro_transfer_matrix[src][tgt]["unseen"]
            g = macro_transfer_matrix[src][tgt]["gain_vs_target_base"]
            row_str += f"{u:.4f} ({g:+.4f})   | "
        print(row_str)
        
    print("-" * 75)
    print(f"Ensemble across 3 Verifiers: Flash={macro_ensemble['flash']['unseen']:.4f} ({macro_ensemble['flash']['gain_vs_base']:+.4f}) | Moment={macro_ensemble['moment']['unseen']:.4f} ({macro_ensemble['moment']['gain_vs_base']:+.4f}) | QD={macro_ensemble['qd']['unseen']:.4f} ({macro_ensemble['qd']['gain_vs_base']:+.4f})")
    print(f"Total pipeline completed in {time.time()-t_start:.2f}s.")

if __name__ == "__main__":
    main()
