#!/usr/bin/env python3
"""
Comprehensive Ablation and Mechanism Study for CoG-Verifier.

Addresses 4 fundamental scientific questions:
1. Question 1 (Routing Rules): Why these 3 semantic branches?
   - Compares: 3-branch routing vs No routing (unified evidence) vs Scrambled routing vs 2-branch routing.
2. Question 2 (Evidence Weights): Why these evidence channel weights?
   - Compares: Heuristic routed weights vs Equal weights vs Single-channel streams vs Seen-Val learned weights.
3. Question 3 (Two-Stream Ratio): Why 50/50 fusion?
   - Sweeps w_det in [0.0, 0.1, 0.2, ..., 1.0] to test stability and optimality.
4. Question 4 (Threshold vs Evidence): How much gain is from threshold shift vs multimodal evidence?
   - Decouples threshold shift on detector alone vs calibrated verifier at identical operating TPR.
"""

import sys
import json
import time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

WORK_DIR = Path(__file__).resolve().parent
BASE_CACHE = ROOT / "experiments/agy_test/detr_decoder_gmr/cache"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {
    "moment": {"name": "Moment-DETR", "col": 1, "sub_fn": "moment_detr_gmr_test_submission.jsonl", "dir": "moment"},
    "qd": {"name": "QD-DETR", "col": 2, "sub_fn": "qd_detr_gmr_test_submission.jsonl", "dir": "qd"},
    "flash": {"name": "FlashVTG", "col": 0, "sub_fn": "hl_test_submission.jsonl", "dir": "flash"}
}

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def cdf(ref, val):
    ref = np.sort(ref)
    return (np.searchsorted(ref, val, "left") + np.searchsorted(ref, val, "right")) / (2.0 * len(ref))

def get_branch_3(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["run", "walk", "slow", "fast"]):
        return "kinetic"
    elif any(w in q for w in ["chair", "couch", "bed", "sofa", "box", "cabinet", "shelf", "table", "cup", "book"]):
        return "interaction"
    else:
        return "transitional"

def get_branch_2(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["run", "walk", "slow", "fast"]):
        return "kinetic"
    else:
        return "non_kinetic"

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

def find_threshold_by_tpr(scores_val, y_val, target_tpr):
    th_candidates = np.percentile(scores_val, np.linspace(1, 99, 197))
    best_th = th_candidates[0]
    best_diff = 999.0
    for cand in th_candidates:
        val_tpr = np.mean((scores_val >= cand)[y_val == 1])
        diff = abs(val_tpr - target_tpr)
        if diff < best_diff:
            best_diff = diff
            best_th = cand
    return best_th

def load_all_split_data():
    data = {}
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

        gt_by_qid = {str(r["qid"]): r.get("relevant_windows", []) for r in te_rows}

        bb_pred_rows = {}
        for bb, cfg in BACKBONES.items():
            sub_path = ROOT / f"results/semantic_existence/multi_split_v2/{split}/{cfg['dir']}/test/{cfg['sub_fn']}"
            bb_pred_rows[bb] = {str(r["qid"]): r for r in rows(sub_path)}

        data[split] = {
            "tr": tr, "val": val, "te": te,
            "tr_q": tr_q, "val_q": val_q, "te_q": te_q,
            "gt_by_qid": gt_by_qid,
            "bb_pred_rows": bb_pred_rows
        }
    return data

def compute_metrics(accept, sc, te, bb_key, data_split):
    parts = te["partitions"]
    u_neg_m = (parts == "U-")
    u_pos_m = (parts == "U+")
    u_m = u_neg_m | u_pos_m
    y_u = (parts[u_m] == "U+").astype(int)

    u_neg_rec = float(np.sum(~accept[u_neg_m]) / np.sum(u_neg_m) * 100)
    u_pos_frr = float(np.sum(~accept[u_pos_m]) / np.sum(u_pos_m) * 100)
    u_auc = float(roc_auc_score(y_u, sc[u_m]) * 100)

    acc_u = accept[u_m]
    tn_u = int(np.sum((y_u == 0) & ~acc_u))
    fn_u = int(np.sum((y_u == 1) & ~acc_u))
    fp_u = int(np.sum((y_u == 0) & acc_u))
    p_u = tn_u / (tn_u + fn_u) if (tn_u + fn_u) > 0 else 0
    r_u = tn_u / (tn_u + fp_u) if (tn_u + fp_u) > 0 else 0
    u_rej_f1 = float(2 * p_u * r_u / (p_u + r_u) * 100) if (p_u + r_u) > 0 else 0.0

    sub_rows = data_split["bb_pred_rows"][bb_key]
    gt_by_qid = data_split["gt_by_qid"]

    rec05_list, gmiou_list = [], []
    for q, acc_i, part in zip(te["qids"], accept, parts):
        if part != "U+":
            continue
        sq = str(q)
        gt = gt_by_qid.get(sq, [])
        if not acc_i:
            pred_wins = []
        else:
            raw_wins = sub_rows.get(sq, {}).get("pred_relevant_windows", [])
            clean_wins = _clean_pred_windows(raw_wins, max_pred_windows=1)
            pred_wins = [[w[0], w[1]] for w in clean_wins[:1]]
        iou = _compute_set_iou_score(pred_wins, gt)
        gmiou_list.append(iou)
        rec05_list.append(1.0 if iou >= 0.5 else 0.0)

    return {
        "u_neg_rec": u_neg_rec,
        "u_pos_frr": u_pos_frr,
        "u_rec05": float(np.mean(rec05_list) * 100),
        "u_gmiou": float(np.mean(gmiou_list) * 100),
        "u_rej_f1": u_rej_f1,
        "u_auc": u_auc
    }

# =========================================================================
# EXPERIMENT 1: THRESHOLD DECOUPLING (Question 4)
# =========================================================================
def run_threshold_decoupling(all_data):
    print("\n" + "=" * 90)
    print("EXPERIMENT 1: THRESHOLD DECOUPLING ABLATION (Question 4)")
    print("Does positive protection come from threshold shift, or genuine feature gain?")
    print("=" * 90)

    results = {bb: {"base_bacc": [], "base_shifted": [], "cog_bacc": [], "cog_shifted": []} for bb in BACKBONES}

    for split in SPLITS:
        sd = all_data[split]
        tr, val, te = sd["tr"], sd["val"], sd["te"]

        tr_b = np.array([get_branch_3(q) for q in sd["tr_q"]])
        val_b = np.array([get_branch_3(q) for q in sd["val_q"]])
        te_b = np.array([get_branch_3(q) for q in sd["te_q"]])

        ev_tr = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te = np.zeros(len(sd["te_q"]), dtype=np.float32)

        for i, q in enumerate(sd["tr_q"]):
            b = tr_b[i]
            x = tr["X"][i]
            ev_tr[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i, q in enumerate(sd["val_q"]):
            b = val_b[i]
            x = val["X"][i]
            ev_val[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i, q in enumerate(sd["te_q"]):
            b = te_b[i]
            x = te["X"][i]
            ev_te[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))

        r_ev_val = np.zeros_like(ev_val)
        r_ev_te = np.zeros_like(ev_te)
        for b in ["kinetic", "interaction", "transitional"]:
            tr_m = tr_b == b
            val_m = val_b == b
            te_m = te_b == b
            r_ev_val[val_m] = cdf(ev_tr[tr_m], ev_val[val_m])
            r_ev_te[te_m] = cdf(ev_tr[tr_m], ev_te[te_m])

        for bb, cfg in BACKBONES.items():
            col = cfg["col"]
            det_tr = tr["X"][:, col]
            det_val = val["X"][:, col]
            det_te = te["X"][:, col]

            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            sc_val_cog = 0.5 * r_det_val + 0.5 * r_ev_val
            sc_te_cog = 0.5 * r_det_te + 0.5 * r_ev_te

            # 1. Base BAcc
            th_base_bacc = find_best_threshold(val["labels"], det_val)
            base_tpr = np.mean((det_val >= th_base_bacc)[val["labels"] == 1])

            # 2. Base Shifted (Target TPR = base_tpr + 0.04)
            target_tpr = min(0.95, base_tpr + 0.04)
            th_base_shifted = find_threshold_by_tpr(det_val, val["labels"], target_tpr)

            # 3. CoG BAcc
            th_cog_bacc = find_best_threshold(val["labels"], sc_val_cog)

            # 4. CoG Shifted (Iso-Sensitivity Guard)
            th_cog_shifted = find_threshold_by_tpr(sc_val_cog, val["labels"], target_tpr)

            m_b_bacc = compute_metrics(det_te >= th_base_bacc, det_te, te, bb, sd)
            m_b_shf = compute_metrics(det_te >= th_base_shifted, det_te, te, bb, sd)
            m_c_bacc = compute_metrics(sc_te_cog >= th_cog_bacc, sc_te_cog, te, bb, sd)
            m_c_shf = compute_metrics(sc_te_cog >= th_cog_shifted, sc_te_cog, te, bb, sd)

            results[bb]["base_bacc"].append(m_b_bacc)
            results[bb]["base_shifted"].append(m_b_shf)
            results[bb]["cog_bacc"].append(m_c_bacc)
            results[bb]["cog_shifted"].append(m_c_shf)

    # Print Macro Table
    print("%-12s | %-16s | %10s | %10s | %10s | %10s | %10s" % ("Backbone", "Configuration", "U- NegRec", "U+ FRR", "U+ R@1(0.5)", "Unseen RejF1", "Unseen AUC"))
    print("-" * 90)
    for bb in BACKBONES:
        for arm, label in [
            ("base_bacc", "Base + BAcc Thresh"),
            ("base_shifted", "Base + Shifted Thresh"),
            ("cog_bacc", "CoG + BAcc Thresh"),
            ("cog_shifted", "CoG + Guard Thresh (Ours)")
        ]:
            arr = results[bb][arm]
            row = (
                BACKBONES[bb]["name"] if arm == "base_bacc" else "",
                label,
                np.mean([x["u_neg_rec"] for x in arr]),
                np.mean([x["u_pos_frr"] for x in arr]),
                np.mean([x["u_rec05"] for x in arr]),
                np.mean([x["u_rej_f1"] for x in arr]),
                np.mean([x["u_auc"] for x in arr])
            )
            print("%-12s | %-24s | %9.2f%% | %9.2f%% | %10.2f%% | %11.2f%% | %9.2f%%" % row)
        print("-" * 90)
    return results

# =========================================================================
# EXPERIMENT 2: FUSION WEIGHT SWEEP (Question 3)
# =========================================================================
def run_fusion_weight_sweep(all_data):
    print("\n" + "=" * 90)
    print("EXPERIMENT 2: FUSION WEIGHT SWEEP (Question 3)")
    print("Why 50/50? Sweeping w_det from 0.0 (pure evidence) to 1.0 (pure detector)")
    print("=" * 90)

    weights = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    sweep_results = {bb: {w: [] for w in weights} for bb in BACKBONES}

    for split in SPLITS:
        sd = all_data[split]
        tr, val, te = sd["tr"], sd["val"], sd["te"]

        tr_b = np.array([get_branch_3(q) for q in sd["tr_q"]])
        val_b = np.array([get_branch_3(q) for q in sd["val_q"]])
        te_b = np.array([get_branch_3(q) for q in sd["te_q"]])

        ev_tr = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te = np.zeros(len(sd["te_q"]), dtype=np.float32)

        for i, q in enumerate(sd["tr_q"]):
            b = tr_b[i]
            x = tr["X"][i]
            ev_tr[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i, q in enumerate(sd["val_q"]):
            b = val_b[i]
            x = val["X"][i]
            ev_val[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i, q in enumerate(sd["te_q"]):
            b = te_b[i]
            x = te["X"][i]
            ev_te[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))

        r_ev_val = np.zeros_like(ev_val)
        r_ev_te = np.zeros_like(ev_te)
        for b in ["kinetic", "interaction", "transitional"]:
            tr_m = tr_b == b
            val_m = val_b == b
            te_m = te_b == b
            r_ev_val[val_m] = cdf(ev_tr[tr_m], ev_val[val_m])
            r_ev_te[te_m] = cdf(ev_tr[tr_m], ev_te[te_m])

        for bb, cfg in BACKBONES.items():
            col = cfg["col"]
            det_tr = tr["X"][:, col]
            det_val = val["X"][:, col]
            det_te = te["X"][:, col]

            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            th_base = find_best_threshold(val["labels"], det_val)
            base_tpr = np.mean((det_val >= th_base)[val["labels"] == 1])
            target_tpr = min(0.95, base_tpr + 0.04)

            for w in weights:
                sc_val = w * r_det_val + (1.0 - w) * r_ev_val
                sc_te = w * r_det_te + (1.0 - w) * r_ev_te
                th = find_threshold_by_tpr(sc_val, val["labels"], target_tpr)
                m = compute_metrics(sc_te >= th, sc_te, te, bb, sd)
                sweep_results[bb][w].append(m)

    print("%-12s | %-6s | %10s | %10s | %10s | %10s | %10s" % ("Backbone", "w_det", "U- NegRec", "U+ FRR", "U+ R@1(0.5)", "Unseen RejF1", "Unseen AUC"))
    print("-" * 80)
    for bb in BACKBONES:
        for w in weights:
            arr = sweep_results[bb][w]
            row = (
                BACKBONES[bb]["name"] if w == weights[0] else "",
                f"{w:.1f}",
                np.mean([x["u_neg_rec"] for x in arr]),
                np.mean([x["u_pos_frr"] for x in arr]),
                np.mean([x["u_rec05"] for x in arr]),
                np.mean([x["u_rej_f1"] for x in arr]),
                np.mean([x["u_auc"] for x in arr])
            )
            print("%-12s | %-6s | %9.2f%% | %9.2f%% | %10.2f%% | %11.2f%% | %9.2f%%" % row)
        print("-" * 80)
    return sweep_results

# =========================================================================
# EXPERIMENT 3: EVIDENCE WEIGHT & CHANNEL ABLATIONS (Question 2)
# =========================================================================
def run_evidence_weight_ablations(all_data):
    print("\n" + "=" * 90)
    print("EXPERIMENT 3: EVIDENCE WEIGHT & CHANNEL ABLATIONS (Question 2)")
    print("Why these evidence weights? Comparing Heuristic vs Equal vs Single Channels vs Learned")
    print("=" * 90)

    arms = [
        "full_heuristic",      # Current routed weights
        "equal_weights",       # 1/3, 1/3, 1/3 per stream
        "peak_alone",          # CLIP peak frame alone (X[:, 5])
        "obj_align_alone",     # CLIP object alignment alone (X[:, 6])
        "vel_diff_alone",      # SlowFast velocity contrast alone (X[:, 8])
        "learned_val_logistic" # Logistic regression weights fit on Seen-val
    ]
    results = {bb: {arm: [] for arm in arms} for bb in BACKBONES}

    for split in SPLITS:
        sd = all_data[split]
        tr, val, te = sd["tr"], sd["val"], sd["te"]
        tr_b = np.array([get_branch_3(q) for q in sd["tr_q"]])
        val_b = np.array([get_branch_3(q) for q in sd["val_q"]])
        te_b = np.array([get_branch_3(q) for q in sd["te_q"]])

        # 1. Full heuristic
        ev_tr_full = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val_full = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te_full = np.zeros(len(sd["te_q"]), dtype=np.float32)
        for i in range(len(sd["tr_q"])):
            b, x = tr_b[i], tr["X"][i]
            ev_tr_full[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["val_q"])):
            b, x = val_b[i], val["X"][i]
            ev_val_full[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["te_q"])):
            b, x = te_b[i], te["X"][i]
            ev_te_full[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))

        # 2. Equal weights
        ev_tr_eq = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val_eq = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te_eq = np.zeros(len(sd["te_q"]), dtype=np.float32)
        for i in range(len(sd["tr_q"])):
            b, x = tr_b[i], tr["X"][i]
            ev_tr_eq[i] = (x[5] + x[8] + x[12])/3.0 if b == "kinetic" else ((x[5] + x[6] + x[3])/3.0 if b == "interaction" else (x[5] + x[3] + x[12])/3.0)
        for i in range(len(sd["val_q"])):
            b, x = val_b[i], val["X"][i]
            ev_val_eq[i] = (x[5] + x[8] + x[12])/3.0 if b == "kinetic" else ((x[5] + x[6] + x[3])/3.0 if b == "interaction" else (x[5] + x[3] + x[12])/3.0)
        for i in range(len(sd["te_q"])):
            b, x = te_b[i], te["X"][i]
            ev_te_eq[i] = (x[5] + x[8] + x[12])/3.0 if b == "kinetic" else ((x[5] + x[6] + x[3])/3.0 if b == "interaction" else (x[5] + x[3] + x[12])/3.0)

        # 3. Single channels
        ev_tr_peak, ev_val_peak, ev_te_peak = tr["X"][:, 5], val["X"][:, 5], te["X"][:, 5]
        ev_tr_obj, ev_val_obj, ev_te_obj = tr["X"][:, 6], val["X"][:, 6], te["X"][:, 6]
        ev_tr_vel, ev_val_vel, ev_te_vel = tr["X"][:, 8], val["X"][:, 8], te["X"][:, 8]

        # 4. Learned on Seen-Val
        clf = LogisticRegression(max_iter=500, random_state=3407)
        feat_cols = [3, 5, 6, 8, 12]
        clf.fit(val["X"][:, feat_cols], val["labels"])
        ev_tr_lr = clf.predict_proba(tr["X"][:, feat_cols])[:, 1]
        ev_val_lr = clf.predict_proba(val["X"][:, feat_cols])[:, 1]
        ev_te_lr = clf.predict_proba(te["X"][:, feat_cols])[:, 1]

        arm_ev = {
            "full_heuristic": (ev_tr_full, ev_val_full, ev_te_full, True),
            "equal_weights": (ev_tr_eq, ev_val_eq, ev_te_eq, True),
            "peak_alone": (ev_tr_peak, ev_val_peak, ev_te_peak, False),
            "obj_align_alone": (ev_tr_obj, ev_val_obj, ev_te_obj, False),
            "vel_diff_alone": (ev_tr_vel, ev_val_vel, ev_te_vel, False),
            "learned_val_logistic": (ev_tr_lr, ev_val_lr, ev_te_lr, False)
        }

        for bb, cfg in BACKBONES.items():
            col = cfg["col"]
            det_tr, det_val, det_te = tr["X"][:, col], val["X"][:, col], te["X"][:, col]
            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            th_base = find_best_threshold(val["labels"], det_val)
            base_tpr = np.mean((det_val >= th_base)[val["labels"] == 1])
            target_tpr = min(0.95, base_tpr + 0.04)

            for arm in arms:
                etr, eval_, ete, is_branch = arm_ev[arm]
                if is_branch:
                    r_ev_val = np.zeros_like(eval_)
                    r_ev_te = np.zeros_like(ete)
                    for b in ["kinetic", "interaction", "transitional"]:
                        tr_m = tr_b == b
                        val_m = val_b == b
                        te_m = te_b == b
                        r_ev_val[val_m] = cdf(etr[tr_m], eval_[val_m])
                        r_ev_te[te_m] = cdf(etr[tr_m], ete[te_m])
                else:
                    r_ev_val = cdf(etr, eval_)
                    r_ev_te = cdf(etr, ete)

                sc_val = 0.5 * r_det_val + 0.5 * r_ev_val
                sc_te = 0.5 * r_det_te + 0.5 * r_ev_te
                th = find_threshold_by_tpr(sc_val, val["labels"], target_tpr)
                m = compute_metrics(sc_te >= th, sc_te, te, bb, sd)
                results[bb][arm].append(m)

    print("%-12s | %-22s | %10s | %10s | %10s | %10s | %10s" % ("Backbone", "Evidence Scheme", "U- NegRec", "U+ FRR", "U+ R@1(0.5)", "Unseen RejF1", "Unseen AUC"))
    print("-" * 92)
    for bb in BACKBONES:
        for arm in arms:
            arr = results[bb][arm]
            row = (
                BACKBONES[bb]["name"] if arm == arms[0] else "",
                arm,
                np.mean([x["u_neg_rec"] for x in arr]),
                np.mean([x["u_pos_frr"] for x in arr]),
                np.mean([x["u_rec05"] for x in arr]),
                np.mean([x["u_rej_f1"] for x in arr]),
                np.mean([x["u_auc"] for x in arr])
            )
            print("%-12s | %-22s | %9.2f%% | %9.2f%% | %10.2f%% | %11.2f%% | %9.2f%%" % row)
        print("-" * 92)
    return results

# =========================================================================
# EXPERIMENT 4: ROUTING RULE ABLATIONS (Question 1)
# =========================================================================
def run_routing_rule_ablations(all_data):
    print("\n" + "=" * 90)
    print("EXPERIMENT 4: ROUTING RULE ABLATIONS (Question 1)")
    print("Why these 3 routing rules? Comparing 3-Branch vs No-Routing vs Scrambled vs 2-Branch")
    print("=" * 90)

    schemes = [
        "3_branch_routing",  # Standard 3 branches
        "no_routing_unified",# Single fixed combination for all queries
        "scrambled_routing", # Inverted branch assignment (kinetic <-> interaction)
        "2_branch_routing"   # Kinetic vs Non-Kinetic
    ]
    results = {bb: {s: [] for s in schemes} for bb in BACKBONES}

    for split in SPLITS:
        sd = all_data[split]
        tr, val, te = sd["tr"], sd["val"], sd["te"]

        tr_b3 = np.array([get_branch_3(q) for q in sd["tr_q"]])
        val_b3 = np.array([get_branch_3(q) for q in sd["val_q"]])
        te_b3 = np.array([get_branch_3(q) for q in sd["te_q"]])

        # 1. 3-Branch
        ev_tr_3 = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val_3 = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te_3 = np.zeros(len(sd["te_q"]), dtype=np.float32)
        for i in range(len(sd["tr_q"])):
            b, x = tr_b3[i], tr["X"][i]
            ev_tr_3[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["val_q"])):
            b, x = val_b3[i], val["X"][i]
            ev_val_3[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["te_q"])):
            b, x = te_b3[i], te["X"][i]
            ev_te_3[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else ((0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))

        # 2. No Routing (Unified)
        ev_tr_uni = 0.45*tr["X"][:, 5] + 0.20*tr["X"][:, 6] + 0.20*tr["X"][:, 8] + 0.15*tr["X"][:, 3]
        ev_val_uni = 0.45*val["X"][:, 5] + 0.20*val["X"][:, 6] + 0.20*val["X"][:, 8] + 0.15*val["X"][:, 3]
        ev_te_uni = 0.45*te["X"][:, 5] + 0.20*te["X"][:, 6] + 0.20*te["X"][:, 8] + 0.15*te["X"][:, 3]

        # 3. Scrambled (kinetic gets interaction weights, interaction gets kinetic)
        ev_tr_scr = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val_scr = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te_scr = np.zeros(len(sd["te_q"]), dtype=np.float32)
        for i in range(len(sd["tr_q"])):
            b, x = tr_b3[i], tr["X"][i]
            ev_tr_scr[i] = (0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "kinetic" else ((0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["val_q"])):
            b, x = val_b3[i], val["X"][i]
            ev_val_scr[i] = (0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "kinetic" else ((0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))
        for i in range(len(sd["te_q"])):
            b, x = te_b3[i], te["X"][i]
            ev_te_scr[i] = (0.45*x[5] + 0.35*x[6] + 0.20*x[3]) if b == "kinetic" else ((0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "interaction" else (0.55*x[5] + 0.30*x[3] + 0.15*x[12]))

        # 4. 2-Branch (Kinetic vs Non-Kinetic)
        tr_b2 = np.array([get_branch_2(q) for q in sd["tr_q"]])
        val_b2 = np.array([get_branch_2(q) for q in sd["val_q"]])
        te_b2 = np.array([get_branch_2(q) for q in sd["te_q"]])
        ev_tr_2 = np.zeros(len(sd["tr_q"]), dtype=np.float32)
        ev_val_2 = np.zeros(len(sd["val_q"]), dtype=np.float32)
        ev_te_2 = np.zeros(len(sd["te_q"]), dtype=np.float32)
        for i in range(len(sd["tr_q"])):
            b, x = tr_b2[i], tr["X"][i]
            ev_tr_2[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else (0.50*x[5] + 0.30*x[6] + 0.20*x[3])
        for i in range(len(sd["val_q"])):
            b, x = val_b2[i], val["X"][i]
            ev_val_2[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else (0.50*x[5] + 0.30*x[6] + 0.20*x[3])
        for i in range(len(sd["te_q"])):
            b, x = te_b2[i], te["X"][i]
            ev_te_2[i] = (0.50*x[5] + 0.35*x[8] + 0.15*x[12]) if b == "kinetic" else (0.50*x[5] + 0.30*x[6] + 0.20*x[3])

        scheme_ev = {
            "3_branch_routing": (ev_tr_3, ev_val_3, ev_te_3, tr_b3, val_b3, te_b3, ["kinetic", "interaction", "transitional"]),
            "no_routing_unified": (ev_tr_uni, ev_val_uni, ev_te_uni, None, None, None, None),
            "scrambled_routing": (ev_tr_scr, ev_val_scr, ev_te_scr, tr_b3, val_b3, te_b3, ["kinetic", "interaction", "transitional"]),
            "2_branch_routing": (ev_tr_2, ev_val_2, ev_te_2, tr_b2, val_b2, te_b2, ["kinetic", "non_kinetic"])
        }

        for bb, cfg in BACKBONES.items():
            col = cfg["col"]
            det_tr, det_val, det_te = tr["X"][:, col], val["X"][:, col], te["X"][:, col]
            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            th_base = find_best_threshold(val["labels"], det_val)
            base_tpr = np.mean((det_val >= th_base)[val["labels"] == 1])
            target_tpr = min(0.95, base_tpr + 0.04)

            for s in schemes:
                etr, eval_, ete, tr_labels, val_labels, te_labels, b_list = scheme_ev[s]
                if b_list is not None:
                    r_ev_val = np.zeros_like(eval_)
                    r_ev_te = np.zeros_like(ete)
                    for b in b_list:
                        tr_m = tr_labels == b
                        val_m = val_labels == b
                        te_m = te_labels == b
                        r_ev_val[val_m] = cdf(etr[tr_m], eval_[val_m])
                        r_ev_te[te_m] = cdf(etr[tr_m], ete[te_m])
                else:
                    r_ev_val = cdf(etr, eval_)
                    r_ev_te = cdf(etr, ete)

                sc_val = 0.5 * r_det_val + 0.5 * r_ev_val
                sc_te = 0.5 * r_det_te + 0.5 * r_ev_te
                th = find_threshold_by_tpr(sc_val, val["labels"], target_tpr)
                m = compute_metrics(sc_te >= th, sc_te, te, bb, sd)
                results[bb][s].append(m)

    print("%-12s | %-20s | %10s | %10s | %10s | %10s | %10s" % ("Backbone", "Routing Scheme", "U- NegRec", "U+ FRR", "U+ R@1(0.5)", "Unseen RejF1", "Unseen AUC"))
    print("-" * 90)
    for bb in BACKBONES:
        for s in schemes:
            arr = results[bb][s]
            row = (
                BACKBONES[bb]["name"] if s == schemes[0] else "",
                s,
                np.mean([x["u_neg_rec"] for x in arr]),
                np.mean([x["u_pos_frr"] for x in arr]),
                np.mean([x["u_rec05"] for x in arr]),
                np.mean([x["u_rej_f1"] for x in arr]),
                np.mean([x["u_auc"] for x in arr])
            )
            print("%-12s | %-20s | %9.2f%% | %9.2f%% | %10.2f%% | %11.2f%% | %9.2f%%" % row)
        print("-" * 90)
    return results

def main():
    print("Loading data across 5 splits...")
    t0 = time.time()
    all_data = load_all_split_data()
    print(f"Data loaded in {time.time() - t0:.2f}s.")

    res1 = run_threshold_decoupling(all_data)
    res2 = run_fusion_weight_sweep(all_data)
    res3 = run_evidence_weight_ablations(all_data)
    res4 = run_routing_rule_ablations(all_data)

    out_file = WORK_DIR / "ablation_results.json"
    full_output = {
        "exp1_threshold_decoupling": {bb: {k: [{m: float(v) for m, v in x.items()} for x in arr] for k, arr in res1[bb].items()} for bb in BACKBONES},
        "exp2_fusion_weight_sweep": {bb: {str(w): [{m: float(v) for m, v in x.items()} for x in arr] for w, arr in res2[bb].items()} for bb in BACKBONES},
        "exp3_evidence_weight_ablations": {bb: {arm: [{m: float(v) for m, v in x.items()} for x in arr] for arm, arr in res3[bb].items()} for bb in BACKBONES},
        "exp4_routing_rule_ablations": {bb: {s: [{m: float(v) for m, v in x.items()} for x in arr] for s, arr in res4[bb].items()} for bb in BACKBONES}
    }
    out_file.write_text(json.dumps(full_output, indent=2))
    print(f"\nAblation study completed and saved to: {out_file}")

if __name__ == "__main__":
    main()
