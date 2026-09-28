"""Paired bootstrap intervals and sign tests for matched-U existence ranking."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


def read(path):
    return [json.loads(line) for line in Path(path).open(encoding="utf-8")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", required=True)
    parser.add_argument("--prediction", action="append", nargs=2, metavar=("MODEL", "PATH"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    pairs = read(args.pairs)
    rng = np.random.default_rng(3407)
    result = {"n_pairs": len(pairs), "interval": "95% paired bootstrap percentile, 20000 resamples", "models": {}}
    for model, path in args.prediction:
        predictions = {str(row["qid"]): float(row["pred_exist_score"]) for row in read(path)}
        scores = np.array([
            1.0 if predictions[str(p["positive_qid"])] > predictions[str(p["negative_qid"])]
            else 0.0 if predictions[str(p["positive_qid"])] < predictions[str(p["negative_qid"])]
            else 0.5
            for p in pairs
        ])
        bootstrap = scores[rng.integers(0, len(scores), size=(20000, len(scores)))].mean(axis=1)
        wins, ties, losses = int(sum(scores == 1)), int(sum(scores == .5)), int(sum(scores == 0))
        result["models"][model] = {
            "wins": wins, "ties": ties, "losses": losses,
            "pair_accuracy": float(scores.mean()),
            "bootstrap_ci95": [float(v) for v in np.quantile(bootstrap, [.025, .975])],
            "sign_test_p_two_sided_excluding_ties": float(binomtest(wins, wins + losses, .5).pvalue),
        }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
