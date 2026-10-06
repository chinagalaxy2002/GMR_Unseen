#!/usr/bin/env python3
"""
2,000-Replicate Joint Video Cluster Bootstrap Statistical Test.
Samples unique video population simultaneously across all 5 splits
to preserve cross-split video correlation (1,164 common videos).
Computes 95% CIs for Delta Unseen AUROC, Delta Seen AUROC,
Paired Diff (WSum - Power), and Delta Unseen Rej-F1.
"""
import sys
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/agy_test/detr_decoder_gmr"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {"moment": 1, "qd": 2, "flash": 0}

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def cdf(ref, val):
    ref = np.sort(ref)
    return (np.searchsorted(ref, val, "left") + np.searchsorted(ref, val, "right")) / (2.0 * len(ref))

def route_evidence(queries, X):
    s_ev = np.zeros(len(queries), dtype=np.float32)
    for i, q in enumerate(queries):
        if any(w in q for w in ["run", "walk", "slow", "fast"]):
            s_ev[i] = 0.50 * X[i, 5] + 0.35 * X[i, 8] + 0.15 * X[i, 12]
        elif any(w in q for w in ["chair", "couch", "bed", "sofa", "box", "cabinet", "shelf", "table", "cup", "book"]):
            s_ev[i] = 0.45 * X[i, 5] + 0.35 * X[i, 6] + 0.20 * X[i, 3]
        else:
            s_ev[i] = 0.55 * X[i, 5] + 0.30 * X[i, 3] + 0.15 * X[i, 12]
    return s_ev

def find_best_threshold(y_val, scores_val):
    best_th, best_bacc = 0.5, -1
    th_candidates = np.percentile(scores_val, np.linspace(5, 95, 91))
    for th in th_candidates:
        pred_pos = scores_val >= th
        tp = np.sum((y_val == 1) & pred_pos)
        fn = np.sum((y_val == 1) & ~pred_pos)
        tn = np.sum((y_val == 0) & ~pred_pos)
        fp = np.sum((y_val == 0) & pred_pos)
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
        bacc = 0.5 * (tpr + tnr)
        if bacc > best_bacc:
            best_bacc = bacc
            best_th = th
    return best_th

def main():
    split_data = {}
    all_vids = set()
    for split in SPLITS:
        tr = np.load(BASE / "cache" / split / "train.npz")
        val = np.load(BASE / "cache" / split / "val.npz")
        te = np.load(BASE / "cache" / split / "test.npz")
        
        tr_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/train.jsonl")
        val_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/val.jsonl")
        te_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/test.jsonl")
        
        tr_q = [r["query"].lower() for r in tr_rows]
        val_q = [r["query"].lower() for r in val_rows if r["partition"] in ["S+", "S-"]]
        te_q = [r["query"].lower() for r in te_rows]
        
        ev_tr = route_evidence(tr_q, tr["X"])
        ev_val = route_evidence(val_q, val["X"])
        ev_te = route_evidence(te_q, te["X"])
        
        r_ev_val = cdf(ev_tr, ev_val)
        r_ev_te = cdf(ev_tr, ev_te)
        
        y_val = val["labels"]
        y_te = te["labels"]
        parts_te = te["partitions"]
        vids_te = np.array(list(map(str, te["vids"])))
        all_vids.update(vids_te)
        
        models = {}
        thresholds = {}
        for bb, col in BACKBONES.items():
            det_tr = tr["X"][:, col]
            det_val = val["X"][:, col]
            det_te = te["X"][:, col]
            
            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)
            
            arms_val = {
                "baseline": det_val,
                "power": (r_det_val ** 0.65) * (r_ev_val ** 0.85),
                "wsum": 0.5 * r_det_val + 0.5 * r_ev_val
            }
            arms_te = {
                "baseline": det_te,
                "power": (r_det_te ** 0.65) * (r_ev_te ** 0.85),
                "wsum": 0.5 * r_det_te + 0.5 * r_ev_te
            }
            
            th_bb = {arm: find_best_threshold(y_val, arms_val[arm]) for arm in arms_val}
            models[bb] = arms_te
            thresholds[bb] = th_bb
            
        split_data[split] = {
            "vids": vids_te,
            "labels": y_te,
            "partitions": parts_te,
            "models": models,
            "thresholds": thresholds,
            "vid_to_idx": {v: np.where(vids_te == v)[0] for v in np.unique(vids_te)}
        }

    unique_vids = np.array(sorted(list(all_vids)))
    N_BOOT = 2000
    rng = np.random.RandomState(3407)

    boot_results = {bb: {
        "gain_unseen_power": [], "gain_unseen_wsum": [],
        "drop_seen_power": [], "drop_seen_wsum": [],
        "diff_unseen_wsum_power": [], "diff_seen_wsum_power": [],
        "rej_f1_u_gain_power": [], "rej_f1_u_gain_wsum": [],
    } for bb in BACKBONES}

    for b in range(N_BOOT):
        sampled_vids = rng.choice(unique_vids, size=len(unique_vids), replace=True)
        vid_counts = {}
        for v in sampled_vids:
            vid_counts[v] = vid_counts.get(v, 0) + 1
            
        macro_metrics = {bb: {k: [] for k in boot_results[bb]} for bb in BACKBONES}
        
        for split in SPLITS:
            sd = split_data[split]
            indices = []
            for v, cnt in vid_counts.items():
                if v in sd["vid_to_idx"]:
                    idx_list = sd["vid_to_idx"][v]
                    for _ in range(cnt):
                        indices.extend(idx_list)
            if not indices:
                continue
            indices = np.array(indices)
            
            y = sd["labels"][indices]
            parts = sd["partitions"][indices]
            is_s = (parts == "S+") | (parts == "S-")
            is_u = (parts == "U+") | (parts == "U-")
            
            if len(np.unique(y[is_s])) < 2 or len(np.unique(y[is_u])) < 2:
                continue
                
            for bb in BACKBONES:
                th = sd["thresholds"][bb]
                s_base = sd["models"][bb]["baseline"][indices]
                s_pow = sd["models"][bb]["power"][indices]
                s_wsum = sd["models"][bb]["wsum"][indices]
                
                b_u = roc_auc_score(y[is_u], s_base[is_u])
                p_u = roc_auc_score(y[is_u], s_pow[is_u])
                w_u = roc_auc_score(y[is_u], s_wsum[is_u])
                
                b_s = roc_auc_score(y[is_s], s_base[is_s])
                p_s = roc_auc_score(y[is_s], s_pow[is_s])
                w_s = roc_auc_score(y[is_s], s_wsum[is_s])
                
                rej_b_u = s_base[is_u] < th["baseline"]
                rej_p_u = s_pow[is_u] < th["power"]
                rej_w_u = s_wsum[is_u] < th["wsum"]
                y_u = y[is_u]
                
                rf_b_u = f1_score(1 - y_u, rej_b_u, zero_division=0)
                rf_p_u = f1_score(1 - y_u, rej_p_u, zero_division=0)
                rf_w_u = f1_score(1 - y_u, rej_w_u, zero_division=0)
                
                macro_metrics[bb]["gain_unseen_power"].append(p_u - b_u)
                macro_metrics[bb]["gain_unseen_wsum"].append(w_u - b_u)
                macro_metrics[bb]["drop_seen_power"].append(p_s - b_s)
                macro_metrics[bb]["drop_seen_wsum"].append(w_s - b_s)
                macro_metrics[bb]["diff_unseen_wsum_power"].append(w_u - p_u)
                macro_metrics[bb]["diff_seen_wsum_power"].append(w_s - p_s)
                macro_metrics[bb]["rej_f1_u_gain_power"].append(rf_p_u - rf_b_u)
                macro_metrics[bb]["rej_f1_u_gain_wsum"].append(rf_w_u - rf_b_u)
                
        for bb in BACKBONES:
            for k in boot_results[bb]:
                if macro_metrics[bb][k]:
                    boot_results[bb][k].append(np.mean(macro_metrics[bb][k]))

    print("=== 2,000 JOINT VIDEO CLUSTER BOOTSTRAP RESULTS (ACROSS ALL 5 SPLITS) ===")
    for bb in BACKBONES:
        print(f"\n--- {bb.upper()} ---")
        for k, name in [
            ("gain_unseen_power", "Unseen Gain PowerProd"),
            ("gain_unseen_wsum", "Unseen Gain WSum"),
            ("drop_seen_power", "Seen Change PowerProd"),
            ("drop_seen_wsum", "Seen Change WSum"),
            ("diff_unseen_wsum_power", "Paired Diff (WSum - Power) Unseen"),
            ("diff_seen_wsum_power", "Paired Diff (WSum - Power) Seen"),
            ("rej_f1_u_gain_power", "Unseen Rej-F1 Gain PowerProd"),
            ("rej_f1_u_gain_wsum", "Unseen Rej-F1 Gain WSum"),
        ]:
            arr = np.array(boot_results[bb][k])
            ci = np.percentile(arr, [2.5, 97.5])
            print("%-35s: %+.2fpp 95%%CI [%+.2f, %+.2f]" % (name, np.mean(arr)*100, ci[0]*100, ci[1]*100))

if __name__ == "__main__":
    main()
