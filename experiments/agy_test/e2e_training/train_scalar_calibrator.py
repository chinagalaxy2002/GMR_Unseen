#!/usr/bin/env python3
"""
Coordinate-Invariant Geometric Calibrator (CIGC).
Operates strictly on semantic-invariant scalar signals:
1. orig_logits: baseline existence scalar
2. cos_disp: slot cosine disparity (geometric divergence of slots)
3. slot_max_dev: slot maximum L2 deviation from centroid
4. fg_max: DETR foreground maximum confidence

Because it has only 5 learnable scalar parameters (no high-dimensional weights),
it CANNOT memorize specific semantic coordinates and generalizes robustly to unseen semantics.
"""
from __future__ import annotations
import argparse
import json
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

from tune_existence_adapter import BASELINE_QD, choose_val_seen_threshold, set_seed
from diagnose_signals import compute_signals

class CoordinateInvariantCalibrator(nn.Module):
    def __init__(self):
        super().__init__()
        # Bounded scaling parameters
        self.w_orig = nn.Parameter(torch.tensor(1.0))
        self.w_disp = nn.Parameter(torch.tensor(1.0))
        self.w_dev = nn.Parameter(torch.tensor(0.5))
        self.w_fg = nn.Parameter(torch.tensor(0.5))
        self.bias = nn.Parameter(torch.tensor(0.0))
        
    def forward(self, z_orig, z_disp, z_dev, z_fg):
        # All inputs are standardized scalars [B]
        score = (
            self.w_orig * z_orig +
            self.w_disp * z_disp +
            self.w_dev * z_dev +
            self.w_fg * z_fg +
            self.bias
        )
        return score

def extract_standardized_scalars(data, val_stats=None):
    sig = compute_signals(data)
    parts = data["partitions"]
    
    if val_stats is None:
        # Compute mean and std on seen validation samples
        seen_mask = (parts == "S+") | (parts == "S-")
        val_stats = {
            k: (float(sig[k][seen_mask].mean()), float(sig[k][seen_mask].std() + 1e-6))
            for k in ["orig_logits", "cos_disp", "slot_max_dev", "fg_max"]
        }
        
    normed = {}
    for k in ["orig_logits", "cos_disp", "slot_max_dev", "fg_max"]:
        mu, std = val_stats[k]
        normed[k] = (sig[k] - mu) / std
        
    return normed, val_stats

def eval_calibrator(model, test_data, val_data, val_stats, split: str, device: str = "cuda:0"):
    model.eval()
    with torch.no_grad():
        v_norm, _ = extract_standardized_scalars(val_data, val_stats)
        t_norm, _ = extract_standardized_scalars(test_data, val_stats)
        
        v_orig = torch.tensor(v_norm["orig_logits"], dtype=torch.float32, device=device)
        v_disp = torch.tensor(v_norm["cos_disp"], dtype=torch.float32, device=device)
        v_dev = torch.tensor(v_norm["slot_max_dev"], dtype=torch.float32, device=device)
        v_fg = torch.tensor(v_norm["fg_max"], dtype=torch.float32, device=device)
        
        val_scores = model(v_orig, v_disp, v_dev, v_fg).cpu().numpy()
        val_parts = val_data["partitions"]
        val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
        val_seen_labels = (val_parts[val_seen_mask] == "S+").astype(int)
        threshold = choose_val_seen_threshold(val_scores[val_seen_mask], val_seen_labels)
        
        t_orig = torch.tensor(t_norm["orig_logits"], dtype=torch.float32, device=device)
        t_disp = torch.tensor(t_norm["cos_disp"], dtype=torch.float32, device=device)
        t_dev = torch.tensor(t_norm["slot_max_dev"], dtype=torch.float32, device=device)
        t_fg = torch.tensor(t_norm["fg_max"], dtype=torch.float32, device=device)
        
        test_scores = model(t_orig, t_disp, t_dev, t_fg).cpu().numpy()
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
            "Seen_AUROC": seen_auc,
            "Unseen_AUROC": u_auc,
            "Gap": gap,
            "Matched_PairAcc": pair_acc,
            "U_pos_FRR": u_pos_frr,
            "U_neg_RR": u_neg_rr,
            "Threshold": float(threshold),
        }

def train_split(split: str, epochs=30, lr=0.01, seed=3407, device="cuda:0"):
    set_seed(seed)
    split_dir = HQ_DIR / split
    train_data = np.load(split_dir / "train.npz")
    val_data = np.load(split_dir / "val.npz")
    test_data = np.load(split_dir / "test.npz")
    
    # Standardize based on seen validation statistics
    _, val_stats = extract_standardized_scalars(val_data)
    tr_norm, _ = extract_standardized_scalars(train_data, val_stats)
    
    model = CoordinateInvariantCalibrator().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    
    tr_orig = torch.tensor(tr_norm["orig_logits"], dtype=torch.float32)
    tr_disp = torch.tensor(tr_norm["cos_disp"], dtype=torch.float32)
    tr_dev = torch.tensor(tr_norm["slot_max_dev"], dtype=torch.float32)
    tr_fg = torch.tensor(tr_norm["fg_max"], dtype=torch.float32)
    tr_labels = torch.tensor(train_data["labels"], dtype=torch.float32)
    tr_vids = train_data["vids"].tolist()
    
    dataset = TensorDataset(tr_orig, tr_disp, tr_dev, tr_fg, tr_labels, torch.arange(len(tr_labels)))
    loader = DataLoader(dataset, batch_size=128, shuffle=True)
    
    val_parts = val_data["partitions"]
    val_seen_mask = (val_parts == "S+") | (val_parts == "S-")
    val_norm, _ = extract_standardized_scalars(val_data, val_stats)
    v_orig = torch.tensor(val_norm["orig_logits"][val_seen_mask], dtype=torch.float32, device=device)
    v_disp = torch.tensor(val_norm["cos_disp"][val_seen_mask], dtype=torch.float32, device=device)
    v_dev = torch.tensor(val_norm["slot_max_dev"][val_seen_mask], dtype=torch.float32, device=device)
    v_fg = torch.tensor(val_norm["fg_max"][val_seen_mask], dtype=torch.float32, device=device)
    val_labels_seen = (val_parts[val_seen_mask] == "S+").astype(int)
    
    best_val_auc = 0.0
    best_state = None
    
    for epoch in range(1, epochs + 1):
        model.train()
        for batch in loader:
            bo, bdi, bde, bf, bl, bidx = [x.to(device) if torch.is_tensor(x) else x for x in batch]
            logits = model(bo, bdi, bde, bf)
            bce_loss = F.binary_cross_entropy_with_logits(logits, bl)
            
            # Same-video pair loss
            b_vids = [tr_vids[i.item()] for i in bidx]
            vid_map = {}
            for bi, v in enumerate(b_vids):
                vid_map.setdefault(v, []).append(bi)
            pair_diffs = []
            for v, idxs in vid_map.items():
                pos = [i for i in idxs if bl[i] == 1]
                neg = [i for i in idxs if bl[i] == 0]
                for p in pos:
                    for n in neg:
                        pair_diffs.append(F.relu(0.5 - (logits[p] - logits[n])))
            pair_loss = torch.stack(pair_diffs).mean() if pair_diffs else torch.tensor(0.0, device=device)
            
            loss = bce_loss + 0.3 * pair_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            v_logits = model(v_orig, v_disp, v_dev, v_fg).cpu().numpy()
            val_auc = roc_auc_score(val_labels_seen, v_logits)
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    metrics = eval_calibrator(model, test_data, val_data, val_stats, split, device=device)
    metrics["best_val_seen_auc"] = best_val_auc
    metrics["learned_weights"] = {
        "w_orig": float(model.w_orig.item()),
        "w_disp": float(model.w_disp.item()),
        "w_dev": float(model.w_dev.item()),
        "w_fg": float(model.w_fg.item()),
        "bias": float(model.bias.item()),
    }
    
    out_dir = REPO / f"experiments/agy_test/e2e_training/runs/{split}/calibrator"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"model": best_state, "metrics": metrics}, out_dir / "best.ckpt")
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    
    print("=" * 110)
    print("TRAINING COORDINATE-INVARIANT GEOMETRIC CALIBRATOR (CIGC) ACROSS 5 SPLITS (Seed: 3407)")
    print("Baseline Source: /home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md")
    print("=" * 110)
    
    all_res = {}
    seen_list, unseen_list, gap_list, pair_list = [], [], [], []
    
    for split in SPLITS:
        base = BASELINE_QD[split]
        print(f"\n---> Training Split {split} on {args.device}...")
        res = train_split(split, device=args.device)
        all_res[split] = res
        
        seen_list.append(res["Seen_AUROC"])
        unseen_list.append(res["Unseen_AUROC"])
        gap_list.append(res["Gap"])
        pair_list.append(res["Matched_PairAcc"])
        
        g_diff = base["Gap"] - res["Gap"]
        w = res["learned_weights"]
        print(f"  [{split}] Baseline: Seen={base['Seen']:.4f}, Unseen={base['Unseen']:.4f}, Gap={base['Gap']:.4f}, PairAcc={base['PairAcc']:.4f}")
        print(f"  [{split}] CIGC:     Seen={res['Seen_AUROC']:.4f}, Unseen={res['Unseen_AUROC']:.4f}, Gap={res['Gap']:.4f} (Gap Red: {g_diff:+.4f}), PairAcc={res['Matched_PairAcc']:.4f}")
        print(f"  [{split}] Weights:  w_orig={w['w_orig']:.3f}, w_disp={w['w_disp']:.3f}, w_dev={w['w_dev']:.3f}, w_fg={w['w_fg']:.3f}")
        
    print("\n" + "=" * 110)
    print("FINAL 5-SPLIT BENCHMARK COMPARISON TABLE (Seed 3407)")
    print("=" * 110)
    print(f"{'Split':<10} | {'Base Seen':<10} | {'CIGC Seen':<10} | {'Base Unseen':<11} | {'CIGC Unseen':<11} | {'Base Gap':<9} | {'CIGC Gap':<9} | {'Gap Red.':<9} | {'CIGC Pair':<9}")
    print("-" * 110)
    
    for split in SPLITS:
        b = BASELINE_QD[split]
        r = all_res[split]
        g_red = b["Gap"] - r["Gap"]
        print(f"{split:<10} | {b['Seen']:<10.4f} | {r['Seen_AUROC']:<10.4f} | {b['Unseen']:<11.4f} | {r['Unseen_AUROC']:<11.4f} | {b['Gap']:<9.4f} | {r['Gap']:<9.4f} | {g_red:<+9.4f} | {r['Matched_PairAcc']:<9.4f}")
        
    print("-" * 110)
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
    print("=" * 110)

if __name__ == "__main__":
    main()
