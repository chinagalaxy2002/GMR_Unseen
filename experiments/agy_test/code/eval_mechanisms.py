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
    # Sort thresholds
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

def eval_localization_gated(rows, labels, spans_xx, fg_scores, exist_scores, threshold):
    raw_hits = []
    gated_hits = []
    raw_correct_refused = 0
    raw_correct_total = 0
    
    for i, row in enumerate(rows):
        if row.get("exist_label", 0) != 1:
            continue
        dur = float(row["duration"])
        gt_wins = row.get("relevant_windows", [])
        
        # Top-1 proposed window by foreground score
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
    
    # Negative rejection rate
    neg_accepted = 0
    neg_total = 0
    for i, row in enumerate(rows):
        if row.get("exist_label", 0) == 0:
            neg_total += 1
            if exist_scores[i] >= threshold:
                neg_accepted += 1
    neg_rejection = (1.0 - neg_accepted / neg_total) if neg_total > 0 else 0.0
    
    # Overall positive FRR
    pos_total = len(raw_hits)
    pos_refused = sum(1 for i, row in enumerate(rows) if row.get("exist_label", 0) == 1 and exist_scores[i] < threshold)
    frr_all = (pos_refused / pos_total) if pos_total > 0 else 0.0
    
    return {
        "raw_R1@0.5": raw_r1,
        "gated_R1@0.5": gated_r1,
        "raw_correct_false_refusal": frr_raw_correct,
        "overall_U+_FRR": frr_all,
        "U-_rejection": neg_rejection,
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

class DecoupledSemanticQualityVerifier(nn.Module):
    """
    Decoupled verification:
    1. Semantic support head: evaluates cross-modal compatibility between query and local window
    2. Quality gating: weights proposals by both foreground confidence and semantic support
    3. Smooth attention aggregation instead of hard single-slot maximum
    """
    def __init__(self, hidden: int = 64):
        super().__init__()
        # Semantic support scorer
        self.semantic_net = nn.Sequential(
            nn.Linear(768, hidden),
            nn.LayerNorm(hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1)
        )
        # Quality-aware temperature
        self.temp = nn.Parameter(torch.ones(1) * 2.0)
        
    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor, fg_scores: torch.Tensor) -> torch.Tensor:
        # q: [B, D], v: [B, K, D], mask: [B, K], fg_scores: [B, K]
        q_exp = q[:, None, :].expand_as(v)
        feat = torch.cat([q_exp, v, q_exp * v], dim=-1)
        sem_logits = self.semantic_net(feat).squeeze(-1) # [B, K]
        
        # Combine semantic logit with log of foreground score
        log_fg = torch.log(fg_scores.clamp(min=1e-4, max=1.0))
        combined = sem_logits + 0.5 * log_fg
        
        # Smooth aggregation (LogSumExp / soft-max) over valid candidates
        combined = combined.masked_fill(~mask, float("-1e4"))
        agg_score = torch.logsumexp(combined / self.temp, dim=-1) * self.temp
        return agg_score

def train_verifier(model, train_data, seen_data, device, epochs=20, lr=1e-3, is_decoupled=False):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    
    y_tr = train_data["labels"].astype(np.float32)
    y_seen = seen_data["labels"].astype(np.float32)
    
    best_auc = -1.0
    best_epoch = -1
    best_state = None
    
    q_tr = torch.from_numpy(train_data["query_mean"]).float()
    v_tr = torch.from_numpy(train_data["local_video"]).float()
    m_tr = torch.from_numpy(train_data["candidate_mask"]).bool()
    fg_tr = torch.from_numpy(train_data["foreground_scores"]).float()
    
    q_se = torch.from_numpy(seen_data["query_mean"]).float().to(device)
    v_se = torch.from_numpy(seen_data["local_video"]).float().to(device)
    m_se = torch.from_numpy(seen_data["candidate_mask"]).bool().to(device)
    fg_se = torch.from_numpy(seen_data["foreground_scores"]).float().to(device)
    
    rng = np.random.default_rng(3407)
    batch_size = 256
    
    for epoch in range(1, epochs + 1):
        model.train()
        order = rng.permutation(len(y_tr))
        for st in range(0, len(order), batch_size):
            idx = order[st:st+batch_size]
            q = q_tr[idx].to(device)
            v = v_tr[idx].to(device)
            m = m_tr[idx].to(device)
            fg = fg_tr[idx].to(device)
            y = torch.from_numpy(y_tr[idx]).to(device)
            
            if is_decoupled:
                pred = model(q, v, m, fg)
            else:
                pred = model(q, v, m)
                
            loss = loss_fn(pred, y)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            if is_decoupled:
                s_pred = model(q_se, v_se, m_se, fg_se).cpu().numpy()
            else:
                s_pred = model(q_se, v_se, m_se).cpu().numpy()
        auc_se = compute_auc(y_seen, s_pred)
        if auc_se > best_auc:
            best_auc = auc_se
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            
    model.load_state_dict(best_state)
    model.eval()
    return model, best_auc, best_epoch

def main():
    set_seed(3407)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load data
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
    
    # Train M1: WindowVerifier
    print("--- Training M1: WindowVerifier ---")
    m1 = WindowVerifier().to(device)
    m1, m1_auc_se, m1_ep = train_verifier(m1, train_npz, seen_npz, device, is_decoupled=False)
    print(f"M1 Selected Epoch: {m1_ep}, Seen AUROC: {m1_auc_se:.4f}")
    
    # Train M2: DecoupledSemanticQualityVerifier
    print("--- Training M2: DecoupledSemanticQualityVerifier ---")
    m2 = DecoupledSemanticQualityVerifier().to(device)
    m2, m2_auc_se, m2_ep = train_verifier(m2, train_npz, seen_npz, device, is_decoupled=True)
    print(f"M2 Selected Epoch: {m2_ep}, Seen AUROC: {m2_auc_se:.4f}")
    
    # Evaluate all models on Seen (for threshold calibration) and U (final generalization evaluation)
    q_u = torch.from_numpy(u_npz["query_mean"]).float().to(device)
    v_u = torch.from_numpy(u_npz["local_video"]).float().to(device)
    m_u = torch.from_numpy(u_npz["candidate_mask"]).bool().to(device)
    fg_u = torch.from_numpy(u_npz["foreground_scores"]).float().to(device)
    
    q_se = torch.from_numpy(seen_npz["query_mean"]).float().to(device)
    v_se = torch.from_numpy(seen_npz["local_video"]).float().to(device)
    m_se = torch.from_numpy(seen_npz["candidate_mask"]).bool().to(device)
    fg_se = torch.from_numpy(seen_npz["foreground_scores"]).float().to(device)
    
    with torch.no_grad():
        m1_seen = m1(q_se, v_se, m_se).cpu().numpy()
        m1_u = m1(q_u, v_u, m_u).cpu().numpy()
        
        m2_seen = m2(q_se, v_se, m_se, fg_se).cpu().numpy()
        m2_u = m2(q_u, v_u, m_u, fg_u).cpu().numpy()
        
    models = {
        "M0_Original_GMR_Adapter": {
            "seen_scores": seen_npz["original_exist_logits"],
            "u_scores": u_npz["original_exist_logits"]
        },
        "M1_Proposal_Window_Verifier": {
            "seen_scores": m1_seen,
            "u_scores": m1_u
        },
        "M2_Decoupled_Semantic_Quality_Verifier": {
            "seen_scores": m2_seen,
            "u_scores": m2_u
        }
    }
    
    # Also evaluate row-permutation control on M1 and M2
    perm = np.random.RandomState(3407).permutation(len(u_npz["labels"]))
    with torch.no_grad():
        m1_u_perm = m1(q_u, v_u[perm], m_u[perm]).cpu().numpy()
        m2_u_perm = m2(q_u, v_u[perm], m_u[perm], fg_u[perm]).cpu().numpy()
        
    results = {}
    for name, obj in models.items():
        s_sc = obj["seen_scores"]
        u_sc = obj["u_scores"]
        
        # Calibrate threshold on Seen (strictly Seen-only)
        th = youden_threshold(seen_npz["labels"], s_sc)
        
        # Metrics on Seen
        s_auc = compute_auc(seen_npz["labels"], s_sc)
        s_pairs = pair_metrics(s_sc, seen_npz["labels"], seen_queries)
        s_gated = eval_localization_gated(seen_rows, seen_npz["labels"], seen_npz["spans_xx"], seen_npz["foreground_scores"], s_sc, th)
        
        # Metrics on U (using Seen calibrated threshold)
        u_auc = compute_auc(u_npz["labels"], u_sc)
        u_pairs = pair_metrics(u_sc, u_npz["labels"], u_queries)
        u_gated = eval_localization_gated(u_rows, u_npz["labels"], u_npz["spans_xx"], u_npz["foreground_scores"], u_sc, th)
        
        results[name] = {
            "Seen_threshold": float(th),
            "Seen_AUROC": s_auc,
            "Seen_pair_metrics": s_pairs,
            "Seen_gated_metrics": s_gated,
            "U_AUROC": u_auc,
            "U_pair_metrics": u_pairs,
            "U_gated_metrics": u_gated,
        }
        
    results["M1_Proposal_Window_Verifier"]["U_video_permuted_AUROC"] = compute_auc(u_npz["labels"], m1_u_perm)
    results["M2_Decoupled_Semantic_Quality_Verifier"]["U_video_permuted_AUROC"] = compute_auc(u_npz["labels"], m2_u_perm)
    
    # Print comparison table
    print("\n" + "="*80)
    print(f"{'Model':<40} | {'Seen AUROC':<10} | {'U AUROC':<10} | {'U+ FRR':<10} | {'U- Rej':<10} | {'Gated R1':<10}")
    print("-" * 80)
    for name, res in results.items():
        print(f"{name:<40} | {res['Seen_AUROC']:<10.4f} | {res['U_AUROC']:<10.4f} | {res['U_gated_metrics']['overall_U+_FRR']:<10.2%} | {res['U_gated_metrics']['U-_rejection']:<10.2%} | {res['U_gated_metrics']['gated_R1@0.5']:<10.4f}")
    print("="*80)
    
    out_file = AGY_TEST / "report/MECHANISM_EVAL_RESULTS.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_file}")

if __name__ == "__main__":
    main()
