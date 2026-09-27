#!/usr/bin/env python3
"""Prepare video review and export only adjudicated GMR negatives."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/semantic_existence")
    parser.add_argument("--reviews", type=Path, help="CSV with qid, decision, reviewer, notes; decision=absent/present/ambiguous")
    parser.add_argument("--user-attests-all-absent", action="store_true",
                        help="Dataset owner explicitly confirms all current test candidates were reviewed and absent")
    args = parser.parse_args()
    if args.reviews and args.user_attests_all_absent:
        parser.error("Use either --reviews or --user-attests-all-absent")
    positives = read_jsonl(args.data / "test_positives.jsonl")
    negatives = read_jsonl(args.data / "test_negative_review_queue.jsonl")
    template = args.data / "negative_review_template.csv"
    fields = ["qid", "video_id", "partition", "query", "source_query", "source_windows", "decision", "reviewer", "notes"]
    with template.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in negatives:
            writer.writerow({"qid": row["qid"], "video_id": row["video_id"],
                             "partition": row["partition"], "query": row["query"],
                             "source_query": row["source_query"],
                             "source_windows": json.dumps(row["source_windows"]),
                             "decision": "", "reviewer": "", "notes": ""})
    if args.reviews is None and not args.user_attests_all_absent:
        print(f"Review template: {template}; {len(negatives)} candidate negatives")
        return
    decisions = {}
    if args.user_attests_all_absent:
        decisions = {row["qid"]: {"decision": "absent", "reviewer": "dataset_owner_user",
                                  "notes": "Dataset owner confirmed all candidates passed review in conversation"}
                     for row in negatives}
    else:
        with args.reviews.open(newline="") as f:
            for row in csv.DictReader(f):
                qid = row["qid"].strip()
                decision = row["decision"].strip().lower()
                if decision not in {"absent", "present", "ambiguous", ""}:
                    raise ValueError(f"Invalid decision for {qid}: {decision}")
                if qid in decisions:
                    raise ValueError(f"Duplicate review for {qid}")
                if decision == "absent" and not row["reviewer"].strip():
                    raise ValueError(f"Missing reviewer for approved negative {qid}")
                decisions[qid] = row
    known = {r["qid"] for r in negatives}
    unknown = set(decisions) - known
    if unknown:
        raise ValueError(f"Unknown negative qids in review: {sorted(unknown)[:5]}")
    approved = []
    for row in negatives:
        review = decisions.get(row["qid"])
        if review and review["decision"].strip().lower() == "absent":
            verified = dict(row)
            verified["existence_status"] = "absent"
            verified["verification_status"] = ("user_attested_video_review" if args.user_attests_all_absent
                                                else "manual_video_review_confirmed")
            verified["reviewer"] = review["reviewer"].strip()
            verified["review_notes"] = review["notes"].strip()
            verified["review_method"] = "dataset_owner_global_attestation" if args.user_attests_all_absent else "qid_level_csv"
            verified["pre_review_absence_evidence"] = verified.pop("absence_evidence", None)
            verified["absence_evidence"] = "dataset_owner_review_attestation" if args.user_attests_all_absent else "qid_level_manual_video_review"
            approved.append(verified)
    if not approved:
        raise ValueError("No reviewed absent negatives; official test export requires video review")
    official = positives + approved
    write_jsonl(args.data / "test_reviewed.jsonl", official)
    approved_ids = {r["qid"] for r in approved}
    pairs = [r for r in read_jsonl(args.data / "matched_u_pairs.jsonl") if r["negative_qid"] in approved_ids]
    write_jsonl(args.data / "matched_u_pairs_reviewed.jsonl", pairs)
    extra_reviewed = {}
    if args.user_attests_all_absent:
        for split in ("train", "val"):
            rows = read_jsonl(args.data / f"{split}_candidates.jsonl")
            for item in rows:
                if item["exist_label"] == 0:
                    item["existence_status"] = "absent"
                    item["verification_status"] = "user_attested_video_review"
                    item["reviewer"] = "dataset_owner_user"
                    item["review_notes"] = "Dataset owner confirmed all candidates passed review in conversation"
                    item["review_method"] = "dataset_owner_global_attestation"
                    item["pre_review_absence_evidence"] = item.pop("absence_evidence", None)
                    item["absence_evidence"] = "dataset_owner_review_attestation"
            write_jsonl(args.data / f"{split}_reviewed.jsonl", rows)
            extra_reviewed[split] = dict(Counter(r["partition"] for r in rows))
    report = {"counts": dict(Counter(r["partition"] for r in official)),
              "reviewed_negatives": len(approved), "matched_u_pairs": len(pairs),
              "unreviewed_or_excluded_negatives": len(negatives) - len(approved),
              "review_method": "dataset_owner_global_attestation" if args.user_attests_all_absent else "qid_level_csv",
              "review_record": "User stated all candidates passed review; no per-qid review file supplied" if args.user_attests_all_absent else str(args.reviews),
              "other_reviewed_splits": extra_reviewed}
    (args.data / "review_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
