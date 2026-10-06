#!/usr/bin/env python3
"""
Extract Target-Specific Candidate Features for FlashVTG, Moment-DETR, and QD-DETR.
Generates candidate-local CLIP, SlowFast, and signed-transition features
strictly based on each model's own predicted candidate proposals.
"""
from __future__ import annotations
import os
import sys
import json
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CLIP_DIR = REPO_ROOT / "features/charades_semantic_existence/clip"
SLOWFAST_DIR = REPO_ROOT / "features/charades_semantic_existence/slowfast"
ALIGNED_DIR = REPO_ROOT / "experiments/agy_test/aligned_calibration_verifier/aligned_features"
FEAT_CACHE_DIR = REPO_ROOT / "experiments/agy_test/cache/features"
RESULTS_DIR = REPO_ROOT / "results/semantic_existence/multi_split_v2"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
MODELS = ["flash", "moment", "qd"]

def norm(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)

def load_video_features(vids, clip_cache, sf_cache):
    for v in set(vids):
        v = str(v)
        if v not in clip_cache:
            p = CLIP_DIR / f"{v}.npz"
            if p.exists():
                c = np.load(p)["features"].astype(np.float32)
                clip_cache[v] = norm(c)
            else:
                clip_cache[v] = None
        if v not in sf_cache:
            p = SLOWFAST_DIR / f"{v}.npz"
            if p.exists():
                s = np.load(p)["features"].astype(np.float32)
                sf_cache[v] = s
            else:
                sf_cache[v] = None

def extract_multimodal_for_spans(
    vids, spans, durations, q_sent, q_act, q_obj, ref_vec, clip_cache, sf_cache
):
    N = len(vids)
    sim_glob = np.zeros(N, dtype=np.float32)
    sim_cand = np.zeros(N, dtype=np.float32)
    sim_peak = np.zeros(N, dtype=np.float32)
    sim_obj = np.zeros(N, dtype=np.float32)
    sim_act = np.zeros(N, dtype=np.float32)
    sf_vel = np.zeros(N, dtype=np.float32)
    sf_disp = np.zeros(N, dtype=np.float32)
    d_act = np.zeros(N, dtype=np.float32)
    d_obj = np.zeros(N, dtype=np.float32)

    ref_sent = float(np.dot(ref_vec, q_sent.mean(axis=0))) # scalar proxy for ref centering
    
    for i in range(N):
        v = str(vids[i])
        c = clip_cache.get(v)
        s = sf_cache.get(v)
        
        st_norm, ed_norm = spans[i, 0], spans[i, 1]
        
        # CLIP features
        if c is not None and len(c) > 0:
            T_c = len(c)
            s_idx = max(0, min(T_c - 1, int(round(st_norm * (T_c - 1)))))
            e_idx = max(0, min(T_c - 1, int(round(ed_norm * (T_c - 1)))))
            if s_idx > e_idx:
                s_idx, e_idx = e_idx, s_idx
                
            # Candidate mean frame
            cand_c = norm(c[s_idx : e_idx + 1].mean(axis=0))
            glob_c = norm(c.mean(axis=0))
            
            ref_s = float(np.dot(ref_vec, q_sent[i]))
            ref_a = float(np.dot(ref_vec, q_act[i]))
            ref_o = float(np.dot(ref_vec, q_obj[i]))
            
            sim_glob[i] = float(np.dot(glob_c, q_sent[i])) - ref_s
            sim_cand[i] = float(np.dot(cand_c, q_sent[i])) - ref_s
            sim_obj[i] = float(np.dot(cand_c, q_obj[i])) - ref_o
            sim_act[i] = float(np.dot(cand_c, q_act[i])) - ref_a
            
            # Peak frame
            all_sims = np.dot(c, q_sent[i]) - ref_s
            sim_peak[i] = float(np.max(all_sims))
            
            # Signed endpoint transitions
            d_act[i] = float(np.dot(c[e_idx] - c[s_idx], q_act[i]))
            d_obj[i] = float(np.dot(c[e_idx] - c[s_idx], q_obj[i]))
            
        # SlowFast features
        if s is not None and len(s) > 1:
            T_s = len(s)
            diffs = np.linalg.norm(s[1:] - s[:-1], axis=-1)
            mean_diff = float(np.mean(diffs))
            s_idx = max(0, min(T_s - 1, int(round(st_norm * (T_s - 1)))))
            e_idx = max(0, min(T_s - 1, int(round(ed_norm * (T_s - 1)))))
            if s_idx > e_idx:
                s_idx, e_idx = e_idx, s_idx
                
            if e_idx > s_idx:
                cand_diff = float(np.mean(diffs[s_idx:e_idx]))
            else:
                cand_diff = float(diffs[s_idx]) if s_idx < len(diffs) else mean_diff
                
            sf_vel[i] = cand_diff - mean_diff
            sf_disp[i] = float(np.linalg.norm(s[e_idx] - s[s_idx]))

    return np.stack([
        sim_glob, sim_cand, sim_peak, sim_obj, sim_act, sf_vel, sf_disp, d_act, d_obj
    ], axis=1)

def process_all():
    print("================================================================================")
    print("       TARGET-SPECIFIC CANDIDATE FEATURE EXTRACTION                             ")
    print("================================================================================")
    t0 = time.time()
    clip_cache = {}
    sf_cache = {}

    for split in SPLITS:
        print(f"\n[{split}] >>> Processing target-specific features...")
        aligned_train = np.load(ALIGNED_DIR / split / "train.npz")
        aligned_val = np.load(ALIGNED_DIR / split / "val.npz")
        aligned_test = np.load(ALIGNED_DIR / split / "test.npz")
        
        train_ref = aligned_train["train_reference"]
        val_map = {q: i for i, q in enumerate(aligned_val["qids"])}
        
        # Pre-cache all videos for this split
        all_vids = set(aligned_train["vids"]) | set(aligned_val["vids"]) | set(aligned_test["vids"])
        load_video_features(all_vids, clip_cache, sf_cache)
        print(f"[{split}] Cached {len(clip_cache)} CLIP and {len(sf_cache)} SlowFast videos in RAM.")
        
        for model in MODELS:
            m_dir = CACHE_DIR / split / model
            m_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{split}/{model}] Assembling datasets...")
            
            # --- 1. TRAIN ---
            m_tr = np.load(FEAT_CACHE_DIR / split / model / "train.npz")
            qids_tr = m_tr["qids"]
            vids_tr = m_tr["vids"]
            dur_tr = m_tr["durations"]
            lbl_tr = m_tr["labels"]
            
            raw_logits_tr = m_tr["original_exist_logits"]
            s_det_tr = 1.0 / (1.0 + np.exp(-raw_logits_tr))
            
            spans_xx = m_tr["spans_xx"]
            fg_scores = m_tr["foreground_scores"]
            best_k = np.argmax(fg_scores, axis=1)
            
            spans_norm_tr = np.zeros((len(qids_tr), 2), dtype=np.float32)
            fg_max_tr = np.zeros(len(qids_tr), dtype=np.float32)
            
            for i in range(len(qids_tr)):
                k = best_k[i]
                fg_max_tr[i] = fg_scores[i, k]
                if model == "flash":
                    c, w = spans_xx[i, k]
                    spans_norm_tr[i] = [max(0.0, min(1.0, c - w / 2.0)), max(0.0, min(1.0, c + w / 2.0))]
                else:
                    s_w, e_w = spans_xx[i, k]
                    spans_norm_tr[i] = [max(0.0, min(1.0, s_w)), max(0.0, min(1.0, e_w))]
                    
            width_tr = spans_norm_tr[:, 1] - spans_norm_tr[:, 0]
            
            mm_tr = extract_multimodal_for_spans(
                vids_tr, spans_norm_tr, dur_tr,
                aligned_train["q_proj_sent"], aligned_train["q_proj_act"], aligned_train["q_proj_obj"],
                train_ref, clip_cache, sf_cache
            )
            # Full 12D: s_det, sim_glob, sim_cand, sim_peak, sim_obj, sim_act, sf_vel, sf_disp, fg_max, span_width, d_act, d_obj
            X_tr = np.concatenate([
                s_det_tr[:, None],
                mm_tr[:, :5], # glob, cand, peak, obj, act
                mm_tr[:, 5:7], # sf_vel, sf_disp
                fg_max_tr[:, None],
                width_tr[:, None],
                mm_tr[:, 7:], # d_act, d_obj
            ], axis=1)
            
            # Mine same-video pairs for train
            pos_idx = np.where(lbl_tr == 1)[0]
            neg_idx = np.where(lbl_tr == 0)[0]
            vid_to_pos = {}
            for idx in pos_idx:
                vid_to_pos.setdefault(vids_tr[idx], []).append(idx)
            same_vid_pairs = []
            for idx in neg_idx:
                v = vids_tr[idx]
                if v in vid_to_pos:
                    for p_idx in vid_to_pos[v]:
                        same_vid_pairs.append((p_idx, idx))
            same_vid_pairs = np.array(same_vid_pairs, dtype=np.int32)
            
            np.savez_compressed(
                m_dir / "train.npz",
                X=X_tr,
                labels=lbl_tr,
                qids=qids_tr,
                vids=vids_tr,
                same_vid_pairs=same_vid_pairs,
            )
            
            # --- 2. VAL ---
            if model == "flash":
                val_path = list((RESULTS_DIR / split / "flash").glob("*/hl_val_submission.jsonl"))[0]
            elif model == "moment":
                val_path = RESULTS_DIR / split / "moment/best_charades_semantic_existence_val_preds.jsonl"
            else:
                val_path = RESULTS_DIR / split / "qd/best_charades_semantic_existence_val_preds.jsonl"
                
            val_items = [json.loads(l) for l in val_path.read_text().splitlines() if l.strip()]
            qids_val = [item["qid"] for item in val_items]
            vids_val = [item["vid"] for item in val_items]
            
            val_sub_indices = [val_map[q] for q in qids_val]
            dur_val = aligned_val["durations"][val_sub_indices]
            lbl_val = aligned_val["labels"][val_sub_indices]
            
            if model == "flash" and "pred_exist_logit" in val_items[0]:
                s_det_val = np.array([1.0 / (1.0 + np.exp(-float(item["pred_exist_logit"]))) for item in val_items], dtype=np.float32)
            else:
                s_det_val = np.array([float(item.get("pred_exist_score", 0.5)) for item in val_items], dtype=np.float32)
            spans_norm_val = np.zeros((len(val_items), 2), dtype=np.float32)
            fg_max_val = np.zeros(len(val_items), dtype=np.float32)
            
            for i, item in enumerate(val_items):
                d = max(1.0, float(dur_val[i]))
                wins = item.get("pred_relevant_windows", [])
                if wins:
                    st_sec, ed_sec = wins[0][:2]
                    fg_max_val[i] = wins[0][2] if len(wins[0]) > 2 else 1.0
                    spans_norm_val[i] = [max(0.0, min(1.0, st_sec / d)), max(0.0, min(1.0, ed_sec / d))]
                else:
                    spans_norm_val[i] = [0.0, 1.0]
                    fg_max_val[i] = 0.5
                    
            width_val = spans_norm_val[:, 1] - spans_norm_val[:, 0]
            mm_val = extract_multimodal_for_spans(
                vids_val, spans_norm_val, dur_val,
                aligned_val["q_proj_sent"][val_sub_indices],
                aligned_val["q_proj_act"][val_sub_indices],
                aligned_val["q_proj_obj"][val_sub_indices],
                train_ref, clip_cache, sf_cache
            )
            X_val = np.concatenate([
                s_det_val[:, None],
                mm_val[:, :5],
                mm_val[:, 5:7],
                fg_max_val[:, None],
                width_val[:, None],
                mm_val[:, 7:],
            ], axis=1)
            
            np.savez_compressed(
                m_dir / "val.npz",
                X=X_val,
                labels=lbl_val,
                qids=np.array(qids_val),
                vids=np.array(vids_val),
            )
            
            # --- 3. TEST ---
            if model == "flash":
                test_path = RESULTS_DIR / split / "flash/test/hl_test_submission.jsonl"
            elif model == "moment":
                test_path = RESULTS_DIR / split / "moment/test/moment_detr_gmr_test_submission.jsonl"
            else:
                test_path = RESULTS_DIR / split / "qd/test/qd_detr_gmr_test_submission.jsonl"
                
            test_items = [json.loads(l) for l in test_path.read_text().splitlines() if l.strip()]
            qids_te = [item["qid"] for item in test_items]
            vids_te = [item["vid"] for item in test_items]
            dur_te = aligned_test["durations"]
            lbl_te = aligned_test["labels"]
            parts_te = aligned_test["partitions"]
            
            if model == "flash" and "pred_exist_logit" in test_items[0]:
                s_det_te = np.array([1.0 / (1.0 + np.exp(-float(item["pred_exist_logit"]))) for item in test_items], dtype=np.float32)
            else:
                s_det_te = np.array([float(item.get("pred_exist_score", 0.5)) for item in test_items], dtype=np.float32)
            spans_norm_te = np.zeros((len(test_items), 2), dtype=np.float32)
            fg_max_te = np.zeros(len(test_items), dtype=np.float32)
            
            for i, item in enumerate(test_items):
                d = max(1.0, float(dur_te[i]))
                wins = item.get("pred_relevant_windows", [])
                if wins:
                    st_sec, ed_sec = wins[0][:2]
                    fg_max_te[i] = wins[0][2] if len(wins[0]) > 2 else 1.0
                    spans_norm_te[i] = [max(0.0, min(1.0, st_sec / d)), max(0.0, min(1.0, ed_sec / d))]
                else:
                    spans_norm_te[i] = [0.0, 1.0]
                    fg_max_te[i] = 0.5
                    
            width_te = spans_norm_te[:, 1] - spans_norm_te[:, 0]
            mm_te = extract_multimodal_for_spans(
                vids_te, spans_norm_te, dur_te,
                aligned_test["q_proj_sent"],
                aligned_test["q_proj_act"],
                aligned_test["q_proj_obj"],
                train_ref, clip_cache, sf_cache
            )
            X_te = np.concatenate([
                s_det_te[:, None],
                mm_te[:, :5],
                mm_te[:, 5:7],
                fg_max_te[:, None],
                width_te[:, None],
                mm_te[:, 7:],
            ], axis=1)
            
            np.savez_compressed(
                m_dir / "test.npz",
                X=X_te,
                labels=lbl_te,
                partitions=parts_te,
                qids=np.array(qids_te),
                vids=np.array(vids_te),
            )
            print(f"[{split}/{model}] Saved Train({len(qids_tr)}), Val({len(qids_val)}), Test({len(qids_te)}) target features.")

    print(f"\nAll target-specific features successfully extracted in {time.time()-t0:.2f}s!")

if __name__ == "__main__":
    process_all()
