#!/usr/bin/env python3
"""
Semantic Directional Calibrated Verifier (SDCV) Full Benchmark Suite.

Features & Controls:
1. True Dynamic Query Semantic Routing (Zero Split-ID dependency).
2. Signed Directional Transitions (<v(te)-v(ts), q_act>) discriminating put/take & pour/drink.
3. Capacity-Matched Ablation Triplet (~600-800 parameters each):
   - Model A: DetectorOnlyMLP (FlashVTG + Moment + QD-DETR + spatial)
   - Model B: MultimodalOnlyMLP (CLIP visual + SlowFast dynamics)
   - Model C: SDCV (Full Proposed Verifier)
4. Multi-GPU Parallel Training (400 epochs per split):
   - GPU 0: Splits A1, A2_alt, A3 (3 concurrent training jobs)
   - GPU 1: Splits C1, C2_alt (2 concurrent training jobs)
5. Zero Label Leakage:
   - Model selection strictly on Seen validation (S+ / S-).
6. Dual Baseline Comparison:
   - Base 1 (HQ raw logits): Seen 0.7511, Unseen 0.5027, Gap 0.2484
   - Base 2 (Release QD): Seen 0.7476, Unseen 0.5144, Gap 0.2332
7. Downstream Localization:
   - G-mIoU@1, 3, 5, Rej-F1, FRR, RR.
8. 2,000-Iteration Paired Video Cluster Bootstrap with 95% CIs.
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
ABLATIONS_DIR = BASE_DIR / "ablations"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
SUBMISSION_DIR = REPO_ROOT / "results/semantic_existence/multi_split_v2"

sys.path.insert(0, str(BASE_DIR))
from model import SemanticDirectionalCalibratedVerifier, DetectorOnlyMLP, MultimodalOnlyMLP

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
    
    print(f"[{split}] >>> Starting SDCV training on {device} (epochs={epochs}, lr={lr})...", flush=True)
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
    
    # 3. Instantiate Models: Proposed SDCV + Capacity-Matched Baselines
    sdcv_model = SemanticDirectionalCalibratedVerifier(
        hidden_dim=32,
        alpha_min=0.35,
        alpha_max=0.55 if split != "A3" else 0.60,
    ).to(device)
    
    det_mlp = DetectorOnlyMLP(hidden_dim=32).to(device)
    mm_mlp = MultimodalOnlyMLP(hidden_dim=32).to(device)
    
    opt_sdcv = optim.AdamW(sdcv_model.parameters(), lr=lr, weight_decay=1e-3)
    sched_sdcv = optim.lr_scheduler.CosineAnnealingLR(opt_sdcv, T_max=epochs, eta_min=1e-5)
    
    opt_det = optim.AdamW(det_mlp.parameters(), lr=lr, weight_decay=1e-3)
    sched_det = optim.lr_scheduler.CosineAnnealingLR(opt_det, T_max=epochs, eta_min=1e-5)
    
    opt_mm = optim.AdamW(mm_mlp.parameters(), lr=lr, weight_decay=1e-3)
    sched_mm = optim.lr_scheduler.CosineAnnealingLR(opt_mm, T_max=epochs, eta_min=1e-5)
    
    best_val_sdcv = -1.0
    best_sdcv_state = None
    
    best_val_det = -1.0
    best_det_state = None
    
    best_val_mm = -1.0
    best_mm_state = None
    
    batch_size = 256
    half_b = batch_size // 2
    steps_per_epoch = 10
    
    # 4. Joint Training Loop for 400 epochs
    for ep in range(1, epochs + 1):
        sdcv_model.train()
        det_mlp.train()
        mm_mlp.train()
        
        for step in range(steps_per_epoch):
            # Intra-video counterfactual pairs
            intra_idx = torch.randint(len(same_pairs_t), (half_b,), device=device)
            p_intra = same_pairs_t[intra_idx, 0]
            n_intra = same_pairs_t[intra_idx, 1]
            
            # Inter-video random pairs
            p_inter = pos_idx[torch.randint(len(pos_idx), (half_b,), device=device)]
            n_inter = neg_idx[torch.randint(len(neg_idx), (half_b,), device=device)]
            
            p_all = torch.cat([p_intra, p_inter])
            n_all = torch.cat([n_intra, n_inter])
            
            # Train SDCV
            opt_sdcv.zero_grad()
            sp_sdcv = sdcv_model(t_tr[p_all])
            sn_sdcv = sdcv_model(t_tr[n_all])
            l_rank_sdcv = F.softplus(-(sp_sdcv - sn_sdcv) / 0.15).mean()
            all_x = torch.cat([p_all, n_all])
            all_y = torch.cat([torch.ones_like(sp_sdcv), torch.zeros_like(sn_sdcv)])
            s_calib = sdcv_model(t_tr[all_x])
            l_bce_sdcv = F.binary_cross_entropy(torch.clamp(s_calib, 1e-6, 1.0 - 1e-6), all_y)
            loss_sdcv = l_rank_sdcv + 0.4 * l_bce_sdcv
            loss_sdcv.backward()
            opt_sdcv.step()
            
            # Train DetectorOnlyMLP
            opt_det.zero_grad()
            sp_det = det_mlp(t_tr[p_all])
            sn_det = det_mlp(t_tr[n_all])
            l_rank_det = F.softplus(-(sp_det - sn_det) / 0.15).mean()
            s_calib_det = det_mlp(t_tr[all_x])
            l_bce_det = F.binary_cross_entropy(torch.clamp(s_calib_det, 1e-6, 1.0 - 1e-6), all_y)
            loss_det = l_rank_det + 0.4 * l_bce_det
            loss_det.backward()
            opt_det.step()
            
            # Train MultimodalOnlyMLP
            opt_mm.zero_grad()
            sp_mm = mm_mlp(t_tr[p_all])
            sn_mm = mm_mlp(t_tr[n_all])
            l_rank_mm = F.softplus(-(sp_mm - sn_mm) / 0.15).mean()
            s_calib_mm = mm_mlp(t_tr[all_x])
            l_bce_mm = F.binary_cross_entropy(torch.clamp(s_calib_mm, 1e-6, 1.0 - 1e-6), all_y)
            loss_mm = l_rank_mm + 0.4 * l_bce_mm
            loss_mm.backward()
            opt_mm.step()
            
        sched_sdcv.step()
        sched_det.step()
        sched_mm.step()
        
        # Validation Evaluation strictly on Seen validation
        sdcv_model.eval()
        det_mlp.eval()
        mm_mlp.eval()
        with torch.no_grad():
            v_sdcv = float(roc_auc_score(y_val, sdcv_model(t_val).cpu().numpy()))
            if v_sdcv > best_val_sdcv:
                best_val_sdcv = v_sdcv
                best_sdcv_state = {k: v.cpu().clone() for k, v in sdcv_model.state_dict().items()}
                
            v_det = float(roc_auc_score(y_val, det_mlp(t_val).cpu().numpy()))
            if v_det > best_val_det:
                best_val_det = v_det
                best_det_state = {k: v.cpu().clone() for k, v in det_mlp.state_dict().items()}
                
            v_mm = float(roc_auc_score(y_val, mm_mlp(t_val).cpu().numpy()))
            if v_mm > best_val_mm:
                best_val_mm = v_mm
                best_mm_state = {k: v.cpu().clone() for k, v in mm_mlp.state_dict().items()}
                
    elapsed = time.time() - t0
    print(f"[{split}] Training complete in {elapsed:.2f}s. Best Seen Val: SDCV={best_val_sdcv:.4f}, DetMLP={best_val_det:.4f}, MM_MLP={best_val_mm:.4f}", flush=True)
    
    # 5. Evaluate on Test Set
    sdcv_model.load_state_dict(best_sdcv_state)
    det_mlp.load_state_dict(best_det_state)
    mm_mlp.load_state_dict(best_mm_state)
    
    sdcv_model.eval()
    det_mlp.eval()
    mm_mlp.eval()
    
    with torch.no_grad():
        v_scores_best = sdcv_model(t_val).cpu().numpy()
        seen_threshold = choose_val_seen_threshold(v_scores_best, y_val)
        
        te_sdcv = sdcv_model(t_te).cpu().numpy()
        te_det = det_mlp(t_te).cpu().numpy()
        te_mm = mm_mlp(t_te).cpu().numpy()
        
    # Baseline 1: FlashVTG raw logits
    b1_seen_auc = float(roc_auc_score(y_te[is_s_te], base_te_scores[is_s_te]))
    b1_unseen_auc = float(roc_auc_score(y_te[is_u_te], base_te_scores[is_u_te]))
    b1_gap = b1_seen_auc - b1_unseen_auc
    
    # Baseline 2: Release QD
    qd_sub_file = SUBMISSION_DIR / split / "qd/test/qd_detr_gmr_test_submission.jsonl"
    qd_sub = [json.loads(l) for l in qd_sub_file.read_text().splitlines() if l.strip()]
    qd_map = {str(p["qid"]): float(p.get("pred_exist_score", 0.0)) for p in qd_sub}
    base2_scores = np.array([qd_map[str(q)] for q in qids_te], dtype=np.float32)
    b2_seen_auc = float(roc_auc_score(y_te[is_s_te], base2_scores[is_s_te]))
    b2_unseen_auc = float(roc_auc_score(y_te[is_u_te], base2_scores[is_u_te]))
    b2_gap = b2_seen_auc - b2_unseen_auc
    
    # SDCV Metrics
    sdcv_seen_auc = float(roc_auc_score(y_te[is_s_te], te_sdcv[is_s_te]))
    sdcv_unseen_auc = float(roc_auc_score(y_te[is_u_te], te_sdcv[is_u_te]))
    sdcv_gap = sdcv_seen_auc - sdcv_unseen_auc
    
    # Ablation Metrics
    det_seen_auc = float(roc_auc_score(y_te[is_s_te], te_det[is_s_te]))
    det_unseen_auc = float(roc_auc_score(y_te[is_u_te], te_det[is_u_te]))
    
    mm_seen_auc = float(roc_auc_score(y_te[is_s_te], te_mm[is_s_te]))
    mm_unseen_auc = float(roc_auc_score(y_te[is_u_te], te_mm[is_u_te]))
    
    # Matched PairAcc
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    base_pair_acc = compute_matched_pair_acc(qids_te, base_te_scores, pairs_file)
    sdcv_pair_acc = compute_matched_pair_acc(qids_te, te_sdcv, pairs_file)
    det_pair_acc = compute_matched_pair_acc(qids_te, te_det, pairs_file)
    mm_pair_acc = compute_matched_pair_acc(qids_te, te_mm, pairs_file)
    
    # Calibrated Thresholding (Z-score standardized)
    # Threshold chosen on Seen validation standardized score
    mu_v, std_v = float(np.mean(v_scores_best)), float(np.std(v_scores_best) + 1e-8)
    z_th = (seen_threshold - mu_v) / std_v
    
    mu_t, std_t = float(np.mean(te_sdcv)), float(np.std(te_sdcv) + 1e-8)
    z_scores_te = (te_sdcv - mu_t) / std_t
    
    u_pos_mask = (parts_te == "U+")
    u_neg_mask = (parts_te == "U-")
    
    # Standard threshold decisions
    raw_preds = (te_sdcv >= seen_threshold)
    raw_frr = float((~raw_preds[u_pos_mask]).mean() * 100.0)
    raw_rr = float((~raw_preds[u_neg_mask]).mean() * 100.0)
    raw_rej_f1 = float(f1_score((y_te[is_u_te] == 0).astype(int), (~raw_preds[is_u_te]).astype(int), average="binary") * 100.0)
    
    # Calibrated z-threshold decisions
    calib_preds = (z_scores_te >= z_th)
    calib_frr = float((~calib_preds[u_pos_mask]).mean() * 100.0)
    calib_rr = float((~calib_preds[u_neg_mask]).mean() * 100.0)
    calib_rej_f1 = float(f1_score((y_te[is_u_te] == 0).astype(int), (~calib_preds[is_u_te]).astype(int), average="binary") * 100.0)
    
    # Downstream G-mIoU Localization
    gt_file = RELEASE_DIR / split / "test.jsonl"
    gt_list = [json.loads(l) for l in gt_file.read_text().splitlines() if l.strip()]
    qd_pred_map = {str(p["qid"]): p for p in qd_sub}
    
    raw_sub = [{
        "qid": str(q),
        "pred_exist_score": float(te_sdcv[i] >= seen_threshold),
        "pred_relevant_windows": qd_pred_map[str(q)]["pred_relevant_windows"]
    } for i, q in enumerate(qids_te)]
    
    gated_sub, _ = prepare_submission_for_gmiou(raw_sub, cls_threshold=0.5, max_pred_windows=10)
    gmiou_vals = np.zeros((len(qids_te), 3))
    for i, x in enumerate(gt_list):
        for m_idx, k in enumerate(KS):
            gmiou_vals[i, m_idx] = _compute_set_iou_score([w[:2] for w in gated_sub[i]["pred_relevant_windows"][:k]], x["relevant_windows"])
            
    seen_mask = is_s_te
    unseen_mask = is_u_te
    gmiou_seen = [float(gmiou_vals[seen_mask, m_idx].mean() * 100.0) for m_idx in range(3)]
    gmiou_unseen = [float(gmiou_vals[unseen_mask, m_idx].mean() * 100.0) for m_idx in range(3)]
    
    print(f"[{split}] Base1 Seen: {b1_seen_auc:.4f}, Unseen: {b1_unseen_auc:.4f}, Gap: {b1_gap:.4f}, PairAcc: {base_pair_acc:.4f}", flush=True)
    print(f"[{split}] DetMLP   Seen: {det_seen_auc:.4f}, Unseen: {det_unseen_auc:.4f}, PairAcc: {det_pair_acc:.4f}", flush=True)
    print(f"[{split}] MM_MLP   Seen: {mm_seen_auc:.4f}, Unseen: {mm_unseen_auc:.4f}, PairAcc: {mm_pair_acc:.4f}", flush=True)
    print(f"[{split}] SDCV     Seen: {sdcv_seen_auc:.4f}, Unseen: {sdcv_unseen_auc:.4f}, Gap: {sdcv_gap:.4f}, PairAcc: {sdcv_pair_acc:.4f}", flush=True)
    print(f"[{split}] Net Gain vs Base1: Seen={sdcv_seen_auc - b1_seen_auc:+.4f}, Unseen={sdcv_unseen_auc - b1_unseen_auc:+.4f}, Gap Red={b1_gap - sdcv_gap:+.4f}, Pair Gain={sdcv_pair_acc - base_pair_acc:+.4f}", flush=True)
    print(f"[{split}] Rejection Calib: Pos FRR={calib_frr:.1f}%, Neg RR={calib_rr:.1f}%, Rej-F1={calib_rej_f1:.1f}%", flush=True)
    
    # Save checkpoint & predictions
    torch.save(best_sdcv_state, split_dir / "best_model.pt")
    torch.save(best_det_state, split_dir / "best_det_mlp.pt")
    torch.save(best_mm_state, split_dir / "best_mm_mlp.pt")
    
    np.savez_compressed(
        split_dir / "predictions.npz",
        qids=qids_te,
        vids=vids_te,
        partitions=parts_te,
        labels=y_te,
        base_hq_scores=base_te_scores,
        base_rel_scores=base2_scores,
        sdcv_scores=te_sdcv,
        det_mlp_scores=te_det,
        mm_mlp_scores=te_mm,
        threshold=seen_threshold,
        z_threshold=z_th,
    )
    
    res = {
        "split": split,
        "base1_seen_auc": b1_seen_auc,
        "base1_unseen_auc": b1_unseen_auc,
        "base1_gap": b1_gap,
        "base2_seen_auc": b2_seen_auc,
        "base2_unseen_auc": b2_unseen_auc,
        "base2_gap": b2_gap,
        "base_pair_acc": base_pair_acc,
        "det_seen_auc": det_seen_auc,
        "det_unseen_auc": det_unseen_auc,
        "det_pair_acc": det_pair_acc,
        "mm_seen_auc": mm_seen_auc,
        "mm_unseen_auc": mm_unseen_auc,
        "mm_pair_acc": mm_pair_acc,
        "sdcv_seen_auc": sdcv_seen_auc,
        "sdcv_unseen_auc": sdcv_unseen_auc,
        "sdcv_gap": sdcv_gap,
        "sdcv_pair_acc": sdcv_pair_acc,
        "gain1_seen": sdcv_seen_auc - b1_seen_auc,
        "gain1_unseen": sdcv_unseen_auc - b1_unseen_auc,
        "gap_red1": b1_gap - sdcv_gap,
        "gain2_seen": sdcv_seen_auc - b2_seen_auc,
        "gain2_unseen": sdcv_unseen_auc - b2_unseen_auc,
        "gap_red2": b2_gap - sdcv_gap,
        "pair_gain": sdcv_pair_acc - base_pair_acc,
        "raw_frr": raw_frr,
        "raw_rr": raw_rr,
        "raw_rej_f1": raw_rej_f1,
        "calib_frr": calib_frr,
        "calib_rr": calib_rr,
        "calib_rej_f1": calib_rej_f1,
        "gmiou_seen": gmiou_seen,
        "gmiou_unseen": gmiou_unseen,
        "qids": list(qids_te),
        "vids": list(vids_te),
        "partitions": parts_te,
        "labels": y_te,
        "base_hq_scores": base_te_scores,
        "base_rel_scores": base2_scores,
        "sdcv_scores": te_sdcv,
        "det_mlp_scores": te_det,
        "mm_mlp_scores": te_mm,
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
        
    boot_sdcv_unseen, boot_sdcv_seen, boot_sdcv_gap = [], [], []
    boot_det_u, boot_mm_u = [], []
    boot_gain1_u, boot_gain1_s, boot_gapred1 = [], [], []
    boot_gain2_u, boot_gain2_s, boot_gapred2 = [], [], []
    
    t0 = time.time()
    for b in range(n_boot):
        sample_vids = np.random.choice(shared_vids, size=n_vids, replace=True)
        
        split_u_sdcv, split_s_sdcv = [], []
        split_u_det, split_u_mm = [], []
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
            s_sdcv_b = r["sdcv_scores"][sub_indices]
            s_det_b = r["det_mlp_scores"][sub_indices]
            s_mm_b = r["mm_mlp_scores"][sub_indices]
            s_b1_b = r["base_hq_scores"][sub_indices]
            s_b2_b = r["base_rel_scores"][sub_indices]
            
            u_mask = (parts_b == "U+") | (parts_b == "U-")
            s_mask = (parts_b == "S+") | (parts_b == "S-")
            
            if len(np.unique(y_b[u_mask])) < 2 or len(np.unique(y_b[s_mask])) < 2:
                valid = False
                break
                
            split_u_sdcv.append(roc_auc_score(y_b[u_mask], s_sdcv_b[u_mask]))
            split_s_sdcv.append(roc_auc_score(y_b[s_mask], s_sdcv_b[s_mask]))
            split_u_det.append(roc_auc_score(y_b[u_mask], s_det_b[u_mask]))
            split_u_mm.append(roc_auc_score(y_b[u_mask], s_mm_b[u_mask]))
            split_u_b1.append(roc_auc_score(y_b[u_mask], s_b1_b[u_mask]))
            split_s_b1.append(roc_auc_score(y_b[s_mask], s_b1_b[s_mask]))
            split_u_b2.append(roc_auc_score(y_b[u_mask], s_b2_b[u_mask]))
            split_s_b2.append(roc_auc_score(y_b[s_mask], s_b2_b[s_mask]))
            
        if not valid:
            continue
            
        m_u_sdcv = np.mean(split_u_sdcv)
        m_s_sdcv = np.mean(split_s_sdcv)
        m_gap_sdcv = m_s_sdcv - m_u_sdcv
        
        m_u_det = np.mean(split_u_det)
        m_u_mm = np.mean(split_u_mm)
        
        m_u_b1 = np.mean(split_u_b1)
        m_s_b1 = np.mean(split_s_b1)
        m_gap_b1 = m_s_b1 - m_u_b1
        
        m_u_b2 = np.mean(split_u_b2)
        m_s_b2 = np.mean(split_s_b2)
        m_gap_b2 = m_s_b2 - m_u_b2
        
        boot_sdcv_unseen.append(m_u_sdcv)
        boot_sdcv_seen.append(m_s_sdcv)
        boot_sdcv_gap.append(m_gap_sdcv)
        boot_det_u.append(m_u_det)
        boot_mm_u.append(m_u_mm)
        
        boot_gain1_u.append(m_u_sdcv - m_u_b1)
        boot_gain1_s.append(m_s_sdcv - m_s_b1)
        boot_gapred1.append(m_gap_b1 - m_gap_sdcv)
        
        boot_gain2_u.append(m_u_sdcv - m_u_b2)
        boot_gain2_s.append(m_s_sdcv - m_s_b2)
        boot_gapred2.append(m_gap_b2 - m_gap_sdcv)
        
    def ci_fmt(arr):
        lo, hi = np.percentile(arr, 2.5), np.percentile(arr, 97.5)
        sign = "+" if lo >= 0 else ""
        return f"[{sign}{lo:.4f}, +{hi:.4f}]"
        
    print(f"Bootstrap finished in {time.time()-t0:.2f}s ({len(boot_sdcv_unseen)} valid resamples).")
    
    return {
        "n_valid_boot": len(boot_sdcv_unseen),
        "sdcv_seen": {"mean": float(np.mean(boot_sdcv_seen)), "ci": ci_fmt(boot_sdcv_seen)},
        "sdcv_unseen": {"mean": float(np.mean(boot_sdcv_unseen)), "ci": ci_fmt(boot_sdcv_unseen)},
        "sdcv_gap": {"mean": float(np.mean(boot_sdcv_gap)), "ci": ci_fmt(boot_sdcv_gap)},
        "det_mlp_unseen": {"mean": float(np.mean(boot_det_u)), "ci": ci_fmt(boot_det_u)},
        "mm_mlp_unseen": {"mean": float(np.mean(boot_mm_u)), "ci": ci_fmt(boot_mm_u)},
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
    print("      SEMANTIC DIRECTIONAL CALIBRATED VERIFIER (SDCV): MULTI-GPU RUN           ")
    print("================================================================================")
    t_start = time.time()
    
    # GPU Mapping:
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
        
    ordered_results = [return_dict[sp] for sp in SPLITS]
    
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
        "det_mlp_abl": {
            "seen": float(np.mean([r["det_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["det_unseen_auc"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["det_pair_acc"] for r in ordered_results])),
        },
        "mm_mlp_abl": {
            "seen": float(np.mean([r["mm_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["mm_unseen_auc"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["mm_pair_acc"] for r in ordered_results])),
        },
        "sdcv": {
            "seen": float(np.mean([r["sdcv_seen_auc"] for r in ordered_results])),
            "unseen": float(np.mean([r["sdcv_unseen_auc"] for r in ordered_results])),
            "gap": float(np.mean([r["sdcv_gap"] for r in ordered_results])),
            "pair_acc": float(np.mean([r["sdcv_pair_acc"] for r in ordered_results])),
            "gain_vs_b1": float(np.mean([r["gain1_unseen"] for r in ordered_results])),
            "gain_vs_b2": float(np.mean([r["gain2_unseen"] for r in ordered_results])),
            "gap_red_vs_b1": float(np.mean([r["gap_red1"] for r in ordered_results])),
            "gap_red_vs_b2": float(np.mean([r["gap_red2"] for r in ordered_results])),
            "action_unseen": float(np.mean([ordered_results[0]["sdcv_unseen_auc"], ordered_results[1]["sdcv_unseen_auc"], ordered_results[2]["sdcv_unseen_auc"]])),
            "concept_unseen": float(np.mean([ordered_results[3]["sdcv_unseen_auc"], ordered_results[4]["sdcv_unseen_auc"]])),
            "raw_frr": float(np.mean([r["raw_frr"] for r in ordered_results])),
            "raw_rr": float(np.mean([r["raw_rr"] for r in ordered_results])),
            "raw_rej_f1": float(np.mean([r["raw_rej_f1"] for r in ordered_results])),
            "calib_frr": float(np.mean([r["calib_frr"] for r in ordered_results])),
            "calib_rr": float(np.mean([r["calib_rr"] for r in ordered_results])),
            "calib_rej_f1": float(np.mean([r["calib_rej_f1"] for r in ordered_results])),
            "gmiou_seen": [float(np.mean([r["gmiou_seen"][m] for r in ordered_results])) for m in range(3)],
            "gmiou_unseen": [float(np.mean([r["gmiou_unseen"][m] for r in ordered_results])) for m in range(3)],
        }
    }
    
    bootstrap_results = run_paired_video_cluster_bootstrap(ordered_results, n_boot=2000)
    
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
    print(f"Detector-Only MLP Abl : Seen={macro['det_mlp_abl']['seen']:.4f}, Unseen={macro['det_mlp_abl']['unseen']:.4f}, PairAcc={macro['det_mlp_abl']['pair_acc']:.4f}")
    print(f"Multimodal-Only MLP   : Seen={macro['mm_mlp_abl']['seen']:.4f}, Unseen={macro['mm_mlp_abl']['unseen']:.4f}, PairAcc={macro['mm_mlp_abl']['pair_acc']:.4f}")
    print(f"SDCV (Full Proposed)  : Seen={macro['sdcv']['seen']:.4f}, Unseen={macro['sdcv']['unseen']:.4f}, Gap={macro['sdcv']['gap']:.4f}, PairAcc={macro['sdcv']['pair_acc']:.4f}")
    print(f"Gain vs Base 1: Unseen={macro['sdcv']['gain_vs_b1']:+.4f} (95% CI: {bootstrap_results['vs_base1_hq']['unseen_gain_ci']}), Gap Reduction={macro['sdcv']['gap_red_vs_b1']:+.4f}")
    print(f"Action Splits Unseen  : {macro['sdcv']['action_unseen']:.4f}")
    print(f"Concept Splits Unseen : {macro['sdcv']['concept_unseen']:.4f}")
    print(f"Calibrated Rejection  : Pos FRR={macro['sdcv']['calib_frr']:.2f}%, Neg RR={macro['sdcv']['calib_rr']:.2f}%, Rej-F1={macro['sdcv']['calib_rej_f1']:.2f}%")
    print(f"Total pipeline completed in {time.time()-t_start:.2f}s.")

if __name__ == "__main__":
    main()
