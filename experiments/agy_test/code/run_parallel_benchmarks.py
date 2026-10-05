from __future__ import annotations
import json, os, random, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
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
    try:
        return float(roc_auc_score(y_true, y_score))
    except Exception:
        return 0.5

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

class OldWindowVerifier(nn.Module):
    def __init__(self, hidden: int = 85):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(768, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor, fg: torch.Tensor = None) -> torch.Tensor:
        q_exp = q[:, None, :].expand_as(v)
        feat = torch.cat([q_exp, v, q_exp * v], dim=-1)
        scores = self.mlp(feat).squeeze(-1)
        return scores.masked_fill(~mask, float("-inf")).amax(dim=1)

class FGDeBiasedVerifier(nn.Module):
    """
    Foreground-Gated De-biased Verifier (FGD-Verifier):
    1. Eliminates direct query-text skip connection to prevent text-frequency shortcuts.
    2. Uses bilinear interaction + video projection.
    3. Multiplicatively / log-odds gates candidates by detector foreground scores.
    4. Smooth LogSumExp aggregation across candidates.
    """
    def __init__(self, dim: int = 256, hidden: int = 64):
        super().__init__()
        self.proj_q = nn.Linear(dim, hidden)
        self.proj_v = nn.Linear(dim, hidden)
        self.net = nn.Sequential(
            nn.Linear(hidden * 2, hidden),
            nn.LayerNorm(hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1)
        )
        self.temp = nn.Parameter(torch.ones(1) * 2.0)
        self.fg_weight = nn.Parameter(torch.ones(1) * 1.0)

    def forward(self, q: torch.Tensor, v: torch.Tensor, mask: torch.Tensor, fg: torch.Tensor) -> torch.Tensor:
        # q: [B, D], v: [B, K, D]
        hq = self.proj_q(q)[:, None, :] # [B, 1, H]
        hv = self.proj_v(v)             # [B, K, H]
        interaction = hq * hv          # [B, K, H]
        
        # Combine interaction with video feature representation (no pure query shortcut!)
        feat = torch.cat([interaction, hv], dim=-1) # [B, K, 2H]
        raw_evidence = self.net(feat).squeeze(-1)   # [B, K]
        
        # Foreground gating: penalize background proposals
        log_fg = torch.log(fg.clamp(min=1e-4, max=1.0))
        gated_evidence = raw_evidence + self.fg_weight * log_fg
        
        # Smooth LogSumExp aggregation over valid candidates
        gated_evidence = gated_evidence.masked_fill(~mask, float("-1e4"))
        agg_score = torch.logsumexp(gated_evidence / self.temp, dim=-1) * self.temp
        return agg_score

def standardize(s_ref, s_target):
    mu, sigma = s_ref.mean(), s_ref.std() + 1e-8
    return (s_target - mu) / sigma

def train_and_eval_single_task(args):
    split, backbone, gpu_id = args
    device = torch.device(f"cuda:{gpu_id}")
    set_seed(3407)
    
    base_dir = REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation"
    feat_dir = base_dir / f"cache/features/{split}/{backbone}"
    view_dir = base_dir / f"data_views/{split}"
    
    train_npz = np.load(feat_dir / "train.npz")
    seen_npz = np.load(feat_dir / "seen.npz")
    u_npz = np.load(feat_dir / "u.npz")
    
    seen_rows = [json.loads(line) for line in open(view_dir / "seen.jsonl")]
    u_rows = [json.loads(line) for line in open(view_dir / "u.jsonl")]
    seen_queries = [r["query"] for r in seen_rows]
    u_queries = [r["query"] for r in u_rows]
    
    q_tr = torch.from_numpy(train_npz["query_mean"]).float()
    v_tr = torch.from_numpy(train_npz["local_video"]).float()
    m_tr = torch.from_numpy(train_npz["candidate_mask"]).bool()
    fg_tr = torch.from_numpy(train_npz["foreground_scores"]).float()
    y_tr = train_npz["labels"].astype(np.float32)
    
    q_se = torch.from_numpy(seen_npz["query_mean"]).float().to(device)
    v_se = torch.from_numpy(seen_npz["local_video"]).float().to(device)
    m_se = torch.from_numpy(seen_npz["candidate_mask"]).bool().to(device)
    fg_se = torch.from_numpy(seen_npz["foreground_scores"]).float().to(device)
    y_se = seen_npz["labels"].astype(np.float32)
    
    q_u = torch.from_numpy(u_npz["query_mean"]).float().to(device)
    v_u = torch.from_numpy(u_npz["local_video"]).float().to(device)
    m_u = torch.from_numpy(u_npz["candidate_mask"]).bool().to(device)
    fg_u = torch.from_numpy(u_npz["foreground_scores"]).float().to(device)
    
    # 1. Train Model 1 (Old Window Verifier)
    m1 = OldWindowVerifier().to(device)
    opt1 = torch.optim.AdamW(m1.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    
    best_auc1, state1 = -1.0, None
    rng = np.random.default_rng(3407)
    for epoch in range(1, 21):
        m1.train()
        order = rng.permutation(len(y_tr))
        for st in range(0, len(order), 256):
            idx = order[st:st+256]
            pred = m1(q_tr[idx].to(device), v_tr[idx].to(device), m_tr[idx].to(device))
            loss = loss_fn(pred, torch.from_numpy(y_tr[idx]).to(device))
            opt1.zero_grad(set_to_none=True); loss.backward(); opt1.step()
        m1.eval()
        with torch.no_grad():
            s_pred = m1(q_se, v_se, m_se).cpu().numpy()
        auc_se = compute_auc(y_se, s_pred)
        if auc_se > best_auc1:
            best_auc1, state1 = auc_se, {k: v.cpu().clone() for k, v in m1.state_dict().items()}
    m1.load_state_dict(state1)
    m1.eval()
    
    # 2. Train Model 2 (Foreground-Gated De-biased Verifier: FGD)
    m2 = FGDeBiasedVerifier().to(device)
    opt2 = torch.optim.AdamW(m2.parameters(), lr=1e-3, weight_decay=1e-4)
    
    best_auc2, state2 = -1.0, None
    for epoch in range(1, 21):
        m2.train()
        order = rng.permutation(len(y_tr))
        for st in range(0, len(order), 256):
            idx = order[st:st+256]
            pred = m2(q_tr[idx].to(device), v_tr[idx].to(device), m_tr[idx].to(device), fg_tr[idx].to(device))
            loss = loss_fn(pred, torch.from_numpy(y_tr[idx]).to(device))
            opt2.zero_grad(set_to_none=True); loss.backward(); opt2.step()
        m2.eval()
        with torch.no_grad():
            s_pred = m2(q_se, v_se, m_se, fg_se).cpu().numpy()
        auc_se = compute_auc(y_se, s_pred)
        if auc_se > best_auc2:
            best_auc2, state2 = auc_se, {k: v.cpu().clone() for k, v in m2.state_dict().items()}
    m2.load_state_dict(state2)
    m2.eval()
    
    with torch.no_grad():
        m1_seen = m1(q_se, v_se, m_se).cpu().numpy()
        m1_u = m1(q_u, v_u, m_u).cpu().numpy()
        
        m2_seen = m2(q_se, v_se, m_se, fg_se).cpu().numpy()
        m2_u = m2(q_u, v_u, m_u, fg_u).cpu().numpy()
        
    orig_seen = seen_npz["original_exist_logits"]
    orig_u = u_npz["original_exist_logits"]
    
    m2_seen_std = standardize(m2_seen, m2_seen)
    m2_u_std = standardize(m2_seen, m2_u)
    orig_seen_std = standardize(orig_seen, orig_seen)
    orig_u_std = standardize(orig_seen, orig_u)
    
    # Calibrated Ensemble (alpha = 0.2)
    ens_seen = 0.2 * orig_seen_std + 0.8 * m2_seen_std
    ens_u = 0.2 * orig_u_std + 0.8 * m2_u_std
    
    methods = {
        "M0_Original": (orig_seen, orig_u),
        "M1_OldVerifier": (m1_seen, m1_u),
        "M2_FGD_Verifier": (m2_seen, m2_u),
        "M3_FGD_Ensemble": (ens_seen, ens_u)
    }
    
    task_res = {}
    for mname, (s_sc, u_sc) in methods.items():
        th = youden_threshold(seen_npz["labels"], s_sc)
        se_auc = compute_auc(seen_npz["labels"], s_sc)
        se_pair = pair_metrics(s_sc, seen_npz["labels"], seen_queries)["macro_pair_acc"]
        se_gated = eval_gated_metrics(seen_rows, seen_npz["labels"], seen_npz["spans_xx"], seen_npz["foreground_scores"], s_sc, th)
        
        u_auc = compute_auc(u_npz["labels"], u_sc)
        u_pair = pair_metrics(u_sc, u_npz["labels"], u_queries)["macro_pair_acc"]
        u_gated = eval_gated_metrics(u_rows, u_npz["labels"], u_npz["spans_xx"], u_npz["foreground_scores"], u_sc, th)
        
        task_res[mname] = {
            "Seen_AUROC": se_auc,
            "Seen_Pair": se_pair,
            "Seen_Gated_R1": se_gated["gated_R1@0.5"],
            "U_AUROC": u_auc,
            "U_Pair": u_pair,
            "U_Gated_R1": u_gated["gated_R1@0.5"],
            "U+_FRR": u_gated["overall_FRR"],
            "U-_Rejection": u_gated["neg_rejection"],
        }
    print(f"[{split}/{backbone}] Done! Base U AUROC: {task_res['M0_Original']['U_AUROC']:.4f} -> FGD Ensemble U AUROC: {task_res['M3_FGD_Ensemble']['U_AUROC']:.4f} (Pair: {task_res['M3_FGD_Ensemble']['U_Pair']:.4f})", flush=True)
    return (split, backbone, task_res)

def main():
    splits = ["A2_alt", "A3", "C1", "C2_alt"]
    backbones = ["qd", "moment", "flash"]
    
    tasks = []
    # Distribute 12 tasks across GPU 0 and GPU 1
    # 6 tasks on GPU 0, 6 tasks on GPU 1
    count = 0
    for sp in splits:
        for bb in backbones:
            gpu_id = 0 if count < 6 else 1
            tasks.append((sp, bb, gpu_id))
            count += 1
            
    print(f"Starting parallel execution of 12 benchmark tasks across 2 GPUs (up to 3 parallel per GPU)...")
    start_time = time.time()
    
    results = {}
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(train_and_eval_single_task, t) for t in tasks]
        for f in futures:
            sp, bb, res = f.result()
            results.setdefault(sp, {})[bb] = res
            
    elapsed = time.time() - start_time
    print(f"\nAll 12 benchmark tasks completed in {elapsed:.2f} seconds!")
    
    # Save results
    out_file = AGY_TEST / "report/FULL_12_SETTINGS_PARALLEL_RESULTS.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_file}")
    
    # Print formatted summary table
    print("\n" + "="*140)
    print(f"{'Split':<8} | {'Backbone':<8} | {'Method':<16} | {'Seen AUROC':<11} | {'Seen Pair':<10} | {'U AUROC':<10} | {'U Pair':<10} | {'U Gated R1':<10} | {'U+ FRR':<10} | {'U- Rej':<10}")
    print("-" * 140)
    for sp in splits:
        for bb in backbones:
            m_res = results[sp][bb]
            for mname in ["M0_Original", "M1_OldVerifier", "M2_FGD_Verifier", "M3_FGD_Ensemble"]:
                r = m_res[mname]
                print(f"{sp:<8} | {bb:<8} | {mname:<16} | {r['Seen_AUROC']:<11.4f} | {r['Seen_Pair']:<10.4f} | {r['U_AUROC']:<10.4f} | {r['U_Pair']:<10.4f} | {r['U_Gated_R1']:<10.4f} | {r['U+_FRR']:<10.2%} | {r['U-_Rejection']:<10.2%}")
            print("-" * 140)
    print("="*140)

if __name__ == "__main__":
    main()
