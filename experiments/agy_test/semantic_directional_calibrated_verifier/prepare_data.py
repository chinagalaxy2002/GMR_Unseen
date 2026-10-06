#!/usr/bin/env python3
"""
Pre-assemble 14-dimensional multi-stream feature matrices for Semantic Directional Calibrated Verifier (SDCV).

14 Channels:
  0: FlashVTG detection probability
  1: Moment-DETR detection probability
  2: QD-DETR detection probability
  3: CLIP global scene context similarity (sim_glob_sent)
  4: CLIP candidate window similarity (sim_cand_sent)
  5: CLIP peak frame visual saliency (sim_peak)
  6: CLIP decomposed object phrase alignment (sim_cand_obj)
  7: CLIP decomposed action phrase alignment (sim_cand_act)
  8: SlowFast candidate velocity contrast (v_cand - v_glob)
  9: SlowFast candidate temporal displacement (||sf(te) - sf(ts)||)
 10: Detector foreground max confidence (fg_max)
 11: Candidate proposal span duration (te - ts)
 12: Signed action state transition: <v(te) - v(ts), q_act> (directional sign!)
 13: Signed object state transition: <v(te) - v(ts), q_obj> (directional sign!)
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
CLIP_DIR = REPO_ROOT / "features/charades_semantic_existence/clip"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def extract_signed_transitions(vids, spans, q_act, q_obj, clip_cache):
    N = len(vids)
    delta_act = np.zeros(N, dtype=np.float32)
    delta_obj = np.zeros(N, dtype=np.float32)
    
    for i in range(N):
        v = str(vids[i])
        if v not in clip_cache:
            f = CLIP_DIR / f"{v}.npz"
            if f.exists():
                c = np.load(f)["features"].astype(np.float32)
                c = c / (np.linalg.norm(c, axis=-1, keepdims=True) + 1e-8)
                clip_cache[v] = c
            else:
                clip_cache[v] = None
        c = clip_cache[v]
        if c is not None and len(c) >= 2:
            T = len(c)
            s_idx = max(0, min(T - 1, int(round(spans[i, 0] * (T - 1)))))
            e_idx = max(0, min(T - 1, int(round(spans[i, 1] * (T - 1)))))
            delta_act[i] = float(np.dot(c[e_idx], q_act[i]) - np.dot(c[s_idx], q_act[i]))
            delta_obj[i] = float(np.dot(c[e_idx], q_obj[i]) - np.dot(c[s_idx], q_obj[i]))
            
    return delta_act[:, None], delta_obj[:, None]

def process_split(split: str, clip_cache: dict):
    print(f"\n==================== PREPARING SDCV DATA: {split} ====================")
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
    
    d_act_tr, d_obj_tr = extract_signed_transitions(
        a_tr["vids"], a_tr["best_spans"], a_tr["q_proj_act"], a_tr["q_proj_obj"], clip_cache
    )
    
    # Assemble 14D: [:6], obj, act, [6:8] (vel, disp), [8:10] (fg, span), d_act, d_obj
    X_tr = np.concatenate([
        X_mcv_tr[:, :6],
        obj_tr,
        act_tr,
        X_mcv_tr[:, 6:8],
        X_mcv_tr[:, 8:10],
        d_act_tr,
        d_obj_tr,
    ], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "train.npz",
        X=X_tr,
        labels=c_tr["labels"],
        qids=c_tr["qids"],
        vids=c_tr["vids"],
        same_vid_pairs=c_tr["same_vid_pairs"],
        q_proj_sent=a_tr["q_proj_sent"],
    )
    print(f"[{split}] Train saved: X shape={X_tr.shape}, pairs={len(c_tr['same_vid_pairs'])}")
    
    # 2. Val
    print(f"[{split}] Processing Val...")
    c_val = np.load(MCV_CACHE / split / "val.npz")
    a_val = np.load(ALIGNED_DIR / split / "val.npz")
    
    X_mcv_val = c_val["X"]
    a_val_map = {str(q): i for i, q in enumerate(a_val["qids"])}
    val_indices = [a_val_map[str(q)] for q in c_val["qids"]]
    
    obj_val = a_val["sim_cand_obj"][val_indices, None]
    act_val = a_val["sim_cand_act"][val_indices, None]
    
    d_act_val, d_obj_val = extract_signed_transitions(
        a_val["vids"][val_indices],
        a_val["best_spans"][val_indices],
        a_val["q_proj_act"][val_indices],
        a_val["q_proj_obj"][val_indices],
        clip_cache,
    )
    
    X_val = np.concatenate([
        X_mcv_val[:, :6],
        obj_val,
        act_val,
        X_mcv_val[:, 6:8],
        X_mcv_val[:, 8:10],
        d_act_val,
        d_obj_val,
    ], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "val.npz",
        X=X_val,
        labels=c_val["labels"],
        qids=c_val["qids"],
        vids=c_val["vids"],
        q_proj_sent=a_val["q_proj_sent"][val_indices],
    )
    print(f"[{split}] Val saved: X shape={X_val.shape}")
    
    # 3. Test
    print(f"[{split}] Processing Test...")
    c_te = np.load(MCV_CACHE / split / "test.npz")
    a_te = np.load(ALIGNED_DIR / split / "test.npz")
    
    X_mcv_te = c_te["X"]
    obj_te = a_te["sim_cand_obj"][:, None]
    act_te = a_te["sim_cand_act"][:, None]
    
    d_act_te, d_obj_te = extract_signed_transitions(
        a_te["vids"], a_te["best_spans"], a_te["q_proj_act"], a_te["q_proj_obj"], clip_cache
    )
    
    X_te = np.concatenate([
        X_mcv_te[:, :6],
        obj_te,
        act_te,
        X_mcv_te[:, 6:8],
        X_mcv_te[:, 8:10],
        d_act_te,
        d_obj_te,
    ], axis=1).astype(np.float32)
    
    np.savez_compressed(
        out_dir / "test.npz",
        X=X_te,
        labels=c_te["labels"],
        partitions=c_te["partitions"],
        qids=c_te["qids"],
        vids=c_te["vids"],
        base_scores=c_te["base_scores"],
        q_proj_sent=a_te["q_proj_sent"],
    )
    print(f"[{split}] Test saved: X shape={X_te.shape} in {time.time()-t0:.2f}s")

def main():
    t_start = time.time()
    clip_cache = {}
    for sp in SPLITS:
        process_split(sp, clip_cache)
    print(f"\nAll 5 splits prepared successfully with 14D features in {time.time()-t_start:.2f}s!")

if __name__ == "__main__":
    main()
