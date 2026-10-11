#!/usr/bin/env python3
"""Run the requested mechanical validation for the C3_CG local release."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/release/charades_cg_gmr_v1/source"
OUT = ROOT / "data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def source_index(include_test_trivial: bool = False) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    source_rows: dict[str, dict[str, Any]] = {}
    valid_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    invalid: dict[str, str] = {}
    sources = [("train.json", "official_train", "S+"), ("novel_composition.json", "novel_composition", "U+")]
    if include_test_trivial:
        sources.append(("test_trivial.json", "test_trivial", "S+"))
    for filename, subset, identity in sources:
        data = read_json(SOURCE / filename)
        for vid, payload in data.items():
            sentences = payload.get("sentences", [])
            timestamps = payload.get("timestamps", [])
            duration = payload.get("duration")
            for i in range(max(len(sentences), len(timestamps))):
                qid = f"{filename}:{vid}:{i}"
                query = sentences[i] if i < len(sentences) else None
                window = timestamps[i] if i < len(timestamps) else None
                reason = None
                try: d = float(duration)
                except (TypeError, ValueError): d = float("nan")
                try:
                    a, b = map(float, window) if isinstance(window, list) and len(window) == 2 else (float("nan"), float("nan"))
                except (TypeError, ValueError): a = b = float("nan")
                if not isinstance(query, str) or not query.strip(): reason = "missing_or_empty_query"
                elif not math.isfinite(d) or d <= 0: reason = "missing_or_invalid_duration"
                elif not math.isfinite(a) or not math.isfinite(b) or not (0 <= a < b <= d): reason = "window_out_of_bounds_or_invalid"
                if reason:
                    invalid[qid] = reason
                    continue
                novels = payload.get("novels", [{}] * len(sentences))[i] if filename == "novel_composition.json" else {}
                row = {"source_qid": qid, "vid": vid, "query": query, "duration": d,
                       "relevant_windows": [[a, b]], "official_subset": subset, "partition": identity,
                       "novels": novels if isinstance(novels, dict) else {}}
                source_rows[qid] = row
                valid_by_file[filename].append(row)
    return source_rows, valid_by_file, invalid


def main() -> None:
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--compare-release", type=Path, help="Verify Train/Val bytes and original test positives unchanged")
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    manifest = read_json(OUT / "source_manifest.json")
    source_names = {Path(item["path"]).name for item in manifest["source_files"]}
    include_test_trivial = "test_trivial.json" in source_names
    expected_sources = {"train.json", "novel_composition.json"}
    if include_test_trivial:
        expected_sources.add("test_trivial.json")
    require(source_names == expected_sources, "unexpected source subset")
    for item in manifest["source_files"]:
        require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], "source checksum mismatch")
    source_rows, valid_by_file, invalid = source_index(include_test_trivial)
    removed = read_jsonl(OUT / "removed_rows.jsonl")
    removed_map = {r["source_qid"]: r["reason"] for r in removed}
    require(len(removed_map) == len(removed), "removed_rows contains duplicate source_qid")
    require(removed_map == invalid, "removed_rows do not exactly match mechanically invalid source rows")
    split_map_data = read_json(OUT / "video_splits.json")
    video_splits = {v: x["split"] for v, x in split_map_data["videos"].items()}
    raw_existing_splits = read_json(ROOT / "data/release/charades_cg_gmr_v1/video_splits.json")["video_splits"]
    for row in valid_by_file["train.json"]:
        prior = raw_existing_splits[row["vid"]]["video_split"]
        require(video_splits[row["vid"]] == ("val" if prior == "val_seen" else "train"), f"Train/Val reassignment mismatch for {row['vid']}")
    main_test_vids = {r["vid"] for filename, rows in valid_by_file.items() if filename != "train.json" for r in rows}
    require(all(video_splits[v] == "test" for v in main_test_vids), "some official main-test video is not assigned to test")

    paths = {"train": OUT / "splits/C3_CG/train.jsonl", "val_seen": OUT / "splits/C3_CG/val_seen.jsonl",
             "test": OUT / "splits/C3_CG/test.jsonl"}
    data = {s: read_jsonl(p) for s, p in paths.items()}
    pairs = read_jsonl(OUT / "splits/C3_CG/pairs.jsonl")
    pair_map = {p["pair_id"]: p for p in pairs}
    require(len(pair_map) == len(pairs), "pairs.jsonl has duplicate pair_id")
    positives: dict[str, list[dict[str, Any]]] = defaultdict(list)
    negatives: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str, str]] = set()
    seen_qids: set[str] = set()
    split_videos: dict[str, set[str]] = defaultdict(set)
    for split, rows in data.items():
        expected_video_split = {"train": "train", "val_seen": "val", "test": "test"}[split]
        for row in rows:
            require(row["qid"] not in seen_qids, f"duplicate global qid: {row['qid']}")
            seen_qids.add(row["qid"])
            split_videos[split].add(row["vid"])
            if split != "test":
                require(row["partition"] in ("S+", "S-"), f"Unseen row outside test: {row['qid']}")
            require(row["exist_label"] in (0, 1), f"invalid exist_label: {row.get('qid')}")
            require(video_splits.get(row["vid"]) == expected_video_split, f"video split leak/mismatch: {row.get('qid')}")
            require(isinstance(row["query"], str) and bool(row["query"].strip()), f"empty query: {row.get('qid')}")
            require(math.isfinite(float(row["duration"])) and float(row["duration"]) > 0, f"invalid duration: {row.get('qid')}")
            if row["exist_label"] == 1:
                require(len(row["relevant_windows"]) == 1, f"positive window count mismatch: {row['qid']}")
                a, b = row["relevant_windows"][0]
                require(0 <= a < b <= row["duration"], f"positive window invalid: {row['qid']}")
                src = source_rows.get(row["source_qid"])
                require(src is not None, f"positive missing source mapping: {row['qid']}")
                require(row["vid"] == src["vid"] and row["query"] == src["query"] and row["relevant_windows"] == src["relevant_windows"], f"positive source mismatch: {row['qid']}")
                require(row["partition"] == src["partition"], f"positive partition mismatch: {row['qid']}")
                require(row["duration"] == src["duration"] and row["official_subset"] == src["official_subset"] and row["novels"] == src["novels"], f"positive source metadata mismatch: {row['qid']}")
                require(row["qid"] == row["source_qid"] and row["source_commit"] == manifest["source_commit"], f"positive source provenance mismatch: {row['qid']}")
                positives[split].append(row)
            else:
                require(row["relevant_windows"] == [], f"negative has nonempty windows: {row['qid']}")
                require(row.get("text_audited") is not True and row.get("video_reviewed") is not True, f"negative falsely marked reviewed: {row['qid']}")
                src = source_rows.get(row["source_qid"])
                require(src is not None, f"negative missing source mapping: {row['qid']}")
                require(row["query"] == src["query"] and row["vid"] != src["vid"], f"negative query/source mismatch: {row['qid']}")
                require(row["partition"] == ("S-" if src["partition"] == "S+" else "U-"), f"negative S/U identity mismatch: {row['qid']}")
                require(row["official_subset"] == src["official_subset"] and row["novels"] == src["novels"], f"negative source identity mismatch: {row['qid']}")
                # Positives may occur later in the file; target duration is checked against source positives below.
                negatives[split].append(row)
                key = (split, row["vid"], row["query"])
                require(key not in seen_pairs, f"duplicate video-query negative: {key}")
                seen_pairs.add(key)
        # Recheck target duration after the full positive pool is available.
    for split, rows in data.items():
        pos_by_vid = {r["vid"]: r for r in positives[split]}
        for row in negatives[split]:
            require(row["vid"] in pos_by_vid, f"negative target video lacks a positive description in same split: {row['qid']}")
            require(row["duration"] == pos_by_vid[row["vid"]]["duration"], f"negative target duration mismatch: {row['qid']}")
    for left, right in (("train", "val_seen"), ("train", "test"), ("val_seen", "test")):
        require(not (split_videos[left] & split_videos[right]), f"video overlap: {left}/{right}")
    pos_by_qid = {r["qid"]: r for rows in positives.values() for r in rows}
    row_split = {r["qid"]: s for s, rows in data.items() for r in rows}
    require(set(pos_by_qid) == set(source_rows), "clean original positives are missing or duplicated")
    neg_by_qid = {r["qid"]: r for rows in negatives.values() for r in rows}
    require(len(pairs) == len(neg_by_qid), "pair table and generated negative counts differ")
    require({p["negative_qid"] for p in pairs} == set(neg_by_qid), "negative pair coverage mismatch")
    paired_sources: set[str] = set()
    for pair in pairs:
        pos, neg = pos_by_qid.get(pair["positive_qid"]), neg_by_qid.get(pair["negative_qid"])
        require(pos is not None and neg is not None, f"pair references missing row: {pair['pair_id']}")
        require(pos["pair_id"] == neg["pair_id"] == pair["pair_id"], f"pair_id mismatch: {pair['pair_id']}")
        require(pair["source_qid"] == pos["source_qid"] == neg["source_qid"], "pair source mismatch")
        require(pair["source_qid"] not in paired_sources, "source has multiple negative pairs")
        paired_sources.add(pair["source_qid"])
        require(pair["source_vid"] == pos["vid"] == neg["source_vid"] and pair["negative_vid"] == neg["vid"], "pair video mismatch")
        require(pos["query"] == neg["query"] and pair["partition"] == pos["partition"] and pair["negative_partition"] == neg["partition"], "pair query/partition mismatch")
        require(row_split[pos["qid"]] == row_split[neg["qid"]] == pair["split"], "pair split mismatch")
    excluded = ("novel_word.json:",) if include_test_trivial else ("novel_word.json:", "test_trivial.json:")
    require(not any(r["source_qid"].startswith(excluded) for rows in data.values() for r in rows), "excluded subset source row entered the extension")

    # Verify the selected candidate is in the exact lowest floor(N/2), recomputing every
    # distinct source query's video scores from the recorded normalized CLIP vectors.
    generation = read_json(OUT / "negative_generation.json")
    cache_path = ROOT / generation["clip"]["cache_path"]
    require(hashlib.sha256(cache_path.read_bytes()).hexdigest() == generation["clip"]["cache_sha256"], "CLIP vector cache hash mismatch")
    cache = np.load(cache_path, allow_pickle=False)
    vector_map = {str(t): v for t, v in zip(cache["texts"], cache["vectors"])}
    audit_path = ROOT / generation["candidate_rank_audit_path"]
    if "candidate_rank_audit_sha256" in generation:
        require(hashlib.sha256(audit_path.read_bytes()).hexdigest() == generation["candidate_rank_audit_sha256"], "sampling audit checksum mismatch")
    audit = read_jsonl(audit_path)
    audit_by_source = {x["source_qid"]: x for x in audit}
    require(len(audit_by_source) == len(audit), "sampling audit has duplicate source ids")
    require(set(audit_by_source) == set(source_rows), "sampling audit source coverage mismatch")
    require(set(cache["texts"].tolist()) == {r["query"] for r in source_rows.values()}, "CLIP cache query coverage mismatch")
    require(np.isfinite(cache["vectors"]).all() and np.allclose(np.linalg.norm(cache["vectors"], axis=1), 1, atol=1e-5), "CLIP vectors not finite/unit normalized")
    negative_by_source = {r["source_qid"]: r for r in neg_by_qid.values()}
    deficits = 0
    ranked_checks = 0
    for split, pos_rows in positives.items():
        by_vid: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in pos_rows: by_vid[row["vid"]].append(row)
        vids = sorted(by_vid)
        ref_rows = [r for vid in vids for r in by_vid[vid]]
        refmat = np.stack([vector_map[r["query"]] for r in ref_rows])
        queries = sorted({r["query"] for r in pos_rows})
        query_matrix = np.stack([vector_map[q] for q in queries])
        # Match the builder's batched float32 matrix multiplication so near ties
        # have the same numeric ordering before the video-ID tie break.
        similarities = query_matrix @ refmat.T
        query_row = {q: i for i, q in enumerate(queries)}
        vid_col = {v: i for i, v in enumerate(vids)}
        offsets, cursor = {}, 0
        for v in vids:
            offsets[v] = (cursor, cursor + len(by_vid[v])); cursor += len(by_vid[v])
        video_scores = np.empty((len(queries), len(vids)), dtype=np.float32)
        for v, (a, b) in offsets.items():
            video_scores[:, vid_col[v]] = similarities[:, a:b].max(axis=1)
        for source in sorted(pos_rows, key=lambda x: x["source_qid"]):
            record = audit_by_source[source["source_qid"]]
            require(record["split"] == split, "sampling audit split mismatch")
            if record["status"] == "deficit":
                require(source["source_qid"] not in negative_by_source and source["pair_id"] is None, "deficit has generated pair")
                deficits += 1
                continue
            require(record["status"] == "generated", "unresolved sampling status")
            require(negative_by_source[source["source_qid"]]["vid"] == record["target_vid"], "sampling audit and released target disagree")
            vscore = {v: float(video_scores[query_row[source["query"]], vid_col[v]]) for v in vids}
            candidates = [v for v in vids if v != source["vid"] and all(r["query"] != source["query"] for r in by_vid[v])]
            ranked = sorted(((vscore[v], v) for v in candidates), key=lambda x: (x[0], x[1]))
            half = len(ranked) // 2
            target = record.get("target_vid")
            rank = next((i + 1 for i, (_, v) in enumerate(ranked) if v == target), None)
            require(len(ranked) == record["candidate_video_count"] and half == record["lowest_half_count"], f"candidate pool mismatch for {source['source_qid']}")
            require(rank is not None and rank <= half, f"selected target outside lowest half for {source['source_qid']}")
            require(rank == record["target_rank_1_indexed"], f"selected target rank mismatch for {source['source_qid']}")
            require(abs(ranked[rank - 1][0] - record["target_score"]) <= 1e-6, f"selected target score mismatch for {source['source_qid']}")
            ranked_checks += 1
    require(len(audit) == sum(len(rows) for rows in positives.values()), "sampling audit does not cover every positive source instance")
    stats = read_json(OUT / "statistics.json")
    require(stats["removed_rows"] == len(removed), "statistics removal count mismatch")
    quadrants = {}
    for split, rows in data.items():
        counts = Counter(r["partition"] for r in rows)
        quadrants[split] = {p: counts.get(p, 0) for p in ("S+", "S-", "U+", "U-")}
        quadrants[split]["total"] = len(rows)
        require(stats["four_quadrant_counts_by_output"][split] == quadrants[split], "statistics quadrant mismatch")
    if include_test_trivial:
        require(all(quadrants["test"][p] > 0 for p in ("S+", "S-", "U+", "U-")), "test lacks a quadrant")
    require(stats["sampling_deficits"]["total"] == deficits and stats["pair_rows"] == len(pairs), "statistics deficit/pair mismatch")
    preservation = {}
    if args.compare_release:
        for name in ("train.jsonl", "val_seen.jsonl"):
            prior = args.compare_release / "splits/C3_CG" / name
            require(prior.read_bytes() == (OUT / "splits/C3_CG" / name).read_bytes(), f"prior {name} changed")
            preservation[name] = "byte-identical"
        old_test = read_jsonl(args.compare_release / "splits/C3_CG/test.jsonl")
        old_positives = {r["qid"]: r for r in old_test if r["exist_label"] == 1}
        require(all(pos_by_qid.get(qid) == row for qid, row in old_positives.items()), "prior test positive changed")
        preservation["prior_test_positives_unchanged"] = len(old_positives)
    summary = {"status": "PASS", "source_clean_counts": {f: len(rows) for f, rows in valid_by_file.items()},
               "removed_rows": len(removed), "positive_counts_by_split": {s: len(rows) for s, rows in positives.items()},
               "negative_counts_by_split": {s: len(rows) for s, rows in negatives.items()},
               "pairs": len(pairs), "sampling_deficits": deficits, "lowest_half_rank_recomputed": ranked_checks,
               "four_quadrant_counts_by_output": quadrants, "prior_release_preservation": preservation,
               "video_counts": {s: len(v) for s, v in split_videos.items()},
               "test_shared_seen_unseen_videos": len({r["vid"] for r in positives["test"] if r["partition"] == "S+"} & {r["vid"] for r in positives["test"] if r["partition"] == "U+"}),
               "checks": ["format", "source correspondence", "video split assignment", "counts", "duplicate negative pairs",
                          "time windows", "labels and S/U identity", "official source scope; Novel-Word absent", "global qid uniqueness", "complete positive and pair coverage", "train/val/test video disjointness",
                          "CLIP lowest-half selection"]}
    write_path = OUT / "validation_report.json"
    write_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
