#!/usr/bin/env python3
"""
P1 Mechanism and Evidence Stream Ablations Script.
Evaluates single feature streams, unified static weights, unrouted evidence,
and directional sign removal across all 5 splits on 3 backbones.
Protocol: Fixed Seen Training CDF, Preserving Average Ties.
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

def route_evidence(queries, X, no_route=False, no_dir=False):
    s_ev = np.zeros(len(queries), dtype=np.float32)
    for i, q in enumerate(queries):
        if no_route:
            s_ev[i] = 0.4 * X[i, 5] + 0.3 * X[i, 3] + 0.3 * X[i, 8]
        else:
            if any(w in q for w in ["run", "walk", "slow", "fast"]):
                dir_feat = 0.0 if no_dir else X[i, 12]
                s_ev[i] = 0.50 * X[i, 5] + 0.35 * X[i, 8] + (0.15 * dir_feat if not no_dir else 0.15 * X[i, 5])
            elif any(w in q for w in ["chair", "couch", "bed", "sofa", "box", "cabinet", "shelf", "table", "cup", "book"]):
                s_ev[i] = 0.45 * X[i, 5] + 0.35 * X[i, 6] + 0.20 * X[i, 3]
            else:
                dir_feat = 0.0 if no_dir else X[i, 12]
                s_ev[i] = 0.55 * X[i, 5] + 0.30 * X[i, 3] + (0.15 * dir_feat if not no_dir else 0.15 * X[i, 5])
    return s_ev

def main():
    variants = [
        "baseline_det",
        "evidence_only",
        "unweighted_prod",
        "min_fusion",
        "weighted_sum_0.5",
        "power_prod_0.65_0.85",
        "unrouted_wsum",
        "nodir_wsum",
    ]

    results = {bb: {v: {"seen": [], "unseen": [], "gap": []} for v in variants} for bb in BACKBONES}

    for split in SPLITS:
        tr = np.load(BASE / "cache" / split / "train.npz")
        te = np.load(BASE / "cache" / split / "test.npz")
        tr_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/train.jsonl")
        te_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/test.jsonl")
        
        tr_q = [r["query"].lower() for r in tr_rows]
        te_q = [r["query"].lower() for r in te_rows]
        
        is_s = np.isin(te["partitions"], ["S+", "S-"])
        is_u = np.isin(te["partitions"], ["U+", "U-"])
        y = te["labels"]
        
        ev_tr = route_evidence(tr_q, tr["X"])
        ev_te = route_evidence(te_q, te["X"])
        r_ev = cdf(ev_tr, ev_te)
        
        ev_tr_un = route_evidence(tr_q, tr["X"], no_route=True)
        ev_te_un = route_evidence(te_q, te["X"], no_route=True)
        r_ev_un = cdf(ev_tr_un, ev_te_un)
        
        ev_tr_nd = route_evidence(tr_q, tr["X"], no_dir=True)
        ev_te_nd = route_evidence(te_q, te["X"], no_dir=True)
        r_ev_nd = cdf(ev_tr_nd, ev_te_nd)
        
        for bb, col in BACKBONES.items():
            det_tr = tr["X"][:, col]
            det_te = te["X"][:, col]
            r_det = cdf(det_tr, det_te)
            
            scores = {
                "baseline_det": det_te,
                "evidence_only": r_ev,
                "unweighted_prod": r_det * r_ev,
                "min_fusion": np.minimum(r_det, r_ev),
                "weighted_sum_0.5": 0.5 * r_det + 0.5 * r_ev,
                "power_prod_0.65_0.85": (r_det ** 0.65) * (r_ev ** 0.85),
                "unrouted_wsum": 0.5 * r_det + 0.5 * r_ev_un,
                "nodir_wsum": 0.5 * r_det + 0.5 * r_ev_nd,
            }
            
            for v, sc in scores.items():
                s_auc = roc_auc_score(y[is_s], sc[is_s])
                u_auc = roc_auc_score(y[is_u], sc[is_u])
                results[bb][v]["seen"].append(s_auc)
                results[bb][v]["unseen"].append(u_auc)
                results[bb][v]["gap"].append(s_auc - u_auc)

    print("=== MECHANISM AND EVIDENCE ABLATION SUMMARY (Macro Across 5 Splits, Fixed Train CDF) ===")
    print("%-22s | %-11s %-13s | %-8s %-10s | %-10s %-12s" % ("Variant", "Moment Seen", "Moment Unseen", "QD Seen", "QD Unseen", "Flash Seen", "Flash Unseen"))
    print("-" * 75)

    for v in variants:
        m_s = np.mean(results["moment"][v]["seen"])
        m_u = np.mean(results["moment"][v]["unseen"])
        q_s = np.mean(results["qd"][v]["seen"])
        q_u = np.mean(results["qd"][v]["unseen"])
        f_s = np.mean(results["flash"][v]["seen"])
        f_u = np.mean(results["flash"][v]["unseen"])
        print("%-22s | %.4f      %.4f        | %.4f   %.4f     | %.4f     %.4f" % (v, m_s, m_u, q_s, q_u, f_s, f_u))

if __name__ == "__main__":
    main()
