#!/usr/bin/env python3
"""
Decomposed Directional Verifier (DDV) End-to-End Training and Benchmark Evaluation.

Execution Protocol:
1. Multi-GPU Parallel Training:
   - GPU 0: Splits A1, A2_alt, A3 (3 concurrent training jobs)
   - GPU 1: Splits C1, C2_alt (2 concurrent training jobs)
2. 400 Epochs per split with Cosine Annealing LR and Dual-Curriculum Loss:
   - Intra-video counterfactual pairs (fine-grained action/object discrimination)
   - Inter-video calibrated pairs (global score alignment)
3. Zero Label Leakage:
   - Model selection strictly on Seen validation (S+ / S-).
   - Binary decision threshold selected strictly on Seen validation.
4. Comprehensive Dual-Baseline Benchmarking:
   - Base 1 (HQ raw logit): Seen 0.7511, Unseen 0.5027, Gap 0.2484
   - Base 2 (Release QD): Seen 0.7476, Unseen 0.5144, Gap 0.2332
5. Downstream Localization:
   - G-mIoU@1, 3, 5, Rej-F1, FRR, RR.
6. Statistical Rigor:
   - 2,000-iteration Paired Video Cluster Bootstrap with 95% CIs.
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
from sklearn.metrics import roc_auc_score, f1_score

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
RUNS_DIR = BASE_DIR / "runs"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
SUBMISSION_DIR = REPO_ROOT / "results/semantic_existence/multi_split_v2"

sys.path.insert(0, str(BASE_DIR))
from model import DecomposedDirectionalVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
KS = [1, 3, 5]

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

def rank_transform(X_ref, X_apply):
    res = np.zeros_like(X_apply)
    for c in range(X_apply.shape[1]):
        sorted_ref = np.sort(X_ref[:, c])
        res[:, c] = np.searchsorted(sorted_ref, X_apply[:, c]) / len(sorted_ref)
    return res

def _compute_set_iou_score(pred_spans, gt_spans):
    if len(pred_spans) == 0:
        return 0.0
    pred_arr = np.array(pred_spans, dtype=float)
    p_min = pred_arr[:, 0].min()
    p_max = pred_arr[:, 1].max()
    pred_span = [p_min, p_max]
    ious = []
    for gt in gt_spans:
        inter = max(0.0, min(pred_span[1], gt[1]) - max(pred_span[0], gt[0]))
        union = max(pred_span[1], gt[1]) - min(pred_span[0], gt[0])
        ious.append(inter / union if union > 0 else 0.0)
    return max(ious) if ious else 0.0

def prepare_submission_for_gmiou(raw_submission, cls_threshold=0.5, max_pred_windows=10):
    gated_submission = []
    for row in raw_submission:
        new_row = dict(row)
        score = float(row.get("pred_exist_score", 0.0))
        if score >= cls_threshold:
            windows = row.get("pred_relevant_windows", [])[:max_pred_windows]
            new_row["pred_relevant_windows"] = windows
        else:
            new_row["pred_relevant_windows"] = []
        gated_submission.append(new_row)
    return gated_submission, cls_threshold

def train_split_worker(
    split: str,
    gpu_id: int,
    seed: int = 3407,
    epochs: int = 400,
    lr: float = 3e-3,
    return_dict: dict | None = None,
):
    set_seed(seed)
    device = torch.device(f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu")
    split_dir = RUNS_DIR / split
    split_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[{split}] >>> Starting DDV training on {device} (epochs={epochs}, lr={lr})...", flush=True)
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
    base_te_scores = te_d["base_scores"]
    
    is_s_te = (parts_te == "S+") | (parts_te == "S-")
    is_u_te = (parts_te == "U+") | (parts_te == "U-")
    
    # 2. Non-Parametric Empirical CDF Rank Normalization
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
    
    # 3. Model & Optimizer
    # Bounded alpha per family
    if split == "A3":
        alpha_min, alpha_max = 0.35, 0.60
    elif split in ["C1", "C2_alt"]:
        alpha_min, alpha_max = 0.35, 0.55
    else:
        alpha_min, alpha_max = 0.35, 0.55
        
    model = DecomposedDirectionalVerifier(
        split=split,
        hidden_dim=32,
        alpha_min=alpha_min,
        alpha_max=alpha_max,
    ).to(device)
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    best_val_auc = -1.0
    best_state = None
    batch_size = 256
    half_b = batch_size // 2
    steps_per_epoch = 10
    
    # 4. Training Loop
    for ep in range(1, epochs + 1):
        model.train()
        for step in range(steps_per_epoch):
            optimizer.zero_grad()
            
            # Intra-video counterfactual pairs (same video positive vs negative)
            intra_idx = torch.randint(len(same_pairs_t), (half_b,), device=device)
            p_intra = same_pairs_t[intra_idx, 0]
            n_intra = same_pairs_t[intra_idx, 1]
            
            # Inter-video random pairs
            p_inter = pos_idx[torch.randint(len(pos_idx), (half_b,), device=device)]
            n_inter = neg_idx[torch.randint(len(neg_idx), (half_b,), device=device)]
            
            p_all = torch.cat([p_intra, p_inter])
            n_all = torch.cat([n_intra, n_inter])
            
            s_p = model(t_tr[p_all])
            s_n = model(t_tr[n_all])
            
            # Contrastive softplus loss
            loss_rank = F.softplus(-(s_p - s_n) / 0.15).mean()
            
            # Calibration BCE loss
            all_x = torch.cat([p_all, n_all])
            all_y = torch.cat([torch.ones_like(s_p), torch.zeros_like(s_n)])
            s_calib = model(t_tr[all_x])
            loss_calib = F.binary_cross_entropy(torch.clamp(s_calib, 1e-6, 1.0 - 1e-6), all_y)
            
            # Multi-detector entropy regularization
            w_d = F.softmax(model.w_det, dim=0)
            entropy = -(w_d * torch.log(w_d + 1e-8)).sum()
            loss_ent = -0.05 * entropy # encourage uniform consensus
            
            loss = loss_rank + 0.4 * loss_calib + loss_ent
            loss.backward()
            optimizer.step()
            
        scheduler.step()
        
        # Validation Evaluation strictly on Seen validation
        model.eval()
        with torch.no_grad():
            v_scores = model(t_val).cpu().numpy()
            v_auc = float(roc_auc_score(y_val, v_scores))
            if v_auc > best_val_auc:
                best_val_auc = v_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    elapsed = time.time() - t0
    print(f"[{split}] Training complete in {elapsed:.2f}s ({epochs} epochs). Best Seen Val AUROC: {best_val_auc:.4f}", flush=True)
    
    # 5. Load Best Model Checkpoint
    model.load_state_dict(best_state)
    model.eval()
    
    # 6. Compute Optimal Seen Decision Threshold strictly on Seen validation
    with torch.no_grad():
        v_scores_best = model(t_val).cpu().numpy()
        seen_threshold = choose_val_seen_threshold(v_scores_best, y_val)
        te_scores = model(t_te).cpu().numpy()
        
    # 7. Evaluate Metrics
    # Baseline 1: Canonical FlashVTG raw logits
    b1_seen_auc = float(roc_auc_score(y_te[is_s_te], base_te_scores[is_s_te]))
    b1_unseen_auc = float(roc_auc_score(y_te[is_u_te], base_te_scores[is_u_te]))
    b1_gap = b1_seen_auc - b1_unseen_auc
    
    # Baseline 2: Official Release QD
    qd_sub_file = SUBMISSION_DIR / split / "qd/test/qd_detr_gmr_test_submission.jsonl"
    qd_sub = [json.loads(l) for l in qd_sub_file.read_text().splitlines() if l.strip()]
    qd_map = {str(p["qid"]): float(p.get("pred_exist_score", 0.0)) for p in qd_sub}
    base2_scores = np.array([qd_map[str(q)] for q in qids_te], dtype=np.float32)
    b2_seen_auc = float(roc_auc_score(y_te[is_s_te], base2_scores[is_s_te]))
    b2_unseen_auc = float(roc_auc_score(y_te[is_u_te], base2_scores[is_u_te]))
    b2_gap = b2_seen_auc - b2_unseen_auc
    
    # DDV Metrics
    ddv_seen_auc = float(roc_auc_score(y_te[is_s_te], te_scores[is_s_te]))
    ddv_unseen_auc = float(roc_auc_score(y_te[is_u_te], te_scores[is_u_te]))
    ddv_gap = ddv_seen_auc - ddv_unseen_auc
    
    # Matched PairAcc
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    base_pair_acc = compute_matched_pair_acc(qids_te, base_te_scores, pairs_file)
    ddv_pair_acc = compute_matched_pair_acc(qids_te, te_scores, pairs_file)
    
    # Decision Rejection Metrics
    u_pos_mask = (parts_te == "U+")
    u_neg_mask = (parts_te == "U-")
    u_preds = (te_scores >= seen_threshold)
    u_pos_frr = float((~u_preds[u_pos_mask]).mean() * 100.0)
    u_neg_rr = float((~u_preds[u_neg_mask]).mean() * 100.0)
    
    rej_pred_u = (~u_preds).astype(int)
    rej_gt_u = (y_te[is_u_te] == 0).astype(int)
    rej_f1 = float(f1_score(rej_gt_u, rej_pred_u[is_u_te], average="binary") * 100.0)
    
    # Downstream G-mIoU Localization
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
        for m, k in enumerate(KS):
            gmiou_vals[i, m] = _compute_set_iou_score([w[:2] for w in gated_sub[i]["pred_relevant_windows"][:k]], x["relevant_windows"])
            
    seen_mask = is_s_te
    unseen_mask = is_u_te
    gmiou_seen = [float(gmiou_vals[seen_mask, m].mean() * 100.0) for m in range(3)]
    gmiou_unseen = [float(gmiou_vals[unseen_mask, m].mean() * 100.0) for m in range(3)]
    
    print(f"[{split}] Base1 Seen: {b1_seen_auc:.4f}, Unseen: {b1_unseen_auc:.4f}, Gap: {b1_gap:.4f}, PairAcc: {base_pair_acc:.4f}", flush=True)
    print(f"[{split}] Base2 Seen: {b2_seen_auc:.4f}, Unseen: {b2_unseen_auc:.4f}, Gap: {b2_gap:.4f}", flush=True)
    print(f"[{split}] DDV   Seen: {ddv_seen_auc:.4f}, Unseen: {ddv_unseen_auc:.4f}, Gap: {ddv_gap:.4f}, PairAcc: {ddv_pair_acc:.4f}", flush=True)
    print(f"[{split}] Net Gain vs Base1: Seen={ddv_seen_auc - b1_seen_auc:+.4f}, Unseen={ddv_unseen_auc - b1_unseen_auc:+.4f}, Gap Red={b1_gap - ddv_gap:+.4f}, Pair Gain={ddv_pair_acc - base_pair_acc:+.4f}", flush=True)
    print(f"[{split}] Net Gain vs Base2: Seen={ddv_seen_auc - b2_seen_auc:+.4f}, Unseen={ddv_unseen_auc - b2_unseen_auc:+.4f}, Gap Red={b2_gap - ddv_gap:+.4f}", flush=True)
    print(f"[{split}] G-mIoU Seen @1,3,5: {[round(v, 2) for v in gmiou_seen]} | Unseen @1,3,5: {[round(v, 2) for v in gmiou_unseen]}", flush=True)
    
    # Save checkpoint & predictions
    torch.save(best_state, split_dir / "best_model.pt")
    np.savez_compressed(
        split_dir / "predictions.npz",
        qids=qids_te,
        vids=vids_te,
        partitions=parts_te,
        labels=y_te,
        base_hq_scores=base_te_scores,
        base_rel_scores=base2_scores,
        ddv_scores=te_scores,
        threshold=seen_threshold,
    )
    
    res = {
        "split": split,
        "val_seen_auc": best_val_auc,
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
    }
    
    if return_dict is not None:
        return_dict[split] = res
    return res

def run_paired_video_cluster_bootstrap(split_results, n_boot=2000, seed=3407):
    print(f"\n==================== RUNNING {n_boot}-ITERATION PAIRED VIDEO CLUSTER BOOTSTRAP ====================")
    set_seed(seed)
    shared_vids = sorted(list(set.union(*[set(r["vids"]) for r in split_results])))
    n_vids = len(shared_vids)
    print(f"Total unique test videos in cluster bootstrap: {n_vids}")
    
    vid_to_idx_per_split = []
    for r in split_results:
        v_map = {}
        for i, v in enumerate(r["vids"]):
            v_map.setdefault(v, []).append(i)
        vid_to_idx_per_split.append(v_map)
        
    boot_ddv_unseen, boot_ddv_seen, boot_ddv_gap = [], [], []
    boot_gain1_u, boot_gain1_s, boot_gapred1 = [], [], []
    boot_gain2_u, boot_gain2_s, boot_gapred2 = [], [], []
    boot_pair_acc = []
    
    t0 = time.time()
    for b in range(n_boot):
        sample_vids = np.random.choice(shared_vids, size=n_vids, replace=True)
        
        split_u_ddv, split_s_ddv = [], []
        split_u_b1, split_s_b1 = [], []
        split_u_b2, split_s_b2 = [], []
        
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
            s_ddv_b = r["ddv_scores"][sub_indices]
            s_b1_b = r["base_hq_scores"][sub_indices]
            s_b2_b = r["base_rel_scores"][sub_indices]
            
            u_mask = (parts_b == "U+") | (parts_b == "U-")
            s_mask = (parts_b == "S+") | (parts_b == "S-")
            
            if len(np.unique(y_b[u_mask])) < 2 or len(np.unique(y_b[s_mask])) < 2:
                valid = False
                break
                
            split_u_ddv.append(roc_auc_score(y_b[u_mask], s_ddv_b[u_mask]))
            split_s_ddv.append(roc_auc_score(y_b[s_mask], s_ddv_b[s_mask]))
            split_u_b1.append(roc_auc_score(y_b[u_mask], s_b1_b[u_mask]))
            split_s_b1.append(roc_auc_score(y_b[s_mask], s_b1_b[s_mask]))
            split_u_b2.append(roc_auc_score(y_b[u_mask], s_b2_b[u_mask]))
            split_s_b2.append(roc_auc_score(y_b[s_mask], s_b2_b[s_mask]))
            
        if not valid:
            continue
            
        m_u_ddv = np.mean(split_u_ddv)
        m_s_ddv = np.mean(split_s_ddv)
        m_gap_ddv = m_s_ddv - m_u_ddv
        
        m_u_b1 = np.mean(split_u_b1)
        m_s_b1 = np.mean(split_s_b1)
        m_gap_b1 = m_s_b1 - m_u_b1
        
        m_u_b2 = np.mean(split_u_b2)
        m_s_b2 = np.mean(split_s_b2)
        m_gap_b2 = m_s_b2 - m_u_b2
        
        boot_ddv_unseen.append(m_u_ddv)
        boot_ddv_seen.append(m_s_ddv)
        boot_ddv_gap.append(m_gap_ddv)
        
        boot_gain1_u.append(m_u_ddv - m_u_b1)
        boot_gain1_s.append(m_s_ddv - m_s_b1)
        boot_gapred1.append(m_gap_b1 - m_gap_ddv)
        
        boot_gain2_u.append(m_u_ddv - m_u_b2)
        boot_gain2_s.append(m_s_ddv - m_s_b2)
        boot_gapred2.append(m_gap_b2 - m_gap_ddv)
        
    def ci_fmt(arr):
        lo, hi = np.percentile(arr, 2.5), np.percentile(arr, 97.5)
        sign = "+" if lo >= 0 else ""
        return f"[{sign}{lo:.4f}, +{hi:.4f}]"
        
    print(f"Bootstrap finished in {time.time()-t0:.2f}s ({len(boot_ddv_unseen)} valid resamples).")
    
    return {
        "n_valid_boot": len(boot_ddv_unseen),
        "ddv_seen": {"mean": float(np.mean(boot_ddv_seen)), "ci": ci_fmt(boot_ddv_seen)},
        "ddv_unseen": {"mean": float(np.mean(boot_ddv_unseen)), "ci": ci_fmt(boot_ddv_unseen)},
        "ddv_gap": {"mean": float(np.mean(boot_ddv_gap)), "ci": ci_fmt(boot_ddv_gap)},
        "vs_base1_hq": {
            "unseen_gain_mean": float(np.mean(boot_gain1_u)),
            "unseen_gain_ci": ci_fmt(boot_gain1_u),
            "seen_gain_mean": float(np.mean(boot_gain1_s)),
            "seen_gain_ci": ci_fmt(boot_gain1_s),
            "gap_red_mean": float(np.mean(boot_gapred1)),
            "gap_red_ci": ci_fmt(boot_gapred1),
        },
        "vs_base2_release": {
            "unseen_gain_mean": float(np.mean(boot_gain2_u)),
            "unseen_gain_ci": ci_fmt(boot_gain2_u),
            "seen_gain_mean": float(np.mean(boot_gain2_s)),
            "seen_gain_ci": ci_fmt(boot_gain2_s),
            "gap_red_mean": float(np.mean(boot_gapred2)),
            "gap_red_ci": ci_fmt(boot_gapred2),
        },
    }

def main():
    print("================================================================================")
    print("      DECOMPOSED DIRECTIONAL VERIFIER (DDV): MULTI-GPU PARALLEL RUN            ")
    print("================================================================================")
    t_start = time.time()
    
    # Parallel Multi-GPU Worker Setup:
    # GPU 0: A1, A2_alt, A3 (3 tasks)
    # GPU 1: C1, C2_alt     (2 tasks)
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
            target=train_split_worker,
            args=(split, gpu_id, 3407, 400, 3e-3, return_dict),
        )
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    # Gather results in order of SPLITS
    ordered_results = [return_dict[sp] for sp in SPLITS]
    
    # Macro averages
    macro = {
        "base1_hq": {
            "seen": float(np.mean([r["base1_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["base1_unseen_auc"] for r in ordered_results])),
            "gap": float(np.mean([r["base1_gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["base_pair_acc"] for r in ordered_results])),
        },
        "base2_release": {
            "seen": float(np.mean([r["base2_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["base2_unseen_auc"] for r in ordered_results])),
            "gap": float(np.mean([r["base2_gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["base_pair_acc"] for r in ordered_results])),
        },
        "ddv": {
            "seen": float(np.mean([r["ddv_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["ddv_unseen_auc"] for r in ordered_results])),
            "gap": float(np.mean([r["ddv_gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["ddv_pair_acc"] for r in ordered_results])),
            "gain_vs_b1": float(np.mean([r["gain1_unseen"] for r in ordered_results])),
            "gain_vs_b2": float(np.mean([r["gain2_unseen"] for r in ordered_results])),
            "gap_red_vs_b1": float(np.mean([r["gap_red1"] for r in ordered_results])),
            "gap_red_vs_b2": float(np.mean([r["gap_red2"] for r in ordered_results])),
            "gmiou_seen": [float(np.mean([r["gmiou_seen"][m] for r in ordered_results])) for m in range(3)],
            "gmiou_unseen": [float(np.mean([r["gmiou_unseen"][m] for r in ordered_results])) for m in range(3)],
            "rej_f1": float(np.mean([r["rej_f1"] for r in ordered_results])),
        }
    }
    
    # Run Bootstrap
    bootstrap_results = run_paired_video_cluster_bootstrap(ordered_results, n_boot=2000)
    
    # Save Clean JSON Summary
    summary_out = {
        "macro": macro,
        "splits": [{k: v for k, v in r.items() if not isinstance(v, (np.ndarray, list)) or k in ["gmiou_seen", "gmiou_unseen"]} for r in ordered_results],
        "bootstrap": bootstrap_results,
    }
    
    with open(BASE_DIR / "benchmark_summary.json", "w") as f:
        json.dump(summary_out, f, indent=2)
    print(f"\nBenchmark summary successfully saved to {BASE_DIR / 'benchmark_summary.json'}!")
    
    print("\n========================= FINAL MACRO RESULTS =========================")
    print(f"Base 1 (HQ raw logit) : Seen={macro['base1_hq']['seen']:.4f}, Unseen={macro['base1_hq']['unseen']:.4f}, Gap={macro['base1_hq']['gap']:.4f}, PairAcc={macro['base1_hq']['pair_acc']:.4f}")
    print(f"Base 2 (Release QD)   : Seen={macro['base2_release']['seen']:.4f}, Unseen={macro['base2_release']['unseen']:.4f}, Gap={macro['base2_release']['gap']:.4f}")
    print(f"DDV-Verifier          : Seen={macro['ddv']['seen']:.4f}, Unseen={macro['ddv']['unseen']:.4f}, Gap={macro['ddv']['gap']:.4f}, PairAcc={macro['ddv']['pair_acc']:.4f}")
    print(f"Gain vs Base 1: Unseen={macro['ddv']['gain_vs_b1']:+.4f} (95% CI: {bootstrap_results['vs_base1_hq']['unseen_gain_ci']}), Gap Reduction={macro['ddv']['gap_red_vs_b1']:+.4f}")
    print(f"Gain vs Base 2: Unseen={macro['ddv']['gain_vs_b2']:+.4f} (95% CI: {bootstrap_results['vs_base2_release']['unseen_gain_ci']}), Gap Reduction={macro['ddv']['gap_red_vs_b2']:+.4f}")
    print(f"Downstream Localization G-mIoU Unseen @1,3,5: {[round(v, 2) for v in macro['ddv']['gmiou_unseen']]}")
    print(f"Total pipeline completed in {time.time()-t_start:.2f}s.")

if __name__ == "__main__":
    main()
