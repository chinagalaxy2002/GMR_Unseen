#!/usr/bin/env python3
"""
Pre-assemble 12-dimensional multi-stream feature matrices for Decomposed Directional Verifier (DDV).
12 Channels:
  0: FlashVTG detection probability (sigmoid of canonical logit)
  1: Moment-DETR detection probability
  2: QD-DETR detection probability
  3: CLIP global scene context similarity (sim_glob_sent)
  4: CLIP candidate window similarity (sim_cand_sent)
  5: CLIP peak frame visual saliency (sim_peak)
  6: CLIP decomposed object phrase alignment (sim_cand_obj)
  7: CLIP decomposed action phrase alignment (sim_cand_act)
  8: SlowFast candidate velocity contrast (m_contrast = v_cand - v_glob)
  9: SlowFast candidate temporal displacement (m_disp = ||sf(te) - sf(ts)||)
 10: Detector foreground max confidence (fg_max)
 11: Candidate proposal span duration (te - ts)
"""
from __future__ import annotations
import os
import json
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
CACHE_OUT = BASE_DIR / "cache"
CACHE_OUT.mkdir(parents=True, exist_ok=True)

MCV_CACHE = REPO_ROOT / "experiments/agy_test/multiscale_counterfactual_verifier/cache_features"
ALIGNED_DIR = REPO_ROOT / "experiments/agy_test/aligned_calibration_verifier/aligned_features"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def process_split(split: str):
    print(f"\n==================== PREPARING DDV DATA: {split} ====================")
    t0 = time.time()
    out_dir = CACHE_OUT / split
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Train
    print(f"[{split}] Processing Train...")
    c_tr = np.load(MCV_CACHE / split / "train.npz")
    a_tr = np.load(ALIGNED_DIR / split / "train.npz")
    
    X_mcv_tr = c_tr["X"] # (N, 10)
    obj_tr = a_tr["sim_cand_obj"][:, None]
    act_tr = a_tr["sim_cand_act"][:, None]
    # assemble 12D: [:6], obj, act, [6:]
    X_tr = np.concatenate([X_mcv_tr[:, :6], obj_tr, act_tr, X_mcv_tr[:, 6:]], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "train.npz",
        X=X_tr,
        labels=c_tr["labels"],
        qids=c_tr["qids"],
        vids=c_tr["vids"],
        same_vid_pairs=c_tr["same_vid_pairs"],
    )
    print(f"[{split}] Train saved: X shape={X_tr.shape}, pairs={len(c_tr['same_vid_pairs'])}")
    
    # 2. Val (Seen validation subset)
    print(f"[{split}] Processing Val...")
    c_val = np.load(MCV_CACHE / split / "val.npz")
    a_val = np.load(ALIGNED_DIR / split / "val.npz")
    
    X_mcv_val = c_val["X"]
    a_val_map = {str(q): i for i, q in enumerate(a_val["qids"])}
    val_indices = [a_val_map[str(q)] for q in c_val["qids"]]
    obj_val = a_val["sim_cand_obj"][val_indices, None]
    act_val = a_val["sim_cand_act"][val_indices, None]
    X_val = np.concatenate([X_mcv_val[:, :6], obj_val, act_val, X_mcv_val[:, 6:]], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "val.npz",
        X=X_val,
        labels=c_val["labels"],
        qids=c_val["qids"],
        vids=c_val["vids"],
    )
    print(f"[{split}] Val saved: X shape={X_val.shape}")
    
    # 3. Test
    print(f"[{split}] Processing Test...")
    c_te = np.load(MCV_CACHE / split / "test.npz")
    a_te = np.load(ALIGNED_DIR / split / "test.npz")
    
    X_mcv_te = c_te["X"]
    obj_te = a_te["sim_cand_obj"][:, None]
    act_te = a_te["sim_cand_act"][:, None]
    X_te = np.concatenate([X_mcv_te[:, :6], obj_te, act_te, X_mcv_te[:, 6:]], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "test.npz",
        X=X_te,
        labels=c_te["labels"],
        partitions=c_te["partitions"],
        qids=c_te["qids"],
        vids=c_te["vids"],
        base_scores=c_te["base_scores"],
    )
    print(f"[{split}] Test saved: X shape={X_te.shape} in {time.time()-t0:.2f}s")

def main():
    for sp in SPLITS:
        process_split(sp)
    print("\nAll splits prepared successfully in cache!")

if __name__ == "__main__":
    main()
