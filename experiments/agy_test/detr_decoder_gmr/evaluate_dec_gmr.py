#!/usr/bin/env python3
"""
DEC-GMR: Decoder-Evidential Conjunctive Verification Evaluation Suite.

Evaluates standalone single-backbone models (Moment-DETR, QD-DETR, FlashVTG)
under Query-Intent Adaptive Conjunctive Gating across all 5 splits.
Runs 2,000-iteration Paired Video Cluster Bootstrap for statistical significance.
"""
from __future__ import annotations
import sys
import os
import json
import random
import time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
RUNS_DIR = BASE_DIR / "runs"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
BACKBONES = {
    "moment": ("Moment-DETR", 1),
    "qd": ("QD-DETR", 2),
    "flash": ("FlashVTG", 0)
}

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)

def compute_matched_pair_acc(qids, scores, pairs_file):
    if not pairs_file.exists():
        return 0.5
    pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
    qid_to_score = dict(zip([str(q) for q in qids], scores))
    accs = []
    for p in pairs:
        pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
        if pq in qid_to_score and nq in qid_to_score:
            sp, sn = qid_to_score[pq], qid_to_score[nq]
            accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
    return float(np.mean(accs)) if accs else 0.5

def route_query_evidence(queries, X):
    """
    Query-Intent Semantic Routing:
    - Kinetic stream for speed/locomotion actions (run, walk, slow, fast)
    - Composite object stream for fine-grained interaction with entities (chair, bed, couch, box, cabinet)
    - State transition stream for manual actions (put, take, drink, pour, open, close)
    """
    s_ev = np.zeros(len(queries), dtype=np.float32)
    for i, q in enumerate(queries):
        if any(w in q for w in ["run", "walk", "slow", "fast"]):
            # Velocity contrast + displacement + action alignment
            s_ev[i] = 0.50 * X[i, 5] + 0.35 * X[i, 8] + 0.15 * X[i, 12]
        elif any(w in q for w in ["chair", "couch", "bed", "sofa", "box", "cabinet", "shelf", "table", "cup", "book"]):
            # Peak frame saliency + object phrase alignment + global context
            s_ev[i] = 0.45 * X[i, 5] + 0.35 * X[i, 6] + 0.20 * X[i, 3]
        else:
            # Peak frame + global context + action displacement
            s_ev[i] = 0.55 * X[i, 5] + 0.30 * X[i, 3] + 0.15 * X[i, 12]
    return s_ev

def evaluate():
    set_seed(3407)
    print("================================================================================")
    print("      DEC-GMR: DECODER-EVIDENTIAL CONJUNCTIVE VERIFICATION BENCHMARK            ")
    print("================================================================================")
    t0 = time.time()
    
    split_results = []
    
    for split in SPLITS:
        split_dir = RUNS_DIR / split
        split_dir.mkdir(parents=True, exist_ok=True)
        
        feat_dir = CACHE_DIR / split
        te_d = np.load(feat_dir / "test.npz")
        X_te = te_d["X"]
        y_te = te_d["labels"]
        parts_te = te_d["partitions"]
        qids_te = te_d["qids"]
        vids_te = te_d["vids"]
        
        is_s_te = (parts_te == "S+") | (parts_te == "S-")
        is_u_te = (parts_te == "U+") | (parts_te == "U-")
        pairs_file = RELEASE_DIR / split / "matched_u_pairs.jsonl"
        
        test_file = RELEASE_DIR / split / "test.jsonl"
        test_rows = [json.loads(l) for l in test_file.open()]
        queries = [r["query"].lower() for r in test_rows]
        
        # 1. Compute Routed Multimodal Evidence
        s_ev = route_query_evidence(queries, X_te)
        r_ev = np.argsort(np.argsort(s_ev)) / len(s_ev)
        
        save_dict = {
            "qids": qids_te,
            "vids": vids_te,
            "partitions": parts_te,
            "labels": y_te,
        }
        
        split_info = {"split": split, "models": {}}
        
        for bb_key, (bb_name, col_idx) in BACKBONES.items():
            s_det = X_te[:, col_idx]
            r_det = np.argsort(np.argsort(s_det)) / len(s_det)
            
            # Baseline metrics
            b_s = float(roc_auc_score(y_te[is_s_te], s_det[is_s_te]))
            b_u = float(roc_auc_score(y_te[is_u_te], s_det[is_u_te]))
            b_pa = compute_matched_pair_acc(qids_te, s_det, pairs_file)
            
            # DEC-GMR Conjunctive Verification
            s_dec = (r_det ** 0.65) * (r_ev ** 0.85)
            
            dec_s = float(roc_auc_score(y_te[is_s_te], s_dec[is_s_te]))
            dec_u = float(roc_auc_score(y_te[is_u_te], s_dec[is_u_te]))
            dec_pa = compute_matched_pair_acc(qids_te, s_dec, pairs_file)
            
            save_dict[f"pred_base_{bb_key}"] = s_det
            save_dict[f"pred_dec_{bb_key}"] = s_dec
            
            split_info["models"][bb_key] = {
                "base_seen": b_s,
                "base_unseen": b_u,
                "base_gap": b_s - b_u,
                "base_pa": b_pa,
                "dec_seen": dec_s,
                "dec_unseen": dec_u,
                "dec_gap": dec_s - dec_u,
                "dec_pa": dec_pa,
                "gain_unseen": dec_u - b_u,
                "gap_reduction": (b_s - b_u) - (dec_s - dec_u),
            }
            print(f"[{split:8s} | {bb_name:12s}] Base: S={b_s:.4f}, U={b_u:.4f} -> DEC-GMR: S={dec_s:.4f}, U={dec_u:.4f} (Gain={dec_u - b_u:+.4f}, PairAcc={dec_pa:.4f})")
            
        np.savez_compressed(split_dir / "predictions.npz", **save_dict)
        split_info["save_dict"] = save_dict
        split_results.append(split_info)
        
    # 2. Compute Macro Averages
    macro_summary = {}
    for bb_key in BACKBONES:
        macro_summary[bb_key] = {
            "base_seen": float(np.mean([s["models"][bb_key]["base_seen"] for s in split_results])),
            "base_unseen": float(np.mean([s["models"][bb_key]["base_unseen"] for s in split_results])),
            "base_gap": float(np.mean([s["models"][bb_key]["base_gap"] for s in split_results])),
            "base_pa": float(np.mean([s["models"][bb_key]["base_pa"] for s in split_results])),
            "dec_seen": float(np.mean([s["models"][bb_key]["dec_seen"] for s in split_results])),
            "dec_unseen": float(np.mean([s["models"][bb_key]["dec_unseen"] for s in split_results])),
            "dec_gap": float(np.mean([s["models"][bb_key]["dec_gap"] for s in split_results])),
            "dec_pa": float(np.mean([s["models"][bb_key]["dec_pa"] for s in split_results])),
            "gain_unseen": float(np.mean([s["models"][bb_key]["gain_unseen"] for s in split_results])),
            "gap_reduction": float(np.mean([s["models"][bb_key]["gap_reduction"] for s in split_results])),
        }
        
    # 3. 2,000-resample Paired Video Cluster Bootstrap
    print("\n==================== RUNNING 2000-ITERATION PAIRED VIDEO CLUSTER BOOTSTRAP ====================")
    shared_vids = sorted(list(set.union(*[set(s["save_dict"]["vids"]) for s in split_results])))
    n_vids = len(shared_vids)
    
    vid_to_idx_per_split = []
    for s in split_results:
        v_map = {}
        for i, v in enumerate(s["save_dict"]["vids"]):
            v_map.setdefault(v, []).append(i)
        vid_to_idx_per_split.append(v_map)
        
    bootstrap_summary = {}
    for bb_key in BACKBONES:
        boot_u_dec, boot_u_base, boot_gain = [], [], []
        for b in range(2000):
            sample_vids = np.random.choice(shared_vids, size=n_vids, replace=True)
            split_dec, split_base = [], []
            valid = True
            for s_idx, s in enumerate(split_results):
                v_map = vid_to_idx_per_split[s_idx]
                sub_indices = []
                for v in sample_vids:
                    if v in v_map:
                        sub_indices.extend(v_map[v])
                if not sub_indices:
                    valid = False
                    break
                y_b = s["save_dict"]["labels"][sub_indices]
                parts_b = s["save_dict"]["partitions"][sub_indices]
                u_m = (parts_b == "U+") | (parts_b == "U-")
                if len(np.unique(y_b[u_m])) < 2:
                    valid = False
                    break
                s_dec = s["save_dict"][f"pred_dec_{bb_key}"][sub_indices]
                s_base = s["save_dict"][f"pred_base_{bb_key}"][sub_indices]
                split_dec.append(roc_auc_score(y_b[u_m], s_dec[u_m]))
                split_base.append(roc_auc_score(y_b[u_m], s_base[u_m]))
                
            if not valid:
                continue
            m_dec = float(np.mean(split_dec))
            m_base = float(np.mean(split_base))
            boot_u_dec.append(m_dec)
            boot_u_base.append(m_base)
            boot_gain.append(m_dec - m_base)
            
        def ci_fmt(arr):
            lo, hi = np.percentile(arr, 2.5), np.percentile(arr, 97.5)
            sign = "+" if lo >= 0 else ""
            return f"[{sign}{lo:.4f}, +{hi:.4f}]"
            
        bootstrap_summary[bb_key] = {
            "dec_mean": float(np.mean(boot_u_dec)),
            "dec_ci": ci_fmt(boot_u_dec),
            "base_mean": float(np.mean(boot_u_base)),
            "base_ci": ci_fmt(boot_u_base),
            "gain_mean": float(np.mean(boot_gain)),
            "gain_ci": ci_fmt(boot_gain),
        }
        print(f"[{bb_key.upper()}] Bootstrap Unseen: {bootstrap_summary[bb_key]['dec_mean']:.4f} {bootstrap_summary[bb_key]['dec_ci']} (Gain: {bootstrap_summary[bb_key]['gain_mean']:+.4f} {bootstrap_summary[bb_key]['gain_ci']})")

    # 4. Save Final Summary
    summary_out = {
        "macro_summary": macro_summary,
        "bootstrap": bootstrap_summary,
        "splits": [{
            "split": s["split"],
            "models": s["models"]
        } for s in split_results]
    }
    with open(BASE_DIR / "benchmark_summary.json", "w") as f:
        json.dump(summary_out, f, indent=2)
        
    print(f"\nBenchmark summary saved to {BASE_DIR / 'benchmark_summary.json'}!")
    print("\n========================= FINAL MACRO PERFORMANCE BENCHMARK =========================")
    for bb_key, (bb_name, _) in BACKBONES.items():
        m = macro_summary[bb_key]
        b = bootstrap_summary[bb_key]
        print(f"\nModel: {bb_name}")
        print(f"  Baseline : Seen={m['base_seen']:.4f}, Unseen={m['base_unseen']:.4f}, Gap={m['base_gap']:.4f}, PairAcc={m['base_pa']:.4f}")
        print(f"  DEC-GMR  : Seen={m['dec_seen']:.4f}, Unseen={m['dec_unseen']:.4f}, Gap={m['dec_gap']:.4f}, PairAcc={m['dec_pa']:.4f}")
        print(f"  NET GAIN : Unseen Gain={m['gain_unseen']:+.4f} (95% CI: {b['gain_ci']}), Gap Reduction={m['gap_reduction']:+.4f}")

    print(f"\nExecution finished in {time.time()-t0:.2f}s.")

if __name__ == "__main__":
    evaluate()
