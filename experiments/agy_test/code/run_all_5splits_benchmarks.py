#!/usr/bin/env python3
"""
Comprehensive 5-split benchmark runner across QD, Moment, and FlashVTG.
Evaluates:
  1. Canonical Baseline (GMR Adapter)
  2. Old Window Verifier (Bilinear skip)
  3. FGD-Verifier (Foreground-Gated De-biased Verifier)
  4. FGD-Ensemble (Calibrated alpha * global + (1-alpha) * local)
  5. Shuffled-Video Dependency Control

All model selection and calibration strictly on Seen validation.
Single seed (default: 3407).
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn
import torch.nn.functional as F

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO))

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_auc(y_true, y_score):
    try:
        y = np.asarray(y_true, dtype=np.int8)
        s = np.asarray(y_score, dtype=np.float64)
        if len(np.unique(y)) < 2:
            return 0.5
        return float(roc_auc_score(y, s))
    except Exception:
        return 0.5

def youden_threshold(y_true, y_score):
    y_true = np.asarray(y_true, dtype=bool)
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float(np.median(y_score))
    
    thresholds = np.unique(y_score)
    if len(thresholds) > 1000:
        thresholds = np.quantile(y_score, np.linspace(0, 1, 1000))
    best_j, best_th = -1.0, float(thresholds[0])
    for th in thresholds:
        pred = y_score >= th
        tpr = (pred & y_true).sum() / n_pos
        fpr = (pred & ~y_true).sum() / n_neg
        j = tpr - fpr
        if j > best_j:
            best_j = j
            best_th = float(th)
    return best_th

def same_query_pair_acc(scores, labels, queries):
    """Pairwise accuracy for queries that appear in both positive and negative instances."""
    groups = {}
    for i, q in enumerate(queries):
        groups.setdefault(q, []).append(i)
    accs, counts = [], []
    for q, idxs in groups.items():
        pos = [i for i in idxs if labels[i] == 1]
        neg = [i for i in idxs if labels[i] == 0]
        if not pos or not neg:
            continue
        vals = [1.0 if scores[p] > scores[n] else 0.5 if scores[p] == scores[n] else 0.0 for p in pos for n in neg]
        accs.append(float(np.mean(vals)))
        counts.append(len(vals))
    macro = float(np.mean(accs)) if accs else 0.5
    weighted = float(np.average(accs, weights=counts)) if accs else 0.5
    return {"macro_pair_acc": macro, "weighted_pair_acc": weighted, "pairs": int(sum(counts)), "queries": len(accs)}

def matched_source_pair_acc(scores, qids, split):
    """Evaluate same-video matched source pairs from release/semantic_existence_v2/{split}/matched_u_pairs.jsonl."""
    pairs_file = REPO / f"data/release/semantic_existence_v2/{split}/matched_u_pairs.jsonl"
    if not pairs_file.exists():
        return {"matched_pair_acc": None, "pairs_evaluated": 0}
    pairs = [json.loads(line) for line in pairs_file.read_text().splitlines() if line.strip()]
    qid_to_score = {str(q): float(s) for q, s in zip(qids, scores)}
    accs = []
    for p in pairs:
        pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
        if pq in qid_to_score and nq in qid_to_score:
            sp = qid_to_score[pq]
            sn = qid_to_score[nq]
            accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    acc = float(np.mean(accs)) if accs else 0.5
    return {"matched_pair_acc": acc, "pairs_evaluated": len(accs)}

def eval_detection_and_gating(rows, labels, spans_xx, fg_scores, exist_scores, threshold):
    raw_hits, gated_hits = [], []
    raw_correct_refused, raw_correct_total = 0, 0
    for i, row in enumerate(rows):
        if row.get("label", row.get("exist_label", 0)) != 1:
            continue
        dur = float(row["duration"])
        gt_wins = row.get("gt_windows", row.get("relevant_windows", []))
        top1_k = int(np.argmax(fg_scores[i]))
        t_st, t_ed = spans_xx[i, top1_k] * dur
        best_iou = 0.0
        for gw in gt_wins:
            gst, ged = float(gw[0]), float(gw[1])
            inter = max(0.0, min(t_ed, ged) - max(t_st, gst))
            union = max(1e-12, t_ed - t_st + ged - gst - inter)
            best_iou = max(best_iou, inter / union)
        hit = best_iou >= 0.5
        raw_hits.append(float(hit))
        accepted = exist_scores[i] >= threshold
        gated_hits.append(float(hit and accepted))
        if hit:
            raw_correct_total += 1
            if not accepted:
                raw_correct_refused += 1

    raw_r1 = float(np.mean(raw_hits)) if raw_hits else 0.0
    gated_r1 = float(np.mean(gated_hits)) if gated_hits else 0.0
    frr_raw_correct = (raw_correct_refused / raw_correct_total) if raw_correct_total > 0 else 0.0

    neg_accepted, neg_total = 0, 0
    for i, row in enumerate(rows):
        if row.get("label", row.get("exist_label", 0)) == 0:
            neg_total += 1
            if exist_scores[i] >= threshold:
                neg_accepted += 1
    neg_rejection = (1.0 - neg_accepted / neg_total) if neg_total > 0 else 0.0
    pos_total = len(raw_hits)
    pos_refused = sum(1 for i, row in enumerate(rows) if row.get("label", row.get("exist_label", 0)) == 1 and exist_scores[i] < threshold)
    frr_all = (pos_refused / pos_total) if pos_total > 0 else 0.0

    return {
        "raw_R1@0.5": raw_r1 * 100.0,
        "gated_R1@0.5": gated_r1 * 100.0,
        "raw_correct_false_refusal": frr_raw_correct * 100.0,
        "U_pos_FRR": frr_all * 100.0,
        "U_neg_RR": neg_rejection * 100.0,
    }

class OldWindowVerifier(nn.Module):
    def __init__(self, hidden: int = 85):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(768, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor, fg: torch.Tensor = None) -> torch.Tensor:
        q_exp = q[:, None, :].expand_as(v)
        feat = torch.cat([q_exp, v, q_exp * v], dim=-1)
        scores = self.mlp(feat).squeeze(-1)
        return scores.masked_fill(~mask, -1e4).amax(dim=1)

class FGDeBiasedVerifier(nn.Module):
    """
    Foreground-Gated De-biased Verifier:
    - No direct query text skip connection.
    - Bilinear cross-modal interaction: hq * hv.
    - Gated by foreground detector log-odds.
    - Smooth LogSumExp aggregation across proposals.
    """
    def __init__(self, dim: int = 256, hidden: int = 64):
        super().__init__()
        self.proj_q = nn.Linear(dim, hidden)
        self.proj_v = nn.Linear(dim, hidden)
        self.net = nn.Sequential(
            nn.Linear(hidden * 2, hidden),
            nn.LayerNorm(hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1)
        )
        self.temp = nn.Parameter(torch.ones(1) * 2.0)
        self.fg_weight = nn.Parameter(torch.ones(1) * 1.0)

    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor, fg: torch.Tensor) -> torch.Tensor:
        hq = self.proj_q(q)[:, None, :]  # [B, 1, H]
        hv = self.proj_v(v)              # [B, K, H]
        interaction = hq * hv           # [B, K, H]
        feat = torch.cat([interaction, hv], dim=-1) # [B, K, 2H]
        evidence = self.net(feat).squeeze(-1)       # [B, K]

        # fg is already probability in [0, 1]
        fg_prob = torch.clamp(fg, min=1e-6, max=1.0)
        log_fg = torch.log(fg_prob)
        gated_evidence = evidence + self.fg_weight * log_fg
        gated_evidence = gated_evidence.masked_fill(~mask, -1e4)

        # Smooth LogSumExp pooling
        tau = torch.clamp(self.temp, min=0.5, max=5.0)
        pooled = tau * torch.logsumexp(gated_evidence / tau, dim=1)
        return pooled

def train_and_eval_model(model_cls, model_kwargs, train_data, seen_data, u_data, device, epochs=15, lr=1e-4, batch_size=64):
    model = model_cls(**model_kwargs).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    criterion = nn.BCEWithLogitsLoss()

    train_q = torch.tensor(train_data["query_mean"], dtype=torch.float32, device=device)
    train_v = torch.tensor(train_data["local_video"], dtype=torch.float32, device=device)
    train_m = torch.tensor(train_data["candidate_mask"], dtype=torch.bool, device=device)
    train_fg = torch.tensor(train_data["foreground_scores"], dtype=torch.float32, device=device)
    train_y = torch.tensor(train_data["labels"], dtype=torch.float32, device=device)
    n_train = len(train_y)

    seen_q = torch.tensor(seen_data["query_mean"], dtype=torch.float32, device=device)
    seen_v = torch.tensor(seen_data["local_video"], dtype=torch.float32, device=device)
    seen_m = torch.tensor(seen_data["candidate_mask"], dtype=torch.bool, device=device)
    seen_fg = torch.tensor(seen_data["foreground_scores"], dtype=torch.float32, device=device)
    seen_y = seen_data["labels"]

    u_q = torch.tensor(u_data["query_mean"], dtype=torch.float32, device=device)
    u_v = torch.tensor(u_data["local_video"], dtype=torch.float32, device=device)
    u_m = torch.tensor(u_data["candidate_mask"], dtype=torch.bool, device=device)
    u_fg = torch.tensor(u_data["foreground_scores"], dtype=torch.float32, device=device)
    u_y = u_data["labels"]

    best_seen_auc = -1.0
    best_state = None

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n_train, device=device)
        for i in range(0, n_train, batch_size):
            idx = perm[i:i + batch_size]
            logits = model(train_q[idx], train_v[idx], train_m[idx], train_fg[idx])
            loss = criterion(logits, train_y[idx])
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        model.eval()
        with torch.no_grad():
            s_logits = model(seen_q, seen_v, seen_m, seen_fg).cpu().numpy()
            s_auc = compute_auc(seen_y, s_logits)
            if s_auc > best_seen_auc:
                best_seen_auc = s_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        seen_scores = model(seen_q, seen_v, seen_m, seen_fg).cpu().numpy()
        u_scores = model(u_q, u_v, u_m, u_fg).cpu().numpy()

        # Shuffled video control (permutation test)
        u_v_perm = u_v[torch.randperm(len(u_v))]
        u_m_perm = u_m[torch.randperm(len(u_m))]
        u_fg_perm = u_fg[torch.randperm(len(u_fg))]
        shuffled_u_scores = model(u_q, u_v_perm, u_m_perm, u_fg_perm).cpu().numpy()

    return {
        "best_seen_auc": float(best_seen_auc),
        "seen_scores": seen_scores,
        "u_scores": u_scores,
        "shuffled_u_scores": shuffled_u_scores,
        "state_dict": best_state,
    }

def run_single_setting(split: str, backbone: str, device_str: str, seed: int = 3407):
    set_seed(seed)
    device = torch.device(device_str)

    feat_dir = AGY_TEST / f"cache/features/{split}/{backbone}"
    train_npz = np.load(feat_dir / "train.npz")
    seen_npz = np.load(feat_dir / "seen.npz")
    u_npz = np.load(feat_dir / "u.npz")

    # Load jsonl metadata for duration & gt_windows
    u_meta_file = feat_dir / "u.jsonl"
    u_rows = [json.loads(l) for l in u_meta_file.read_text().splitlines() if l.strip()]

    # 1. Baseline Canonical Evaluation
    s_labels = seen_npz["labels"]
    u_labels = u_npz["labels"]
    s_base_scores = seen_npz["original_exist_logits"]
    u_base_scores = u_npz["original_exist_logits"]
    u_qids = [str(q) for q in u_npz["qids"]]
    u_queries = [r["query"] for r in u_rows]

    s_base_auc = compute_auc(s_labels, s_base_scores)
    base_th = youden_threshold(s_labels, s_base_scores)
    u_base_auc = compute_auc(u_labels, u_base_scores)
    base_same_q = same_query_pair_acc(u_base_scores, u_labels, u_queries)
    base_matched = matched_source_pair_acc(u_base_scores, u_qids, split)
    base_det = eval_detection_and_gating(u_rows, u_labels, u_npz["spans_xx"], u_npz["foreground_scores"], u_base_scores, base_th)

    baseline_res = {
        "seen_AUROC": s_base_auc,
        "unseen_AUROC": u_base_auc,
        "seen_unseen_gap": s_base_auc - u_base_auc,
        "matched_pair_acc": base_matched["matched_pair_acc"],
        "same_query_pair_acc": base_same_q["macro_pair_acc"],
        "seen_threshold": float(base_th),
        **base_det,
    }

    # 2. Train Old Window Verifier
    old_res = train_and_eval_model(OldWindowVerifier, {"hidden": 85}, train_npz, seen_npz, u_npz, device, epochs=15, lr=1e-4)
    old_th = youden_threshold(s_labels, old_res["seen_scores"])
    old_u_auc = compute_auc(u_labels, old_res["u_scores"])
    old_shuffled_auc = compute_auc(u_labels, old_res["shuffled_u_scores"])
    old_same_q = same_query_pair_acc(old_res["u_scores"], u_labels, u_queries)
    old_matched = matched_source_pair_acc(old_res["u_scores"], u_qids, split)
    old_det = eval_detection_and_gating(u_rows, u_labels, u_npz["spans_xx"], u_npz["foreground_scores"], old_res["u_scores"], old_th)

    old_verifier_metrics = {
        "seen_AUROC": old_res["best_seen_auc"],
        "unseen_AUROC": old_u_auc,
        "seen_unseen_gap": old_res["best_seen_auc"] - old_u_auc,
        "shuffled_video_AUROC": old_shuffled_auc,
        "matched_pair_acc": old_matched["matched_pair_acc"],
        "same_query_pair_acc": old_same_q["macro_pair_acc"],
        "seen_threshold": float(old_th),
        **old_det,
    }

    # 3. Train FGD-Verifier (Ours)
    fgd_res = train_and_eval_model(FGDeBiasedVerifier, {"dim": 256, "hidden": 64}, train_npz, seen_npz, u_npz, device, epochs=15, lr=1e-4)
    fgd_th = youden_threshold(s_labels, fgd_res["seen_scores"])
    fgd_u_auc = compute_auc(u_labels, fgd_res["u_scores"])
    fgd_shuffled_auc = compute_auc(u_labels, fgd_res["shuffled_u_scores"])
    fgd_same_q = same_query_pair_acc(fgd_res["u_scores"], u_labels, u_queries)
    fgd_matched = matched_source_pair_acc(fgd_res["u_scores"], u_qids, split)
    fgd_det = eval_detection_and_gating(u_rows, u_labels, u_npz["spans_xx"], u_npz["foreground_scores"], fgd_res["u_scores"], fgd_th)

    fgd_metrics = {
        "seen_AUROC": fgd_res["best_seen_auc"],
        "unseen_AUROC": fgd_u_auc,
        "seen_unseen_gap": fgd_res["best_seen_auc"] - fgd_u_auc,
        "shuffled_video_AUROC": fgd_shuffled_auc,
        "matched_pair_acc": fgd_matched["matched_pair_acc"],
        "same_query_pair_acc": fgd_same_q["macro_pair_acc"],
        "seen_threshold": float(fgd_th),
        **fgd_det,
    }

    # 4. Calibrated Ensemble (alpha * global + (1 - alpha) * local)
    # Calibrate alpha strictly on Seen validation!
    best_ens_alpha = 0.5
    best_ens_seen_auc = -1.0
    for a in np.linspace(0.0, 1.0, 11):
        combo_seen = a * s_base_scores + (1.0 - a) * fgd_res["seen_scores"]
        auc = compute_auc(s_labels, combo_seen)
        if auc > best_ens_seen_auc:
            best_ens_seen_auc = auc
            best_ens_alpha = float(a)

    ens_seen_scores = best_ens_alpha * s_base_scores + (1.0 - best_ens_alpha) * fgd_res["seen_scores"]
    ens_u_scores = best_ens_alpha * u_base_scores + (1.0 - best_ens_alpha) * fgd_res["u_scores"]
    ens_th = youden_threshold(s_labels, ens_seen_scores)
    ens_u_auc = compute_auc(u_labels, ens_u_scores)
    ens_same_q = same_query_pair_acc(ens_u_scores, u_labels, u_queries)
    ens_matched = matched_source_pair_acc(ens_u_scores, u_qids, split)
    ens_det = eval_detection_and_gating(u_rows, u_labels, u_npz["spans_xx"], u_npz["foreground_scores"], ens_u_scores, ens_th)

    ensemble_metrics = {
        "optimal_seen_alpha": best_ens_alpha,
        "seen_AUROC": best_ens_seen_auc,
        "unseen_AUROC": ens_u_auc,
        "seen_unseen_gap": best_ens_seen_auc - ens_u_auc,
        "matched_pair_acc": ens_matched["matched_pair_acc"],
        "same_query_pair_acc": ens_same_q["macro_pair_acc"],
        "seen_threshold": float(ens_th),
        **ens_det,
    }

    # Save checkpoint
    ckpt_dir = AGY_TEST / f"checkpoints/{split}/{backbone}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    torch.save(fgd_res["state_dict"], ckpt_dir / "fgd_verifier.pt")

    result = {
        "split": split,
        "backbone": backbone,
        "seed": seed,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "baseline_canonical": baseline_res,
        "old_window_verifier": old_verifier_metrics,
        "fgd_verifier": fgd_metrics,
        "fgd_ensemble": ensemble_metrics,
        "summary": {
            "delta_U_AUROC_vs_baseline": fgd_metrics["unseen_AUROC"] - baseline_res["unseen_AUROC"],
            "delta_U_AUROC_ens_vs_baseline": ensemble_metrics["unseen_AUROC"] - baseline_res["unseen_AUROC"],
            "gap_reduction_pp": (baseline_res["seen_unseen_gap"] - ensemble_metrics["seen_unseen_gap"]) * 100.0,
            "delta_matched_pair_acc": (ensemble_metrics["matched_pair_acc"] or 0.0) - (baseline_res["matched_pair_acc"] or 0.0),
            "delta_same_q_pair_acc": ensemble_metrics["same_query_pair_acc"] - baseline_res["same_query_pair_acc"],
            "delta_U_neg_RR": ensemble_metrics["U_neg_RR"] - baseline_res["U_neg_RR"],
            "delta_gated_R1": ensemble_metrics["gated_R1@0.5"] - baseline_res["gated_R1@0.5"],
        }
    }
    
    print(f"[{split}/{backbone}] Done! Base U: {baseline_res['unseen_AUROC']:.4f} -> FGD: {fgd_metrics['unseen_AUROC']:.4f} -> Ens: {ensemble_metrics['unseen_AUROC']:.4f} | Ens Gap: {ensemble_metrics['seen_unseen_gap']:.4f} (was {baseline_res['seen_unseen_gap']:.4f})", flush=True)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="all")
    parser.add_argument("--backbone", default="all")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--output_file", default=str(AGY_TEST / "report/BENCHMARK_RESULTS.json"))
    args = parser.parse_args()

    splits = ["A1", "A2_alt", "A3", "C1", "C2_alt"] if args.split == "all" else [args.split]
    backbones = ["qd", "moment", "flash"] if args.backbone == "all" else [args.backbone]

    results = []
    for sp in splits:
        for bb in backbones:
            print(f"\n================ Running {sp} / {bb} on {args.device} (seed {args.seed}) ================", flush=True)
            res = run_single_setting(sp, bb, args.device, args.seed)
            results.append(res)

    out_p = Path(args.output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved {len(results)} benchmark results to {out_p}")

if __name__ == "__main__":
    main()
