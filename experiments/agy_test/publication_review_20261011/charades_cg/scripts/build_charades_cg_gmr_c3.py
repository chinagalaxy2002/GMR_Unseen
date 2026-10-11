#!/usr/bin/env python3
"""Build the source-faithful Charades-CG-GMR C3_CG extension."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import types
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/release/charades_cg_gmr_v1"
SOURCE = BASE / "source"
WORK = BASE / "work/c3_cg"
OUT = ROOT / "data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1"
CLIP_CODE = Path("/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video")
WEIGHTS = Path("/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt")
SEED = 3407
SOURCE_COMMIT = "2372337e9166b8e26b83ce936a8474c6ae127290"
SOURCES = (
    ("train.json", "official_train", "train_pool", "seen"),
    ("novel_composition.json", "novel_composition", "test", "unseen"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def expanded_rows() -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    removed: list[dict[str, Any]] = []
    for filename, subset, official_split, identity in SOURCES:
        data = json.loads((SOURCE / filename).read_text(encoding="utf-8"))
        for vid, payload in data.items():
            sentences = payload.get("sentences")
            timestamps = payload.get("timestamps")
            duration = payload.get("duration")
            count = max(len(sentences) if isinstance(sentences, list) else 0,
                        len(timestamps) if isinstance(timestamps, list) else 0)
            for i in range(count):
                qid = f"{filename}:{vid}:{i}"
                reason = None
                query = sentences[i] if isinstance(sentences, list) and i < len(sentences) else None
                window = timestamps[i] if isinstance(timestamps, list) and i < len(timestamps) else None
                try:
                    d = float(duration)
                except (TypeError, ValueError):
                    d = float("nan")
                if not isinstance(vid, str) or not vid:
                    reason = "missing_or_invalid_video_id"
                elif not isinstance(query, str) or not query.strip():
                    reason = "missing_or_empty_query"
                elif not math.isfinite(d) or d <= 0:
                    reason = "missing_or_invalid_duration"
                elif not isinstance(window, list) or len(window) != 2:
                    reason = "missing_or_invalid_window"
                else:
                    try:
                        start, end = map(float, window)
                    except (TypeError, ValueError):
                        start = end = float("nan")
                    if not math.isfinite(start) or not math.isfinite(end) or not (0 <= start < end <= d):
                        reason = "window_out_of_bounds_or_invalid"
                if reason:
                    removed.append({"source_qid": qid, "source_file": filename, "source_vid": vid,
                                    "sentence_index": i, "reason": reason, "query": query,
                                    "relevant_windows": [window] if window is not None else [], "duration": duration})
                    continue
                novels = payload.get("novels", [{}] * len(sentences))[i] if "novels" in payload else {}
                row = {
                    "qid": qid, "source_qid": qid, "vid": vid, "query": query,
                    "relevant_windows": [[float(window[0]), float(window[1])]], "duration": d,
                    "exist_label": 1, "official_subset": subset, "official_split": official_split,
                    "novels": novels if isinstance(novels, dict) else {},
                    "source_file": filename, "source_commit": SOURCE_COMMIT,
                }
                if identity == "seen":
                    row["partition"] = "S+"
                elif identity == "unseen":
                    row["partition"] = "U+"
                else:
                    row["partition"] = "NOVEL_WORD_EXCLUDED"
                    news = payload.get("news", [{}] * len(sentences))[i] if isinstance(sentences, list) and i < len(sentences) else {}
                    row["news"] = news if isinstance(news, dict) else {}
                groups[filename].append(row)
    return groups, removed


def video_assignment(groups: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, str], dict[str, Any]]:
    existing = json.loads((BASE / "video_splits.json").read_text(encoding="utf-8"))
    old = existing["video_splits"]
    assignment: dict[str, str] = {}
    for row in groups["train.json"]:
        vid = row["vid"]
        prior = old.get(vid, {}).get("video_split")
        if prior not in {"train", "val_seen"}:
            raise ValueError(f"No reusable seed-3407 train/val assignment for {vid}: {prior}")
        assignment[vid] = "train" if prior == "train" else "val"
    test_vids = {r["vid"] for filename, _, split, _ in SOURCES if split == "test" for r in groups[filename]}
    for vid in test_vids:
        assignment[vid] = "test"
    overlap = set(assignment) & {r["vid"] for r in groups["train.json"] if assignment.get(r["vid"]) == "test"}
    if overlap:
        raise ValueError(f"Official train and test source video overlap: {sorted(overlap)[:5]}")
    return assignment, {
        "seed": SEED,
        "train_validation_sampling": existing.get("train_validation_sampling"),
        "reused_train_validation_assignments": True,
        "official_test_policy": "all cleaned included official test videos map to test; query subset identities are retained",
        "video_counts": dict(Counter(assignment.values())),
    }


def encode_texts(texts: list[str]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    if not all(text.isascii() for text in texts):
        raise ValueError("Identity ftfy requires ASCII source queries")
    if not WEIGHTS.is_file():
        raise FileNotFoundError(WEIGHTS)
    sys.path.insert(0, str(CLIP_CODE / "clip"))
    # Every source sentence is ASCII, so identity ftfy is equivalent to OpenAI CLIP cleanup.
    ftfy_stub = types.ModuleType("ftfy")
    ftfy_stub.fix_text = lambda value: value
    sys.modules["ftfy"] = ftfy_stub
    from simple_tokenizer import SimpleTokenizer

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = torch.jit.load(str(WEIGHTS), map_location=device).eval()
    tokenizer = SimpleTokenizer()
    sot, eot = tokenizer.encoder["<|startoftext|>"], tokenizer.encoder["<|endoftext|>"]
    vectors: dict[str, np.ndarray] = {}
    with torch.inference_mode():
        for start in range(0, len(texts), 256):
            batch = texts[start:start + 256]
            tokens = torch.zeros((len(batch), 77), dtype=torch.long, device=device)
            for i, text in enumerate(batch):
                ids = [sot] + tokenizer.encode(text) + [eot]
                if len(ids) > 77:
                    raise ValueError(f"CLIP token limit exceeded; no truncation allowed: {text!r}")
                tokens[i, :len(ids)] = torch.tensor(ids, device=device)
            output = model.encode_text(tokens)
            output = output["pooler_output"] if isinstance(output, dict) else output
            output = F.normalize(output.float(), dim=-1).cpu().numpy().astype(np.float32)
            vectors.update(zip(batch, output))
    meta = {
        "encoder": "OpenAI CLIP ViT-B/32", "weights_path": str(WEIGHTS), "weights_sha256": sha256(WEIGHTS),
        "clip_code_path": str(CLIP_CODE), "clip_model_sha256": sha256(CLIP_CODE / "clip/model.py"),
        "tokenizer_sha256": sha256(CLIP_CODE / "clip/simple_tokenizer.py"), "torch": torch.__version__,
        "numpy": np.__version__, "device": device, "unique_text_count": len(vectors),
        "normalization": "L2 unit norm", "token_context": 77, "truncation": False,
        "unicode_handling": "identity ftfy; source queries verified ASCII",
    }
    return vectors, meta


def prepare_vectors(texts: list[str], reuse_release: Path | None) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Reuse exact prior vectors so extending test cannot perturb Train/Val rankings."""
    if reuse_release is None:
        return encode_texts(texts)
    generation = json.loads((reuse_release / "negative_generation.json").read_text(encoding="utf-8"))
    old_meta = generation["clip"]
    old_cache = ROOT / old_meta["cache_path"]
    if sha256(old_cache) != old_meta["cache_sha256"]:
        raise ValueError("Prior CLIP cache checksum mismatch")
    for key, path in (("weights_sha256", WEIGHTS), ("clip_model_sha256", CLIP_CODE / "clip/model.py"),
                      ("tokenizer_sha256", CLIP_CODE / "clip/simple_tokenizer.py")):
        if sha256(path) != old_meta[key]:
            raise ValueError(f"Prior encoder provenance mismatch: {key}")
    with np.load(old_cache, allow_pickle=False) as cache:
        prior = {str(t): v.copy() for t, v in zip(cache["texts"], cache["vectors"])}
    vectors = {t: prior[t] for t in texts if t in prior}
    missing = [t for t in texts if t not in vectors]
    meta = dict(old_meta)
    for key in ("cache_path", "cache_sha256", "cache_bytes"):
        meta.pop(key, None)
    if missing:
        extra, extra_meta = encode_texts(missing)
        for key in ("encoder", "weights_sha256", "clip_model_sha256", "tokenizer_sha256",
                    "normalization", "token_context", "truncation", "unicode_handling"):
            if extra_meta[key] != old_meta[key]:
                raise ValueError(f"New and reused encoder configuration differs: {key}")
        vectors.update(extra)
        meta["new_encoding_environment"] = {k: extra_meta[k] for k in ("torch", "numpy", "device")}
    meta.update({"unique_text_count": len(vectors), "reused_text_count": len(texts) - len(missing),
                 "newly_encoded_text_count": len(missing), "reused_cache_path": old_meta["cache_path"],
                 "reused_cache_sha256": old_meta["cache_sha256"]})
    return vectors, meta


def build_negatives(split: str, positives: list[dict[str, Any]], vecs: dict[str, np.ndarray], rng: random.Random,
                    audit: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_vid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    durations: dict[str, float] = {}
    for row in positives:
        by_vid[row["vid"]].append(row)
        durations[row["vid"]] = row["duration"]
    vids = sorted(by_vid)
    queries = sorted({r["query"] for r in positives})
    ref_rows = [r for vid in vids for r in by_vid[vid]]
    ref_matrix = np.stack([vecs[r["query"]] for r in ref_rows])
    query_matrix = np.stack([vecs[q] for q in queries])
    similarities = query_matrix @ ref_matrix.T
    video_column = {vid: i for i, vid in enumerate(vids)}
    query_row = {q: i for i, q in enumerate(queries)}
    video_scores = np.empty((len(queries), len(vids)), dtype=np.float32)
    cursor = 0
    for vid in vids:
        end = cursor + len(by_vid[vid])
        video_scores[:, video_column[vid]] = similarities[:, cursor:end].max(axis=1)
        cursor = end
    assigned_by_query: dict[str, set[str]] = defaultdict(set)
    negatives, pairs = [], []
    # Stable order independent of source JSON object insertion details.
    for source in sorted(positives, key=lambda r: r["source_qid"]):
        query, source_vid = source["query"], source["vid"]
        candidates = [v for v in vids if v != source_vid and all(r["query"] != query for r in by_vid[v])]
        ranked: list[tuple[float, str]] = []
        scores = video_scores[query_row[query]]
        for vid in candidates:
            ranked.append((float(scores[video_column[vid]]), vid))
        ranked.sort(key=lambda x: (x[0], x[1]))
        half_count = len(ranked) // 2
        low = [vid for _, vid in ranked[:half_count]]
        available = [v for v in low if v not in assigned_by_query[query]]
        if len(ranked) < 2 or not available:
            audit.append({"source_qid": source["source_qid"], "split": split, "status": "deficit",
                          "candidate_video_count": len(ranked), "lowest_half_count": half_count,
                          "available_after_duplicate_pair_guard": len(available),
                          "reason": "fewer_than_two_candidates" if len(ranked) < 2 else "no_unique_target_remaining"})
            continue
        target_vid = rng.choice(available)
        assigned_by_query[query].add(target_vid)
        rank = next(i + 1 for i, (_, v) in enumerate(ranked) if v == target_vid)
        pair_id = "c3cg-" + hashlib.sha256(source["source_qid"].encode()).hexdigest()[:16]
        neg = {
            "qid": f"{pair_id}-neg", "pair_id": pair_id, "vid": target_vid, "query": query,
            "relevant_windows": [], "duration": durations[target_vid], "exist_label": 0,
            "partition": "S-" if source["partition"] == "S+" else "U-",
            "official_subset": source["official_subset"], "novels": source["novels"],
            "source_qid": source["source_qid"], "source_vid": source_vid,
            "construction_method": "mout_in_domain_clip_reassignment",
            "sampling_source": "Moment of Untruth §3.3 In-Domain negatives; lowest-scoring half of same-split videos",
        }
        source["pair_id"] = pair_id
        negatives.append(neg)
        pairs.append({"pair_id": pair_id, "split": split, "positive_qid": source["qid"],
                      "negative_qid": neg["qid"], "source_qid": source["source_qid"],
                      "source_vid": source_vid, "negative_vid": target_vid,
                      "official_subset": source["official_subset"], "novels": source["novels"],
                      "partition": source["partition"], "negative_partition": neg["partition"]})
        digest = hashlib.sha256("\n".join(f"{score:.9f}\t{vid}" for score, vid in ranked).encode()).hexdigest()
        audit.append({"source_qid": source["source_qid"], "split": split, "status": "generated",
                      "target_vid": target_vid, "target_score": ranked[rank - 1][0], "target_rank_1_indexed": rank,
                      "candidate_video_count": len(ranked), "lowest_half_count": half_count,
                      "target_is_in_lowest_half": rank <= half_count,
                      "ranked_candidates_sha256": digest, "duplicate_text_targets_prevented": True})
    return negatives, pairs


def main() -> None:
    global OUT, WORK, SOURCES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-test-trivial", action="store_true", help="Include official Seen test queries")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--reuse-embeddings-from", type=Path, help="Prior release with verified CLIP cache")
    args = parser.parse_args()
    if args.include_test_trivial:
        SOURCES = SOURCES + (("test_trivial.json", "test_trivial", "test", "seen"),)
        OUT = OUT.with_name("charades_cg_gmr_v2")
        WORK = WORK.with_name("c3_cg_v2")
    OUT = (args.output_dir or OUT).resolve()
    WORK = (args.work_dir or WORK).resolve()
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f"Preserve existing release; choose a fresh --output-dir: {OUT}")
    if WORK.exists() and any(WORK.iterdir()):
        raise FileExistsError(f"Preserve existing construction evidence; choose a fresh --work-dir: {WORK}")
    groups, removed = expanded_rows()
    assignment, split_meta = video_assignment(groups)
    train = [r for r in groups["train.json"] if assignment[r["vid"]] == "train"]
    val = [r for r in groups["train.json"] if assignment[r["vid"]] == "val"]
    test = [r for filename, _, split, _ in SOURCES if split == "test" for r in groups[filename]]
    for r in train: r["video_split"] = "train"
    for r in val: r["video_split"] = "val"
    for r in test: r["video_split"] = "test"
    pools = {"train": train, "val_seen": val, "test": test}
    unique_texts = sorted({r["query"] for rows in pools.values() for r in rows})
    vecs, clip_meta = prepare_vectors(unique_texts, args.reuse_embeddings_from)
    WORK.mkdir(parents=True, exist_ok=True)
    cache = WORK / "clip_text_vectors.npz"
    np.savez_compressed(cache, texts=np.array(unique_texts), vectors=np.stack([vecs[t] for t in unique_texts]))
    clip_meta.update({"cache_path": str(cache.relative_to(ROOT)), "cache_sha256": sha256(cache), "cache_bytes": cache.stat().st_size})
    rng = random.Random(SEED)
    audits: list[dict[str, Any]] = []
    all_pairs: list[dict[str, Any]] = []
    negs: dict[str, list[dict[str, Any]]] = {}
    for split, rows in pools.items():
        negs[split], pairs = build_negatives(split, rows, vecs, rng, audits)
        all_pairs.extend(pairs)
    train_all = sorted(train + negs["train"], key=lambda r: (r["source_qid"], r["exist_label"]))
    val_all = sorted(val + negs["val_seen"], key=lambda r: (r["source_qid"], r["exist_label"]))
    test_all = sorted(test + negs["test"], key=lambda r: (r["source_qid"], r["exist_label"]))
    for rows in (train_all, val_all, test_all):
        for r in rows:
            r.setdefault("pair_id", None)
    write_jsonl(OUT / "removed_rows.jsonl", removed)
    write_json(OUT / "video_splits.json", {"seed": SEED, "assignment_method": split_meta,
                                              "videos": {v: {"split": s} for v, s in sorted(assignment.items())}})
    write_jsonl(OUT / "splits/C3_CG/train.jsonl", train_all)
    write_jsonl(OUT / "splits/C3_CG/val_seen.jsonl", val_all)
    write_jsonl(OUT / "splits/C3_CG/test.jsonl", test_all)
    write_jsonl(OUT / "splits/C3_CG/pairs.jsonl", all_pairs)
    (OUT / "splits/C3_CG/novel_word_excluded.jsonl").unlink(missing_ok=True)
    write_jsonl(WORK / "negative_sampling_audit.jsonl", audits)

    source_files = []
    for filename, *_ in SOURCES:
        path = SOURCE / filename
        source_files.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {"dataset": "Charades-CG-GMR", "extension": "C3_CG", "source_commit": SOURCE_COMMIT,
                "source_files": source_files,
                "construction_plan": "docs/research/charades_cg_gmr_agent_pipeline/PIPELINE_PLAN.md revision-4",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "included_subsets": [subset for _, subset, _, _ in SOURCES],
                "excluded_subsets": [s for s in ("test_trivial", "novel_word") if s not in {x[1] for x in SOURCES}],
                "seen_unseen_definition": "Official Train/Test-Trivial are Seen; Novel-Composition is Unseen; identities inherited from source, without semantic re-audit"}
    write_json(OUT / "source_manifest.json", manifest)
    generation = {"method": "Moment of Untruth §3.3 In-Domain negatives", "paper": "https://arxiv.org/html/2502.08544v2#S3.SS3",
                  "clip": clip_meta, "seed": SEED, "processing_order": "positive instances sorted by source_qid; split order train, val_seen, test",
                  "candidate_pool": "clean positives in the same split; test pool combines all included official test subsets and all their descriptions per video",
                  "score": "max cosine(CLIP(query), CLIP(each positive query of candidate video))",
                  "exclusions": ["source video", "any video containing an exactly identical query"],
                  "selection": "sort ascending by (score, video_id), retain floor(N/2), sample uniformly from available targets",
                  "duplicate_negative_guard": "for identical text within a split, assign distinct target videos where possible",
                  "insufficient_candidate_policy": "record deficit, do not use another negative mechanism",
                  "candidate_rank_audit_path": str((WORK / "negative_sampling_audit.jsonl").relative_to(ROOT)),
                  "candidate_rank_audit_sha256": sha256(WORK / "negative_sampling_audit.jsonl")}
    write_json(OUT / "negative_generation.json", generation)
    counts = {}
    for name, rows in (("train", train_all), ("val_seen", val_all), ("test", test_all)):
        c = Counter(r["partition"] for r in rows)
        counts[name] = {p: c.get(p, 0) for p in ("S+", "S-", "U+", "U-")}
        counts[name]["total"] = len(rows)
    positives_by_source = {n: len(groups[n]) for n, *_ in SOURCES}
    positive_split_counts = {"train": len(train), "val": len(val),
                             "test_seen": sum(r["partition"] == "S+" for r in test),
                             "test_unseen": sum(r["partition"] == "U+" for r in test)}
    deficits = Counter(a["split"] for a in audits if a["status"] == "deficit")
    statistics = {"positive_counts": positive_split_counts, "negative_counts": {"train": len(negs["train"]), "val": len(negs["val_seen"]), "test": len(negs["test"])},
                  "four_quadrant_counts_by_output": counts, "removed_rows": len(removed),
                  "removed_by_reason": dict(Counter(r["reason"] for r in removed)),
                  "clean_positive_rows_by_source": positives_by_source,
                  "sampling_deficits": {"train": deficits.get("train", 0), "val_seen": deficits.get("val_seen", 0), "test": deficits.get("test", 0), "total": sum(deficits.values())},
                  "unique_clean_queries_encoded": len(unique_texts), "pair_rows": len(all_pairs),
                  "video_counts": split_meta["video_counts"]}
    write_json(OUT / "statistics.json", statistics)
    readme = f"""# Charades-CG-GMR C3_CG extension\n\nRelease: `{OUT.relative_to(ROOT)}/`. Independent of A1–C2. Included official subsets: {', '.join(manifest['included_subsets'])}. Novel-Word remains excluded. Official Test-Trivial is the Seen test reference and Novel-Composition is Unseen; these are inherited source identities, without semantic re-audit. Unseen refers to the downstream composition split, not pretrained-model exposure.\n\nSource positives retain exact queries, videos, time windows and composition markers; invalid source rows are removed without clipping. Train/Val reuse the seed-3407 video assignments. Train, validation and test videos are disjoint; the two test query subsets may share videos.\n\nNegatives use Moment of Untruth §3.3 in-domain text reassignment: OpenAI CLIP ViT-B/32 text embeddings, max cosine against every positive description on each same-split candidate video, then uniform sampling among the lowest-scoring floor(50%) of eligible videos. Query text is unchanged; S/U follows the source query. All included test descriptions are combined per video for both Seen and Unseen queries. Negatives have `relevant_windows=[]` and are construction labels; they are neither agent text-audited nor confirmed absent by video inspection.\n\n| Output | S+ | S− | U+ | U− | Total |\n|---|---:|---:|---:|---:|---:|\n""" + "".join(f"| {s} | {v['S+']} | {v['S-']} | {v['U+']} | {v['U-']} | {v['total']} |\n" for s, v in counts.items()) + f"\nRemoved source rows within included subsets: {len(removed)}. Sampling deficits: {sum(deficits.values())}. See `statistics.json`, `negative_generation.json`, `removed_rows.jsonl`, and `splits/C3_CG/`.\n\nUse Seen validation only to freeze checkpoints, thresholds and hyperparameters. Report AUROC, actual Rej-F1, end-to-end G-mIoU@1 separately on Seen/Unseen and Gap = Seen − Unseen (percentage points, preserving negative gaps). Also report overall Rej-F1, rejection rate, S+/U+ false rejection rates, overall G-mIoU@1 and all class counts. Use video-cluster bootstrap 95% CIs, jointly resampling shared test videos across subsets; for baseline comparisons use paired intervals for Unseen Net Gain, Seen Change and Gap Reduction with the same split/backbone. Rej-F1 and G-mIoU gaps depend on class proportions. C3_CG alone is not a five-split macro result. Preserve predictions, calibration metadata and bootstrap artifacts as required by AGENTS.md. No model training or evaluation is included in this release.\n"
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"output": str(OUT), "counts": counts, "positive_counts": positive_split_counts,
                      "removed_rows": len(removed), "sampling_deficits": dict(deficits), "pairs": len(all_pairs),
                      "clip_device": clip_meta["device"], "embedding_cache": str(cache)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
