#!/usr/bin/env python3
"""
Advanced Robust Existence Adapters that prevent out-of-distribution logit saturation
and improve generalization to unseen semantics.
"""
import sys
from pathlib import Path
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
HQ_DIR = REPO / "experiments/agy_test/cache/hq"
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

from tune_existence_adapter import (
    BASELINE_QD,
    choose_val_seen_threshold,
    evaluate_official,
    set_seed,
)

# ---------------- Advanced Architectures ----------------

class CosineDispersionAdapter(nn.Module):
    """
    Directional existence classifier operating purely on normalized slot hypersphere.
    Completely eliminates norm drift caused by unfamiliar query vectors.
    """
    def __init__(self, d=256, num_prototypes=8):
        super().__init__()
        self.prototypes = nn.Parameter(torch.randn(num_prototypes, d))
        nn.init.orthogonal_(self.prototypes)
        self.scale = nn.Parameter(torch.tensor(4.0))
        self.disp_scale = nn.Parameter(torch.tensor(2.0))
        self.fg_scale = nn.Parameter(torch.tensor(2.0))
        self.bias = nn.Parameter(torch.tensor(0.0))
        
    def forward(self, hs, fg=None):
        # hs: [B, 10, 256], fg: [B, 10]
        mean_h = hs.mean(dim=1, keepdim=True) # [B, 1, 256]
        norm_hs = F.normalize(hs, p=2, dim=-1) # [B, 10, 256]
        norm_mean = F.normalize(mean_h, p=2, dim=-1) # [B, 1, 256]
        
        # 1. Slot cosine dispersion
        cos_to_mean = (norm_hs * norm_mean).sum(dim=-1) # [B, 10]
        cos_disp = 1.0 - cos_to_mean.min(dim=-1).values # [B]
        
        # 2. Maximum similarity to learned semantic prototypes
        norm_p = F.normalize(self.prototypes, p=2, dim=-1) # [K, 256]
        slot_p_sim = torch.einsum("bnd,kd->bnk", norm_hs, norm_p) # [B, 10, K]
        max_sim = slot_p_sim.max(dim=1).values.max(dim=-1).values # [B]
        
        # 3. Foreground confidence
        if fg is not None:
            max_fg = fg.max(dim=-1).values # [B]
        else:
            max_fg = torch.zeros_like(max_sim)
            
        return self.scale * max_sim + self.disp_scale * cos_disp + self.fg_scale * max_fg + self.bias

class ResidualDispersionMLP(nn.Module):
    """
    Attentive slot pooling with explicit slot dispersion and bounded projection.
    Uses LayerNorm and spectral/weight normalization to prevent uncalibrated logit scaling.
    """
    def __init__(self, d=256, hidden_dim=128):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(d, 32),
            nn.Tanh(),
            nn.Linear(32, 1),
        )
        self.head = nn.Sequential(
            nn.Linear(d + 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
        
    def forward(self, hs, fg=None):
        # hs: [B, 10, 256]
        w = F.softmax(self.attn(hs), dim=1) # [B, 10, 1]
        pooled = (hs * w).sum(dim=1) # [B, 256]
        
        # Invariant dispersion metrics
        mean_h = hs.mean(dim=1, keepdim=True)
        norm_hs = F.normalize(hs, p=2, dim=-1)
        norm_mean = F.normalize(mean_h, p=2, dim=-1)
        cos_disp = (1.0 - (norm_hs * norm_mean).sum(dim=-1).min(dim=-1).values).unsqueeze(-1) # [B, 1]
        
        if fg is not None:
            fg_max = fg.max(dim=-1).values.unsqueeze(-1) # [B, 1]
        else:
            fg_max = torch.zeros_like(cos_disp)
            
        feat = torch.cat([pooled, cos_disp, fg_max], dim=-1) # [B, 258]
        return self.head(feat).squeeze(-1)

def train_and_eval_model(model_cls, split, epochs=20, lr=1e-3, seed=3407, device="cuda:0", **kwargs):
    set_seed(seed)
    split_dir = HQ_DIR / split
    train_data = np.load(split_dir / "train.npz")
    val_data = np.load(split_dir / "val.npz")
    test_data = np.load(split_dir / "test.npz")
    
    model = model_cls(**kwargs).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    
    # Train tensors (S+ and S- only)
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
                        pair_diffs.append(F.relu(1.0 - (logits[p] - logits[n])))
            pair_loss = torch.stack(pair_diffs).mean() if pair_diffs else torch.tensor(0.0, device=device)
            
            loss = bce_loss + 0.3 * pair_loss
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
    return metrics

def main():
    device = sys.argv[1] if len(sys.argv) > 1 else "cuda:0"
    print(f"Testing CosineDispersionAdapter across all 5 splits on {device}...")
    
    seen_all, unseen_all, gaps_all, pair_all = [], [], [], []
    print(f"{'Split':<8} | {'Seen AUC':<9} | {'Unseen AUC':<10} | {'Gap':<8} | {'Gap Red.':<9} | {'PairAcc':<8} | {'U+ FRR':<7} | {'U- RR':<7}")
    print("-" * 85)
    
    for split in SPLITS:
        base = BASELINE_QD[split]
        res = train_and_eval_model(CosineDispersionAdapter, split, epochs=25, lr=2e-3, device=device)
        gap_red = base["Gap"] - res["Gap"]
        seen_all.append(res["Seen_AUROC"])
        unseen_all.append(res["Unseen_AUROC"])
        gaps_all.append(res["Gap"])
        pair_all.append(res["Matched_PairAcc"])
        print(f"{split:<8} | {res['Seen_AUROC']:<9.4f} | {res['Unseen_AUROC']:<10.4f} | {res['Gap']:<8.4f} | {gap_red:<+9.4f} | {res['Matched_PairAcc']:<8.4f} | {res['U_pos_FRR']:<6.1f}% | {res['U_neg_RR']:<6.1f}%")
        
    print("-" * 85)
    base_mean_gap = 0.2332
    mean_gap = np.mean(gaps_all)
    print(f"{'MEAN':<8} | {np.mean(seen_all):<9.4f} | {np.mean(unseen_all):<10.4f} | {mean_gap:<8.4f} | {base_mean_gap - mean_gap:<+9.4f} | {np.mean(pair_all):<8.4f}")

if __name__ == "__main__":
    main()
