"""Decompose U+ localization loss into raw grounding and hard refusal effects."""
import argparse
import json
from pathlib import Path

import numpy as np


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).open(encoding="utf-8")]


def top1_iou(row, prediction, key):
    windows = prediction.get(key, [])
    if not windows:
        return 0.0
    best = max(windows, key=lambda x: x[2])
    values = []
    for gt in row["relevant_windows"]:
        intersection = max(0.0, min(best[1], gt[1]) - max(best[0], gt[0]))
        union = max(best[1], gt[1]) - min(best[0], gt[0])
        values.append(intersection / union if union > 0 else 0.0)
    return max(values)


def cluster_ci(rows, difference, rng, repeats=10000):
    # Resample videos to retain dependence between queries from the same video.
    vids = sorted({r["vid"] for r in rows})
    groups = {vid: [] for vid in vids}
    for index, row in enumerate(rows):
        groups[row["vid"]].append(index)
    totals = np.array([difference[groups[vid]].sum() for vid in vids], dtype=float)
    sizes = np.array([len(groups[vid]) for vid in vids], dtype=float)
    draws = rng.integers(0, len(vids), size=(repeats, len(vids)))
    means = totals[draws].sum(axis=1) / sizes[draws].sum(axis=1)
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def summarize(rows, plain_predictions, gmr_predictions, threshold, rng):
    plain = np.array([
        top1_iou(r, plain_predictions[str(r["qid"])], "pred_relevant_windows") >= 0.5
        for r in rows
    ], dtype=float)
    raw = np.array([
        top1_iou(r, gmr_predictions[str(r["qid"])], "pred_relevant_windows_pre_exist") >= 0.5
        for r in rows
    ], dtype=float)
    accepted = np.array([
        float(gmr_predictions[str(r["qid"])]["pred_exist_score"]) >= threshold
        for r in rows
    ], dtype=float)
    gated = raw * accepted
    raw_loss = plain - raw
    refusal_loss = raw - gated
    return {
        "n": len(rows),
        "videos": len({r["vid"] for r in rows}),
        "plain_R1_iou05": float(plain.mean()),
        "gmr_raw_R1_iou05": float(raw.mean()),
        "gmr_hard_gated_R1_iou05": float(gated.mean()),
        "plain_minus_gmr_raw": float(raw_loss.mean()),
        "plain_minus_gmr_raw_ci95_video_cluster": cluster_ci(rows, raw_loss, rng),
        "gmr_raw_minus_hard_gated": float(refusal_loss.mean()),
        "gmr_raw_minus_hard_gated_ci95_video_cluster": cluster_ci(rows, refusal_loss, rng),
        "gmr_false_refusal_rate": float(1.0 - accepted.mean()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--gmr-root", required=True)
    parser.add_argument("--localization-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    release = Path(args.release)
    gmr_root = Path(args.gmr_root)
    loc_root = Path(args.localization_root)
    rows = read_jsonl(release / "test.jsonl")
    positive = [r for r in rows if r["partition"] in ("S+", "U+")]
    pair_ids = {str(p["positive_qid"]) for p in read_jsonl(release / "matched_u_pairs.jsonl")}
    paths = {
        "moment": ("moment_detr_gmr_test_submission.jsonl", "moment_detr_gmr_test_submission.jsonl"),
        "qd": ("qd_detr_gmr_test_submission.jsonl", "qd_detr_gmr_test_submission.jsonl"),
        "flash": ("hl_test_submission.jsonl", "hl_test_submission.jsonl"),
    }
    rng = np.random.default_rng(3407)
    result = {
        "protocol": "Plain trained on S+; GMR trained on S+/S-; both seed 3407. GMR hard gate uses seen-validation threshold. Effects are descriptive, not causal isolation of the existence head.",
        "bootstrap": "95% percentile interval, 10,000 video-cluster resamples",
        "models": {},
    }
    for model, (plain_name, gmr_name) in paths.items():
        plain = {str(x["qid"]): x for x in read_jsonl(loc_root / model / "test" / plain_name)}
        gmr = {str(x["qid"]): x for x in read_jsonl(gmr_root / model / "test" / gmr_name)}
        expected = {str(r["qid"]) for r in positive}
        if not expected.issubset(plain) or not expected.issubset(gmr):
            raise ValueError(f"Prediction coverage mismatch for {model}")
        threshold = float(json.loads((gmr_root / model / "diagnostics.json").read_text())["threshold"])
        subsets = {
            "S+": [r for r in positive if r["partition"] == "S+"],
            "U+": [r for r in positive if r["partition"] == "U+"],
            "matched_U+": [r for r in positive if str(r["qid"]) in pair_ids],
        }
        result["models"][model] = {
            "seen_validation_threshold": threshold,
            **{name: summarize(subset, plain, gmr, threshold, rng) for name, subset in subsets.items()},
        }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
