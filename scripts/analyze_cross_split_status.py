#!/usr/bin/env python3
"""Compare identical test queries that are unseen in one split and seen in another."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def best_r1(row: dict, prediction: dict) -> int | None:
    if not row["exist_label"]:
        return None
    windows = prediction.get("pred_relevant_windows_pre_exist", prediction.get("pred_relevant_windows", []))
    if not windows:
        return 0
    predicted = max(windows, key=lambda w: w[2])
    a, b = predicted[:2]
    for c, d in row["relevant_windows"]:
        intersection = max(0.0, min(b, d) - max(a, c))
        union = max(b, d) - min(a, c)
        if union > 0 and intersection / union >= 0.5:
            return 1
    return 0


def video_cluster_interval(group: list[dict], field: str, repetitions: int = 2000) -> list[float]:
    by_video = defaultdict(list)
    for row in group:
        by_video[row["video_id"]].append(float(row[field]))
    videos = sorted(by_video)
    rng = random.Random(3407)
    values = []
    for _ in range(repetitions):
        sampled = [by_video[rng.choice(videos)] for _ in videos]
        flat = [value for cluster in sampled for value in cluster]
        values.append(sum(flat) / len(flat))
    values.sort()
    return [values[int(0.025 * (repetitions - 1))], values[int(0.975 * (repetitions - 1))]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True,
                        help="JSON with splits [{id, release, optional predictions, optional seen_threshold}]")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    splits = config["splits"]
    if len({s["id"] for s in splits}) != len(splits):
        raise ValueError("Duplicate split IDs")
    rows_by_split = {}
    predictions = {}
    for split in splits:
        split_id = split["id"]
        rows_by_split[split_id] = {str(r["qid"]): r for r in read_jsonl(
            Path(split["release"]) / split.get("test_file", "test.jsonl"))}
        if "predictions" in split:
            predictions[split_id] = {str(r["qid"]): r for r in read_jsonl(Path(split["predictions"]))}
    output = []
    for source in splits:
        source_id = source["id"]
        for target in splits:
            target_id = target["id"]
            if target_id == source_id:
                continue
            for qid, unseen in rows_by_split[source_id].items():
                if unseen["semantic_status"] != "unseen":
                    continue
                seen = rows_by_split[target_id].get(qid)
                if seen is None or seen["semantic_status"] != "seen":
                    continue
                fingerprint = ("video_id", "query", "exist_label", "relevant_windows")
                if any(unseen[k] != seen[k] for k in fingerprint):
                    raise ValueError(f"Same qid changed source content: {qid}, {source_id}, {target_id}")
                record = {"qid": qid, "unseen_split": source_id, "seen_split": target_id,
                          "novelty_type": unseen["novelty_type"], "exist_label": unseen["exist_label"],
                          "video_id": unseen["video_id"], "query": unseen["query"]}
                if source_id in predictions and target_id in predictions:
                    up = predictions[source_id].get(qid)
                    sp = predictions[target_id].get(qid)
                    if up is None or sp is None:
                        raise ValueError(f"Missing prediction for cross-status qid {qid}")
                    us, ss = float(up["pred_exist_score"]), float(sp["pred_exist_score"])
                    record.update(unseen_exist_score=us, seen_exist_score=ss,
                                  seen_minus_unseen_score=ss-us,
                                  unseen_raw_r1=best_r1(unseen, up), seen_raw_r1=best_r1(seen, sp))
                    if "seen_threshold" in source and "seen_threshold" in target and unseen["exist_label"]:
                        record["unseen_hard_r1"] = int(us >= source["seen_threshold"]) * record["unseen_raw_r1"]
                        record["seen_hard_r1"] = int(ss >= target["seen_threshold"]) * record["seen_raw_r1"]
                output.append(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        if output:
            writer = csv.DictWriter(f, fieldnames=list(output[0]))
            writer.writeheader()
            writer.writerows(output)
    groups = defaultdict(list)
    for row in output:
        groups[(row["unseen_split"], row["seen_split"], row["novelty_type"], row["exist_label"])].append(row)
    summary = []
    for key, group in sorted(groups.items()):
        item = dict(zip(("unseen_split", "seen_split", "novelty_type", "exist_label"), key))
        item["n"] = len(group)
        item["videos"] = len({r["video_id"] for r in group})
        if "seen_minus_unseen_score" in group[0]:
            item["mean_seen_minus_unseen_score"] = sum(r["seen_minus_unseen_score"] for r in group) / len(group)
            item["score_delta_video_cluster_95ci"] = video_cluster_interval(group, "seen_minus_unseen_score")
            if key[3]:
                for metric in ("raw_r1", "hard_r1"):
                    if f"seen_{metric}" in group[0]:
                        delta_field = f"seen_minus_unseen_{metric}"
                        for row in group:
                            row[delta_field] = row[f"seen_{metric}"] - row[f"unseen_{metric}"]
                        item[f"mean_{delta_field}"] = sum(r[delta_field] for r in group) / len(group)
                        item[f"{metric}_delta_video_cluster_95ci"] = video_cluster_interval(group, delta_field)
        summary.append(item)
    summary_path = args.output.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cross_status_rows": len(output), "groups": len(summary),
                      "output": str(args.output), "summary": str(summary_path)}, indent=2))


if __name__ == "__main__":
    main()
