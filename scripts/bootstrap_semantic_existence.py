#!/usr/bin/env python3
"""Video-cluster bootstrap CIs for four-quadrant test diagnostics."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def iou(a: list[float], b: list[float]) -> float:
    intersection = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return intersection / union if union > 0 else 0.0


def raw_r1(row: dict, prediction: dict) -> float:
    windows = prediction.get("pred_relevant_windows_pre_exist", prediction.get("pred_relevant_windows", []))
    if not windows:
        return 0.0
    top = max(windows, key=lambda w: w[2])
    return float(any(iou(top, gt) >= 0.5 for gt in row["relevant_windows"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path, required=True,
                        help="Seen-validation calibrated threshold and point diagnostics")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=3407)
    args = parser.parse_args()
    test = read_jsonl(args.release / "test.jsonl")
    pairs = read_jsonl(args.release / "matched_u_pairs.jsonl")
    predictions = {str(row["qid"]): row for row in read_jsonl(args.predictions)}
    diag = json.loads(args.diagnostics.read_text())
    threshold = float(diag["threshold"])
    if set(predictions) != {str(row["qid"]) for row in test}:
        raise ValueError("Prediction qids do not exactly match test qids")
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in test:
        pred = predictions[str(row["qid"])]
        item = {"part": row["partition"], "score": float(pred["pred_exist_score"]),
                "accepted": float(pred["pred_exist_score"]) >= threshold}
        if row["exist_label"]:
            item["raw_r1"] = raw_r1(row, pred)
            item["gated_r1"] = item["raw_r1"] * item["accepted"]
        by_video[row["video_id"]].append(item)
    pair_by_video: dict[str, list[float]] = defaultdict(list)
    row_by_qid = {str(row["qid"]): row for row in test}
    for pair in pairs:
        positive, negative = predictions[str(pair["positive_qid"])], predictions[str(pair["negative_qid"])]
        score = float(positive["pred_exist_score"])
        other = float(negative["pred_exist_score"])
        pair_by_video[row_by_qid[str(pair["positive_qid"])]["video_id"]].append(
            float(score > other) + 0.5 * float(score == other))
    videos = sorted(by_video)
    rng = random.Random(args.seed)
    metrics = ("seen_auroc", "unseen_auroc", "uplus_frr", "uminus_rr", "pair_accuracy",
               "uplus_raw_r1", "uplus_gated_r1")
    samples = {key: [] for key in metrics}
    for _ in range(args.repetitions):
        selected = [rng.choice(videos) for _ in videos]
        rows = [item for video in selected for item in by_video[video]]
        values = {}
        for key, positive_part, negative_part in (("seen_auroc", "S+", "S-"),
                                                   ("unseen_auroc", "U+", "U-")):
            subset = [row for row in rows if row["part"] in (positive_part, negative_part)]
            labels = [row["part"] == positive_part for row in subset]
            values[key] = roc_auc_score(labels, [row["score"] for row in subset])
        uplus = [row for row in rows if row["part"] == "U+"]
        uminus = [row for row in rows if row["part"] == "U-"]
        values["uplus_frr"] = np.mean([not row["accepted"] for row in uplus])
        values["uminus_rr"] = np.mean([not row["accepted"] for row in uminus])
        values["uplus_raw_r1"] = np.mean([row["raw_r1"] for row in uplus])
        values["uplus_gated_r1"] = np.mean([row["gated_r1"] for row in uplus])
        pair_values = [value for video in selected for value in pair_by_video[video]]
        values["pair_accuracy"] = np.mean(pair_values)
        for key in metrics:
            samples[key].append(float(values[key]))
    result = {"method": "percentile bootstrap resampling test videos with replacement",
              "seed": args.seed, "repetitions": args.repetitions, "test_videos": len(videos),
              "threshold": threshold, "metrics": {}}
    point = {
        "seen_auroc": diag["AUROC"]["seen"],
        "unseen_auroc": diag["AUROC"]["unseen"],
        "uplus_frr": diag["quadrants"]["U+"]["false_refusal"],
        "uminus_rr": diag["quadrants"]["U-"]["rejection_rate"],
        "pair_accuracy": diag["matched_pair_accuracy"],
        "uplus_raw_r1": diag["quadrants"]["U+"]["raw_R1_iou05"],
        "uplus_gated_r1": diag["quadrants"]["U+"]["gated_R1_iou05"],
    }
    for key in metrics:
        vals = sorted(samples[key])
        result["metrics"][key] = {
            "point": point[key],
            "ci95": [vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))]],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "test_videos": len(videos),
                      "metrics": {k: v["ci95"] for k, v in result["metrics"].items()}}, indent=2))


if __name__ == "__main__":
    main()
