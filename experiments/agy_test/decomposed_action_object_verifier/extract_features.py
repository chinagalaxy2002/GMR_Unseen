#!/usr/bin/env python3
"""
Feature extractor for Decomposed Action-Object Verifier (DAO-Verifier).
Extracts aligned decomposed multimodal representations across 5 splits.
Zero edits to original repo code.
"""
import os
import sys
import json
import re
import time
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
FEATURES_DIR = Path(__file__).resolve().parent / "features"
HQ_DIR = REPO_ROOT / "experiments/agy_test/cache/hq"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
CLIP_DIR = Path("/home/guoxiangyu/paper/新建文件夹/charades/vid_clip")
SF_DIR = Path("/home/guoxiangyu/paper/新建文件夹/charades/vid_slowfast")

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
SUBSETS = ["train", "val", "test"]

def extract_spans(query):
    return [(m.start(), m.end(), m.group()) for m in re.finditer(r'\w+|[^\w\s]', query)]

def get_token_vectors(query, feat, act_span, obj_span):
    spans = extract_spans(query)
    L = len(feat)
    if len(spans) + 2 == L:
        act_toks = [i + 1 for i, (s, e, _) in enumerate(spans) if act_span and not (e <= act_span[0] or s >= act_span[1])]
        obj_toks = [i + 1 for i, (s, e, _) in enumerate(spans) if obj_span and not (e <= obj_span[0] or s >= obj_span[1])]
    else:
        q_len = len(query)
        act_toks, obj_toks = [], []
        for i in range(1, L - 1):
            tok_center_char = (i - 0.5) / (L - 2) * q_len
            if act_span and act_span[0] <= tok_center_char <= act_span[1]:
                act_toks.append(i)
            if obj_span and obj_span[0] <= tok_center_char <= obj_span[1]:
                obj_toks.append(i)
        if act_span and not act_toks:
            act_center = (act_span[0] + act_span[1]) / 2.0
            act_toks = [max(1, min(L - 2, int(round((act_center / q_len) * (L - 2) + 0.5))))]
        if obj_span and not obj_toks:
            obj_center = (obj_span[0] + obj_span[1]) / 2.0
            obj_toks = [max(1, min(L - 2, int(round((obj_center / q_len) * (L - 2) + 0.5))))]
            
    sent_vec = feat[1:-1].mean(axis=0) if L > 2 else feat.mean(axis=0)
    act_vec = feat[act_toks].mean(axis=0) if act_toks else sent_vec
    obj_vec = feat[obj_toks].mean(axis=0) if obj_toks else sent_vec
    return act_vec.astype(np.float32), obj_vec.astype(np.float32), sent_vec.astype(np.float32)

def process_split_subset(split, subset):
    out_dir = FEATURES_DIR / split
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{subset}.npz"
    if out_file.exists():
        print(f"[{split}/{subset}] Already extracted at {out_file}, skipping.")
        return

    print(f"[{split}/{subset}] Extracting decomposed features...")
    t0 = time.time()

    # Load HQ data (slot states, proposals, logits)
    hq_path = HQ_DIR / split / f"{subset}.npz"
    hq = np.load(hq_path)
    qids = list(hq["qids"])
    vids = list(hq["vids"])
    hs = hq["hs"] # (N, 10, 256)
    fg = hq["fg"] # (N, 10)
    spans = hq["spans"] # (N, 10, 2)
    orig_logits = hq["orig_logits"].astype(np.float32)
    partitions = hq["partitions"]
    durations = hq["durations"].astype(np.float32)
    labels = hq["labels"].astype(np.int8)

    # Load release JSONL for annotations
    jsonl_path = RELEASE_DIR / split / f"{subset}.jsonl"
    with open(jsonl_path, "r", encoding="utf-8") as f:
        meta_items = {item["qid"]: item for item in (json.loads(line) for line in f)}

    # Cache unique videos in memory
    unique_vids = set(vids)
    print(f"[{split}/{subset}] Caching {len(unique_vids)} unique videos...")
    vid_cache = {}
    for vid in unique_vids:
        c_p = CLIP_DIR / f"{vid}.npz"
        s_p = SF_DIR / f"{vid}.npz"
        c_feat = np.load(c_p)["features"].astype(np.float32)
        s_feat = np.load(s_p)["features"].astype(np.float32)
        min_l = min(len(c_feat), len(s_feat))
        c_feat = c_feat[:min_l]
        s_feat = s_feat[:min_l]
        vid_cache[vid] = (c_feat, s_feat)

    N = len(qids)
    text_dir = REPO_ROOT / f"features/semantic_existence_v2/{split}/clip_text"

    q_act_arr = np.zeros((N, 512), dtype=np.float32)
    q_obj_arr = np.zeros((N, 512), dtype=np.float32)
    q_sent_arr = np.zeros((N, 512), dtype=np.float32)
    v_sf_cand_arr = np.zeros((N, 2304), dtype=np.float32)
    v_sf_start_arr = np.zeros((N, 2304), dtype=np.float32)
    v_sf_end_arr = np.zeros((N, 2304), dtype=np.float32)
    v_sf_glob_arr = np.zeros((N, 2304), dtype=np.float32)
    v_clip_cand_arr = np.zeros((N, 512), dtype=np.float32)
    v_clip_glob_arr = np.zeros((N, 512), dtype=np.float32)
    fg_max_arr = np.zeros((N,), dtype=np.float32)
    best_spans_arr = np.zeros((N, 2), dtype=np.float32)
    h_pool_arr = np.zeros((N, 512), dtype=np.float32)
    
    construction_types = []
    source_qids = []
    actions = []
    objects = []

    for i in range(N):
        qid = qids[i]
        vid = vids[i]
        meta = meta_items[qid]
        query = meta["query"]
        sg = meta.get("semantic_graph", {})
        
        construction_types.append(meta.get("construction_type", "original_positive"))
        source_qids.append(meta.get("source_qid", ""))
        actions.append(sg.get("action", ""))
        objects.append(sg.get("object", "") or "")

        # Text features
        t_path = text_dir / f"qid{qid}.npz"
        t_feat = np.load(t_path)["last_hidden_state"].astype(np.float32)
        q_act, q_obj, q_sent = get_token_vectors(query, t_feat, sg.get("action_span"), sg.get("object_span"))
        q_act_arr[i] = q_act
        q_obj_arr[i] = q_obj
        q_sent_arr[i] = q_sent

        # Best detector slot
        best_k = int(np.argmax(fg[i]))
        fg_max_arr[i] = fg[i, best_k]
        best_spans_arr[i] = spans[i, best_k]
        
        # Dual-pooled decoder hidden states: [p_max, p_mean]
        h_pool_arr[i, :256] = hs[i].max(axis=0)
        h_pool_arr[i, 256:] = hs[i].mean(axis=0)

        # Video window features
        c_feat, s_feat = vid_cache[vid]
        T = len(s_feat)
        s0, s1 = best_spans_arr[i]
        st = max(0, min(T - 1, int(np.floor(s0 * T))))
        ed = min(T, max(st + 1, int(np.ceil(s1 * T))))
        
        v_sf_cand_arr[i] = s_feat[st:ed].mean(axis=0)
        if ed - st >= 2:
            mid = (st + ed) // 2
            v_sf_start_arr[i] = s_feat[st:mid].mean(axis=0)
            v_sf_end_arr[i] = s_feat[mid:ed].mean(axis=0)
        else:
            v_sf_start_arr[i] = v_sf_cand_arr[i]
            v_sf_end_arr[i] = v_sf_cand_arr[i]
            
        v_sf_glob_arr[i] = s_feat.mean(axis=0)
        v_clip_cand_arr[i] = c_feat[st:ed].mean(axis=0)
        v_clip_glob_arr[i] = c_feat.mean(axis=0)

    print(f"[{split}/{subset}] Saving {N} items to {out_file}...")
    np.savez_compressed(
        out_file,
        qids=np.array(qids),
        vids=np.array(vids),
        partitions=np.array(partitions),
        labels=labels,
        orig_logits=orig_logits,
        durations=durations,
        fg_max=fg_max_arr,
        best_spans=best_spans_arr,
        h_pool=h_pool_arr,
        q_act=q_act_arr,
        q_obj=q_obj_arr,
        q_sent=q_sent_arr,
        v_sf_cand=v_sf_cand_arr,
        v_sf_start=v_sf_start_arr,
        v_sf_end=v_sf_end_arr,
        v_sf_glob=v_sf_glob_arr,
        v_clip_cand=v_clip_cand_arr,
        v_clip_glob=v_clip_glob_arr,
        construction_types=np.array(construction_types),
        source_qids=np.array(source_qids),
        actions=np.array(actions),
        objects=np.array(objects),
    )
    print(f"[{split}/{subset}] Done in {time.time()-t0:.2f}s.")

def main():
    for split in SPLITS:
        for subset in SUBSETS:
            process_split_subset(split, subset)
    print("All 5 splits and subsets extracted successfully!")

if __name__ == "__main__":
    main()
