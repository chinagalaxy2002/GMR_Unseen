#!/usr/bin/env python3
"""Profile candidate holdouts from original, unfiltered Charades positives."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import spacy

from build_semantic_existence import (
    ACTION_NEIGHBORS, OBJECT_NEIGHBORS, all_event_pairs, all_verb_lemmas,
    canonicalize, pair, read_jsonl, stable_bucket, vn_index,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--verbnet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    vn = vn_index(args.verbnet)
    rows = []
    for source_split, path in (("train", args.train), ("test", args.test)):
        original = read_jsonl(path)
        for raw, doc in zip(original, nlp.pipe((r["query"] for r in original), batch_size=256)):
            graph = canonicalize(doc, vn)
            vid = raw.get("vid", raw.get("video_id"))
            split = "test" if source_split == "test" else ("val" if stable_bucket(vid) < 10 else "train")
            rows.append({"qid": str(raw["qid"]), "vid": vid, "split": split,
                         "action": graph["action"], "object": graph["object"],
                         "pair": "|".join(pair(graph)) if pair(graph) else None,
                         "verbs": sorted(all_verb_lemmas(doc)),
                         "pairs": sorted("|".join(p) for p in all_event_pairs(doc))})
    by_action = defaultdict(lambda: defaultdict(list))
    by_pair = defaultdict(lambda: defaultdict(list))
    video_actions = defaultdict(set)
    video_objects = defaultdict(set)
    for r in rows:
        if r["action"] and r["object"]:
            by_action[r["action"]][r["split"]].append(r)
            by_pair[r["pair"]][r["split"]].append(r)
        for event in r["pairs"]:
            action, obj = event.split("|", 1)
            video_actions[r["vid"]].add(action)
            video_objects[r["vid"]].add(obj)

    def fields(groups: dict, key: str) -> dict:
        all_rows = [r for part in groups.values() for r in part]
        tr, va, te = (groups.get(s, []) for s in ("train", "val", "test"))
        objects = Counter(r["object"] for r in all_rows)
        actions = Counter(r["action"] for r in all_rows)
        return {
            "semantic": key,
            "train_positives": len(tr), "val_positives": len(va), "test_positives": len(te),
            "train_videos": len({r["vid"] for r in tr}),
            "val_videos": len({r["vid"] for r in va}),
            "test_videos": len({r["vid"] for r in te}),
            "train_source_qids": len({r["qid"] for r in tr}),
            "test_source_qids": len({r["qid"] for r in te}),
            "distinct_objects": len(objects),
            "top_object": objects.most_common(1)[0][0] if objects else "",
            "top_object_share": round(objects.most_common(1)[0][1] / len(all_rows), 4) if all_rows else 0,
            "distinct_actions": len(actions),
        }

    actions = []
    for action, groups in sorted(by_action.items()):
        f = fields(groups, action)
        f["train_any_verb_or_event_rows"] = sum(
            action in r["verbs"] or any(p.startswith(action + "|") for p in r["pairs"])
            for r in rows if r["split"] == "train")
        f["test_any_verb_or_event_rows"] = sum(
            action in r["verbs"] or any(p.startswith(action + "|") for p in r["pairs"])
            for r in rows if r["split"] == "test")
        f["action_neighbor"] = ";".join(ACTION_NEIGHBORS.get(action, []))
        f["test_positive_object_edit_opportunities"] = sum(
            bool(set(OBJECT_NEIGHBORS.get(r["object"], [])) & video_objects[r["vid"]])
            for r in groups.get("test", []))
        actions.append(f)
    compositions = []
    train_action = Counter(r["action"] for r in rows if r["split"] == "train" and r["pair"])
    train_object = Counter(r["object"] for r in rows if r["split"] == "train" and r["pair"])
    for key, groups in sorted(by_pair.items()):
        f = fields(groups, key)
        action, obj = key.split("|", 1)
        tr = groups.get("train", [])
        f["remaining_train_action_positives"] = train_action[action] - len(tr)
        f["remaining_train_object_positives"] = train_object[obj] - len(tr)
        f["test_same_video_recombination_opportunities"] = sum(
            action in video_actions[r["vid"]] and r["action"] != action and r["object"] == obj
            for r in rows if r["split"] == "test")
        f["test_object_edit_opportunities"] = sum(
            bool(set(OBJECT_NEIGHBORS.get(r["object"], [])) & video_objects[r["vid"]])
            for r in groups.get("test", []))
        compositions.append(f)
    write_csv(args.out / "action_candidates.csv", actions)
    write_csv(args.out / "composition_candidates.csv", compositions)
    (args.out / "profile_provenance.json").write_text(json.dumps({
        "sources": {str(p.resolve()): sha256(p) for p in (args.train, args.test)},
        "original_positive_rows": len(rows),
        "parsed_action_object_rows": sum(bool(r["pair"]) for r in rows),
        "action_candidates": len(actions), "composition_candidates": len(compositions),
        "note": "Edit opportunities are unfiltered upper-bound proxies, not reviewed negatives or confirmed pairs.",
    }, indent=2) + "\n")
    print(json.dumps({"actions": len(actions), "compositions": len(compositions),
                      "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
