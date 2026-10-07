#!/usr/bin/env python3
"""
Co-Generalization Verifier (CoG-Verifier) for Generalized Moment Retrieval (GMR).
Solves the co-generalization challenge across 5 frozen splits (A1, A2_alt, A3, C1, C2_alt)
and 3 diverse backbones (Moment-DETR, QD-DETR, FlashVTG).

Core Principles:
1. Multi-Stream Semantic Evidence Calibration:
   Routes evidence according to query semantic stream (kinetic, interaction, transitional)
   and standardizes reference quantiles strictly within each stream reference distribution.
2. Iso-Sensitivity Validation Guard (Seen-Val Only):
   Chooses decision threshold strictly on Seen validation set to preserve detector
   sensitivity (TPR) while maximizing negative rejection. Zero Unseen label leakage.
3. Simultaneous 3-Way Generalization:
   - 少拒绝陌生真事件: Lower U+ False Rejection Rate (FRR)
   - 多拒绝虚假伪事件: Higher U- Negative Recall and Unseen Rej-F1
   - 精准输出好片段: Higher U+ Gated Recall@1 (IoU >= 0.5, >= 0.3) and G-mIoU
"""

import sys
import json
import time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

WORK_DIR = Path(__file__).resolve().parent
BASE_CACHE = ROOT / "experiments/agy_test/detr_decoder_gmr/cache"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {
    "moment": {
        "name": "Moment-DETR",
        "dir": "moment",
        "col": 1,
        "sub_fn": "moment_detr_gmr_test_submission.jsonl"
    },
    "qd": {
        "name": "QD-DETR",
        "dir": "qd",
        "col": 2,
        "sub_fn": "qd_detr_gmr_test_submission.jsonl"
    },
    "flash": {
        "name": "FlashVTG",
        "dir": "flash",
        "col": 0,
        "sub_fn": "hl_test_submission.jsonl"
    }
}

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def get_branch(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["run", "walk", "slow", "fast"]):
        return "kinetic"
    elif any(w in q for w in ["chair", "couch", "bed", "sofa", "box", "cabinet", "shelf", "table", "cup", "book"]):
        return "interaction"
    else:
        return "transitional"

def route_evidence(queries, X):
    s_ev = np.zeros(len(queries), dtype=np.float32)
    for i, q in enumerate(queries):
        b = get_branch(q)
        if b == "kinetic":
            s_ev[i] = 0.50 * X[i, 5] + 0.35 * X[i, 8] + 0.15 * X[i, 12]
        elif b == "interaction":
            s_ev[i] = 0.45 * X[i, 5] + 0.35 * X[i, 6] + 0.20 * X[i, 3]
        else:
            s_ev[i] = 0.55 * X[i, 5] + 0.30 * X[i, 3] + 0.15 * X[i, 12]
    return s_ev

def cdf(ref, val):
    ref = np.sort(ref)
    return (np.searchsorted(ref, val, "left") + np.searchsorted(ref, val, "right")) / (2.0 * len(ref))

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

def run_evaluation(eps_guard: float = 0.04):
    out_records = {}
    detailed_metrics = {bb_key: {"baseline": {}, "cog": {}} for bb_key in BACKBONES}

    print("=" * 85)
    print(f"RUNNING CO-GENERALIZATION VERIFIER EVALUATION (Eps Guard = +{eps_guard:.2f})")
    print("=" * 85)

    for bb_key, bb_cfg in BACKBONES.items():
        bb_name = bb_cfg["name"]
        bb_dir = bb_cfg["dir"]
        col = bb_cfg["col"]
        sub_fn = bb_cfg["sub_fn"]

        print(f"\n>>> Processing Backbone: {bb_name.upper()} <<<")
        out_records[bb_key] = {}

        for arm in ["baseline", "cog"]:
            detailed_metrics[bb_key][arm] = {
                "u_neg_rec": [],
                "u_pos_frr": [],
                "u_rec05": [],
                "u_rec03": [],
                "u_gmiou": [],
                "u_rej_f1": [],
                "u_auc": [],
                "s_auc": [],
                "s_neg_rec": [],
                "s_pos_frr": [],
                "s_rec05": [],
                "s_gmiou": [],
                "all_rej_f1": [],
                "all_rr": [],
                "all_gmiou": []
            }

        for split in SPLITS:
            tr = np.load(BASE_CACHE / split / "train.npz")
            val = np.load(BASE_CACHE / split / "val.npz")
            te = np.load(BASE_CACHE / split / "test.npz")

            tr_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/train.jsonl")
            val_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/val.jsonl")
            te_rows = rows(ROOT / f"data/release/semantic_existence_v2/{split}/test.jsonl")

            tr_q = [r["query"].lower() for r in tr_rows]
            val_q = [r["query"].lower() for r in val_rows if r["partition"] in ["S+", "S-"]]
            te_q = [r["query"].lower() for r in te_rows]

            tr_b = np.array([get_branch(q) for q in tr_q])
            val_b = np.array([get_branch(q) for q in val_q])
            te_b = np.array([get_branch(q) for q in te_q])

            # Route Evidence
            ev_tr = route_evidence(tr_q, tr["X"])
            ev_val = route_evidence(val_q, val["X"])
            ev_te = route_evidence(te_q, te["X"])

            # Branch-Conditioned Reference Calibration
            r_ev_val = np.zeros_like(ev_val)
            r_ev_te = np.zeros_like(ev_te)
            for b in ["kinetic", "interaction", "transitional"]:
                tr_m = tr_b == b
                val_m = val_b == b
                te_m = te_b == b
                r_ev_val[val_m] = cdf(ev_tr[tr_m], ev_val[val_m])
                r_ev_te[te_m] = cdf(ev_tr[tr_m], ev_te[te_m])

            det_tr = tr["X"][:, col]
            det_val = val["X"][:, col]
            det_te = te["X"][:, col]

            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            # Baseline Seen-Val Threshold
            th_base = find_best_threshold(val["labels"], det_val)
            base_val_tpr = np.mean((det_val >= th_base)[val["labels"] == 1])

            # CoG Verification Score
            sc_val_cog = 0.5 * r_det_val + 0.5 * r_ev_val
            sc_te_cog = 0.5 * r_det_te + 0.5 * r_ev_te

            # Iso-Sensitivity Guarded Threshold Selection on Seen-Val
            target_tpr = min(0.95, base_val_tpr + eps_guard)
            th_candidates = np.percentile(sc_val_cog, np.linspace(1, 99, 197))
            th_cog = th_candidates[0]
            best_diff = 999.0
            for cand in th_candidates:
                val_tpr = np.mean((sc_val_cog >= cand)[val["labels"] == 1])
                diff = abs(val_tpr - target_tpr)
                if diff < best_diff:
                    best_diff = diff
                    th_cog = cand

            sub_path = ROOT / f"results/semantic_existence/multi_split_v2/{split}/{bb_dir}/test/{sub_fn}"
            sub_rows = {str(r["qid"]): r for r in rows(sub_path)}
            gt_by_qid = {str(r["qid"]): r.get("relevant_windows", []) for r in te_rows}

            parts = te["partitions"]
            y_te = te["labels"]
            u_neg_m = (parts == "U-")
            u_pos_m = (parts == "U+")
            u_m = u_neg_m | u_pos_m
            s_neg_m = (parts == "S-")
            s_pos_m = (parts == "S+")
            s_m = s_neg_m | s_pos_m

            for arm in ["baseline", "cog"]:
                if arm == "baseline":
                    sc = det_te
                    th = th_base
                else:
                    sc = sc_te_cog
                    th = th_cog

                accept = sc >= th

                # Unseen Existence Metrics
                u_neg_recall = float(np.sum(~accept[u_neg_m]) / np.sum(u_neg_m) * 100)
                u_pos_frr = float(np.sum(~accept[u_pos_m]) / np.sum(u_pos_m) * 100)
                u_auc = float(roc_auc_score((parts[u_m] == "U+").astype(int), sc[u_m]) * 100)
                s_auc = float(roc_auc_score((parts[s_m] == "S+").astype(int), sc[s_m]) * 100)

                # Unseen Rej-F1
                acc_u = accept[u_m]
                y_u = (parts[u_m] == "U+").astype(int)
                tn_u = int(np.sum((y_u == 0) & ~acc_u))
                fn_u = int(np.sum((y_u == 1) & ~acc_u))
                fp_u = int(np.sum((y_u == 0) & acc_u))
                p_u = tn_u / (tn_u + fn_u) if (tn_u + fn_u) > 0 else 0
                r_u = tn_u / (tn_u + fp_u) if (tn_u + fp_u) > 0 else 0
                u_rej_f1 = float(2 * p_u * r_u / (p_u + r_u) * 100) if (p_u + r_u) > 0 else 0.0

                # Seen Existence Metrics
                s_neg_recall = float(np.sum(~accept[s_neg_m]) / np.sum(s_neg_m) * 100)
                s_pos_frr = float(np.sum(~accept[s_pos_m]) / np.sum(s_pos_m) * 100)

                # Localization Metrics (U+ and S+)
                u_rec05_list, u_rec03_list, u_gmiou_list = [], [], []
                s_rec05_list, s_gmiou_list = [], []
                all_gmiou_list = []

                for q, acc, part in zip(te["qids"], accept, parts):
                    sq = str(q)
                    gt = gt_by_qid.get(sq, [])
                    if not acc:
                        pred_wins = []
                    else:
                        raw_wins = sub_rows.get(sq, {}).get("pred_relevant_windows", [])
                        clean_wins = _clean_pred_windows(raw_wins, max_pred_windows=1)
                        pred_wins = [[w[0], w[1]] for w in clean_wins[:1]]
                    iou = _compute_set_iou_score(pred_wins, gt)
                    all_gmiou_list.append(iou)

                    if part == "U+":
                        u_gmiou_list.append(iou)
                        u_rec05_list.append(1.0 if iou >= 0.5 else 0.0)
                        u_rec03_list.append(1.0 if iou >= 0.3 else 0.0)
                    elif part == "S+":
                        s_gmiou_list.append(iou)
                        s_rec05_list.append(1.0 if iou >= 0.5 else 0.0)

                u_rec05 = float(np.mean(u_rec05_list) * 100)
                u_rec03 = float(np.mean(u_rec03_list) * 100)
                u_gmiou = float(np.mean(u_gmiou_list) * 100)
                s_rec05 = float(np.mean(s_rec05_list) * 100)
                s_gmiou = float(np.mean(s_gmiou_list) * 100)
                all_gmiou = float(np.mean(all_gmiou_list) * 100)

                # Overall Metrics
                tn_all = int(np.sum((y_te == 0) & ~accept))
                fn_all = int(np.sum((y_te == 1) & ~accept))
                fp_all = int(np.sum((y_te == 0) & accept))
                p_all = tn_all / (tn_all + fn_all) if (tn_all + fn_all) > 0 else 0
                r_all = tn_all / (tn_all + fp_all) if (tn_all + fp_all) > 0 else 0
                all_rej_f1 = float(2 * p_all * r_all / (p_all + r_all) * 100) if (p_all + r_all) > 0 else 0.0
                all_rr = float((tn_all + fn_all) / len(y_te) * 100)

                # Store metrics
                m = detailed_metrics[bb_key][arm]
                m["u_neg_rec"].append(u_neg_recall)
                m["u_pos_frr"].append(u_pos_frr)
                m["u_rec05"].append(u_rec05)
                m["u_rec03"].append(u_rec03)
                m["u_gmiou"].append(u_gmiou)
                m["u_rej_f1"].append(u_rej_f1)
                m["u_auc"].append(u_auc)
                m["s_auc"].append(s_auc)
                m["s_neg_rec"].append(s_neg_recall)
                m["s_pos_frr"].append(s_pos_frr)
                m["s_rec05"].append(s_rec05)
                m["s_gmiou"].append(s_gmiou)
                m["all_rej_f1"].append(all_rej_f1)
                m["all_rr"].append(all_rr)
                m["all_gmiou"].append(all_gmiou)

    return detailed_metrics

def print_summary(detailed_metrics):
    print("\n" + "=" * 105)
    print("MACRO BENCHMARK RESULTS ACROSS 5 FROZEN SPLITS (A1, A2_alt, A3, C1, C2_alt)")
    print("=" * 105)

    headers = [
        "Backbone", "Method", "U- NegRec(%)", "U+ FRR(%)", "U+ R@1(0.5)",
        "U+ R@1(0.3)", "U+ G-mIoU", "U- Rej-F1", "U- AUC(%)", "S- AUC(%)"
    ]
    row_fmt = "%-12s | %-11s | %12.2f | %9.2f | %11.2f | %11.2f | %9.2f | %9.2f | %9.2f | %9.2f"
    print("%-12s | %-11s | %12s | %9s | %11s | %11s | %9s | %9s | %9s | %9s" % tuple(headers))
    print("-" * 105)

    summary_json = {}

    for bb_key, bb_cfg in BACKBONES.items():
        bb_name = bb_cfg["name"]
        summary_json[bb_key] = {}
        for arm in ["baseline", "cog"]:
            m = detailed_metrics[bb_key][arm]
            row_vals = (
                bb_name if arm == "baseline" else "",
                "Baseline" if arm == "baseline" else "CoG-Verifier",
                np.mean(m["u_neg_rec"]),
                np.mean(m["u_pos_frr"]),
                np.mean(m["u_rec05"]),
                np.mean(m["u_rec03"]),
                np.mean(m["u_gmiou"]),
                np.mean(m["u_rej_f1"]),
                np.mean(m["u_auc"]),
                np.mean(m["s_auc"])
            )
            print(row_fmt % row_vals)
            summary_json[bb_key][arm] = {k: float(np.mean(v)) for k, v in m.items()}
        print("-" * 105)

    # Save benchmark summary
    out_file = WORK_DIR / "benchmark_summary.json"
    out_file.write_text(json.dumps(summary_json, indent=2))
    print(f"\nSaved benchmark summary to: {out_file}")

if __name__ == "__main__":
    metrics = run_evaluation(eps_guard=0.04)
    print_summary(metrics)
