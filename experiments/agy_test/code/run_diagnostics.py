from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO))

def main():
    print("=== Running Comprehensive GMR Failure Diagnostics on A2_alt/QD ===")
    
    # 1. Load cached features
    seen_npz = np.load(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/cache/features/A2_alt/qd/seen.npz")
    u_npz = np.load(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/cache/features/A2_alt/qd/u.npz")
    
    seen_rows = [json.loads(line) for line in open(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/data_views/A2_alt/seen.jsonl")]
    u_rows = [json.loads(line) for line in open(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/data_views/A2_alt/u.jsonl")]
    
    y_seen = seen_npz["labels"]
    y_u = u_npz["labels"]
    
    orig_seen = seen_npz["original_exist_logits"]
    orig_u = u_npz["original_exist_logits"]
    
    # Check baseline AUROC
    auc_seen = roc_auc_score(y_seen, orig_seen)
    auc_u = roc_auc_score(y_u, orig_u)
    print(f"Original GMR Adapter AUROC: Seen = {auc_seen:.4f}, Unseen = {auc_u:.4f}")
    
    # Diagnostic 1: Score & Logit Distribution Breakdown
    diag1 = {
        "S+": {
            "mean_logit": float(orig_seen[y_seen==1].mean()),
            "std_logit": float(orig_seen[y_seen==1].std()),
            "median_logit": float(np.median(orig_seen[y_seen==1])),
            "max_fg_score": float(seen_npz["foreground_scores"][y_seen==1].max(axis=1).mean()),
        },
        "S-": {
            "mean_logit": float(orig_seen[y_seen==0].mean()),
            "std_logit": float(orig_seen[y_seen==0].std()),
            "median_logit": float(np.median(orig_seen[y_seen==0])),
            "max_fg_score": float(seen_npz["foreground_scores"][y_seen==0].max(axis=1).mean()),
        },
        "U+": {
            "mean_logit": float(orig_u[y_u==1].mean()),
            "std_logit": float(orig_u[y_u==1].std()),
            "median_logit": float(np.median(orig_u[y_u==1])),
            "max_fg_score": float(u_npz["foreground_scores"][y_u==1].max(axis=1).mean()),
        },
        "U-": {
            "mean_logit": float(orig_u[y_u==0].mean()),
            "std_logit": float(orig_u[y_u==0].std()),
            "median_logit": float(np.median(orig_u[y_u==0])),
            "max_fg_score": float(u_npz["foreground_scores"][y_u==0].max(axis=1).mean()),
        },
    }
    print("Diagnostic 1 - Distribution breakdown:")
    print(json.dumps(diag1, indent=2))
    
    # Diagnostic 2: Localization-Conditioned Existence in U+
    # Evaluate raw localization IoU for U+
    spans_u = u_npz["spans_xx"] # [N, 10, 2] normalized coordinates
    fg_u = u_npz["foreground_scores"] # [N, 10]
    durations_u = u_npz["durations"]
    
    raw_correct = []
    best_ious = []
    top1_ious = []
    for i, row in enumerate(u_rows):
        if row.get("exist_label", 0) != 1:
            continue
        dur = float(row["duration"])
        gt_wins = row.get("relevant_windows", [])
        
        # Top-1 proposed window by foreground score
        top1_k = int(np.argmax(fg_u[i]))
        t_st, t_ed = spans_u[i, top1_k] * dur
        
        # compute max IoU with GT
        best_iou_top1 = 0.0
        for gw in gt_wins:
            gst, ged = float(gw[0]), float(gw[1])
            inter = max(0.0, min(t_ed, ged) - max(t_st, gst))
            union = max(1e-12, t_ed - t_st + ged - gst - inter)
            best_iou_top1 = max(best_iou_top1, inter / union)
        top1_ious.append(best_iou_top1)
        
        # Also compute best IoU across all 10 candidates (proposal recall)
        max_iou_all = 0.0
        for k in range(10):
            st, ed = spans_u[i, k] * dur
            for gw in gt_wins:
                gst, ged = float(gw[0]), float(gw[1])
                inter = max(0.0, min(ed, ged) - max(st, gst))
                union = max(1e-12, ed - st + ged - gst - inter)
                max_iou_all = max(max_iou_all, inter / union)
        best_ious.append(max_iou_all)
        raw_correct.append(best_iou_top1 >= 0.5)
        
    raw_correct = np.array(raw_correct)
    top1_ious = np.array(top1_ious)
    best_ious = np.array(best_ious)
    u_pos_logits = orig_u[y_u==1]
    
    diag2 = {
        "u_pos_count": int(len(raw_correct)),
        "raw_correct_count": int(raw_correct.sum()),
        "raw_R1@0.5": float(raw_correct.mean()),
        "proposal_recall@0.5_K=10": float((best_ious >= 0.5).mean()),
        "raw_correct_mean_logit": float(u_pos_logits[raw_correct].mean()),
        "raw_correct_median_logit": float(np.median(u_pos_logits[raw_correct])),
        "raw_incorrect_mean_logit": float(u_pos_logits[~raw_correct].mean()),
        "raw_incorrect_median_logit": float(np.median(u_pos_logits[~raw_correct])),
    }
    print("Diagnostic 2 - Localization-Conditioned Existence:")
    print(json.dumps(diag2, indent=2))
    
    # Diagnostic 3: Window Verifier vs Baseline vs GT Oracle
    # Load verifier scores from cross_confirmation run
    runs_dir = REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/runs/A2_alt/qd"
    if (runs_dir / "predictions_u.json").exists():
        v_u = json.loads((runs_dir / "predictions_u.json").read_text())
        v_scores = np.array(v_u["scores"])
        print(f"Verifier U AUROC: {roc_auc_score(y_u, v_scores):.4f}")
    
    # Save diagnostic results
    out_file = AGY_TEST / "report/DIAGNOSTIC_RESULTS.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump({"diag1_distribution": diag1, "diag2_localization_conditioned": diag2}, f, indent=2)
    print(f"Saved diagnostic report to {out_file}")

if __name__ == "__main__":
    main()
