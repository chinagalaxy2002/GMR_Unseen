"""Recompute the released text-only diagnostic and assess matched-U uncertainty."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).open(encoding="utf-8")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    release = Path(args.release)
    train = read_jsonl(release / "train.jsonl")
    test = read_jsonl(release / "test.jsonl")
    pairs = read_jsonl(release / "matched_u_pairs.jsonl")

    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=3, max_features=50000)
    x_train = vectorizer.fit_transform(r["query"] for r in train)
    model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=0)
    model.fit(x_train, [r["exist_label"] for r in train])
    scores = model.predict_proba(vectorizer.transform(r["query"] for r in test))[:, 1]
    score_by_qid = {str(r["qid"]): float(s) for r, s in zip(test, scores)}
    unseen = [i for i, r in enumerate(test) if r["semantic_status"] == "unseen"]
    unseen_auc = float(roc_auc_score([test[i]["exist_label"] for i in unseen], scores[unseen]))
    values = np.array([
        1.0 if score_by_qid[str(p["positive_qid"])] > score_by_qid[str(p["negative_qid"])]
        else 0.0 if score_by_qid[str(p["positive_qid"])] < score_by_qid[str(p["negative_qid"])]
        else 0.5
        for p in pairs
    ])
    wins, ties, losses = int(sum(values == 1)), int(sum(values == .5)), int(sum(values == 0))
    rng = np.random.default_rng(3407)
    vids = sorted({p["video_id"] for p in pairs})
    groups = {vid: [] for vid in vids}
    for i, pair in enumerate(pairs):
        groups[pair["video_id"]].append(i)
    totals = np.array([values[groups[vid]].sum() for vid in vids])
    sizes = np.array([len(groups[vid]) for vid in vids])
    draws = rng.integers(0, len(vids), size=(20000, len(vids)))
    bootstrap = totals[draws].sum(axis=1) / sizes[draws].sum(axis=1)
    result = {
        "method": "same character 2-4 gram TF-IDF and class-balanced logistic regression as audit_text_only.py",
        "train_rows": len(train), "test_rows": len(test),
        "unseen_auroc": unseen_auc,
        "matched_pair_n": len(pairs), "matched_video_n": len(vids),
        "wins": wins, "ties": ties, "losses": losses,
        "matched_pair_accuracy": float(values.mean()),
        "video_cluster_bootstrap_ci95": [float(x) for x in np.quantile(bootstrap, [.025, .975])],
        "sign_test_p_two_sided_excluding_ties": float(binomtest(wins, wins + losses, .5).pvalue),
    }
    if round(unseen_auc, 4) != 0.5678 or round(float(values.mean()), 4) != 0.5421:
        raise ValueError("Recomputed text-only result differs from release diagnostic")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
