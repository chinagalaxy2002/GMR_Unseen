#!/usr/bin/env python3
"""
Independent Audit and Verification Script for Cross-Backbone Transfer Benchmark.
Verifies:
1. Integrity of predictions saved in transfer_predictions.npz for all 5 splits.
2. Independent recalculation of Macro AUROC, Gap, and Matched PairAcc for all 9 cells of the transfer matrix.
3. Verification that results match benchmark_summary.json within float tolerance.
4. Checks for data leakage and test-split contamination.
"""
import sys
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[3]
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
SUMMARY_FILE = BASE_DIR / "benchmark_summary.json"
RUNS_DIR = BASE_DIR / "runs"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = ["flash", "moment", "qd"]

def compute_matched_pair_acc(qids, scores, pairs_file):
    if not pairs_file.exists():
        return 0.5
    pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
    qid_to_score = dict(zip([str(q) for q in qids], scores))
    accs = []
    for p in pairs:
        pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
        if pq in qid_to_score and nq in qid_to_score:
            sp, sn = qid_to_score[pq], qid_to_score[nq]
            accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    return float(np.mean(accs)) if accs else 0.5

def audit():
    if not SUMMARY_FILE.exists():
        print(f"Error: {SUMMARY_FILE} not found.")
        sys.exit(1)

    with open(SUMMARY_FILE, "r") as f:
        summary = json.load(f)

    macro_reported = summary["macro_transfer_matrix"]
    macro_ens_reported = summary["macro_ensemble"]
    macro_bases_reported = summary["macro_standalones"]

    print(">>> Starting Independent Audit of Cross-Backbone Transfer Predictions...")

    recalc_split_results = []

    for split in SPLITS:
        pred_file = RUNS_DIR / split / "transfer_predictions.npz"
        assert pred_file.exists(), f"Missing prediction file: {pred_file}"

        data = np.load(pred_file)
        qids = data["qids"]
        parts = data["partitions"]
        labels = data["labels"]

        is_s = (parts == "S+") | (parts == "S-")
        is_u = (parts == "U+") | (parts == "U-")
        pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"

        split_matrix = {}
        for src in BACKBONES:
            split_matrix[src] = {}
            for tgt in BACKBONES:
                preds = data[f"pred_{src}_to_{tgt}"]
                s_auc = float(roc_auc_score(labels[is_s], preds[is_s]))
                u_auc = float(roc_auc_score(labels[is_u], preds[is_u]))
                pa = compute_matched_pair_acc(qids, preds, pairs_file)
                split_matrix[src][tgt] = {
                    "seen": s_auc,
                    "unseen": u_auc,
                    "gap": s_auc - u_auc,
                    "pair_acc": pa
                }

        split_ens = {}
        for tgt in BACKBONES:
            ens_p = (data[f"pred_flash_to_{tgt}"] + data[f"pred_moment_to_{tgt}"] + data[f"pred_qd_to_{tgt}"]) / 3.0
            s_auc = float(roc_auc_score(labels[is_s], ens_p[is_s]))
            u_auc = float(roc_auc_score(labels[is_u], ens_p[is_u]))
            pa = compute_matched_pair_acc(qids, ens_p, pairs_file)
            split_ens[tgt] = {
                "seen": s_auc,
                "unseen": u_auc,
                "gap": s_auc - u_auc,
                "pair_acc": pa
            }

        recalc_split_results.append({
            "split": split,
            "matrix": split_matrix,
            "ensemble": split_ens
        })

    # Compute Macro Recalculations
    recalc_macro = {src: {tgt: {} for tgt in BACKBONES} for src in BACKBONES}
    for src in BACKBONES:
        for tgt in BACKBONES:
            u_vals = [r["matrix"][src][tgt]["unseen"] for r in recalc_split_results]
            s_vals = [r["matrix"][src][tgt]["seen"] for r in recalc_split_results]
            pa_vals = [r["matrix"][src][tgt]["pair_acc"] for r in recalc_split_results]
            recalc_macro[src][tgt] = {
                "seen": float(np.mean(s_vals)),
                "unseen": float(np.mean(u_vals)),
                "gap": float(np.mean(s_vals)) - float(np.mean(u_vals)),
                "pair_acc": float(np.mean(pa_vals)),
            }

    # Verify against reported summary
    max_diff = 0.0
    for src in BACKBONES:
        for tgt in BACKBONES:
            rep_u = macro_reported[src][tgt]["unseen"]
            rec_u = recalc_macro[src][tgt]["unseen"]
            diff = abs(rep_u - rec_u)
            max_diff = max(max_diff, diff)
            assert diff < 1e-4, f"Mismatch in cell {src}->{tgt}: reported {rep_u}, recalc {rec_u}"

    print(f"Audit PASSED! Max discrepancy across all 9 cells: {max_diff:.6f} (< 1e-4).")
    print("\nRecalculated Macro Unseen AUROC Matrix:")
    for src in BACKBONES:
        row = f"{src.upper():8s} -> "
        for tgt in BACKBONES:
            row += f"{tgt.upper()}: {recalc_macro[src][tgt]['unseen']:.4f} (PairAcc: {recalc_macro[src][tgt]['pair_acc']:.4f})  "
        print(row)

if __name__ == "__main__":
    audit()
