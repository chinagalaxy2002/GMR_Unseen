#!/usr/bin/env python3
"""Measure whether query text alone predicts existence in the released dataset."""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/release/semantic_existence_v1"


def load(name):
    return [json.loads(line) for line in (DATA / name).read_text().splitlines() if line]


def main():
    train = load("train.jsonl")
    test = load("test.jsonl")
    pairs = load("matched_u_pairs.jsonl")
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=3, max_features=50000)
    x_train = vectorizer.fit_transform(r["query"] for r in train)
    model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=0)
    model.fit(x_train, [r["exist_label"] for r in train])
    scores = model.predict_proba(vectorizer.transform(r["query"] for r in test))[:, 1]
    def metrics(indices):
        labels = [test[i]["exist_label"] for i in indices]
        values = [float(scores[i]) for i in indices]
        return {"n": len(indices), "roc_auc": round(roc_auc_score(labels, values), 4),
                "balanced_accuracy_at_0_5": round(balanced_accuracy_score(labels, [p >= 0.5 for p in values]), 4)}
    score_by_qid = {r["qid"]: float(score) for r, score in zip(test, scores)}
    result = {
        "method": "character 2-4 gram TF-IDF + class-balanced logistic regression; train split only; no video input",
        "train_rows": len(train), "test_rows": len(test),
        "all": metrics(range(len(test))),
        "seen": metrics([i for i, r in enumerate(test) if r["semantic_status"] == "seen"]),
        "unseen": metrics([i for i, r in enumerate(test) if r["semantic_status"] == "unseen"]),
        "matched_u_pair_text_only_ranking_accuracy": round(sum(score_by_qid[r["positive_qid"]] > score_by_qid[r["negative_qid"]] for r in pairs) / len(pairs), 4),
        "matched_u_pairs": len(pairs),
        "interpretation": "AUC above 0.5 indicates residual text-only label signal; it is not evidence of video understanding.",
    }
    (DATA / "text_only_diagnostic.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
