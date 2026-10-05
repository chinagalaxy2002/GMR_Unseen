#!/usr/bin/env python3
"""
Final Reproducible Pipeline: Geometric Dispersion-Calibrated Existence Model.
Directly addresses user mandate:
"相对于基线结果，能更好的缓解在未见语义的拒绝识别的退化，表现上来看，就是AUROC降低的少一些。
其中整理的表格为/home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md。"

Runs full training (Seed: 3407) and official evaluation on all 5 splits:
A1, A2_alt, A3, C1, C2_alt.
Outputs exact checkpoint, metrics.json, predictions.jsonl, and final summary report.
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
OUT_ROOT = REPO / "experiments/agy_test/e2e_training/results_final"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

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

def compute_signals(data):
    hs = torch.tensor(data["hs"]) # [N, 10, 256]
    fg = torch.tensor(data["fg"]) # [N, 10]
    orig_logits = np.squeeze(data["orig_logits"]) # [N]
    
    mean_h = hs.mean(dim=1, keepdim=True)
    norm_hs = F.normalize(hs, p=2, dim=-1)
    norm_mean = F.normalize(mean_h, p=2, dim=-1)
    cos_disp = (1.0 - (norm_hs * norm_mean).sum(dim=-1).min(dim=-1).values).numpy()
    
    diff = hs - mean_h
    slot_max_dev = diff.norm(p=2, dim=-1).max(dim=-1).values.numpy()
    
    fg_max = fg.max(dim=-1).values.numpy()
    
    return {
        "orig_logits": orig_logits,
        "cos_disp": cos_disp,
        "slot_max_dev": slot_max_dev,
        "fg_max": fg_max,
    }

def extract_standardized_scalars(data, val_stats=None):
    sig = compute_signals(data)
    parts = data["partitions"]
    
    if val_stats is None:
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

class RobustExistenceCalibrator(nn.Module):
    """
    Coordinate-Invariant Multi-Evidence Existence Calibrator
    """
    def __init__(self):
        super().__init__()
        self.raw_w_orig = nn.Parameter(torch.tensor(0.0)) # [0.5, 1.2]
        self.raw_w_disp = nn.Parameter(torch.tensor(0.5)) # [0.5, 2.0]
        self.raw_w_dev = nn.Parameter(torch.tensor(0.2))  # [0.2, 1.5]
        self.raw_w_fg = nn.Parameter(torch.tensor(0.0))   # [0.1, 1.0]
        self.bias = nn.Parameter(torch.tensor(0.0))
        
    @property
    def w_orig(self):
        return 0.5 + 0.7 * torch.sigmoid(self.raw_w_orig)
    @property
    def w_disp(self):
        return 0.5 + 1.5 * torch.sigmoid(self.raw_w_disp)
    @property
    def w_dev(self):
        return 0.2 + 1.3 * torch.sigmoid(self.raw_w_dev)
    @property
    def w_fg(self):
        return 0.1 + 0.9 * torch.sigmoid(self.raw_w_fg)
        
    def forward(self, z_o, z_c, z_d, z_f):
        return self.w_orig * z_o + self.w_disp * z_c + self.w_dev * z_d + self.w_fg * z_f + self.bias

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

def train_and_eval_split(split: str, epochs=25, lr=0.02, seed=3407):
    set_seed(seed)
    split_dir = HQ_DIR / split
    train_data = np.load(split_dir / "train.npz")
    val_data = np.load(split_dir / "val.npz")
    test_data = np.load(split_dir / "test.npz")
    
    # 1. Standardize based on seen validation statistics
    _, val_stats = extract_standardized_scalars(val_data)
    tr_norm, _ = extract_standardized_scalars(train_data, val_stats)
    v_norm, _ = extract_standardized_scalars(val_data, val_stats)
    t_norm, _ = extract_standardized_scalars(test_data, val_stats)
    
    val_parts = val_data["partitions"]
    val_seen = (val_parts == "S+") | (val_parts == "S-")
    val_y = (val_parts[val_seen] == "S+").astype(int)
    
    model = RobustExistenceCalibrator()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    
    tr_o = torch.tensor(tr_norm["orig_logits"], dtype=torch.float32)
    tr_c = torch.tensor(tr_norm["cos_disp"], dtype=torch.float32)
    tr_d = torch.tensor(tr_norm["slot_max_dev"], dtype=torch.float32)
    tr_f = torch.tensor(tr_norm["fg_max"], dtype=torch.float32)
    tr_y = torch.tensor(train_data["labels"], dtype=torch.float32)
    
    dataset = TensorDataset(tr_o, tr_c, tr_d, tr_f, tr_y)
    loader = DataLoader(dataset, batch_size=128, shuffle=True)
    
    v_o = torch.tensor(v_norm["orig_logits"][val_seen], dtype=torch.float32)
    v_c = torch.tensor(v_norm["cos_disp"][val_seen], dtype=torch.float32)
    v_d = torch.tensor(v_norm["slot_max_dev"][val_seen], dtype=torch.float32)
    v_f = torch.tensor(v_norm["fg_max"][val_seen], dtype=torch.float32)
    
    best_auc, best_state = 0.0, None
    for ep in range(1, epochs + 1):
        model.train()
        for bo, bc, bd, bf, by in loader:
            out = model(bo, bc, bd, bf)
            loss = F.binary_cross_entropy_with_logits(out, by)
            opt.zero_grad()
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            v_scores = model(v_o, v_c, v_d, v_f).numpy()
            v_auc = roc_auc_score(val_y, v_scores)
            if v_auc > best_auc:
                best_auc = v_auc
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
                
    model.load_state_dict(best_state)
    
    # 2. Threshold selection on val_seen
    with torch.no_grad():
        all_v = model(torch.tensor(v_norm["orig_logits"], dtype=torch.float32),
                      torch.tensor(v_norm["cos_disp"], dtype=torch.float32),
                      torch.tensor(v_norm["slot_max_dev"], dtype=torch.float32),
                      torch.tensor(v_norm["fg_max"], dtype=torch.float32)).numpy()
        threshold = choose_val_seen_threshold(all_v[val_seen], val_y)
        
        all_t = model(torch.tensor(t_norm["orig_logits"], dtype=torch.float32),
                      torch.tensor(t_norm["cos_disp"], dtype=torch.float32),
                      torch.tensor(t_norm["slot_max_dev"], dtype=torch.float32),
                      torch.tensor(t_norm["fg_max"], dtype=torch.float32)).numpy()
                      
    # 3. Test Evaluation
    test_parts = test_data["partitions"]
    test_qids = [str(q) for q in test_data["qids"]]
    
    seen_mask = (test_parts == "S+") | (test_parts == "S-")
    seen_labels = (test_parts[seen_mask] == "S+").astype(int)
    seen_auc = float(roc_auc_score(seen_labels, all_t[seen_mask]))
    
    u_mask = (test_parts == "U+") | (test_parts == "U-")
    u_labels = (test_parts[u_mask] == "U+").astype(int)
    u_auc = float(roc_auc_score(u_labels, all_t[u_mask]))
    
    gap = seen_auc - u_auc
    
    pairs_file = REPO / f"data/release/semantic_existence_v2/{split}/matched_u_pairs.jsonl"
    qid_to_score = dict(zip(test_qids, all_t))
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
    u_pos_frr = float((all_t[u_pos_mask] < threshold).mean() * 100.0)
    u_neg_rr = float((all_t[u_neg_mask] < threshold).mean() * 100.0)
    
    metrics = {
        "split": split,
        "seed": seed,
        "Seen_AUROC": seen_auc,
        "Unseen_AUROC": u_auc,
        "Gap": gap,
        "Matched_PairAcc": pair_acc,
        "U_pos_FRR": u_pos_frr,
        "U_neg_RR": u_neg_rr,
        "Threshold": float(threshold),
        "best_val_seen_auc": float(best_auc),
        "learned_weights": {
            "w_orig": float(model.w_orig.item()),
            "w_disp": float(model.w_disp.item()),
            "w_dev": float(model.w_dev.item()),
            "w_fg": float(model.w_fg.item()),
            "bias": float(model.bias.item()),
        },
    }
    
    # 4. Save results and predictions
    split_out = OUT_ROOT / split
    split_out.mkdir(parents=True, exist_ok=True)
    torch.save({"model": best_state, "val_stats": val_stats, "metrics": metrics}, split_out / "best.ckpt")
    with open(split_out / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    with open(split_out / "predictions.jsonl", "w") as f:
        for q, sc, p in zip(test_qids, all_t, test_parts):
            f.write(json.dumps({"qid": q, "pred_score": float(sc), "partition": str(p)}) + "\n")
            
    return metrics

def main():
    print("=" * 115)
    print("RUNNING FINAL BENCHMARK EVALUATION (Seed: 3407)")
    print("Benchmark Baseline: /home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md")
    print("=" * 115)
    
    all_metrics = {}
    seen_list, unseen_list, gap_list, pair_list = [], [], [], []
    
    for split in SPLITS:
        base = BASELINE_QD[split]
        print(f"\n---> Training and Evaluating Split {split} (Seed 3407)...")
        m = train_and_eval_split(split, epochs=25, lr=0.02, seed=3407)
        all_metrics[split] = m
        
        seen_list.append(m["Seen_AUROC"])
        unseen_list.append(m["Unseen_AUROC"])
        gap_list.append(m["Gap"])
        pair_list.append(m["Matched_PairAcc"])
        
        g_diff = base["Gap"] - m["Gap"]
        w = m["learned_weights"]
        print(f"  [{split}] Baseline: Seen={base['Seen']:.4f}, Unseen={base['Unseen']:.4f}, Gap={base['Gap']:.4f}, PairAcc={base['PairAcc']:.4f}")
        print(f"  [{split}] GDCA:     Seen={m['Seen_AUROC']:.4f}, Unseen={m['Unseen_AUROC']:.4f}, Gap={m['Gap']:.4f} (Gap Red: {g_diff:+.4f}), PairAcc={m['Matched_PairAcc']:.4f}")
        print(f"  [{split}] Weights:  w_orig={w['w_orig']:.3f}, w_disp={w['w_disp']:.3f}, w_dev={w['w_dev']:.3f}, w_fg={w['w_fg']:.3f}")
        
    print("\n" + "=" * 115)
    print("OFFICIAL 5-SPLIT BENCHMARK COMPARISON TABLE (Seed 3407)")
    print("=" * 115)
    print(f"{'Split':<10} | {'Base Seen':<10} | {'GDCA Seen':<10} | {'Base Unseen':<11} | {'GDCA Unseen':<11} | {'Base Gap':<9} | {'GDCA Gap':<9} | {'Gap Red.':<9} | {'Base Pair':<9} | {'GDCA Pair':<9}")
    print("-" * 115)
    
    for split in SPLITS:
        b = BASELINE_QD[split]
        m = all_metrics[split]
        g_red = b["Gap"] - m["Gap"]
        print(f"{split:<10} | {b['Seen']:<10.4f} | {m['Seen_AUROC']:<10.4f} | {b['Unseen']:<11.4f} | {m['Unseen_AUROC']:<11.4f} | {b['Gap']:<9.4f} | {m['Gap']:<9.4f} | {g_red:<+9.4f} | {b['PairAcc']:<9.4f} | {m['Matched_PairAcc']:<9.4f}")
        
    print("-" * 115)
    b_mean_seen = 0.7476
    b_mean_unseen = 0.5144
    b_mean_gap = 0.2332
    b_mean_pair = 0.5294
    
    m_seen = np.mean(seen_list)
    m_unseen = np.mean(unseen_list)
    m_gap = np.mean(gap_list)
    m_pair = np.mean(pair_list)
    m_gap_red = b_mean_gap - m_gap
    
    print(f"{'MEAN':<10} | {b_mean_seen:<10.4f} | {m_seen:<10.4f} | {b_mean_unseen:<11.4f} | {m_unseen:<11.4f} | {b_mean_gap:<9.4f} | {m_gap:<9.4f} | {m_gap_red:<+9.4f} | {b_mean_pair:<9.4f} | {m_pair:<9.4f}")
    print("=" * 115)
    
    summary = {
        "benchmark_baseline": BASELINE_QD,
        "mean_baseline": {"Seen": b_mean_seen, "Unseen": b_mean_unseen, "Gap": b_mean_gap, "PairAcc": b_mean_pair},
        "per_split_results": all_metrics,
        "mean_results": {
            "Seen_AUROC": float(m_seen),
            "Unseen_AUROC": float(m_unseen),
            "Gap": float(m_gap),
            "Gap_Reduction": float(m_gap_red),
            "Matched_PairAcc": float(m_pair),
        }
    }
    with open(OUT_ROOT / "benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nAll results, checkpoints, and predictions saved to: {OUT_ROOT}")

if __name__ == "__main__":
    main()
