#!/usr/bin/env python3
"""
2,000-Replicate Joint Video Cluster Bootstrap Statistical Test for CoG-Verifier.
Preserves cross-split video correlation (1,164 common videos across 5 splits).

Evaluates 6 core hypotheses:
1. Reduction in U+ False Rejection Rate (少拒绝陌生真事件): Delta > 0
2. Gain in U- Negative Recall (多拒绝虚假伪事件): Delta > 0
3. Gain in U+ Gated Recall@1 (IoU >= 0.5) (精准输出好片段): Delta > 0
4. Gain in U+ G-mIoU@1 (高品质输出好片段): Delta > 0
5. Gain in Unseen Rej-F1: Delta > 0
6. Gain in Unseen AUROC: Delta > 0
"""

import sys
import json
import time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

WORK_DIR = Path(__file__).resolve().parent
BASE_CACHE = ROOT / "experiments/agy_test/detr_decoder_gmr/cache"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {
    "moment": {"name": "Moment-DETR", "dir": "moment", "col": 1, "sub_fn": "moment_detr_gmr_test_submission.jsonl"},
    "qd": {"name": "QD-DETR", "dir": "qd", "col": 2, "sub_fn": "qd_detr_gmr_test_submission.jsonl"},
    "flash": {"name": "FlashVTG", "dir": "flash", "col": 0, "sub_fn": "hl_test_submission.jsonl"}
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

def precompute_data(eps_guard=0.04):
    split_data = {}
    all_vids = set()

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

        ev_tr = route_evidence(tr_q, tr["X"])
        ev_val = route_evidence(val_q, val["X"])
        ev_te = route_evidence(te_q, te["X"])

        r_ev_val = np.zeros_like(ev_val)
        r_ev_te = np.zeros_like(ev_te)
        for b in ["kinetic", "interaction", "transitional"]:
            tr_m = tr_b == b
            val_m = val_b == b
            te_m = te_b == b
            r_ev_val[val_m] = cdf(ev_tr[tr_m], ev_val[val_m])
            r_ev_te[te_m] = cdf(ev_tr[tr_m], ev_te[te_m])

        gt_by_qid = {str(r["qid"]): r.get("relevant_windows", []) for r in te_rows}

        bb_models = {}
        bb_thresholds = {}
        bb_raw_ious = {}

        for bb, cfg in BACKBONES.items():
            col = cfg["col"]
            det_tr = tr["X"][:, col]
            det_val = val["X"][:, col]
            det_te = te["X"][:, col]

            r_det_val = cdf(det_tr, det_val)
            r_det_te = cdf(det_tr, det_te)

            th_base = find_best_threshold(val["labels"], det_val)
            base_val_tpr = np.mean((det_val >= th_base)[val["labels"] == 1])

            sc_val_cog = 0.5 * r_det_val + 0.5 * r_ev_val
            sc_te_cog = 0.5 * r_det_te + 0.5 * r_ev_te

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

            sub_path = ROOT / f"results/semantic_existence/multi_split_v2/{split}/{cfg['dir']}/test/{cfg['sub_fn']}"
            sub_rows = {str(r["qid"]): r for r in rows(sub_path)}

            ious = np.zeros(len(te["qids"]), dtype=np.float32)
            for i, q in enumerate(te["qids"]):
                sq = str(q)
                gt = gt_by_qid.get(sq, [])
                raw_wins = sub_rows.get(sq, {}).get("pred_relevant_windows", [])
                clean_wins = _clean_pred_windows(raw_wins, max_pred_windows=1)
                pred_wins = [[w[0], w[1]] for w in clean_wins[:1]]
                ious[i] = _compute_set_iou_score(pred_wins, gt)

            bb_models[bb] = {
                "base_score": det_te,
                "cog_score": sc_te_cog,
            }
            bb_thresholds[bb] = {
                "base_th": th_base,
                "cog_th": th_cog,
            }
            bb_raw_ious[bb] = ious

        vids_te = np.array(list(map(str, te["vids"])))
        all_vids.update(vids_te)

        split_data[split] = {
            "vids": vids_te,
            "labels": te["labels"],
            "partitions": te["partitions"],
            "models": bb_models,
            "thresholds": bb_thresholds,
            "raw_ious": bb_raw_ious,
            "vid_to_idx": {v: np.where(vids_te == v)[0] for v in np.unique(vids_te)}
        }

    return split_data, sorted(list(all_vids))

def run_joint_bootstrap(N_BOOT=2000, seed=3407, eps_guard=0.04):
    print(f"Precomputing split data for {len(SPLITS)} splits and {len(BACKBONES)} backbones...")
    t0 = time.time()
    split_data, unique_vids_list = precompute_data(eps_guard=eps_guard)
    unique_vids = np.array(unique_vids_list)
    print(f"Precomputation complete in {time.time() - t0:.2f}s. Total unique videos: {len(unique_vids)}")

    rng = np.random.RandomState(seed)

    # 6 Target Statistics to Track
    metrics = [
        "u_frr_reduction",      # U+ FRR: Base - CoG (positive = good, fewer true events killed)
        "u_neg_rec_gain",       # U- NegRec: CoG - Base (positive = good, more fake events rejected)
        "u_rec05_gain",         # U+ R@1(0.5): CoG - Base (positive = good, more moments accurate)
        "u_gmiou_gain",         # U+ G-mIoU: CoG - Base (positive = good, higher mIoU)
        "u_rej_f1_gain",        # Unseen Rej-F1: CoG - Base
        "u_auc_gain"            # Unseen AUROC: CoG - Base
    ]

    boot_draws = {bb: {m: [] for m in metrics} for bb in BACKBONES}

    print(f"\nRunning {N_BOOT} Joint Paired Video Cluster Bootstrap Draws (Seed={seed})...")
    t_boot = time.time()

    for b in range(N_BOOT):
        sampled_vids = rng.choice(unique_vids, size=len(unique_vids), replace=True)
        vid_counts = {}
        for v in sampled_vids:
            vid_counts[v] = vid_counts.get(v, 0) + 1

        macro_draw = {bb: {m: [] for m in metrics} for bb in BACKBONES}

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

            parts = sd["partitions"][indices]
            is_u_pos = (parts == "U+")
            is_u_neg = (parts == "U-")
            is_u = is_u_pos | is_u_neg

            if np.sum(is_u_pos) == 0 or np.sum(is_u_neg) == 0:
                continue

            y_u = (parts[is_u] == "U+").astype(int)

            for bb in BACKBONES:
                sc_base = sd["models"][bb]["base_score"][indices]
                sc_cog = sd["models"][bb]["cog_score"][indices]
                th_b = sd["thresholds"][bb]["base_th"]
                th_c = sd["thresholds"][bb]["cog_th"]
                raw_iou = sd["raw_ious"][bb][indices]

                # Decisions
                acc_b = sc_base >= th_b
                acc_c = sc_cog >= th_c

                # 1. U+ FRR
                frr_b = np.mean(~acc_b[is_u_pos]) * 100
                frr_c = np.mean(~acc_c[is_u_pos]) * 100
                diff_frr = frr_b - frr_c # positive = reduction in false rejection

                # 2. U- Neg Recall
                nrec_b = np.mean(~acc_b[is_u_neg]) * 100
                nrec_c = np.mean(~acc_c[is_u_neg]) * 100
                diff_nrec = nrec_c - nrec_b # positive = increase in negative rejection

                # 3. U+ Gated R@1 (0.5)
                # Gated IoU is raw_iou if accepted, 0.0 otherwise
                gated_iou_b = np.where(acc_b[is_u_pos], raw_iou[is_u_pos], 0.0)
                gated_iou_c = np.where(acc_c[is_u_pos], raw_iou[is_u_pos], 0.0)
                rec05_b = np.mean(gated_iou_b >= 0.5) * 100
                rec05_c = np.mean(gated_iou_c >= 0.5) * 100
                diff_rec05 = rec05_c - rec05_b

                # 4. U+ G-mIoU
                gmiou_b = np.mean(gated_iou_b) * 100
                gmiou_c = np.mean(gated_iou_c) * 100
                diff_gmiou = gmiou_c - gmiou_b

                # 5. Unseen Rej-F1
                rej_b_u = ~acc_b[is_u]
                rej_c_u = ~acc_c[is_u]
                f1_b = f1_score(1 - y_u, rej_b_u, zero_division=0) * 100
                f1_c = f1_score(1 - y_u, rej_c_u, zero_division=0) * 100
                diff_f1 = f1_c - f1_b

                # 6. Unseen AUROC
                auc_b = roc_auc_score(y_u, sc_base[is_u]) * 100
                auc_c = roc_auc_score(y_u, sc_cog[is_u]) * 100
                diff_auc = auc_c - auc_b

                macro_draw[bb]["u_frr_reduction"].append(diff_frr)
                macro_draw[bb]["u_neg_rec_gain"].append(diff_nrec)
                macro_draw[bb]["u_rec05_gain"].append(diff_rec05)
                macro_draw[bb]["u_gmiou_gain"].append(diff_gmiou)
                macro_draw[bb]["u_rej_f1_gain"].append(diff_f1)
                macro_draw[bb]["u_auc_gain"].append(diff_auc)

        for bb in BACKBONES:
            for m in metrics:
                boot_draws[bb][m].append(float(np.mean(macro_draw[bb][m])))

        if (b + 1) % 500 == 0:
            print(f"  Draw {b + 1}/{N_BOOT} complete ({time.time() - t_boot:.1f}s)")

    print(f"\nBootstrap completed in {time.time() - t_boot:.1f}s.")

    # Compute Statistics
    report_dict = {}
    print("\n" + "=" * 90)
    print("JOINT VIDEO CLUSTER BOOTSTRAP SIGNIFICANCE REPORT (2,000 DRAWS)")
    print("=" * 90)

    for bb, cfg in BACKBONES.items():
        bb_name = cfg["name"]
        print(f"\n--- {bb_name.upper()} ---")
        report_dict[bb] = {}
        for m in metrics:
            arr = np.array(boot_draws[bb][m])
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr))
            ci_low = float(np.percentile(arr, 2.5))
            ci_high = float(np.percentile(arr, 97.5))
            p_val = float(np.mean(arr <= 0)) if mean_val > 0 else float(np.mean(arr >= 0))
            is_sig = ci_low > 0

            report_dict[bb][m] = {
                "mean": mean_val,
                "std": std_val,
                "ci_95": [ci_low, ci_high],
                "p_value": p_val,
                "significant": is_sig
            }

            sig_str = "YES (p < 0.05)" if is_sig else "NO"
            print(f"  {m:20s}: Mean = {mean_val:+6.2f} pp | 95% CI: [{ci_low:+6.2f}, {ci_high:+6.2f}] | Sig > 0: {sig_str}")

    out_file = WORK_DIR / "bootstrap_significance_summary.json"
    out_file.write_text(json.dumps(report_dict, indent=2))
    print(f"\nSaved bootstrap significance summary to: {out_file}")
    return report_dict

if __name__ == "__main__":
    run_joint_bootstrap(N_BOOT=2000, seed=3407, eps_guard=0.04)
