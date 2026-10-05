#!/usr/bin/env python3
"""
Clean Aligned Feature Extractor for Aligned Calibration Verifier.

Strict Standards:
1. True CLIP ViT-B/32 text projection: text embeddings are projected into the shared vision-language space.
2. Pure query text tokenization using SimpleTokenizer (zero reliance on dataset span metadata).
3. Predefined unlabelled train-video reference centering:
   score(q, v) = cos(q_proj, v) - cos(q_proj, v_train_ref)
4. Full parity & identity cache: bitwise identical embeddings for duplicate query texts.
5. Zero leakage assertion checks on all subsets.
"""
import os
import sys
import json
import time
import re
from pathlib import Path
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parent
FEATURES_DIR = BASE_DIR / "aligned_features"
HQ_DIR = REPO_ROOT / "experiments/agy_test/cache/hq"
RELEASE_DIR = REPO_ROOT / "data/release/semantic_existence_v2"
VIDEO_CLIP_DIR = Path(os.environ.get("AC_VIDEO_CLIP_DIR", "/home/guoxiangyu/paper/新建文件夹/charades/vid_clip"))
VIDEO_SF_DIR = Path("/home/guoxiangyu/paper/新建文件夹/charades/vid_slowfast")
CLIP_CODE = Path(os.environ.get("AC_CLIP_CODE", "/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video"))
WEIGHTS = Path(os.environ.get("AC_CLIP_WEIGHTS", "/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt"))

SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
SUBSETS = ["train", "val", "test"]

def norm(x):
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12)

def cosine(a, b):
    return (norm(a) * norm(b)).sum(-1)

# Dynamic module loading for CLIP without torchvision dependency
def load_clip_modules():
    import importlib.util
    def module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    tm = module("clip_tokenizer", CLIP_CODE / "clip/simple_tokenizer.py")
    cm = module("clip_model", CLIP_CODE / "clip/model.py")
    tokenizer = tm.SimpleTokenizer()

    def tokenize(texts):
        output = torch.zeros((len(texts), 77), dtype=torch.long)
        for i, text in enumerate(texts):
            ids = [tokenizer.encoder["<|startoftext|>"]] + tokenizer.encode(text) + [tokenizer.encoder["<|endoftext|>"]]
            if len(ids) > 77:
                ids = ids[:76] + [tokenizer.encoder["<|endoftext|>"]]
            output[i, :len(ids)] = torch.tensor(ids)
        return output

    state = torch.jit.load(str(WEIGHTS), map_location="cpu").state_dict()
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = cm.build_model(state).to(dev)
    model.eval()
    return tokenizer, tokenize, model, dev

# Comprehensive action and object patterns for Charades vocabulary
ACTION_TERMS = [
    "run", "runs", "running", "ran",
    "sit", "sits", "sitting", "sat",
    "take", "takes", "taking", "took", "taken",
    "put", "puts", "putting",
    "hold", "holds", "holding", "held",
    "throw", "throws", "throwing", "threw", "thrown",
    "stand", "stands", "standing", "stood",
    "wake", "wakes", "waking", "woke", "woken", "awaken", "awake",
    "drink", "drinks", "drinking", "drank", "drunk",
    "eat", "eats", "eating", "ate", "eaten",
    "close", "closes", "closing", "closed", "shut",
    "open", "opens", "opening", "opened",
    "walk", "walks", "walking", "walked",
    "pour", "pours", "pouring", "poured",
    "turn", "turns", "turning", "turned",
    "play", "plays", "playing", "played",
    "watch", "watches", "watching", "watched",
    "wash", "washes", "washing", "washed",
    "clean", "cleans", "cleaning", "cleaned",
    "cook", "cooks", "cooking", "cooked",
    "read", "reads", "reading",
    "laugh", "laughs", "laughing", "laughed",
    "smile", "smiles", "smiling", "smiled",
    "sneeze", "sneezes", "sneezing", "sneezed",
    "cough", "coughs", "coughing", "coughed",
    "cry", "cries", "crying", "cried",
    "grasp", "grasps", "grasping", "grasped",
    "grab", "grabs", "grabbing", "grabbed",
    "look", "looks", "looking", "looked",
    "lie", "lies", "lying", "lay", "lain",
    "talk", "talks", "talking", "talked",
    "work", "works", "working", "worked",
    "leave", "leaves", "leaving", "left",
]

def extract_action_and_object_phrases(query):
    """
    Rule-based extraction based STRICTLY on query string alone.
    Zero dependency on dataset labels or semantic_graph annotations.
    """
    q_lower = query.lower().strip()
    
    # 1. Action phrase
    action_phrase = None
    for act in sorted(ACTION_TERMS, key=len, reverse=True):
        pattern = r"\b" + re.escape(act) + r"\b"
        m = re.search(pattern, q_lower)
        if m:
            action_phrase = m.group(0)
            break
            
    # 2. Object phrase (heuristic noun chunk after action, or last noun)
    # E.g., "person drinking a glass of water" -> "glass of water"
    tokens = re.findall(r"\w+", q_lower)
    object_phrase = None
    if action_phrase and action_phrase in tokens:
        idx = tokens.index(action_phrase)
        rem = tokens[idx + 1:]
        # Remove common stop words
        filtered = [w for w in rem if w not in {"a", "an", "the", "some", "of", "to", "in", "on", "at", "from", "with", "into", "their", "his", "her", "person", "they"}]
        if filtered:
            object_phrase = " ".join(filtered)
            
    if not action_phrase:
        action_phrase = query
    if not object_phrase:
        object_phrase = query

    return action_phrase, object_phrase

def encode_all_texts(all_texts, tokenize, model, dev, batch_size=128):
    """Encodes a list of unique texts into L2-normalized CLIP projected EOT vectors."""
    unique_texts = sorted(set(all_texts))
    lookup = {}
    print(f"Encoding {len(unique_texts)} unique text strings with CLIP ViT-B/32 text_projection...")
    t0 = time.time()
    with torch.no_grad():
        for start in range(0, len(unique_texts), batch_size):
            batch = unique_texts[start:start + batch_size]
            tokens = tokenize(batch).to(dev)
            hidden = model.encode_text(tokens)["last_hidden_state"].float()
            last = tokens.argmax(-1)
            ii = torch.arange(len(batch), device=dev)
            projected = hidden[ii, last] @ model.text_projection.float()
            vecs = norm(projected.cpu().numpy())
            for i, txt in enumerate(batch):
                lookup[txt] = vecs[i].astype(np.float32)
    print(f"Finished encoding in {time.time() - t0:.2f}s.")
    return lookup

def process_split(split, tokenizer, tokenize, model, dev):
    print(f"\n{'='*70}\nProcessing Split: {split}\n{'='*70}")
    out_split_dir = FEATURES_DIR / split
    out_split_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Gather all queries and extract phrases
    all_texts_for_split = set()
    split_meta = {}
    
    for subset in SUBSETS:
        jsonl_path = RELEASE_DIR / split / f"{subset}.jsonl"
        with open(jsonl_path, "r", encoding="utf-8") as f:
            items = [json.loads(line) for line in f]
        split_meta[subset] = items
        for it in items:
            q = it["query"].strip()
            act_p, obj_p = extract_action_and_object_phrases(q)
            all_texts_for_split.add(q)
            all_texts_for_split.add(act_p)
            all_texts_for_split.add(obj_p)
            
    # 2. Encode all text phrases into true projected EOT
    text_lookup = encode_all_texts(list(all_texts_for_split), tokenize, model, dev)
    
    # 3. Compute unique train-video reference center
    print(f"[{split}] Computing unlabelled unique train-video reference...")
    train_hq = np.load(HQ_DIR / split / "train.npz")
    train_vids = list(train_hq["vids"])
    unique_train_vids = sorted(set(train_vids))
    print(f"[{split}] Found {len(unique_train_vids)} unique training videos.")
    
    train_vid_vecs = []
    video_feature_cache = {}
    
    for vid in unique_train_vids:
        c_p = VIDEO_CLIP_DIR / f"{vid}.npz"
        feat = np.load(c_p)["features"].astype(np.float32)
        # Store in cache
        video_feature_cache[vid] = feat
        # Global video representation (L2-normalized mean frame)
        g_vec = norm(feat.mean(axis=0))
        train_vid_vecs.append(g_vec)
        
    train_reference = norm(np.mean(train_vid_vecs, axis=0)).astype(np.float32)
    print(f"[{split}] Train reference vector computed (norm={np.linalg.norm(train_reference):.4f}).")
    
    # 4. Process each subset (train, val, test)
    for subset in SUBSETS:
        out_file = out_split_dir / f"{subset}.npz"
        print(f"\n[{split}/{subset}] Processing aligned features...")
        t0 = time.time()
        
        hq_path = HQ_DIR / split / f"{subset}.npz"
        hq = np.load(hq_path)
        qids = list(hq["qids"])
        vids = list(hq["vids"])
        hs = hq["hs"] # (N, 10, 256)
        fg = hq["fg"] # (N, 10)
        spans = hq["spans"] # (N, 10, 2) in [center, width]
        orig_logits = hq["orig_logits"].astype(np.float32)
        partitions = hq["partitions"]
        durations = hq["durations"].astype(np.float32)
        labels = hq["labels"].astype(np.int8)
        
        meta_items = {item["qid"]: item for item in split_meta[subset]}
        N = len(qids)
        
        # Pre-cache any videos not already in memory
        subset_unique_vids = set(vids)
        for vid in subset_unique_vids:
            if vid not in video_feature_cache:
                c_p = VIDEO_CLIP_DIR / f"{vid}.npz"
                video_feature_cache[vid] = np.load(c_p)["features"].astype(np.float32)
                
        # Arrays to build
        q_proj_sent_arr = np.zeros((N, 512), dtype=np.float32)
        q_proj_act_arr = np.zeros((N, 512), dtype=np.float32)
        q_proj_obj_arr = np.zeros((N, 512), dtype=np.float32)
        
        v_clip_cand_arr = np.zeros((N, 512), dtype=np.float32)
        v_clip_glob_arr = np.zeros((N, 512), dtype=np.float32)
        
        sim_cand_sent_arr = np.zeros((N,), dtype=np.float32)
        sim_glob_sent_arr = np.zeros((N,), dtype=np.float32)
        sim_cand_act_arr = np.zeros((N,), dtype=np.float32)
        sim_cand_obj_arr = np.zeros((N,), dtype=np.float32)
        
        raw_cos_cand_sent_arr = np.zeros((N,), dtype=np.float32)
        raw_cos_glob_sent_arr = np.zeros((N,), dtype=np.float32)
        
        fg_max_arr = np.zeros((N,), dtype=np.float32)
        h_pool_arr = np.zeros((N, 512), dtype=np.float32)
        best_spans_arr = np.zeros((N, 2), dtype=np.float32)
        
        construction_types = []
        source_qids = []
        queries = []
        action_phrases = []
        object_phrases = []
        
        for i in range(N):
            qid = qids[i]
            vid = vids[i]
            meta = meta_items[qid]
            query = meta["query"].strip()
            act_p, obj_p = extract_action_and_object_phrases(query)
            
            queries.append(query)
            action_phrases.append(act_p)
            object_phrases.append(obj_p)
            construction_types.append(meta.get("construction_type", "original_positive"))
            source_qids.append(meta.get("source_qid", ""))
            
            # Projected text vectors
            q_sent = text_lookup[query]
            q_act = text_lookup[act_p]
            q_obj = text_lookup[obj_p]
            
            q_proj_sent_arr[i] = q_sent
            q_proj_act_arr[i] = q_act
            q_proj_obj_arr[i] = q_obj
            
            # Detector states
            best_k = int(np.argmax(fg[i]))
            fg_max_arr[i] = fg[i, best_k]
            h_pool_arr[i, :256] = hs[i].max(axis=0)
            h_pool_arr[i, 256:] = hs[i].mean(axis=0)
            
            # Window slicing: [center, width] -> [center - width/2, center + width/2]
            c, w = spans[i, best_k]
            st_norm = float(np.clip(c - w / 2.0, 0.0, 1.0))
            ed_norm = float(np.clip(c + w / 2.0, 0.0, 1.0))
            best_spans_arr[i] = [st_norm, ed_norm]
            
            # Video frames
            v_feat = video_feature_cache[vid]
            T = len(v_feat)
            st_f = max(0, min(T - 1, int(np.floor(st_norm * T))))
            ed_f = min(T, max(st_f + 1, int(np.ceil(ed_norm * T))))
            
            cand_f = norm(v_feat[st_f:ed_f].mean(axis=0)).astype(np.float32)
            glob_f = norm(v_feat.mean(axis=0)).astype(np.float32)
            
            v_clip_cand_arr[i] = cand_f
            v_clip_glob_arr[i] = glob_f
            
            # Raw cosines
            cos_cand_s = float(np.dot(q_sent, cand_f))
            cos_glob_s = float(np.dot(q_sent, glob_f))
            cos_cand_a = float(np.dot(q_act, cand_f))
            cos_cand_o = float(np.dot(q_obj, cand_f))
            
            raw_cos_cand_sent_arr[i] = cos_cand_s
            raw_cos_glob_sent_arr[i] = cos_glob_s
            
            # Reference centered (debiased) similarities:
            # Score(q, v) = cos(q, v) - cos(q, ref)
            ref_s = float(np.dot(q_sent, train_reference))
            ref_a = float(np.dot(q_act, train_reference))
            ref_o = float(np.dot(q_obj, train_reference))
            
            sim_cand_sent_arr[i] = cos_cand_s - ref_s
            sim_glob_sent_arr[i] = cos_glob_s - ref_s
            sim_cand_act_arr[i] = cos_cand_a - ref_a
            sim_cand_obj_arr[i] = cos_cand_o - ref_o
            
        # Zero-leakage check on phrases
        diff_act_obj = np.linalg.norm(q_proj_act_arr - q_proj_obj_arr, axis=1)
        if len(np.unique(labels)) == 2:
            from sklearn.metrics import roc_auc_score
            dist_auc = roc_auc_score(labels, diff_act_obj)
            print(f"[{split}/{subset}] Leakage audit: ||q_act - q_obj|| AUROC = {dist_auc:.4f} (must NOT be 1.0)")
            assert dist_auc < 0.85, f"LEAKAGE DETECTED in {split}/{subset}!"
            
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
            q_proj_sent=q_proj_sent_arr,
            q_proj_act=q_proj_act_arr,
            q_proj_obj=q_proj_obj_arr,
            v_clip_cand=v_clip_cand_arr,
            v_clip_glob=v_clip_glob_arr,
            sim_cand_sent=sim_cand_sent_arr,
            sim_glob_sent=sim_glob_sent_arr,
            sim_cand_act=sim_cand_act_arr,
            sim_cand_obj=sim_cand_obj_arr,
            raw_cos_cand_sent=raw_cos_cand_sent_arr,
            raw_cos_glob_sent=raw_cos_glob_sent_arr,
            train_reference=train_reference,
            construction_types=np.array(construction_types),
            source_qids=np.array(source_qids),
            queries=np.array(queries),
            action_phrases=np.array(action_phrases),
            object_phrases=np.array(object_phrases),
        )
        print(f"[{split}/{subset}] Done in {time.time() - t0:.2f}s.")

def main():
    print("=" * 80)
    print("Extracting Clean Aligned Features with ViT-B/32 Projection & Train Reference Centering")
    print("=" * 80)
    tokenizer, tokenize, model, dev = load_clip_modules()
    for split in SPLITS:
        process_split(split, tokenizer, tokenize, model, dev)
    print("\nAll 5 splits successfully extracted with proper CLIP alignment and reference centering!")

if __name__ == "__main__":
    main()
