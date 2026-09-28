"""Compare strict seen-only GMR runs with semantic-seen reference runs."""
import argparse
import json
from pathlib import Path

import numpy as np


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).open(encoding="utf-8")]


def video_cluster_ci(video_ids, differences, rng, repeats=10000):
    vids = sorted(set(video_ids))
    groups = {vid: [] for vid in vids}
    for index, vid in enumerate(video_ids):
        groups[vid].append(index)
    totals = np.array([np.asarray(differences)[groups[vid]].sum() for vid in vids])
    sizes = np.array([len(groups[vid]) for vid in vids])
    draws = rng.integers(0, len(vids), size=(repeats, len(vids)))
    bootstrap = totals[draws].sum(axis=1) / sizes[draws].sum(axis=1)
    return [float(x) for x in np.quantile(bootstrap, [.025, .975])]


def flatten(diagnostics):
    q = diagnostics["quadrants"]
    return {
        "seen_auroc": diagnostics["AUROC"]["seen"],
        "unseen_auroc": diagnostics["AUROC"]["unseen"],
        "matched_pair_accuracy": diagnostics["matched_pair_accuracy"],
        "S_plus_false_refusal": q["S+"]["false_refusal"],
        "S_minus_rejection": q["S-"]["rejection_rate"],
        "U_plus_false_refusal": q["U+"]["false_refusal"],
        "U_minus_rejection": q["U-"]["rejection_rate"],
        "U_plus_raw_R1_iou05": q["U+"]["raw_R1_iou05"],
        "U_plus_hard_gated_R1_iou05": q["U+"]["gated_R1_iou05"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-root", required=True)
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    strict_root = Path(args.strict_root)
    reference_root = Path(args.reference_root)
    release = Path(args.release)
    test = read_jsonl(release / "test.jsonl")
    pairs = read_jsonl(release / "matched_u_pairs.jsonl")
    rng = np.random.default_rng(3407)
    result = {
        "protocol": "Same seed 3407 and test set; strict train S+/S- (8,317 rows), reference train adds 2,679 held-out positives (10,996 rows). Both select and calibrate on val seen only.",
        "interpretation_limit": "The added held-out semantics and larger positive training set change together; deltas are descriptive, not a causal estimate of semantic novelty alone.",
        "models": {},
    }
    for model in ("moment", "qd", "flash"):
        strict_diag = json.loads((strict_root / model / "diagnostics.json").read_text())
        reference_diag = json.loads((reference_root / model / "diagnostics.json").read_text())
        strict = flatten(strict_diag)
        reference = flatten(reference_diag)
        name = {"moment": "moment_detr_gmr_test_submission.jsonl", "qd": "qd_detr_gmr_test_submission.jsonl", "flash": "hl_test_submission.jsonl"}[model]
        strict_predictions = {str(x["qid"]): x for x in read_jsonl(strict_root / model / "test" / name)}
        reference_predictions = {str(x["qid"]): x for x in read_jsonl(reference_root / model / "test" / name)}
        ci = {}
        for partition, metric in (("U+", "U_plus_false_refusal"), ("U-", "U_minus_rejection")):
            rows = [x for x in test if x["partition"] == partition]
            difference = [
                int(float(reference_predictions[str(x["qid"])]["pred_exist_score"]) < reference_diag["threshold"])
                - int(float(strict_predictions[str(x["qid"])]["pred_exist_score"]) < strict_diag["threshold"])
                for x in rows
            ]
            ci[metric] = video_cluster_ci([x["vid"] for x in rows], difference, rng)
        pair_difference = []
        for pair in pairs:
            pos, neg = str(pair["positive_qid"]), str(pair["negative_qid"])
            def rank(predictions):
                a = float(predictions[pos]["pred_exist_score"])
                b = float(predictions[neg]["pred_exist_score"])
                return 1.0 if a > b else 0.0 if a < b else 0.5
            pair_difference.append(rank(reference_predictions) - rank(strict_predictions))
        ci["matched_pair_accuracy"] = video_cluster_ci([x["video_id"] for x in pairs], pair_difference, rng)
        result["models"][model] = {
            "strict": strict,
            "semantic_seen_reference": reference,
            "reference_minus_strict": {k: reference[k] - strict[k] for k in strict},
            "reference_minus_strict_ci95_video_cluster": ci,
        }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
