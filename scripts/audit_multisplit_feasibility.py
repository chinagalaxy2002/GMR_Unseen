#!/usr/bin/env python3
"""Apply frozen multi-split quality gates to candidate or reviewed data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--reviewed", action="store_true")
    parser.add_argument("--parser-qc", type=Path, help="Completed semantic parser QC CSV")
    parser.add_argument("--batch-attestation", type=Path,
                        help="Dataset-owner confirmation for the exact parser QC template")
    args = parser.parse_args()
    if args.reviewed and (args.parser_qc is None) == (args.batch_attestation is None):
        parser.error("Reviewed feasibility requires exactly one parser QC source")
    specs = json.loads((args.selection / "split_specs.json").read_text())
    rules = json.loads((args.selection / "selection_rules.json").read_text())
    parser_qc = {}
    if args.parser_qc:
        for row in csv.DictReader(args.parser_qc.open(newline="")):
            parser_qc.setdefault((row["split_id"], row["semantic"]), []).append(row)
    if args.batch_attestation:
        attestation = json.loads(args.batch_attestation.read_text())
        template_path = args.selection / "parser_qc_template.csv"
        if attestation.get("parser_qc_template_sha256") != hashlib.sha256(template_path.read_bytes()).hexdigest() or \
                attestation.get("confirmed_by") != "dataset_owner_user" or \
                attestation.get("all_parser_samples_correct") is not True:
            raise ValueError("Batch attestation does not match the current parser QC template")
    results = []
    for spec in specs:
        split_id = spec["id"]
        root = args.work_root / split_id
        path = root / ("test_reviewed.jsonl" if args.reviewed else "test_candidates.jsonl")
        if not path.exists():
            continue
        rows = read_jsonl(path)
        positives = [r for r in rows if r["partition"] == "U+" and
                     r["novelty_type"] == ("unseen_action" if spec["axis"] == "action" else "unseen_composition")]
        negatives = [r for r in rows if r["partition"] == "U-" and
                     r["novelty_type"] == ("unseen_action" if spec["axis"] == "action" else "unseen_composition")]
        pairs = read_jsonl(root / ("matched_u_pairs_reviewed.jsonl" if args.reviewed else "matched_u_pairs.jsonl"))
        counts = Counter(r["semantic_graph"]["action"] if spec["axis"] == "action" else
                         r["semantic_graph"]["action"] + "|" + r["semantic_graph"]["object"] for r in positives)
        maximum = max(counts.values()) / len(positives) if positives else 1.0
        coverage = len(pairs) / len(positives) if positives else 0.0
        measures = {
            "u_positive": len(positives), "u_negative": len(negatives),
            "u_positive_videos": len({r["video_id"] for r in positives}),
            "matched_pairs": len(pairs), "matched_pair_coverage": round(coverage, 4),
            "largest_semantic_share": round(maximum, 4), "per_semantic_u_positive": dict(counts),
        }
        gates = {
            "u_positive": len(positives) >= rules["formal_test_min_u_positive"],
            "u_negative": len(negatives) >= rules["formal_test_min_u_negative"],
            "u_positive_videos": measures["u_positive_videos"] >= rules["formal_test_min_u_positive_videos"],
            "matched_pairs": len(pairs) >= rules["formal_test_min_matched_pairs"],
            "matched_pair_coverage": coverage >= rules["formal_test_min_matched_pair_u_positive_coverage"],
            "largest_semantic_share": maximum <= rules[
                "formal_action_max_largest_action_share" if spec["axis"] == "action" else
                "formal_composition_max_largest_pair_share"],
        }
        if args.reviewed:
            if args.batch_attestation:
                measures["parser_qc"] = {"source": "dataset_owner_global_attestation",
                                         "sample_count": sum(1 for _ in csv.DictReader(
                                             (args.selection / "parser_qc_template.csv").open(newline="")))}
                gates["parser_qc"] = True
            else:
                parser_scores = {}
                for semantic in (spec["held_actions"] if spec["axis"] == "action" else spec["held_compositions"]):
                    sample = parser_qc.get((split_id, semantic), [])
                    valid = all(r["decision"].strip().lower() in {"correct", "incorrect", "ambiguous"} and
                                r["reviewer"].strip() for r in sample)
                    correct = sum(r["decision"].strip().lower() == "correct" for r in sample)
                    fraction = correct / len(sample) if sample else 0.0
                    parser_scores[semantic] = {"sampled": len(sample), "correct_fraction": round(fraction, 4),
                                               "all_reviewed": valid}
                measures["parser_qc"] = parser_scores
                gates["parser_qc"] = all(
                    r["sampled"] >= min(rules["parser_qc_sample_per_semantic"], counts.get(semantic, 0)) and
                    r["correct_fraction"] >= rules["parser_qc_min_correct_fraction"] and r["all_reviewed"]
                    for semantic, r in parser_scores.items())
        results.append({"id": split_id, "axis": spec["axis"], "status": "reviewed" if args.reviewed else "candidate_upper_bound",
                        "measures": measures, "gates": gates, "passes_all_gates": all(gates.values())})
    output = args.selection / ("reviewed_feasibility.json" if args.reviewed else "candidate_feasibility.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"audited": len(results), "passes": [r["id"] for r in results if r["passes_all_gates"]],
                      "fails": [r["id"] for r in results if not r["passes_all_gates"]],
                      "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
