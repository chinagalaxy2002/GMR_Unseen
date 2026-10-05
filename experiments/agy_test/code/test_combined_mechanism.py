from __future__ import annotations
import json, random, sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO))

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_auc(y_true, y_score):
    return float(roc_auc_score(y_true, y_score))

def youden_threshold(y_true, y_score):
    thresholds = np.unique(y_score)
    if len(thresholds) > 1000:
        thresholds = np.quantile(y_score, np.linspace(0, 1, 1000))
    best_j, best_th = -1.0, float(thresholds[0])
    y_true = np.asarray(y_true, dtype=bool)
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float(np.median(y_score))
    for th in thresholds:
        pred = y_score >= th
        tpr = (pred & y_true).sum() / n_pos
        fpr = (pred & ~y_true).sum() / n_neg
        j = tpr - fpr
        if j > best_j:
            best_j = j
            best_th = float(th)
    return best_th

def pair_metrics(scores, labels, queries):
    groups = {}
    for i, q in enumerate(queries):
        groups.setdefault(q, []).append(i)
    accs, counts = [], []
    for q, idxs in groups.items():
        pos = [i for i in idxs if labels[i] == 1]
        neg = [i for i in idxs if labels[i] == 0]
        if not pos or not neg:
            continue
        vals = [1.0 if scores[p] > scores[n] else 0.5 if scores[p] == scores[n] else 0.0 for p in pos for n in neg]
        accs.append(float(np.mean(vals)))
        counts.append(len(vals))
    macro = float(np.mean(accs)) if accs else 0.5
    weighted = float(np.average(accs, weights=counts)) if accs else 0.5
    return {"macro_pair_acc": macro, "weighted_pair_acc": weighted, "pairs": int(sum(counts)), "queries": len(accs)}

def eval_gated_metrics(rows, labels, spans_xx, fg_scores, exist_scores, threshold):
    raw_hits, gated_hits = [], []
    raw_correct_refused, raw_correct_total = 0, 0
    for i, row in enumerate(rows):
        if row.get("exist_label", 0) != 1:
            continue
        dur = float(row["duration"])
        gt_wins = row.get("relevant_windows", [])
        top1_k = int(np.argmax(fg_scores[i]))
        t_st, t_ed = spans_xx[i, top1_k] * dur
        best_iou = 0.0
        for gw in gt_wins:
            gst, ged = float(gw[0]), float(gw[1])
            inter = max(0.0, min(t_ed, ged) - max(t_st, gst))
            union = max(1e-12, t_ed - t_st + ged - gst - inter)
            best_iou = max(best_iou, inter / union)
        hit = best_iou >= 0.5
        raw_hits.append(float(hit))
        accepted = exist_scores[i] >= threshold
        gated_hits.append(float(hit and accepted))
        if hit:
            raw_correct_total += 1
            if not accepted:
                raw_correct_refused += 1
    raw_r1 = float(np.mean(raw_hits)) if raw_hits else 0.0
    gated_r1 = float(np.mean(gated_hits)) if gated_hits else 0.0
    frr_raw_correct = (raw_correct_refused / raw_correct_total) if raw_correct_total > 0 else 0.0
    
    neg_accepted, neg_total = 0, 0
    for i, row in enumerate(rows):
        if row.get("exist_label", 0) == 0:
            neg_total += 1
            if exist_scores[i] >= threshold:
                neg_accepted += 1
    neg_rejection = (1.0 - neg_accepted / neg_total) if neg_total > 0 else 0.0
    pos_total = len(raw_hits)
    pos_refused = sum(1 for i, row in enumerate(rows) if row.get("exist_label", 0) == 1 and exist_scores[i] < threshold)
    frr_all = (pos_refused / pos_total) if pos_total > 0 else 0.0
    
    return {
        "raw_R1@0.5": raw_r1,
        "gated_R1@0.5": gated_r1,
        "raw_correct_false_refusal": frr_raw_correct,
        "overall_FRR": frr_all,
        "neg_rejection": neg_rejection,
    }

class WindowVerifier(nn.Module):
    def __init__(self, hidden: int = 85):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(768, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        q_exp = q[:, None, :].expand_as(v)
        feat = torch.cat([q_exp, v, q_exp * v], dim=-1)
        scores = self.mlp(feat).squeeze(-1)
        return scores.masked_fill(~mask, float("-inf")).amax(dim=1)

def main():
    set_seed(3407)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load features
    data_dir = REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation"
    feat_dir = data_dir / "cache/features/A2_alt/qd"
    view_dir = data_dir / "data_views/A2_alt"
    
    train_npz = np.load(feat_dir / "train.npz")
    seen_npz = np.load(feat_dir / "seen.npz")
    u_npz = np.load(feat_dir / "u.npz")
    
    seen_rows = [json.loads(line) for line in open(view_dir / "seen.jsonl")]
    u_rows = [json.loads(line) for line in open(view_dir / "u.jsonl")]
    seen_queries = [r["query"] for r in seen_rows]
    u_queries = [r["query"] for r in u_rows]
    
    # Train WindowVerifier
    wv = WindowVerifier().to(device)
    optimizer = torch.optim.AdamW(wv.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    
    q_tr = torch.from_numpy(train_npz["query_mean"]).float()
    v_tr = torch.from_numpy(train_npz["local_video"]).float()
    m_tr = torch.from_numpy(train_npz["candidate_mask"]).bool()
    y_tr = train_npz["labels"].astype(np.float32)
    
    q_se = torch.from_numpy(seen_npz["query_mean"]).float().to(device)
    v_se = torch.from_numpy(seen_npz["local_video"]).float().to(device)
    m_se = torch.from_numpy(seen_npz["candidate_mask"]).bool().to(device)
    y_se = seen_npz["labels"].astype(np.float32)
    
    best_auc, best_state = -1.0, None
    rng = np.random.default_rng(3407)
    for epoch in range(1, 21):
        wv.train()
        order = rng.permutation(len(y_tr))
        for st in range(0, len(order), 256):
            idx = order[st:st+256]
            pred = wv(q_tr[idx].to(device), v_tr[idx].to(device), m_tr[idx].to(device))
            loss = loss_fn(pred, torch.from_numpy(y_tr[idx]).to(device))
            optimizer.zero_grad(set_to_none=True); loss.backward(); optimizer.step()
        wv.eval()
        with torch.no_grad():
            s_pred = wv(q_se, v_se, m_se).cpu().numpy()
        auc_se = compute_auc(y_se, s_pred)
        if auc_se > best_auc:
            best_auc, best_state = auc_se, {k: v.cpu().clone() for k, v in wv.state_dict().items()}
    wv.load_state_dict(best_state)
    wv.eval()
    
    # Get verifier predictions
    q_u = torch.from_numpy(u_npz["query_mean"]).float().to(device)
    v_u = torch.from_numpy(u_npz["local_video"]).float().to(device)
    m_u = torch.from_numpy(u_npz["candidate_mask"]).bool().to(device)
    
    with torch.no_grad():
        wv_seen = wv(q_se, v_se, m_se).cpu().numpy()
        wv_u = wv(q_u, v_u, m_u).cpu().numpy()
        
    # Standardize scores on Seen (zero mean, unit std)
    def standardize(s_ref, s_target):
        mu, sigma = s_ref.mean(), s_ref.std() + 1e-8
        return (s_target - mu) / sigma
        
    wv_seen_std = standardize(wv_seen, wv_seen)
    wv_u_std = standardize(wv_seen, wv_u)
    
    orig_seen = seen_npz["original_exist_logits"]
    orig_u = u_npz["original_exist_logits"]
    orig_seen_std = standardize(orig_seen, orig_seen)
    orig_u_std = standardize(orig_seen, orig_u)
    
    # Load slot-level foreground-gated scores from previous step
    # We can compute foreground gating directly:
    fg_seen = seen_npz["foreground_scores"]
    fg_u = u_npz["foreground_scores"]
    
    # Let's test a sweep of alpha on Seen validation only (alpha in [0, 0.2, 0.5, 0.8, 1.0])
    alphas = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    sweep_results = []
    
    for alpha in alphas:
        comb_seen = alpha * orig_seen_std + (1.0 - alpha) * wv_seen_std
        comb_u = alpha * orig_u_std + (1.0 - alpha) * wv_u_std
        
        # Fit threshold strictly on Seen
        th = youden_threshold(seen_npz["labels"], comb_seen)
        
        se_auc = compute_auc(seen_npz["labels"], comb_seen)
        se_pair = pair_metrics(comb_seen, seen_npz["labels"], seen_queries)["macro_pair_acc"]
        se_gated = eval_gated_metrics(seen_rows, seen_npz["labels"], seen_npz["spans_xx"], fg_seen, comb_seen, th)
        
        u_auc = compute_auc(u_npz["labels"], comb_u)
        u_pair = pair_metrics(comb_u, u_npz["labels"], u_queries)["macro_pair_acc"]
        u_gated = eval_gated_metrics(u_rows, u_npz["labels"], u_npz["spans_xx"], fg_u, comb_u, th)
        
        sweep_results.append({
            "alpha": alpha,
            "Seen_AUROC": se_auc,
            "Seen_pair": se_pair,
            "Seen_gated_R1": se_gated["gated_R1@0.5"],
            "U_AUROC": u_auc,
            "U_pair": u_pair,
            "U_gated_R1": u_gated["gated_R1@0.5"],
            "U+_FRR": u_gated["overall_FRR"],
            "U-_Rejection": u_gated["neg_rejection"],
            "raw_correct_FRR": u_gated["raw_correct_false_refusal"]
        })
        
    print("\n" + "="*110)
    print(f"{'Alpha':<6} | {'Seen AUROC':<10} | {'Seen Pair':<10} | {'Seen R1':<10} | {'U AUROC':<10} | {'U Pair':<10} | {'U Gated R1':<10} | {'U+ FRR':<10} | {'U- Rej':<10}")
    print("-" * 110)
    for r in sweep_results:
        print(f"{r['alpha']:<6.1f} | {r['Seen_AUROC']:<10.4f} | {r['Seen_pair']:<10.4f} | {r['Seen_gated_R1']:<10.4f} | {r['U_AUROC']:<10.4f} | {r['U_pair']:<10.4f} | {r['U_gated_R1']:<10.4f} | {r['U+_FRR']:<10.2%} | {r['U-_Rejection']:<10.2%}")
    print("="*110)
    
    out_file = AGY_TEST / "report/ALPHA_SWEEP_RESULTS.json"
    with open(out_file, "w") as f:
        json.dump(sweep_results, f, indent=2)
    print(f"Saved alpha sweep to {out_file}")

if __name__ == "__main__":
    main()
