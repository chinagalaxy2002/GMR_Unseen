#!/usr/bin/env python3
"""
Evaluate various structural & non-parametric signals directly on the cached representations
to identify the exact mechanism that discriminates U+ from U- across all 5 splits.
"""
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
HQ_DIR = REPO / "experiments/agy_test/cache/hq"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def choose_val_seen_threshold(scores, labels):
    thresholds = np.unique(scores)
    if len(thresholds) > 1000:
        thresholds = np.quantile(scores, np.linspace(0, 1, 1000))
    pos = (labels == 1)
    neg = (labels == 0)
    best_bal, best_th = -1.0, float(thresholds[0])
    for th in thresholds:
        pred = (scores >= th)
        bal = 0.5 * (float(pred[pos].mean()) + float((~pred[neg]).mean()))
        if bal > best_bal:
            best_bal = bal
            best_th = float(th)
    return best_th

def eval_scores(split, val_scores, test_scores):
    val_data = np.load(HQ_DIR / split / "val.npz")
    test_data = np.load(HQ_DIR / split / "test.npz")
    
    val_parts = val_data["partitions"]
    val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
    val_seen_labels = (val_parts[val_seen_mask] == "S+").astype(int)
    threshold = choose_val_seen_threshold(val_scores[val_seen_mask], val_seen_labels)
    
    test_parts = test_data["partitions"]
    test_qids = [str(q) for q in test_data["qids"]]
    
    seen_mask = (test_parts == "S+") | (test_parts == "S-")
    seen_labels = (test_parts[seen_mask] == "S+").astype(int)
    seen_auc = float(roc_auc_score(seen_labels, test_scores[seen_mask]))
    
    u_mask = (test_parts == "U+") | (test_parts == "U-")
    u_labels = (test_parts[u_mask] == "U+").astype(int)
    u_auc = float(roc_auc_score(u_labels, test_scores[u_mask]))
    
    gap = seen_auc - u_auc
    
    pairs_file = REPO / f"data/release/semantic_existence_v2/{split}/matched_u_pairs.jsonl"
    qid_to_score = dict(zip(test_qids, test_scores))
    pair_accs = []
    if pairs_file.exists():
        pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
        for p in pairs:
            pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
            if pq in qid_to_score and nq in qid_to_score:
                sp, sn = qid_to_score[pq], qid_to_score[nq]
                pair_accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    pair_acc = float(np.mean(pair_accs)) if pair_accs else 0.5
    
    u_pos_mask = (test_parts == "U+")
    u_neg_mask = (test_parts == "U-")
    u_pos_frr = float((test_scores[u_pos_mask] < threshold).mean() * 100.0)
    u_neg_rr = float((test_scores[u_neg_mask] < threshold).mean() * 100.0)
    
    return {
        "Seen": seen_auc,
        "Unseen": u_auc,
        "Gap": gap,
        "PairAcc": pair_acc,
        "U+ FRR": u_pos_frr,
        "U- RR": u_neg_rr,
    }

def compute_signals(data):
    hs = torch.tensor(data["hs"]) # [N, 10, 256]
    fg = torch.tensor(data["fg"]) # [N, 10]
    orig_logits = np.squeeze(data["orig_logits"]) # [N]
    
    # 1. Original logits
    s_orig = orig_logits
    
    # 2. Foreground confidence
    s_fg_max = fg.max(dim=-1).values.numpy()
    s_fg_mean = fg.mean(dim=-1).numpy()
    
    # 3. Slot Variance (Mean L2 distance from mean slot)
    mean_h = hs.mean(dim=1, keepdim=True) # [N, 1, 256]
    diff = hs - mean_h # [N, 10, 256]
    s_slot_var = diff.norm(p=2, dim=-1).mean(dim=-1).numpy()
    
    # 4. Max slot deviation from mean
    s_slot_max_dev = diff.norm(p=2, dim=-1).max(dim=-1).values.numpy()
    
    # 5. Slot Cosine Disparity: 1 - min cosine similarity between any slot and mean
    norm_hs = F.normalize(hs, p=2, dim=-1)
    norm_mean = F.normalize(mean_h, p=2, dim=-1)
    cos_sim = (norm_hs * norm_mean).sum(dim=-1) # [N, 10]
    s_cos_disp = (1.0 - cos_sim.min(dim=-1).values).numpy()
    
    # 6. Hybrid combination: e.g. slot_var * fg_max or normalized rank
    return {
        "orig_logits": s_orig,
        "fg_max": s_fg_max,
        "fg_mean": s_fg_mean,
        "slot_var": s_slot_var,
        "slot_max_dev": s_slot_max_dev,
        "cos_disp": s_cos_disp,
    }

def main():
    signals = ["orig_logits", "fg_max", "slot_var", "slot_max_dev", "cos_disp"]
    print("=" * 110)
    print(f"{'Split':<8} | {'Signal':<15} | {'Seen AUC':<9} | {'Unseen AUC':<10} | {'Gap':<8} | {'PairAcc':<8} | {'U+ FRR':<7} | {'U- RR':<7}")
    print("=" * 110)
    
    for split in SPLITS:
        val_data = np.load(HQ_DIR / split / "val.npz")
        test_data = np.load(HQ_DIR / split / "test.npz")
        
        val_sig = compute_signals(val_data)
        test_sig = compute_signals(test_data)
        
        for sig in signals:
            res = eval_scores(split, val_sig[sig], test_sig[sig])
            print(f"{split:<8} | {sig:<15} | {res['Seen']:<9.4f} | {res['Unseen']:<10.4f} | {res['Gap']:<8.4f} | {res['PairAcc']:<8.4f} | {res['U+ FRR']:<6.1f}% | {res['U- RR']:<6.1f}%")
        print("-" * 110)

if __name__ == "__main__":
    main()
