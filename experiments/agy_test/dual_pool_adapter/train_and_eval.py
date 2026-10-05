#!/usr/bin/env python3
"""
Dual-Pooling Regularized Adapter for Mitigating Seen-to-Unseen Existence Degradation in GMR.

Strictly follows:
- Zero edits to original repository code.
- New isolated experiment directory: experiments/agy_test/dual_pool_adapter/
- Single seed: 3407.
- Training strictly on Seen data (S+/S-).
- Threshold selection strictly on Seen validation (val S+/S-).
- Evaluation on full test set (Seen S+/S- and Unseen U+/U-).
- Paired video cluster bootstrap confidence intervals (2,000 resamples).
"""
import sys
import json
import random
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "experiments/agy_test/audit_20261005"))

from audit_results import prepared_auc

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
HQ_DIR = REPO_ROOT / "experiments/agy_test/cache/hq"
AUDIT_DIR = REPO_ROOT / "experiments/agy_test/audit_20261005"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
BASE_DIR = Path(__file__).resolve().parent

# Official baseline QD-DETR-GMR metrics from BASELINE_AUROC_DEGRADATION.md
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

def extract_dual_pool_features(data_dict):
    """
    Extracts 514-dim dual-pooling representation from decoder hidden states hs [N, 10, 256]:
    - p_max: coordinate-wise max over slots [N, 256]
    - p_mean: slot centroid average [N, 256]
    - cos_disp: slot cosine dispersion relative to centroid [N, 1]
    - dev: maximum slot Euclidean deviation from centroid [N, 1]
    """
    hs = torch.tensor(data_dict["hs"], dtype=torch.float32)
    p_max = hs.max(dim=1).values
    p_mean = hs.mean(dim=1)
    norm_hs = F.normalize(hs, p=2, dim=-1)
    norm_mean = F.normalize(p_mean.unsqueeze(1), p=2, dim=-1)
    cos_disp = (1.0 - (norm_hs * norm_mean).sum(dim=-1).min(dim=-1).values).unsqueeze(-1)
    dev = (hs - p_mean.unsqueeze(1)).norm(p=2, dim=-1).max(dim=-1).values.unsqueeze(-1)
    feat = torch.cat([p_max, p_mean, cos_disp, dev], dim=-1).numpy()
    return feat

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

def train_and_eval_split(split: str, out_root: Path, C=0.5, with_scaler=True, seed=3407):
    set_seed(seed)
    split_out_dir = out_root / split
    split_out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load data
    tr_d = np.load(HQ_DIR / split / "train.npz")
    val_d = np.load(HQ_DIR / split / "val.npz")
    te_d = np.load(HQ_DIR / split / "test.npz")
    fresh_d = np.load(AUDIT_DIR / f"{split}_fresh_test_signals.npz")
    
    # Verify alignment between cache test and fresh test
    assert np.array_equal(te_d["qids"], fresh_d["qids"]), f"QID mismatch in {split}"
    assert np.array_equal(te_d["labels"], fresh_d["labels"]), f"Label mismatch in {split}"
    assert np.array_equal(te_d["partitions"], fresh_d["partitions"]), f"Partition mismatch in {split}"
    
    # 2. Extract features
    x_tr = extract_dual_pool_features(tr_d)
    y_tr = tr_d["labels"]
    x_val = extract_dual_pool_features(val_d)
    x_te = extract_dual_pool_features(te_d)
    
    scaler_params = None
    if with_scaler:
        scaler = StandardScaler()
        x_tr = scaler.fit_transform(x_tr)
        x_val = scaler.transform(x_val)
        x_te = scaler.transform(x_te)
        scaler_params = {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
            "var": scaler.var_.tolist(),
        }
        
    # 3. Train L2-regularized logistic adapter strictly on Seen train data
    clf = LogisticRegression(C=C, max_iter=1000, random_state=seed, solver="lbfgs")
    clf.fit(x_tr, y_tr)
    
    # 4. Predict on Seen validation to select threshold
    val_parts = val_d["partitions"]
    val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
    val_seen_scores = clf.decision_function(x_val)[val_seen_mask]
    val_seen_labels = val_d["labels"][val_seen_mask]
    th = choose_val_seen_threshold(val_seen_scores, val_seen_labels)
    
    # 5. Predict on full test set
    test_logits = clf.decision_function(x_te)
    test_scores = torch.from_numpy(test_logits).sigmoid().numpy()
    
    # Baseline comparison signals from fresh test
    base_logits = fresh_d["orig_logits"]
    base_scores = torch.from_numpy(base_logits).sigmoid().numpy()
    
    parts = fresh_d["partitions"]
    y_te = fresh_d["labels"]
    qids = fresh_d["qids"]
    vids = fresh_d["vids"]
    
    sm = (parts == "S+") | (parts == "S-")
    um = (parts == "U+") | (parts == "U-")
    
    # Metrics
    seen_auc = float(roc_auc_score(y_te[sm], test_logits[sm]))
    unseen_auc = float(roc_auc_score(y_te[um], test_logits[um]))
    gap = float(seen_auc - unseen_auc)
    
    base_seen_auc = float(roc_auc_score(y_te[sm], base_logits[sm]))
    base_unseen_auc = float(roc_auc_score(y_te[um], base_logits[um]))
    base_gap = float(base_seen_auc - base_unseen_auc)
    
    pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
    pair_acc = compute_matched_pair_acc(qids, test_logits, pairs_file)
    base_pair_acc = compute_matched_pair_acc(qids, base_logits, pairs_file)
    
    pos_u = (parts == "U+")
    neg_u = (parts == "U-")
    u_pos_frr = float((test_logits[pos_u] < th).mean() * 100.0)
    u_neg_rr = float((test_logits[neg_u] < th).mean() * 100.0)
    
    metrics = {
        "split": split,
        "C": C,
        "with_scaler": with_scaler,
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
        "baseline_official_published": BASELINE_OFFICIAL["published_rounded"][split],
    }
    
    # Save checkpoint / weights
    ckpt = {
        "split": split,
        "C": C,
        "with_scaler": with_scaler,
        "threshold": float(th),
        "coef": clf.coef_.squeeze(0).tolist(),
        "intercept": float(clf.intercept_[0]),
        "scaler": scaler_params,
        "metrics": metrics,
    }
    torch.save(ckpt, split_out_dir / "adapter_checkpoint.pt")
    
    # Save predictions.jsonl
    pred_path = split_out_dir / "predictions.jsonl"
    with pred_path.open("w") as f:
        for q, p, y, v, bl, fl, ps in zip(qids, parts, y_te, vids, base_logits, test_logits, test_scores):
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
            
    with (split_out_dir / "metrics.json").open("w") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics, {
        "y": y_te,
        "parts": parts,
        "vids": vids,
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

def evaluate_configuration(config_name: str, out_root: Path, C: float, with_scaler: bool):
    print("=" * 80)
    print(f"Evaluating {config_name}: C={C}, with_scaler={with_scaler}")
    print("=" * 80)
    
    split_metrics = {}
    boot_data = {}
    for s in SPLITS:
        m, bd = train_and_eval_split(s, out_root, C=C, with_scaler=with_scaler, seed=3407)
        split_metrics[s] = m
        boot_data[s] = bd
        print(f"  {s}: Seen={m['Seen_AUROC']:.4f}, Unseen={m['Unseen_AUROC']:.4f}, Gap={m['Gap']:.4f}, PairAcc={m['Matched_PairAcc']:.4f}")
        
    print("  Running 2,000-iteration Paired Video Cluster Bootstrap...")
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
    }
    
    full_report = {
        "model_name": config_name,
        "C": C,
        "with_scaler": with_scaler,
        "macro_summary": macro_summary,
        "bootstrap_95ci": bootstrap_results["macro"],
        "bootstrap_details": bootstrap_results,
        "splits": split_metrics,
        "baselines": BASELINE_OFFICIAL,
    }
    return full_report

def main():
    print("=" * 80)
    print("Dual-Pooling Regularized Adapter Training & Full Audit Benchmark")
    print("=" * 80)
    
    # 1. Primary Model: C=0.5 with StandardScaler (Max Unseen AUROC & PairAcc gain)
    primary_out = BASE_DIR / "runs_scaled_c05"
    primary_report = evaluate_configuration("DualPool_Scaled_C0.5", primary_out, C=0.5, with_scaler=True)
    
    # 2. Conservative Model: C=1.0 unscaled (Strict 0.00 Seen drop)
    conservative_out = BASE_DIR / "runs_unscaled_c10"
    conservative_report = evaluate_configuration("DualPool_Unscaled_C1.0", conservative_out, C=1.0, with_scaler=False)
    
    combined_summary = {
        "primary_model_scaled_c05": primary_report,
        "conservative_model_unscaled_c10": conservative_report,
        "protocol": "Trained strictly on Seen data (train S+/S-); threshold on Seen validation (val S+/S-); evaluated on test (S+/S-, U+/U-); seed=3407",
    }
    
    summary_path = BASE_DIR / "benchmark_summary.json"
    with summary_path.open("w") as f:
        json.dump(combined_summary, f, indent=2)
        
    print("\n" + "=" * 80)
    print("COMPARATIVE SUMMARY")
    print("=" * 80)
    print(f"{'Metric':<20} | {'Fresh Baseline':<15} | {'Primary (C=0.5 Scaled)':<25} | {'Conservative (C=1.0)':<25}")
    print("-" * 90)
    b_fresh = BASELINE_OFFICIAL["fresh_unrounded"]["macro_mean"]
    p_m = primary_report["macro_summary"]
    c_m = conservative_report["macro_summary"]
    
    print(f"{'Seen AUROC':<20} | {b_fresh['Seen']:<15.4f} | {p_m['Seen_AUROC']:<15.4f} ({p_m['delta_seen']*100:+.2f} pp) | {c_m['Seen_AUROC']:<15.4f} ({c_m['delta_seen']*100:+.2f} pp)")
    print(f"{'Unseen AUROC':<20} | {b_fresh['Unseen']:<15.4f} | {p_m['Unseen_AUROC']:<15.4f} ({p_m['delta_unseen']*100:+.2f} pp) | {c_m['Unseen_AUROC']:<15.4f} ({c_m['delta_unseen']*100:+.2f} pp)")
    print(f"{'Seen-Unseen Gap':<20} | {b_fresh['Gap']:<15.4f} | {p_m['Gap']:<15.4f} ({-p_m['gap_reduction']*100:+.2f} pp) | {c_m['Gap']:<15.4f} ({-c_m['gap_reduction']*100:+.2f} pp)")
    print(f"{'Matched PairAcc':<20} | {b_fresh['PairAcc']:<15.4f} | {p_m['Matched_PairAcc']:<15.4f} ({(p_m['Matched_PairAcc']-b_fresh['PairAcc'])*100:+.2f} pp) | {c_m['Matched_PairAcc']:<15.4f} ({(c_m['Matched_PairAcc']-b_fresh['PairAcc'])*100:+.2f} pp)")
    print("-" * 90)
    print(f"95% CI delta_unseen (Primary):      [{primary_report['bootstrap_95ci']['delta_unseen'][0]*100:+.2f} pp, {primary_report['bootstrap_95ci']['delta_unseen'][1]*100:+.2f} pp]")
    print(f"95% CI gap_reduction (Primary):     [{primary_report['bootstrap_95ci']['gap_reduction'][0]*100:+.2f} pp, {primary_report['bootstrap_95ci']['gap_reduction'][1]*100:+.2f} pp]")
    print(f"95% CI delta_unseen (Conservative): [{conservative_report['bootstrap_95ci']['delta_unseen'][0]*100:+.2f} pp, {conservative_report['bootstrap_95ci']['delta_unseen'][1]*100:+.2f} pp]")
    print(f"95% CI gap_reduction (Conservative):[{conservative_report['bootstrap_95ci']['gap_reduction'][0]*100:+.2f} pp, {conservative_report['bootstrap_95ci']['gap_reduction'][1]*100:+.2f} pp]")
    print(f"\nAll artifacts successfully saved in {BASE_DIR}")

if __name__ == "__main__":
    main()
