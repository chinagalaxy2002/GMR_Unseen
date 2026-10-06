#!/usr/bin/env python3
"""
Independent Audit and Verification Script for DEC-GMR.
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
MODELS = ["moment", "qd", "flash"]

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

    macro_reported = summary["macro_summary"]
    print(">>> Starting Independent Audit of DEC-GMR Predictions across all 3 backbones...")

    recalc_splits = []
    for split in SPLITS:
        pred_file = RUNS_DIR / split / "predictions.npz"
        assert pred_file.exists(), f"Missing prediction file: {pred_file}"

        data = np.load(pred_file)
        qids = data["qids"]
        parts = data["partitions"]
        labels = data["labels"]

        is_s = (parts == "S+") | (parts == "S-")
        is_u = (parts == "U+") | (parts == "U-")
        pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"

        split_dict = {}
        for bb in MODELS:
            dec_preds = data[f"pred_dec_{bb}"]
            base_preds = data[f"pred_base_{bb}"]

            dec_s = float(roc_auc_score(labels[is_s], dec_preds[is_s]))
            dec_u = float(roc_auc_score(labels[is_u], dec_preds[is_u]))
            dec_pa = compute_matched_pair_acc(qids, dec_preds, pairs_file)

            base_s = float(roc_auc_score(labels[is_s], base_preds[is_s]))
            base_u = float(roc_auc_score(labels[is_u], base_preds[is_u]))
            base_pa = compute_matched_pair_acc(qids, base_preds, pairs_file)

            split_dict[bb] = {
                "base_seen": base_s, "base_unseen": base_u, "base_pa": base_pa,
                "dec_seen": dec_s, "dec_unseen": dec_u, "dec_pa": dec_pa,
                "gain": dec_u - base_u
            }
        recalc_splits.append(split_dict)

    # Recalculate macro
    for bb in MODELS:
        rep_u = macro_reported[bb]["dec_unseen"]
        rec_u = float(np.mean([s[bb]["dec_unseen"] for s in recalc_splits]))
        diff = abs(rep_u - rec_u)
        assert diff < 1e-4, f"Discrepancy for {bb}: reported {rep_u}, recalc {rec_u}"
        print(f"[{bb.upper():10s}] Audit PASSED! Recalc Unseen: {rec_u:.4f} (Reported: {rep_u:.4f}, diff={diff:.6f})")

if __name__ == "__main__":
    audit()
