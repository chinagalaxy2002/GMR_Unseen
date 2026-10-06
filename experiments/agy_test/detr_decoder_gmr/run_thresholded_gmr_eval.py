#!/usr/bin/env python3
"""
Seen-Validation Threshold Selection and Evaluation Script.
Selects binary decision threshold tau* maximizing Balanced Accuracy on Seen validation.
Applies tau* to test set to compute Rej-F1, Rejection Rate (RR), S+ FRR, U+ FRR, and G-mIoU@1.
"""
import sys
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

BASE = ROOT / "experiments/agy_test/detr_decoder_gmr"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {
    "moment": ("moment", 1, "moment_detr_gmr_test_submission.jsonl"),
    "qd": ("qd", 2, "qd_detr_gmr_test_submission.jsonl"),
    "flash": ("flash", 0, "hl_test_submission.jsonl")
}

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
    results = {bb: {arm: {"rej_f1": [], "rr": [], "s_frr": [], "u_frr": [], "gmiou1": []}
                   for arm in ["baseline", "power", "wsum"]}
               for bb in BACKBONES}

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
        
        gt_by_qid = {str(r["qid"]): r.get("relevant_windows", []) for r in te_rows}
        
        for bb_key, (bb_dir, col, sub_fn) in BACKBONES.items():
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
            
            sub_path = ROOT / f"results/semantic_existence/multi_split_v2/{split}/{bb_dir}/test/{sub_fn}"
            sub_rows = {str(r["qid"]): r for r in rows(sub_path)}
            
            for arm in ["baseline", "power", "wsum"]:
                th = find_best_threshold(y_val, arms_val[arm])
                sc = arms_te[arm]
                accept = sc >= th
                
                tp = int(np.sum((y_te == 1) & accept))
                fn = int(np.sum((y_te == 1) & ~accept))
                tn = int(np.sum((y_te == 0) & ~accept))
                fp = int(np.sum((y_te == 0) & accept))
                
                rej_p = tn / (tn + fn) if (tn + fn) > 0 else 0
                rej_r = tn / (tn + fp) if (tn + fp) > 0 else 0
                rej_f1 = 2 * rej_p * rej_r / (rej_p + rej_r) if (rej_p + rej_r) > 0 else 0
                rr = (tn + fn) / len(y_te)
                
                s_plus = (parts_te == "S+")
                s_frr = float(np.sum(~accept[s_plus]) / np.sum(s_plus)) if np.sum(s_plus) > 0 else 0
                
                u_plus = (parts_te == "U+")
                u_frr = float(np.sum(~accept[u_plus]) / np.sum(u_plus)) if np.sum(u_plus) > 0 else 0
                
                gmiou_scores = []
                for q, acc in zip(te["qids"], accept):
                    sq = str(q)
                    gt = gt_by_qid.get(sq, [])
                    if not acc:
                        pred_wins = []
                    else:
                        raw_wins = sub_rows.get(sq, {}).get("pred_relevant_windows", [])
                        clean_wins = _clean_pred_windows(raw_wins, max_pred_windows=1)
                        pred_wins = [[w[0], w[1]] for w in clean_wins[:1]]
                    gmiou_scores.append(_compute_set_iou_score(pred_wins, gt))
                gmiou1 = float(np.mean(gmiou_scores)) * 100
                
                results[bb_key][arm]["rej_f1"].append(rej_f1 * 100)
                results[bb_key][arm]["rr"].append(rr * 100)
                results[bb_key][arm]["s_frr"].append(s_frr * 100)
                results[bb_key][arm]["u_frr"].append(u_frr * 100)
                results[bb_key][arm]["gmiou1"].append(gmiou1)

    print("=== THRESHOLDED EVALUATION (Seen-Val Selected Threshold, Macro Across 5 Splits) ===")
    print("%-8s | %-10s | %-10s | %-8s | %-8s | %-8s | %-10s" % ("Backbone", "Arm", "Rej-F1(%)", "RR(%)", "S+FRR(%)", "U+FRR(%)", "G-mIoU@1(%)"))
    print("-" * 75)
    for bb in BACKBONES:
        for arm in ["baseline", "power", "wsum"]:
            f1 = np.mean(results[bb][arm]["rej_f1"])
            rr = np.mean(results[bb][arm]["rr"])
            s_frr = np.mean(results[bb][arm]["s_frr"])
            u_frr = np.mean(results[bb][arm]["u_frr"])
            gm = np.mean(results[bb][arm]["gmiou1"])
            print("%-8s | %-10s | %10.2f | %8.2f | %8.2f | %8.2f | %10.2f" % (bb.upper(), arm, f1, rr, s_frr, u_frr, gm))
        print("-" * 75)

if __name__ == "__main__":
    main()
