#!/usr/bin/env python3
"""
Decomposed Action-Object Verifier (DAO-Verifier) Training & Evaluation Pipeline.

Strict Protocol Compliance:
- Zero edits to original repo code.
- Isolated directory: experiments/agy_test/decomposed_action_object_verifier/
- Single seed: 3407.
- Training strictly on Seen data (train S+/S-).
- Checkpoint selection strictly on Seen validation (val S+/S-) maximizing Seen Val AUROC.
- Threshold selection strictly on Seen validation (val S+/S-) maximizing balanced accuracy.
- Evaluation on full test set (Seen S+/S- and Unseen U+/U-).
- Paired video cluster bootstrap confidence intervals (2,000 resamples).
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
FEATURES_DIR = BASE_DIR / "clean_features"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
AUDIT_DIR = REPO_ROOT / "experiments/agy_test/audit_20261005"
RUNS_DIR = BASE_DIR / "clean_runs"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(AUDIT_DIR))
sys.path.insert(0, str(BASE_DIR))

from audit_results import prepared_auc
from model import DecomposedActionObjectVerifier

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

BASELINE_OFFICIAL = {
    "published_rounded": {
        "A1": {"Seen": 0.7827, "Unseen": 0.5058, "Gap": 0.2769, "PairAcc": 0.5721},
        "A2_alt": {"Seen": 0.7442, "Unseen": 0.4727, "Gap": 0.2714, "PairAcc": 0.4557},
        "A3": {"Seen": 0.7334, "Unseen": 0.4870, "Gap": 0.2464, "PairAcc": 0.4535},
        "C1": {"Seen": 0.7798, "Unseen": 0.5618, "Gap": 0.2180, "PairAcc": 0.6354},
        "C2_alt": {"Seen": 0.6979, "Unseen": 0.5447, "Gap": 0.1532, "PairAcc": 0.5303},
        "macro_mean": {"Seen": 0.7476, "Unseen": 0.5144, "Gap": 0.2332, "PairAcc": 0.5294},
    },
    "fresh_unrounded": {
        "A1": {"Seen": 0.7862, "Unseen": 0.5080, "Gap": 0.2782, "PairAcc": 0.5577},
        "A2_alt": {"Seen": 0.7542, "Unseen": 0.4169, "Gap": 0.3373, "PairAcc": 0.3418},
        "A3": {"Seen": 0.7405, "Unseen": 0.4826, "Gap": 0.2579, "PairAcc": 0.4729},
        "C1": {"Seen": 0.7799, "Unseen": 0.5656, "Gap": 0.2143, "PairAcc": 0.6458},
        "C2_alt": {"Seen": 0.6953, "Unseen": 0.5436, "Gap": 0.1517, "PairAcc": 0.5152},
        "macro_mean": {"Seen": 0.7512, "Unseen": 0.5033, "Gap": 0.2479, "PairAcc": 0.5180},
    }
}

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def to_tensor_dict(d, device):
    return {
        "v_sf_cand": torch.tensor(d["v_sf_cand"], dtype=torch.float32, device=device),
        "v_sf_start": torch.tensor(d["v_sf_start"], dtype=torch.float32, device=device),
        "v_sf_end": torch.tensor(d["v_sf_end"], dtype=torch.float32, device=device),
        "v_sf_glob": torch.tensor(d["v_sf_glob"], dtype=torch.float32, device=device),
        "v_clip_cand": torch.tensor(d["v_clip_cand"], dtype=torch.float32, device=device),
        "v_clip_glob": torch.tensor(d["v_clip_glob"], dtype=torch.float32, device=device),
        "q_act": torch.tensor(d["q_act"], dtype=torch.float32, device=device),
        "q_obj": torch.tensor(d["q_obj"], dtype=torch.float32, device=device),
        "h_pool": torch.tensor(d["h_pool"], dtype=torch.float32, device=device),
        "orig_logits": torch.tensor(d["orig_logits"], dtype=torch.float32, device=device),
        "fg_max": torch.tensor(d["fg_max"], dtype=torch.float32, device=device),
        "labels": torch.tensor(d["labels"], dtype=torch.float32, device=device),
    }

class GatedDAOVerifier(DecomposedActionObjectVerifier):
    """
    Gated DAO-Verifier:
    Uses detector candidate foreground confidence as an adaptive gate for decomposed evidence.
    """
    def forward(self, batch):
        res = super().forward(batch)
        fg = batch["fg_max"]
        # Smooth sigmoid gate centered around fg=0.2
        gate = torch.sigmoid(5.0 * (fg - 0.2))
        s_gated = res["s_det"] + gate * (res["alpha_act"] * res["ev_act"] + res["alpha_obj"] * res["ev_obj"])
        res["s_exist"] = s_gated
        return res

def choose_val_seen_threshold(scores, labels):
    """Select threshold on Seen validation set by maximizing balanced accuracy."""
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

def compute_matched_pair_acc(qids, scores, pairs_file):
    """Computes pairwise ranking accuracy on matched unseen query pairs."""
    qid_to_score = dict(zip([str(q) for q in qids], scores))
    if not pairs_file.exists():
        return 0.5
    pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
    pair_accs = []
    for p in pairs:
        pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
        if pq in qid_to_score and nq in qid_to_score:
            sp, sn = qid_to_score[pq], qid_to_score[nq]
            pair_accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    return float(np.mean(pair_accs)) if pair_accs else 0.5

def train_and_eval_split(split: str, device: torch.device, epochs=40, lr=1e-3, weight_decay=1e-4, seed=3407):
    set_seed(seed)
    split_out_dir = RUNS_DIR / split
    split_out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{split}] Loading decomposed features...")
    tr_d = np.load(FEATURES_DIR / split / "train.npz")
    val_d = np.load(FEATURES_DIR / split / "val.npz")
    te_d = np.load(FEATURES_DIR / split / "test.npz")

    # Match same-video counterfactual pairs in Seen train
    tr_qids = list(tr_d["qids"])
    qid_to_idx = {q: i for i, q in enumerate(tr_qids)}

    act_pairs, obj_pairs = [], []
    for i in range(len(tr_qids)):
        src_qid = str(tr_d["source_qids"][i])
        if src_qid in qid_to_idx:
            if tr_d["construction_types"][i] == "action_counterfactual":
                act_pairs.append((qid_to_idx[src_qid], i))
            elif tr_d["construction_types"][i] == "object_counterfactual":
                obj_pairs.append((qid_to_idx[src_qid], i))

    print(f"[{split}] Seen Train counterfactual pairs: Action={len(act_pairs)}, Object={len(obj_pairs)}")

    tr_t = to_tensor_dict(tr_d, device)
    val_t = to_tensor_dict(val_d, device)
    te_t = to_tensor_dict(te_d, device)

    # Masks for evaluation
    val_seen_mask = (val_d["partitions"] == "S+") | (val_d["partitions"] == "S-")
    val_seen_labels = val_d["labels"][val_seen_mask]

    te_seen_mask = (te_d["partitions"] == "S+") | (te_d["partitions"] == "S-")
    te_unseen_mask = (te_d["partitions"] == "U+") | (te_d["partitions"] == "U-")
    te_labels = te_d["labels"]
    te_qids = te_d["qids"]
    te_vids = te_d["vids"]
    te_parts = te_d["partitions"]
    te_types = te_d["construction_types"]

    # Baseline metrics
    base_logits = te_d["orig_logits"]
    base_seen_auc = float(roc_auc_score(te_labels[te_seen_mask], base_logits[te_seen_mask]))
    base_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], base_logits[te_unseen_mask]))
    base_gap = base_seen_auc - base_unseen_auc
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    base_pair_acc = compute_matched_pair_acc(te_qids, base_logits, pairs_file)

    # Initialize Gated DAO-Verifier
    model = GatedDAOVerifier().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    pos_idx = torch.where(tr_t["labels"] == 1)[0]
    neg_idx = torch.where(tr_t["labels"] == 0)[0]
    pos_weight = torch.tensor([(len(neg_idx)) / len(pos_idx)], device=device)
    bce_loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    act_pos_idx = torch.tensor([p[0] for p in act_pairs], device=device) if act_pairs else torch.empty(0, dtype=torch.long, device=device)
    act_neg_idx = torch.tensor([p[1] for p in act_pairs], device=device) if act_pairs else torch.empty(0, dtype=torch.long, device=device)
    obj_pos_idx = torch.tensor([p[0] for p in obj_pairs], device=device) if obj_pairs else torch.empty(0, dtype=torch.long, device=device)
    obj_neg_idx = torch.tensor([p[1] for p in obj_pairs], device=device) if obj_pairs else torch.empty(0, dtype=torch.long, device=device)

    best_val_auc = -1.0
    best_epoch = -1
    best_state = None

    print(f"[{split}] Training DAO-Verifier for {epochs} epochs strictly on Seen data...")
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        out = model(tr_t)
        loss_bce = bce_loss_fn(out["s_exist"], tr_t["labels"])

        loss_act = torch.tensor(0.0, device=device)
        if len(act_pos_idx) > 0:
            ev_act_pos = out["ev_act"][act_pos_idx]
            ev_act_neg = out["ev_act"][act_neg_idx]
            loss_act = F.relu(0.8 - (ev_act_pos - ev_act_neg)).mean()

        loss_obj = torch.tensor(0.0, device=device)
        if len(obj_pos_idx) > 0:
            ev_obj_pos = out["ev_obj"][obj_pos_idx]
            ev_obj_neg = out["ev_obj"][obj_neg_idx]
            loss_obj = F.relu(0.8 - (ev_obj_pos - ev_obj_neg)).mean()

        # Prior loss: prior branch captures the marginal text bias
        loss_prior = F.mse_loss(out["prior_act"], out["raw_act"].detach()) + F.mse_loss(out["prior_obj"], out["raw_obj"].detach())

        total_loss = loss_bce + 1.0 * loss_act + 0.5 * loss_obj + 0.1 * loss_prior
        total_loss.backward()
        optimizer.step()

        # Evaluate strictly on Seen validation
        model.eval()
        with torch.no_grad():
            val_out = model(val_t)
            val_scores = val_out["s_exist"][val_seen_mask].cpu().numpy()
            val_auc = float(roc_auc_score(val_seen_labels, val_scores))
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_epoch = epoch
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    print(f"[{split}] Best Seen Val AUROC: {best_val_auc:.4f} at epoch {best_epoch} (total time {time.time()-t0:.1f}s)")

    # Load best checkpoint strictly selected on Seen validation
    model.load_state_dict(best_state)
    model.eval()

    # Threshold selection strictly on Seen validation
    with torch.no_grad():
        val_out = model(val_t)
        val_scores = val_out["s_exist"][val_seen_mask].cpu().numpy()
        th = choose_val_seen_threshold(val_scores, val_seen_labels)

    # Evaluate on full test set
    with torch.no_grad():
        te_out = model(te_t)
        test_logits = te_out["s_exist"].cpu().numpy()
        test_scores = torch.from_numpy(test_logits).sigmoid().numpy()

    # Compute Test Metrics
    seen_auc = float(roc_auc_score(te_labels[te_seen_mask], test_logits[te_seen_mask]))
    unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], test_logits[te_unseen_mask]))
    gap = seen_auc - unseen_auc
    pair_acc = compute_matched_pair_acc(te_qids, test_logits, pairs_file)

    pos_u = (te_parts == "U+")
    neg_u = (te_parts == "U-")
    u_pos_frr = float((test_logits[pos_u] < th).mean() * 100.0)
    u_neg_rr = float((test_logits[neg_u] < th).mean() * 100.0)

    # Breakdown by Counterfactual Construction Type
    act_cf_mask = te_unseen_mask & ((te_types == "action_counterfactual") | (te_labels == 1))
    act_cf_auc = float(roc_auc_score(te_labels[act_cf_mask], test_logits[act_cf_mask])) if np.sum(te_types == "action_counterfactual") > 0 else float("nan")
    base_act_cf_auc = float(roc_auc_score(te_labels[act_cf_mask], base_logits[act_cf_mask])) if np.sum(te_types == "action_counterfactual") > 0 else float("nan")

    obj_cf_mask = te_unseen_mask & ((te_types == "object_counterfactual") | (te_labels == 1))
    obj_cf_auc = float(roc_auc_score(te_labels[obj_cf_mask], test_logits[obj_cf_mask])) if np.sum(te_types == "object_counterfactual") > 0 else float("nan")
    base_obj_cf_auc = float(roc_auc_score(te_labels[obj_cf_mask], base_logits[obj_cf_mask])) if np.sum(te_types == "object_counterfactual") > 0 else float("nan")

    # 1. Visual Permutation Diagnostic Control (Shuffling video features across queries)
    rng_perm = np.random.default_rng(seed)
    perm_idx = rng_perm.permutation(len(te_labels))
    te_t_perm = {k: v.clone() for k, v in te_t.items()}
    for k in ["v_sf_cand", "v_sf_start", "v_sf_end", "v_sf_glob", "v_clip_cand", "v_clip_glob", "h_pool"]:
        te_t_perm[k] = te_t[k][perm_idx]
    with torch.no_grad():
        perm_out = model(te_t_perm)
        perm_logits = perm_out["s_exist"].cpu().numpy()
    perm_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], perm_logits[te_unseen_mask]))
    perm_pair_acc = compute_matched_pair_acc(te_qids, perm_logits, pairs_file)

    # 2. Text-Only Diagnostic Control (Zeroed Visual Evidence)
    te_t_zero = {k: v.clone() for k, v in te_t.items()}
    for k in ["v_sf_cand", "v_sf_start", "v_sf_end", "v_sf_glob", "v_clip_cand", "v_clip_glob"]:
        te_t_zero[k] = torch.zeros_like(te_t[k])
    with torch.no_grad():
        zero_out = model(te_t_zero)
        zero_logits = zero_out["s_exist"].cpu().numpy()
    zero_unseen_auc = float(roc_auc_score(te_labels[te_unseen_mask], zero_logits[te_unseen_mask]))
    zero_pair_acc = compute_matched_pair_acc(te_qids, zero_logits, pairs_file)

    metrics = {
        "split": split,
        "best_epoch": best_epoch,
        "best_val_seen_auc": best_val_auc,
        "threshold": float(th),
        "Seen_AUROC": seen_auc,
        "Unseen_AUROC": unseen_auc,
        "Gap": gap,
        "Matched_PairAcc": pair_acc,
        "U_pos_FRR": u_pos_frr,
        "U_neg_RR": u_neg_rr,
        "Action_CF_AUROC": act_cf_auc,
        "Object_CF_AUROC": obj_cf_auc,
        "delta_seen": seen_auc - base_seen_auc,
        "delta_unseen": unseen_auc - base_unseen_auc,
        "gap_reduction": base_gap - gap,
        "baseline_fresh": {
            "Seen_AUROC": base_seen_auc,
            "Unseen_AUROC": base_unseen_auc,
            "Gap": base_gap,
            "Matched_PairAcc": base_pair_acc,
            "Action_CF_AUROC": base_act_cf_auc,
            "Object_CF_AUROC": base_obj_cf_auc,
        },
        "baseline_official_published": BASELINE_OFFICIAL["published_rounded"][split],
        "visual_permutation_control": {
            "Unseen_AUROC": perm_unseen_auc,
            "Matched_PairAcc": perm_pair_acc,
        },
        "text_only_control": {
            "Unseen_AUROC": zero_unseen_auc,
            "Matched_PairAcc": zero_pair_acc,
        },
    }

    # Save checkpoint
    torch.save({
        "split": split,
        "best_epoch": best_epoch,
        "threshold": float(th),
        "state_dict": best_state,
        "metrics": metrics,
    }, split_out_dir / "verifier_checkpoint.pt")

    # Save predictions.jsonl
    pred_path = split_out_dir / "predictions.jsonl"
    with pred_path.open("w", encoding="utf-8") as f:
        for q, p, y, v, bl, fl, ps in zip(te_qids, te_parts, te_labels, te_vids, base_logits, test_logits, test_scores):
            f.write(json.dumps({
                "qid": str(q),
                "partition": str(p),
                "exist_label": int(y),
                "vid": str(v),
                "baseline_logit": float(bl),
                "final_logit": float(fl),
                "pred_score": float(ps),
                "pred_exist": bool(fl >= th),
            }) + "\n")

    with (split_out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[{split}] Test Results:")
    print(f"  Seen AUROC:   {seen_auc:.4f} (baseline {base_seen_auc:.4f}, delta {metrics['delta_seen']:+.4f})")
    print(f"  Unseen AUROC: {unseen_auc:.4f} (baseline {base_unseen_auc:.4f}, delta {metrics['delta_unseen']:+.4f})")
    print(f"  Gap:          {gap:.4f} (baseline {base_gap:.4f}, gap reduction {metrics['gap_reduction']:+.4f})")
    print(f"  PairAcc:      {pair_acc:.4f} (baseline {base_pair_acc:.4f})")
    print(f"  Action CF AUC:{act_cf_auc:.4f} (baseline {base_act_cf_auc:.4f})")

    return metrics, {
        "y": te_labels,
        "parts": te_parts,
        "vids": te_vids,
        "original": base_logits,
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
    print("Decomposed Action-Object Verifier (DAO-Verifier) Benchmarking Across 5 Splits")
    print("Seed: 3407 | Strict Seen-Only Training & Threshold Selection")
    print("=" * 80)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Execution device:", device)

    split_metrics = {}
    boot_data = {}

    for split in SPLITS:
        m, bd = train_and_eval_split(split, device=device, epochs=40, lr=1e-3, seed=3407)
        split_metrics[split] = m
        boot_data[split] = bd

    print("\nRunning 2,000-iteration Paired Video Cluster Bootstrap across all 5 splits...")
    bootstrap_results = run_cluster_bootstrap(boot_data, n_repeats=2000, seed=20261005)

    macro_summary = {
        "Seen_AUROC": float(np.mean([m["Seen_AUROC"] for m in split_metrics.values()])),
        "Unseen_AUROC": float(np.mean([m["Unseen_AUROC"] for m in split_metrics.values()])),
        "Gap": float(np.mean([m["Gap"] for m in split_metrics.values()])),
        "Matched_PairAcc": float(np.mean([m["Matched_PairAcc"] for m in split_metrics.values()])),
        "U_pos_FRR": float(np.mean([m["U_pos_FRR"] for m in split_metrics.values()])),
        "U_neg_RR": float(np.mean([m["U_neg_RR"] for m in split_metrics.values()])),
        "Action_CF_AUROC": float(np.mean([m["Action_CF_AUROC"] for m in split_metrics.values()])),
        "delta_seen": float(np.mean([m["delta_seen"] for m in split_metrics.values()])),
        "delta_unseen": float(np.mean([m["delta_unseen"] for m in split_metrics.values()])),
        "gap_reduction": float(np.mean([m["gap_reduction"] for m in split_metrics.values()])),
        "baseline_macro_fresh": {
            "Seen_AUROC": float(np.mean([m["baseline_fresh"]["Seen_AUROC"] for m in split_metrics.values()])),
            "Unseen_AUROC": float(np.mean([m["baseline_fresh"]["Unseen_AUROC"] for m in split_metrics.values()])),
            "Gap": float(np.mean([m["baseline_fresh"]["Gap"] for m in split_metrics.values()])),
            "Matched_PairAcc": float(np.mean([m["baseline_fresh"]["Matched_PairAcc"] for m in split_metrics.values()])),
            "Action_CF_AUROC": float(np.mean([m["baseline_fresh"]["Action_CF_AUROC"] for m in split_metrics.values()])),
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
        "model_name": "Decomposed_Action_Object_Verifier_Gated",
        "macro_summary": macro_summary,
        "bootstrap_95ci": bootstrap_results["macro"],
        "splits": split_metrics,
        "per_split_bootstrap": bootstrap_results["per_split"],
    }

    summary_file = BASE_DIR / "clean_benchmark_summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    print("\n" + "=" * 80)
    print("5-SPLIT BENCHMARK SUMMARY (DAO-Verifier vs Baseline):")
    print("=" * 80)
    print(f"Mean Seen AUROC:   {macro_summary['Seen_AUROC']:.4f} (baseline {macro_summary['baseline_macro_fresh']['Seen_AUROC']:.4f}, delta {macro_summary['delta_seen']:+.4f})")
    print(f"Mean Unseen AUROC: {macro_summary['Unseen_AUROC']:.4f} (baseline {macro_summary['baseline_macro_fresh']['Unseen_AUROC']:.4f}, delta {macro_summary['delta_unseen']:+.4f}) [95% CI: {bootstrap_results['macro']['delta_unseen']}]")
    print(f"Mean Gap:          {macro_summary['Gap']:.4f} (baseline {macro_summary['baseline_macro_fresh']['Gap']:.4f}, gap reduction {macro_summary['gap_reduction']:+.4f}) [95% CI: {bootstrap_results['macro']['gap_reduction']}]")
    print(f"Mean PairAcc:      {macro_summary['Matched_PairAcc']:.4f} (baseline {macro_summary['baseline_macro_fresh']['Matched_PairAcc']:.4f})")
    print(f"Mean Action CF AUC:{macro_summary['Action_CF_AUROC']:.4f} (baseline {macro_summary['baseline_macro_fresh']['Action_CF_AUROC']:.4f})")
    print(f"Permuted Visual:   Unseen AUROC={macro_summary['visual_permutation_control']['Unseen_AUROC']:.4f}, PairAcc={macro_summary['visual_permutation_control']['Matched_PairAcc']:.4f}")
    print(f"Text-Only Control: Unseen AUROC={macro_summary['text_only_control']['Unseen_AUROC']:.4f}, PairAcc={macro_summary['text_only_control']['Matched_PairAcc']:.4f}")
    print(f"\nAll results saved to {summary_file}")

if __name__ == "__main__":
    main()
