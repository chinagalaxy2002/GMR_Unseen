#!/usr/bin/env python3
"""
Geometric Dispersion-Calibrated Adapter (GDCA) for Generalized Moment Retrieval.
Addresses Seen -> Unseen AUROC degradation by:
1. Replacing coordinate-wise max with attentive convex combination (strictly bounded norm).
2. Incorporating intrinsic geometric slot dispersion (cos_disp, max_dev) which discriminates
   event-positive from event-negative queries invariantly across seen and unseen semantics.
3. Training with feature perturbation and same-video contrastive pair regularization.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
HQ_DIR = REPO / "experiments/agy_test/cache/hq"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

# Official Baselines from /home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md
BASELINE_QD = {
    "A1": {"Seen": 0.7827, "Unseen": 0.5058, "Gap": 0.2769, "PairAcc": 0.5721},
    "A2_alt": {"Seen": 0.7442, "Unseen": 0.4727, "Gap": 0.2714, "PairAcc": 0.4557},
    "A3": {"Seen": 0.7334, "Unseen": 0.4870, "Gap": 0.2464, "PairAcc": 0.4535},
    "C1": {"Seen": 0.7798, "Unseen": 0.5618, "Gap": 0.2180, "PairAcc": 0.6354},
    "C2_alt": {"Seen": 0.6979, "Unseen": 0.5447, "Gap": 0.1532, "PairAcc": 0.5303},
}

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class GDCA(nn.Module):
    """
    Geometric Dispersion-Calibrated Adapter
    """
    def __init__(self, d=256, hidden_dim=128, noise_std=0.08):
        super().__init__()
        self.noise_std = noise_std
        self.ln = nn.LayerNorm(d)
        
        # Soft attention over slots for convex combination
        self.attn = nn.Sequential(
            nn.Linear(d, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )
        
        # Output classifier head
        # Input: pooled_slot (d) + cos_disp (1) + max_dev (1) + fg_max (1) = d + 3
        self.head = nn.Sequential(
            nn.Linear(d + 3, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, 1),
        )
        
        # Calibration gate
        self.disp_bias = nn.Parameter(torch.tensor(0.5))
        
    def forward(self, hs, fg=None):
        # hs: [B, 10, 256], fg: [B, 10]
        if self.training and self.noise_std > 0:
            hs = hs + self.noise_std * torch.randn_like(hs)
            
        norm_h = self.ln(hs) # [B, 10, 256]
        
        # 1. Attentive convex pooling
        attn_w = F.softmax(self.attn(norm_h), dim=1) # [B, 10, 1]
        pooled = (norm_h * attn_w).sum(dim=1) # [B, 256]
        
        # 2. Geometric Slot Dispersion Metrics
        mean_h = norm_h.mean(dim=1, keepdim=True) # [B, 1, 256]
        unit_h = F.normalize(norm_h, p=2, dim=-1)
        unit_mean = F.normalize(mean_h, p=2, dim=-1)
        
        # Cosine disparity: distance of most divergent slot from slot centroid
        cos_disp = (1.0 - (unit_h * unit_mean).sum(dim=-1).min(dim=-1).values).unsqueeze(-1) # [B, 1]
        
        # L2 max deviation: magnitude of maximum slot deviation from centroid
        diff = norm_h - mean_h
        max_dev = diff.norm(p=2, dim=-1).max(dim=-1).values.unsqueeze(-1) # [B, 1]
        
        # 3. Maximum Foreground Probability
        if fg is not None:
            max_fg = fg.max(dim=-1).values.unsqueeze(-1) # [B, 1]
        else:
            max_fg = torch.zeros_like(cos_disp)
            
        # 4. Joint Feature Vector
        feat = torch.cat([pooled, cos_disp, max_dev, max_fg], dim=-1) # [B, 259]
        logits = self.head(feat).squeeze(-1) # [B]
        
        return logits

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

def evaluate_official(model, test_data, val_data, split: str, device: str = "cuda:0"):
    model.eval()
    with torch.no_grad():
        val_hs = torch.tensor(val_data["hs"], device=device)
        val_fg = torch.tensor(val_data["fg"], device=device)
        val_scores = model(val_hs, val_fg).cpu().numpy()
        val_parts = val_data["partitions"]
        val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
        val_seen_labels = (val_parts[val_seen_mask] == "S+").astype(int)
        threshold = choose_val_seen_threshold(val_scores[val_seen_mask], val_seen_labels)
        
        test_hs = torch.tensor(test_data["hs"], device=device)
        test_fg = torch.tensor(test_data["fg"], device=device)
        test_scores = model(test_hs, test_fg).cpu().numpy()
        test_parts = test_data["partitions"]
        test_qids = [str(q) for q in test_data["qids"]]
        
        seen_mask = (test_parts == "S+") | (test_parts == "S-")
        seen_labels = (test_parts[seen_mask] == "S+").astype(int)
        seen_auc = float(roc_auc_score(seen_labels, test_scores[seen_mask]))
        
        u_mask = (test_parts == "U+") | (test_parts == "U-")
        u_labels = (test_parts[u_mask] == "U+").astype(int)
        u_auc = float(roc_auc_score(u_labels, test_scores[u_mask]))
        
        gap = seen_auc - u_auc
        
        u_pos_mask = (test_parts == "U+")
        u_neg_mask = (test_parts == "U-")
        u_pos_frr = float((test_scores[u_pos_mask] < threshold).mean() * 100.0)
        u_neg_rr = float((test_scores[u_neg_mask] < threshold).mean() * 100.0)
        
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
        
        return {
            "Seen_AUROC": seen_auc,
            "Unseen_AUROC": u_auc,
            "Gap": gap,
            "Matched_PairAcc": pair_acc,
            "U_pos_FRR": u_pos_frr,
            "U_neg_RR": u_neg_rr,
            "Threshold": float(threshold),
        }

def train_split(split: str, epochs=15, lr=5e-4, weight_decay=1e-3, pair_weight=0.25, seed=3407, device="cuda:0"):
    set_seed(seed)
    split_dir = HQ_DIR / split
    train_data = np.load(split_dir / "train.npz")
    val_data = np.load(split_dir / "val.npz")
    test_data = np.load(split_dir / "test.npz")
    
    model = GDCA(d=256, hidden_dim=128, noise_std=0.08).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    tr_hs = torch.tensor(train_data["hs"], dtype=torch.float32)
    tr_fg = torch.tensor(train_data["fg"], dtype=torch.float32)
    tr_labels = torch.tensor(train_data["labels"], dtype=torch.float32)
    tr_vids = train_data["vids"].tolist()
    
    dataset = TensorDataset(tr_hs, tr_fg, tr_labels, torch.arange(len(tr_labels)))
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    val_parts = val_data["partitions"]
    val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
    val_hs_seen = torch.tensor(val_data["hs"][val_seen_mask], dtype=torch.float32, device=device)
    val_fg_seen = torch.tensor(val_data["fg"][val_seen_mask], dtype=torch.float32, device=device)
    val_labels_seen = (val_parts[val_seen_mask] == "S+").astype(int)
    
    best_val_auc = 0.0
    best_state = None
    
    for epoch in range(1, epochs + 1):
        model.train()
        for batch in loader:
            b_hs, b_fg, b_labels, b_idx = [x.to(device) if torch.is_tensor(x) else x for x in batch]
            logits = model(b_hs, b_fg)
            bce_loss = F.binary_cross_entropy_with_logits(logits, b_labels)
            
            # Same-video contrastive pair loss
            loss = bce_loss
            if pair_weight > 0:
                b_vids = [tr_vids[i.item()] for i in b_idx]
                vid_map = {}
                for bi, v in enumerate(b_vids):
                    vid_map.setdefault(v, []).append(bi)
                pair_diffs = []
                for v, idxs in vid_map.items():
                    pos = [i for i in idxs if b_labels[i] == 1]
                    neg = [i for i in idxs if b_labels[i] == 0]
                    for p in pos:
                        for n in neg:
                            pair_diffs.append(F.relu(0.5 - (logits[p] - logits[n])))
                if pair_diffs:
                    pair_loss = torch.stack(pair_diffs).mean()
                    loss = bce_loss + pair_weight * pair_loss
                    
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            v_logits = model(val_hs_seen, val_fg_seen).cpu().numpy()
            val_auc = roc_auc_score(val_labels_seen, v_logits)
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    metrics = evaluate_official(model, test_data, val_data, split, device=device)
    metrics["best_val_seen_auc"] = best_val_auc
    
    # Save checkpoint
    out_dir = REPO / f"experiments/agy_test/e2e_training/runs/{split}/gdca"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"model": best_state, "metrics": metrics}, out_dir / "best.ckpt")
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=5e-4)
    args = parser.parse_args()
    
    print("=" * 105)
    print("TRAINING GEOMETRIC DISPERSION-CALIBRATED ADAPTER (GDCA) ACROSS 5 SPLITS (Seed: 3407)")
    print("Benchmark Baseline: /home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md")
    print("=" * 105)
    
    all_res = {}
    seen_list, unseen_list, gap_list, pair_list = [], [], [], []
    
    for split in SPLITS:
        base = BASELINE_QD[split]
        print(f"\n---> Training Split {split} on {args.device}...")
        res = train_split(split, epochs=args.epochs, lr=args.lr, device=args.device)
        all_res[split] = res
        
        seen_list.append(res["Seen_AUROC"])
        unseen_list.append(res["Unseen_AUROC"])
        gap_list.append(res["Gap"])
        pair_list.append(res["Matched_PairAcc"])
        
        g_diff = base["Gap"] - res["Gap"]
        print(f"  [{split}] Baseline: Seen={base['Seen']:.4f}, Unseen={base['Unseen']:.4f}, Gap={base['Gap']:.4f}, PairAcc={base['PairAcc']:.4f}")
        print(f"  [{split}] GDCA:     Seen={res['Seen_AUROC']:.4f}, Unseen={res['Unseen_AUROC']:.4f}, Gap={res['Gap']:.4f} (Gap Red: {g_diff:+.4f}), PairAcc={res['Matched_PairAcc']:.4f}")
        
    print("\n" + "=" * 105)
    print("FINAL 5-SPLIT BENCHMARK COMPARISON TABLE (Seed 3407)")
    print("=" * 105)
    print(f"{'Split':<10} | {'Base Seen':<10} | {'GDCA Seen':<10} | {'Base Unseen':<11} | {'GDCA Unseen':<11} | {'Base Gap':<9} | {'GDCA Gap':<9} | {'Gap Red.':<9} | {'GDCA Pair':<9}")
    print("-" * 105)
    
    for split in SPLITS:
        b = BASELINE_QD[split]
        r = all_res[split]
        g_red = b["Gap"] - r["Gap"]
        print(f"{split:<10} | {b['Seen']:<10.4f} | {r['Seen_AUROC']:<10.4f} | {b['Unseen']:<11.4f} | {r['Unseen_AUROC']:<11.4f} | {b['Gap']:<9.4f} | {r['Gap']:<9.4f} | {g_red:<+9.4f} | {r['Matched_PairAcc']:<9.4f}")
        
    print("-" * 105)
    b_mean_seen = 0.7476
    b_mean_unseen = 0.5144
    b_mean_gap = 0.2332
    b_mean_pair = 0.5294
    
    m_seen = np.mean(seen_list)
    m_unseen = np.mean(unseen_list)
    m_gap = np.mean(gap_list)
    m_pair = np.mean(pair_list)
    m_gap_red = b_mean_gap - m_gap
    
    print(f"{'MEAN':<10} | {b_mean_seen:<10.4f} | {m_seen:<10.4f} | {b_mean_unseen:<11.4f} | {m_unseen:<11.4f} | {b_mean_gap:<9.4f} | {m_gap:<9.4f} | {m_gap_red:<+9.4f} | {m_pair:<9.4f}")
    print("=" * 105)

if __name__ == "__main__":
    main()
