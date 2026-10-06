#!/usr/bin/env python3
"""
Pre-extract clean multimodal feature matrices for Multi-Scale Counterfactual Verifier (MCV).
Combines:
- 3 Detector logits (FlashVTG, Moment-DETR, QD-DETR)
- 3 Visual signals (CLIP global, candidate, peak frame)
- 2 Kinetic signals (SlowFast velocity contrast, window displacement)
- 2 Detector spatial signals (fg_max, span width)
- Same-video counterfactual pair mining for training sets.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "cache_features"
MULTI_SPLIT_ROOT = REPO_ROOT / "results/semantic_existence/multi_split_v2"
ALIGNED_FEAT_DIR = REPO_ROOT / "experiments/agy_test/aligned_calibration_verifier/aligned_features"
SLOWFAST_DIR = REPO_ROOT / "features/charades_semantic_existence/slowfast"
CLIP_DIR = REPO_ROOT / "features/charades_semantic_existence/clip"

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

def extract_kinetic_and_peak_features(vids, spans, q_projs, u_refs):
    """
    Extracts:
    1. m_contrast: candidate frame-difference velocity minus global velocity
    2. m_disp: SlowFast displacement between start and end of span
    3. s_cp: CLIP peak frame similarity with query
    """
    m_contrast_l, m_disp_l, s_cp_l = [], [], []
    
    # Cache loaded video features to avoid repeated disk reads
    sf_cache = {}
    clip_cache = {}
    
    for i, vid in enumerate(vids):
        # 1. SlowFast
        if vid not in sf_cache:
            sf_file = SLOWFAST_DIR / f"{vid}.npz"
            if sf_file.exists():
                sf = np.load(sf_file)["features"].astype(np.float32)
                T = len(sf)
                if T >= 2:
                    diff = np.diff(sf, axis=0)
                    vel = np.linalg.norm(diff, axis=-1)
                else:
                    vel = np.zeros(1, dtype=np.float32)
                sf_cache[vid] = (sf, vel, T)
            else:
                sf_cache[vid] = (None, None, 0)
                
        sf, vel, T_sf = sf_cache[vid]
        if sf is not None and T_sf >= 2:
            s_idx = max(0, min(T_sf - 2, int(spans[i, 0] * (T_sf - 1))))
            e_idx = max(s_idx + 1, min(T_sf - 1, int(spans[i, 1] * (T_sf - 1)) + 1))
            m_cand = float(np.mean(vel[s_idx:e_idx]))
            m_glob = float(np.mean(vel))
            m_contrast_l.append(m_cand - m_glob)
            
            s_f = max(0, min(T_sf - 1, int(spans[i, 0] * T_sf)))
            e_f = max(0, min(T_sf - 1, int(spans[i, 1] * T_sf)))
            m_disp = float(np.linalg.norm(sf[e_f] - sf[s_f]))
            m_disp_l.append(m_disp)
        else:
            m_contrast_l.append(0.0)
            m_disp_l.append(0.0)
            
        # 2. CLIP Peak
        if vid not in clip_cache:
            clip_file = CLIP_DIR / f"{vid}.npz"
            if clip_file.exists():
                v_clip = np.load(clip_file)["features"].astype(np.float32)
                v_clip_norm = v_clip / (np.linalg.norm(v_clip, axis=-1, keepdims=True) + 1e-8)
                clip_cache[vid] = v_clip_norm
            else:
                clip_cache[vid] = None
                
        v_clip_norm = clip_cache[vid]
        if v_clip_norm is not None:
            sims = np.dot(v_clip_norm, q_projs[i]) - np.dot(u_refs, q_projs[i])
            s_cp_l.append(float(np.max(sims)))
        else:
            s_cp_l.append(0.0)
            
    return np.array(m_contrast_l, dtype=np.float32), np.array(m_disp_l, dtype=np.float32), np.array(s_cp_l, dtype=np.float32)

def process_split(split: str):
    print(f"\n==================== PROCESSING SPLIT: {split} ====================")
    t0 = time.time()
    out_split_dir = OUT_DIR / split
    out_split_dir.mkdir(parents=True, exist_ok=True)
    
    # ----------------- 1. TRAIN -----------------
    print(f"[{split}] Loading Train...")
    tr_d = np.load(ALIGNED_FEAT_DIR / split / "train.npz")
    qids_tr = [str(q) for q in tr_d["qids"]]
    vids_tr = [str(v) for v in tr_d["vids"]]
    lbls_tr = tr_d["labels"]
    spans_tr = tr_d["best_spans"]
    q_proj_tr = tr_d["q_proj_sent"]
    ref_tr = tr_d["train_reference"]
    
    fl_tr = np.load(REPO_ROOT / f"experiments/agy_test/cache/features/{split}/flash/train.npz")["original_exist_logits"]
    mo_tr_raw = np.load(REPO_ROOT / f"experiments/agy_test/cache/features/{split}/moment/train.npz")["original_exist_logits"]
    qd_tr_raw = np.load(REPO_ROOT / f"experiments/agy_test/cache/features/{split}/qd/train.npz")["original_exist_logits"]
    # Convert training logits to probabilities to unify scale with validation and test pred_exist_score
    mo_tr = 1.0 / (1.0 + np.exp(-mo_tr_raw))
    qd_tr = 1.0 / (1.0 + np.exp(-qd_tr_raw))
    
    cg_tr = tr_d["sim_glob_sent"]
    cc_tr = tr_d["sim_cand_sent"]
    fg_tr = tr_d["fg_max"]
    width_tr = spans_tr[:, 1] - spans_tr[:, 0]
    
    m_cont_tr, m_disp_tr, cp_tr = extract_kinetic_and_peak_features(vids_tr, spans_tr, q_proj_tr, ref_tr)
    
    # Mine same-video counterfactual pairs for train
    pos_idx = np.where(lbls_tr == 1)[0]
    neg_idx = np.where(lbls_tr == 0)[0]
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
    print(f"[{split}] Train: {len(qids_tr)} samples, {len(same_vid_pairs)} same-video counterfactual pairs.")
    
    # Feature matrix: 10 dimensions (scale-unified)
    X_tr = np.stack([fl_tr, mo_tr, qd_tr, cg_tr, cc_tr, cp_tr, m_cont_tr, m_disp_tr, fg_tr, width_tr], axis=1)
    
    np.savez_compressed(
        out_split_dir / "train.npz",
        X=X_tr,
        labels=lbls_tr,
        qids=np.array(qids_tr),
        vids=np.array(vids_tr),
        same_vid_pairs=same_vid_pairs,
    )
    
    # ----------------- 2. VAL -----------------
    print(f"[{split}] Loading Val...")
    val_d = np.load(ALIGNED_FEAT_DIR / split / "val.npz")
    qids_val_all = [str(q) for q in val_d["qids"]]
    parts_val_all = val_d["partitions"]
    lbls_val_all = val_d["labels"]
    vids_val_all = [str(v) for v in val_d["vids"]]
    spans_val_all = val_d["best_spans"]
    q_proj_val_all = val_d["q_proj_sent"]
    is_s_val = (parts_val_all == "S+") | (parts_val_all == "S-")
    
    fl_val_file = list((MULTI_SPLIT_ROOT / split / "flash").glob("*/hl_val_submission.jsonl"))[0]
    with open(fl_val_file) as f:
        p_fl_val = {p["qid"]: float(p.get("pred_exist_logit", p.get("pred_exist_score", 0.0))) for p in map(json.loads, f)}
    with open(MULTI_SPLIT_ROOT / split / "moment/best_charades_semantic_existence_val_preds.jsonl") as f:
        p_mo_val = {p["qid"]: float(p.get("pred_exist_score", 0.0)) for p in map(json.loads, f)}
    with open(MULTI_SPLIT_ROOT / split / "qd/best_charades_semantic_existence_val_preds.jsonl") as f:
        p_qd_val = {p["qid"]: float(p.get("pred_exist_logit", p.get("pred_exist_score", 0.0))) for p in map(json.loads, f)}

    valid_val_idx = [i for i, q in enumerate(qids_val_all) if is_s_val[i] and q in p_fl_val and q in p_mo_val and q in p_qd_val]
    qids_val = [qids_val_all[i] for i in valid_val_idx]
    vids_val = [vids_val_all[i] for i in valid_val_idx]
    lbls_val = lbls_val_all[valid_val_idx]
    spans_val = spans_val_all[valid_val_idx]
    q_proj_val = q_proj_val_all[valid_val_idx]
    
    fl_val = np.array([p_fl_val[q] for q in qids_val], dtype=np.float32)
    mo_val = np.array([p_mo_val[q] for q in qids_val], dtype=np.float32)
    qd_val = np.array([p_qd_val[q] for q in qids_val], dtype=np.float32)
    cg_val = val_d["sim_glob_sent"][valid_val_idx]
    cc_val = val_d["sim_cand_sent"][valid_val_idx]
    fg_val = val_d["fg_max"][valid_val_idx]
    width_val = spans_val[:, 1] - spans_val[:, 0]
    
    m_cont_val, m_disp_val, cp_val = extract_kinetic_and_peak_features(vids_val, spans_val, q_proj_val, ref_tr)
    X_val = np.stack([fl_val, mo_val, qd_val, cg_val, cc_val, cp_val, m_cont_val, m_disp_val, fg_val, width_val], axis=1)
    
    np.savez_compressed(
        out_split_dir / "val.npz",
        X=X_val,
        labels=lbls_val,
        qids=np.array(qids_val),
        vids=np.array(vids_val),
    )
    
    # ----------------- 3. TEST -----------------
    print(f"[{split}] Loading Test...")
    te_d = np.load(ALIGNED_FEAT_DIR / split / "test.npz")
    qids_te = [str(q) for q in te_d["qids"]]
    parts_te = te_d["partitions"]
    lbls_te = te_d["labels"]
    vids_te = [str(v) for v in te_d["vids"]]
    spans_te = te_d["best_spans"]
    q_proj_te = te_d["q_proj_sent"]
    
    with open(MULTI_SPLIT_ROOT / split / "flash/test/hl_test_submission.jsonl") as f:
        p_fl_te = {p["qid"]: float(p.get("pred_exist_logit", p.get("pred_exist_score", 0.0))) for p in map(json.loads, f)}
    with open(MULTI_SPLIT_ROOT / split / "moment/test/moment_detr_gmr_test_submission.jsonl") as f:
        p_mo_te = {p["qid"]: float(p.get("pred_exist_score", 0.0)) for p in map(json.loads, f)}
    with open(MULTI_SPLIT_ROOT / split / "qd/test/qd_detr_gmr_test_submission.jsonl") as f:
        p_qd_te = {p["qid"]: float(p.get("pred_exist_logit", p.get("pred_exist_score", 0.0))) for p in map(json.loads, f)}

    fl_te = np.array([p_fl_te[q] for q in qids_te], dtype=np.float32)
    mo_te = np.array([p_mo_te[q] for q in qids_te], dtype=np.float32)
    qd_te = np.array([p_qd_te[q] for q in qids_te], dtype=np.float32)
    cg_te = te_d["sim_glob_sent"]
    cc_te = te_d["sim_cand_sent"]
    fg_te = te_d["fg_max"]
    width_te = spans_te[:, 1] - spans_te[:, 0]
    
    m_cont_te, m_disp_te, cp_te = extract_kinetic_and_peak_features(vids_te, spans_te, q_proj_te, ref_tr)
    X_te = np.stack([fl_te, mo_te, qd_te, cg_te, cc_te, cp_te, m_cont_te, m_disp_te, fg_te, width_te], axis=1)
    
    np.savez_compressed(
        out_split_dir / "test.npz",
        X=X_te,
        labels=lbls_te,
        partitions=parts_te,
        qids=np.array(qids_te),
        vids=np.array(vids_te),
        base_scores=te_d["orig_logits"],
    )
    print(f"[{split}] Finished in {time.time()-t0:.2f}s.")

def main():
    t_start = time.time()
    for sp in SPLITS:
        process_split(sp)
    print(f"\nAll 5 splits pre-extracted successfully in {time.time()-t_start:.2f}s!")

if __name__ == "__main__":
    main()
