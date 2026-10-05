#!/usr/bin/env python3
"""
Tuning and Benchmarking Existence Adapter Architectures on Cached H^q features.
Strictly evaluates Seen AUROC (S+/S-), Unseen AUROC (U+/U-), Seen-Unseen Gap,
and Matched PairAcc using the exact official protocol from scripts/analyze_semantic_existence.py.
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
import torch.nn.functional as F
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
HQ_DIR = REPO / "experiments/agy_test/cache/hq"

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

# ----------------- Candidate Architectures -----------------

class BaselineCoordinateMax(nn.Module):
    """Original GMR Adapter: coordinate-wise max over slots followed by 2-layer MLP."""
    def __init__(self, d=256, hidden_dim=256):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
    def forward(self, hs, fg=None):
        pooled = hs.max(dim=1).values # [B, 256] coordinate-wise max
        return self.mlp(pooled).squeeze(-1)

class ScalarMaxMILAdapter(nn.Module):
    """Evaluates each slot as an independent coherent vector, then takes smooth max (LogSumExp)."""
    def __init__(self, d=256, hidden_dim=256, tau=1.0):
        super().__init__()
        self.slot_mlp = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
        self.tau = tau
    def forward(self, hs, fg=None):
        scores = self.slot_mlp(hs).squeeze(-1) # [B, 10]
        return self.tau * torch.logsumexp(scores / self.tau, dim=-1)

class AttentiveConvexAdapter(nn.Module):
    """Soft attention convex combination over slots: norm bounded by max_i ||h_i||."""
    def __init__(self, d=256, hidden_dim=256):
        super().__init__()
        self.attn_net = nn.Sequential(
            nn.Linear(d, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )
        self.mlp = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
    def forward(self, hs, fg=None):
        weights = F.softmax(self.attn_net(hs), dim=1) # [B, 10, 1]
        pooled = (hs * weights).sum(dim=1) # [B, 256]
        return self.mlp(pooled).squeeze(-1)

class ContrastiveSlotAdapter(nn.Module):
    """Slot representation augmented with deviation from background mean: [h_i, h_i - mean(h)]."""
    def __init__(self, d=256, hidden_dim=256, tau=1.0):
        super().__init__()
        self.slot_mlp = nn.Sequential(
            nn.Linear(d * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
        self.tau = tau
    def forward(self, hs, fg=None):
        mean_h = hs.mean(dim=1, keepdim=True)
        diff = hs - mean_h
        feat = torch.cat([hs, diff], dim=-1) # [B, 10, 512]
        scores = self.slot_mlp(feat).squeeze(-1) # [B, 10]
        return self.tau * torch.logsumexp(scores / self.tau, dim=-1)

class HybridEvidenceAdapter(nn.Module):
    """Combines attentive slot pooling with foreground confidence and slot spread."""
    def __init__(self, d=256, hidden_dim=256):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(d + 1, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )
        # Input: [pooled_h, mean_fg, slot_var]
        self.head = nn.Sequential(
            nn.Linear(d + 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
    def forward(self, hs, fg=None):
        bsz = hs.shape[0]
        if fg is None:
            fg = torch.ones((bsz, 10), device=hs.device) / 10.0
        
        # 1. Attentive pooling guided by both slot feature and foreground confidence
        feat_joint = torch.cat([hs, fg.unsqueeze(-1)], dim=-1) # [B, 10, D+1]
        weights = F.softmax(self.attn(feat_joint), dim=1) # [B, 10, 1]
        pooled = (hs * weights).sum(dim=1) # [B, D]
        
        # 2. Intrinsic features
        mean_fg = fg.mean(dim=-1, keepdim=True) # [B, 1]
        mean_h = hs.mean(dim=1, keepdim=True)
        slot_var = (hs - mean_h).norm(p=2, dim=-1).mean(dim=-1, keepdim=True) # [B, 1]
        
        combined_feat = torch.cat([pooled, mean_fg, slot_var], dim=-1) # [B, D+2]
        return self.head(combined_feat).squeeze(-1)

# ----------------- Training & Official Protocol Evaluation -----------------

def choose_val_seen_threshold(scores, labels):
    """Chooses threshold by balanced accuracy on val_seen, matching scripts/analyze_semantic_existence.py."""
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
        # 1. Val_seen for threshold selection
        val_hs = torch.tensor(val_data["hs"], device=device)
        val_fg = torch.tensor(val_data["fg"], device=device)
        val_scores = model(val_hs, val_fg).cpu().numpy()
        val_parts = val_data["partitions"]
        val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
        val_seen_labels = (val_parts[val_seen_mask] == "S+").astype(int)
        threshold = choose_val_seen_threshold(val_scores[val_seen_mask], val_seen_labels)
        
        # 2. Test evaluation
        test_hs = torch.tensor(test_data["hs"], device=device)
        test_fg = torch.tensor(test_data["fg"], device=device)
        test_scores = model(test_hs, test_fg).cpu().numpy()
        test_parts = test_data["partitions"]
        test_qids = [str(q) for q in test_data["qids"]]
        
        # Seen AUROC
        seen_mask = (test_parts == "S+") | (test_parts == "S-")
        seen_labels = (test_parts[seen_mask] == "S+").astype(int)
        seen_auc = float(roc_auc_score(seen_labels, test_scores[seen_mask]))
        
        # Unseen AUROC
        u_mask = (test_parts == "U+") | (test_parts == "U-")
        u_labels = (test_parts[u_mask] == "U+").astype(int)
        u_auc = float(roc_auc_score(u_labels, test_scores[u_mask]))
        
        # Seen-Unseen Gap
        gap = seen_auc - u_auc
        
        # Operating point metrics
        u_pos_mask = (test_parts == "U+")
        u_neg_mask = (test_parts == "U-")
        u_pos_frr = float((test_scores[u_pos_mask] < threshold).mean() * 100.0)
        u_neg_rr = float((test_scores[u_neg_mask] < threshold).mean() * 100.0)
        
        # Matched Pair Accuracy
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

def train_and_eval(arch_name: str, split: str, epochs: int = 15, lr: float = 5e-4, seed: int = 3407, device: str = "cuda:0", pair_weight: float = 0.2):
    set_seed(seed)
    split_dir = HQ_DIR / split
    train_data = np.load(split_dir / "train.npz")
    val_data = np.load(split_dir / "val.npz")
    test_data = np.load(split_dir / "test.npz")
    
    # Instantiate Model
    if arch_name == "baseline_max":
        model = BaselineCoordinateMax()
    elif arch_name == "scalar_max":
        model = ScalarMaxMILAdapter(tau=1.0)
    elif arch_name == "attentive_convex":
        model = AttentiveConvexAdapter()
    elif arch_name == "contrastive_slot":
        model = ContrastiveSlotAdapter(tau=1.0)
    elif arch_name == "hybrid_evidence":
        model = HybridEvidenceAdapter()
    else:
        raise ValueError(f"Unknown architecture: {arch_name}")
        
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    
    # Train tensors (S+ and S- only)
    tr_hs = torch.tensor(train_data["hs"], dtype=torch.float32)
    tr_fg = torch.tensor(train_data["fg"], dtype=torch.float32)
    tr_labels = torch.tensor(train_data["labels"], dtype=torch.float32)
    tr_vids = train_data["vids"].tolist()
    
    dataset = TensorDataset(tr_hs, tr_fg, tr_labels, torch.arange(len(tr_labels)))
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Validation Seen data for checkpoint selection
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
            
        # Check validation Seen AUROC
        model.eval()
        with torch.no_grad():
            v_logits = model(val_hs_seen, val_fg_seen).cpu().numpy()
            val_auc = roc_auc_score(val_labels_seen, v_logits)
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    # Load best checkpoint and evaluate on test set
    model.load_state_dict(best_state)
    metrics = evaluate_official(model, test_data, val_data, split, device=device)
    metrics["best_val_seen_auc"] = best_val_auc
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="A1")
    parser.add_argument("--arch", default="hybrid_evidence", choices=["baseline_max", "scalar_max", "attentive_convex", "contrastive_slot", "hybrid_evidence"])
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    
    print(f"[{args.split}] Training {args.arch} for {args.epochs} epochs on {args.device}...")
    res = train_and_eval(args.arch, args.split, epochs=args.epochs, lr=args.lr, device=args.device)
    base = BASELINE_QD[args.split]
    
    print(f"\n==================== [{args.split} - {args.arch}] ====================")
    print(f"  Seen AUROC:       {base['Seen']:.4f} -> {res['Seen_AUROC']:.4f} ({res['Seen_AUROC'] - base['Seen']:+.4f})")
    print(f"  Unseen AUROC:     {base['Unseen']:.4f} -> {res['Unseen_AUROC']:.4f} ({res['Unseen_AUROC'] - base['Unseen']:+.4f})")
    print(f"  Seen-Unseen Gap:  {base['Gap']:.4f} -> {res['Gap']:.4f} ({res['Gap'] - base['Gap']:+.4f})")
    print(f"  Matched PairAcc:  {base['PairAcc']:.4f} -> {res['Matched_PairAcc']:.4f} ({res['Matched_PairAcc'] - base['PairAcc']:+.4f})")
    print(f"  U+ False Refusal: {res['U_pos_FRR']:.1f}%")
    print(f"  U- Rejection:     {res['U_neg_RR']:.1f}%")
    print(f"===================================================================\n")

if __name__ == "__main__":
    main()
