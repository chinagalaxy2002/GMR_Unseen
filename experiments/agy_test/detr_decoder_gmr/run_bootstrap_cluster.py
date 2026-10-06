#!/usr/bin/env python3
"""
2,000-Replicate Paired Video Cluster Bootstrap Statistical Test.
Measures Delta Unseen, Delta Seen, Delta Gap and Paired Differences
between Weighted Sum (0.5+0.5) and Power-law Product (0.65, 0.85).
Protocol: Fixed Seen Training CDF, Preserving Average Ties, Seed 3407.
"""
import sys
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

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

def main():
    split_data = {}
    for split in SPLITS:
        tr = np.load(BASE / "cache" / split / "train.npz")
        te = np.load(BASE / "cache" / split / "test.npz")
        tr_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/train.jsonl")
        te_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/test.jsonl")
        
        tr_q = [r["query"].lower() for r in tr_rows]
        te_q = [r["query"].lower() for r in te_rows]
        
        ev_tr = route_evidence(tr_q, tr["X"])
        ev_te = route_evidence(te_q, te["X"])
        r_ev = cdf(ev_tr, ev_te)
        
        split_data[split] = {
            "vids": np.array(te["vids"]),
            "labels": te["labels"],
            "partitions": te["partitions"],
            "r_ev": r_ev,
            "models": {}
        }
        
        for bb, col in BACKBONES.items():
            det_tr = tr["X"][:, col]
            det_te = te["X"][:, col]
            r_det = cdf(det_tr, det_te)
            
            split_data[split]["models"][bb] = {
                "base": det_te,
                "power": (r_det ** 0.65) * (r_ev ** 0.85),
                "wsum": 0.5 * r_det + 0.5 * r_ev,
            }

    rng = np.random.RandomState(3407)
    N_BOOT = 2000
    split_vids = {s: np.unique(split_data[s]["vids"]) for s in SPLITS}

    boot_diffs = {bb: {"unseen": [], "seen": []} for bb in BACKBONES}
    boot_unseen_gains = {bb: {"power": [], "wsum": []} for bb in BACKBONES}
    boot_seen_drops = {bb: {"power": [], "wsum": []} for bb in BACKBONES}

    for b in range(N_BOOT):
        macro_diff_unseen = {bb: [] for bb in BACKBONES}
        macro_diff_seen = {bb: [] for bb in BACKBONES}
        macro_gain_unseen = {bb: {"power": [], "wsum": []} for bb in BACKBONES}
        macro_gain_seen = {bb: {"power": [], "wsum": []} for bb in BACKBONES}
        
        for split in SPLITS:
            vids_u = split_vids[split]
            sampled_vids = rng.choice(vids_u, size=len(vids_u), replace=True)
            
            idx_map = {}
            for i, v in enumerate(split_data[split]["vids"]):
                idx_map.setdefault(v, []).append(i)
            
            sampled_indices = []
            for v in sampled_vids:
                if v in idx_map:
                    sampled_indices.extend(idx_map[v])
            sampled_indices = np.array(sampled_indices)
            
            parts = split_data[split]["partitions"][sampled_indices]
            y = split_data[split]["labels"][sampled_indices]
            is_s = (parts == "S+") | (parts == "S-")
            is_u = (parts == "U+") | (parts == "U-")
            
            if len(np.unique(y[is_s])) < 2 or len(np.unique(y[is_u])) < 2:
                continue
                
            for bb in BACKBONES:
                s_base = split_data[split]["models"][bb]["base"][sampled_indices]
                s_pow = split_data[split]["models"][bb]["power"][sampled_indices]
                s_wsum = split_data[split]["models"][bb]["wsum"][sampled_indices]
                
                b_u = roc_auc_score(y[is_u], s_base[is_u])
                p_u = roc_auc_score(y[is_u], s_pow[is_u])
                w_u = roc_auc_score(y[is_u], s_wsum[is_u])
                
                b_s = roc_auc_score(y[is_s], s_base[is_s])
                p_s = roc_auc_score(y[is_s], s_pow[is_s])
                w_s = roc_auc_score(y[is_s], s_wsum[is_s])
                
                macro_diff_unseen[bb].append(w_u - p_u)
                macro_diff_seen[bb].append(w_s - p_s)
                
                macro_gain_unseen[bb]["power"].append(p_u - b_u)
                macro_gain_unseen[bb]["wsum"].append(w_u - b_u)
                
                macro_gain_seen[bb]["power"].append(p_s - b_s)
                macro_gain_seen[bb]["wsum"].append(w_s - b_s)
                
        for bb in BACKBONES:
            if macro_diff_unseen[bb]:
                boot_diffs[bb]["unseen"].append(np.mean(macro_diff_unseen[bb]))
                boot_diffs[bb]["seen"].append(np.mean(macro_diff_seen[bb]))
                boot_unseen_gains[bb]["power"].append(np.mean(macro_gain_unseen[bb]["power"]))
                boot_unseen_gains[bb]["wsum"].append(np.mean(macro_gain_unseen[bb]["wsum"]))
                boot_seen_drops[bb]["power"].append(np.mean(macro_gain_seen[bb]["power"]))
                boot_seen_drops[bb]["wsum"].append(np.mean(macro_gain_seen[bb]["wsum"]))

    print("=== 2,000 PAIRED CLUSTER BOOTSTRAP RESULTS ===")
    for bb in BACKBONES:
        diff_u = np.array(boot_diffs[bb]["unseen"])
        diff_s = np.array(boot_diffs[bb]["seen"])
        ci_diff_u = np.percentile(diff_u, [2.5, 97.5])
        ci_diff_s = np.percentile(diff_s, [2.5, 97.5])
        
        gain_pow = np.array(boot_unseen_gains[bb]["power"])
        gain_wsum = np.array(boot_unseen_gains[bb]["wsum"])
        ci_gain_pow = np.percentile(gain_pow, [2.5, 97.5])
        ci_gain_wsum = np.percentile(gain_wsum, [2.5, 97.5])
        
        drop_pow = np.array(boot_seen_drops[bb]["power"])
        drop_wsum = np.array(boot_seen_drops[bb]["wsum"])
        ci_drop_pow = np.percentile(drop_pow, [2.5, 97.5])
        ci_drop_wsum = np.percentile(drop_wsum, [2.5, 97.5])
        
        print(f"\n--- {bb.upper()} ---")
        print(f"Unseen Gain PowerProd: {np.mean(gain_pow)*100:+.2f}pp 95%CI [{ci_gain_pow[0]*100:+.2f}, {ci_gain_pow[1]*100:+.2f}]")
        print(f"Unseen Gain WSum     : {np.mean(gain_wsum)*100:+.2f}pp 95%CI [{ci_gain_wsum[0]*100:+.2f}, {ci_gain_wsum[1]*100:+.2f}]")
        print(f"Seen Change PowerProd: {np.mean(drop_pow)*100:+.2f}pp 95%CI [{ci_drop_pow[0]*100:+.2f}, {ci_drop_pow[1]*100:+.2f}]")
        print(f"Seen Change WSum     : {np.mean(drop_wsum)*100:+.2f}pp 95%CI [{ci_drop_wsum[0]*100:+.2f}, {ci_drop_wsum[1]*100:+.2f}]")
        print(f"Paired Diff (WSum - Power) Unseen: {np.mean(diff_u)*100:+.2f}pp 95%CI [{ci_diff_u[0]*100:+.2f}, {ci_diff_u[1]*100:+.2f}]")
        print(f"Paired Diff (WSum - Power) Seen  : {np.mean(diff_s)*100:+.2f}pp 95%CI [{ci_diff_s[0]*100:+.2f}, {ci_diff_s[1]*100:+.2f}]")

if __name__ == "__main__":
    main()
