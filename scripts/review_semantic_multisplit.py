#!/usr/bin/env python3
"""Export a deduplicated video-review queue and import per-qid decisions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--split-ids", nargs="+", required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, help="Completed template with decision, reviewer, notes")
    parser.add_argument("--batch-attestation", type=Path,
                        help="Dataset-owner confirmation for the exact current review template")
    parser.add_argument("--shared-action", type=Path, help="Candidate shared S- pool for A groups")
    parser.add_argument("--shared-composition", type=Path, help="Candidate shared S- pool for C groups")
    parser.add_argument("--prior-release", type=Path,
                        help="Reuse only exact negative rows released in v1, preserving their review provenance")
    args = parser.parse_args()
    if args.reviews and args.batch_attestation:
        parser.error("Use either per-qid reviews or a batch attestation")
    if args.reviews and args.reviews.resolve() == args.template.resolve():
        parser.error("--reviews must be a completed copy of --template, never the template itself")
    allowed_train = {}
    if args.shared_action:
        allowed_train["action"] = {r["qid"] for r in read_jsonl(args.shared_action)}
    if args.shared_composition:
        allowed_train["composition"] = {r["qid"] for r in read_jsonl(args.shared_composition)}
    candidates = {}
    occurrences = defaultdict(set)
    prior = {}
    prior_manifest_hash = None
    if args.prior_release:
        prior_manifest_hash = hashlib.sha256((args.prior_release / "manifest.json").read_bytes()).hexdigest()
        prior = {r["qid"]: r for part in ("train", "val", "test")
                 for r in read_jsonl(args.prior_release / f"{part}.jsonl") if r["exist_label"] == 0}
    for split_id in args.split_ids:
        axis = "action" if split_id.startswith("A") else "composition"
        for part in ("train", "val", "test"):
            for row in read_jsonl(args.work_root / split_id / f"{part}_candidates.jsonl"):
                if row["exist_label"]:
                    continue
                if part == "train" and axis in allowed_train and row["qid"] not in allowed_train[axis]:
                    continue
                qid = row["qid"]
                if qid in candidates and any(candidates[qid][k] != row[k] for k in
                                              ("video_id", "query", "source_qid", "exist_label")):
                    raise ValueError(f"Same qid has different negative content: {qid}")
                candidates[qid] = row
                occurrences[qid].add((split_id, part))
    reusable = {}
    for qid, row in candidates.items():
        old = prior.get(qid)
        if old is None:
            continue
        fingerprint = ("video_id", "query", "source_qid", "exist_label", "relevant_windows")
        if all(old[k] == row[k] for k in fingerprint) and \
                all(old["semantic_graph"][k] == row["semantic_graph"][k]
                    for k in ("action", "object", "object_role", "relation")) and \
                old["verification_status"] in {"user_attested_video_review", "manual_video_review_confirmed"}:
            reusable[qid] = old
    args.template.parent.mkdir(parents=True, exist_ok=True)
    columns = ("qid", "video_id", "query", "source_query", "split_memberships",
               "decision", "reviewer", "notes")
    if args.template.exists() and any(row.get("decision", "").strip() for row in
                                      csv.DictReader(args.template.open(newline=""))):
        raise FileExistsError("Review template contains decisions; refusing to overwrite it")
    with args.template.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for qid, row in sorted(candidates.items()):
            if qid in reusable:
                continue
            writer.writerow({"qid": qid, "video_id": row["video_id"], "query": row["query"],
                             "source_query": row["source_query"],
                             "split_memberships": ";".join(f"{s}:{p}" for s, p in sorted(occurrences[qid])),
                             "decision": "", "reviewer": "", "notes": ""})
    if args.reviews is None and args.batch_attestation is None:
        print(json.dumps({"unique_negative_candidates": len(candidates),
                          "exact_prior_review_reuse": len(reusable),
                          "new_negative_review_candidates": len(candidates) - len(reusable),
                          "review_template": str(args.template)}, indent=2))
        return
    reviews = {}
    if args.batch_attestation:
        attestation = json.loads(args.batch_attestation.read_text())
        template_hash = hashlib.sha256(args.template.read_bytes()).hexdigest()
        if attestation.get("negative_review_template_sha256") != template_hash or \
                attestation.get("confirmed_by") != "dataset_owner_user" or \
                attestation.get("all_new_negatives_absent") is not True:
            raise ValueError("Batch attestation does not match the current negative review queue")
    else:
        with args.reviews.open(newline="") as f:
            for item in csv.DictReader(f):
                qid = item["qid"].strip()
                if qid in reviews or qid not in candidates or qid in reusable:
                    raise ValueError(f"Duplicate or unknown review qid: {qid}")
                row = candidates[qid]
                if item["video_id"] != row["video_id"] or item["query"] != row["query"]:
                    raise ValueError(f"Review text or video mismatch: {qid}")
                decision = item["decision"].strip().lower()
                if decision not in {"", "absent", "present", "ambiguous"}:
                    raise ValueError(f"Invalid review decision: {qid}")
                if decision == "absent" and not item["reviewer"].strip():
                    raise ValueError(f"Missing reviewer for absent decision: {qid}")
                reviews[qid] = item
    review_record = args.batch_attestation or args.reviews
    report = {"review_record": str(review_record.resolve()),
              "review_record_sha256": hashlib.sha256(review_record.read_bytes()).hexdigest(),
              "unique_negative_candidates": len(candidates),
              "exact_prior_review_reuse": len(reusable),
              "prior_release_manifest_sha256": prior_manifest_hash,
              "decisions": dict(Counter(r["decision"].strip().lower() for r in reviews.values())),
              "per_split": {}}
    for split_id in args.split_ids:
        axis = "action" if split_id.startswith("A") else "composition"
        report["per_split"][split_id] = {}
        for part in ("train", "val", "test"):
            rows = read_jsonl(args.work_root / split_id / f"{part}_candidates.jsonl")
            reviewed = []
            for row in rows:
                if row["exist_label"]:
                    reviewed.append(row)
                    continue
                if part == "train" and axis in allowed_train and row["qid"] not in allowed_train[axis]:
                    continue
                if row["qid"] in reusable:
                    old = reusable[row["qid"]]
                    approved = dict(row)
                    for field in ("verification_status", "reviewer", "review_notes", "existence_status",
                                  "absence_evidence", "pre_review_absence_evidence"):
                        if field in old:
                            approved[field] = old[field]
                    approved["review_method"] = "v1_exact_released_row_review_reuse"
                    approved["prior_release_manifest_sha256"] = prior_manifest_hash
                    reviewed.append(approved)
                    continue
                decision = ("absent" if args.batch_attestation else
                            reviews.get(row["qid"], {}).get("decision", "").strip().lower())
                if decision != "absent":
                    continue
                approved = dict(row)
                approved["verification_status"] = ("user_attested_video_review" if args.batch_attestation
                                                   else "manual_video_review_confirmed")
                approved["reviewer"] = ("dataset_owner_user" if args.batch_attestation else
                                        reviews[row["qid"]]["reviewer"].strip())
                approved["review_notes"] = ("Dataset owner confirmed this exact candidate batch in conversation"
                                            if args.batch_attestation else reviews[row["qid"]]["notes"].strip())
                approved["review_method"] = ("dataset_owner_global_attestation" if args.batch_attestation
                                             else "qid_level_csv")
                approved["existence_status"] = "absent"
                approved["pre_review_absence_evidence"] = approved.pop("absence_evidence", None)
                approved["absence_evidence"] = ("dataset_owner_review_attestation" if args.batch_attestation
                                                else "qid_level_manual_video_review")
                reviewed.append(approved)
            write_jsonl(args.work_root / split_id / f"{part}_reviewed.jsonl", reviewed)
            report["per_split"][split_id][part] = dict(Counter(r["partition"] for r in reviewed))
        reviewed_test = {r["qid"] for r in read_jsonl(args.work_root / split_id / "test_reviewed.jsonl")}
        matched = [p for p in read_jsonl(args.work_root / split_id / "matched_u_pairs.jsonl")
                   if p["positive_qid"] in reviewed_test and p["negative_qid"] in reviewed_test]
        write_jsonl(args.work_root / split_id / "matched_u_pairs_reviewed.jsonl", matched)
        report["per_split"][split_id]["matched_u_pairs_reviewed"] = len(matched)
        reused_count = sum(r["exist_label"] == 0 and r.get("review_method") ==
                           "v1_exact_released_row_review_reuse" for part in ("train", "val", "test")
                           for r in read_jsonl(args.work_root / split_id / f"{part}_reviewed.jsonl"))
        (args.work_root / split_id / "review_report.json").write_text(json.dumps({
            "review_method": ("dataset_owner_global_attestation_with_v1_exact_reuse" if args.batch_attestation
                              else "mixed_qid_csv_and_exact_v1_reuse" if reused_count else "qid_level_csv"),
            "exact_v1_reused_rows": reused_count,
            "prior_release_manifest_sha256": prior_manifest_hash,
            "review_record": report["review_record"],
            "review_record_sha256": report["review_record_sha256"],
            "counts": report["per_split"][split_id],
        }, ensure_ascii=False, indent=2) + "\n")
    report_path = args.template.parent / "batch_review_import_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"reviewed_splits": args.split_ids, "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
