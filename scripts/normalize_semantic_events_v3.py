#!/usr/bin/env python3
"""Validate and import query-level positive event normalization batches."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data/processed/semantic_existence_v3"
PROGRESS = ROOT / "docs/semantic_existence_v3_construction/progress.json"
EVENT_FIELDS = (
    "action_family", "action_surface", "theme", "source", "goal", "location",
    "instrument", "polarity", "aspect", "anchor_role", "anchor_object", "manner",
    "state_change",
)
PIPELINE_VERSION = "v3-event-normalization-1.1.0"
SUPPORT_OBJECTS = {"bed", "chair", "couch", "sofa", "armchair", "stool", "bench", "table"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        # Accept a JSON array from an earlier resumable assignment update, then
        # rewrite the queue to canonical JSONL during the next import.
        value = json.loads(text)
        if not isinstance(value, list):
            raise ValueError(f"Expected JSONL or a JSON array in {path}")
        return value
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def atomic_json(path: Path, value) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    temp.replace(path)


def canonicalize_event(event: dict) -> None:
    for field in ("theme", "source", "goal", "location", "anchor_object", "state_change"):
        value = event.get(field)
        if isinstance(value, str):
            event[field] = re.sub(r"\bsofa\b", "couch", value, flags=re.IGNORECASE)


def harmonize_event(query: str, event: dict) -> bool:
    """Apply consistent action-family and support-object roles across batches."""
    before = json.dumps(event, ensure_ascii=False, sort_keys=True)
    family = event.get("action_family")
    surface = str(event.get("action_surface") or "").lower()
    if family == "sit_down":
        event["action_family"] = "sit"
    elif family == "put":
        clothing = re.search(
            r"\b(?:put|putting|puts)\s+on\s+(?:the\s+|a\s+|their\s+)?"
            r"(?:clothes|clothing|shirt|pants|trousers|shoes|socks|jacket|coat|dress)\b",
            query, re.I,
        )
        event["action_family"] = "dress" if clothing else "physical_place"
    elif family in {"place", "set_down"}:
        event["action_family"] = "physical_place"

    if event.get("action_family") == "sit":
        match = re.search(
            r"\bsit(?:ting|s)?(?:\s+down)?\s+(?:on|in|at)\s+(?:the\s+|a\s+|an\s+|their\s+|this\s+)?"
            r"(?P<object>(?:(?:kitchen|dining|living room)\s+)?"
            r"(?:bed|chair|couch|sofa|armchair|stool|bench|table))\b",
            query, re.I,
        )
        if match:
            object_name = re.sub(r"\s+", " ", match.group("object").lower()).replace("sofa", "couch")
            if object_name.split()[-1] in SUPPORT_OBJECTS:
                event["agent"] = event.get("agent") or "person"
                event["theme"] = None
                event["source"] = None
                event["goal"] = None
                event["instrument"] = None
                event["location"] = object_name
                event["anchor_role"] = "support_surface" if object_name.split()[-1] in {
                    "bed", "chair", "couch", "armchair", "stool", "bench",
                } else "location"
                event["anchor_object"] = object_name
                if "down" in surface:
                    event["state_change"] = f"person becomes seated on {object_name}"
                elif event.get("state_change") in {"seated", "seated at"}:
                    event["state_change"] = f"person seated on {object_name}"
    return before != json.dumps(event, ensure_ascii=False, sort_keys=True)


def import_batch(args) -> None:
    assignment_path = WORK / "positives/batch_assignments.json"
    assignment_doc = read_json(assignment_path)
    batch = next((item for item in assignment_doc["assignments"] if item["batch_id"] == args.batch), None)
    if batch is None:
        raise SystemExit(f"Unknown positive batch: {args.batch}")
    if batch["status"] == "imported":
        raise SystemExit(f"{args.batch} is already imported")
    results = read_jsonl(ROOT / batch["output_path"])
    expected = set(batch["parse_ids"])
    parse_ids = [row.get("parse_id") for row in results]
    if len(parse_ids) != len(expected) or set(parse_ids) != expected or len(parse_ids) != len(set(parse_ids)):
        raise SystemExit(f"{args.batch} parse_id coverage mismatch")
    queue = read_jsonl(WORK / "positives/query_queue.jsonl")
    queue_by_id = {row["parse_id"]: row for row in queue if row.get("parse_id")}
    raw_by_qid = {row["qid"]: row for row in read_jsonl(WORK / "positives/raw.jsonl")}
    event_path = WORK / "positives/events.jsonl"
    disposition_path = WORK / "positives/dispositions.jsonl"
    events = {row["parse_id"]: row for row in read_jsonl(event_path)} if event_path.exists() else {}
    dispositions = {row["qid"]: row for row in read_jsonl(disposition_path)} if disposition_path.exists() else {}
    now = datetime.now(timezone.utc).isoformat()
    counts = Counter()
    qid_coverage = 0
    for row in results:
        parse_id = row["parse_id"]
        if parse_id in events:
            raise SystemExit(f"Duplicate normalized query: {parse_id}")
        source = queue_by_id.get(parse_id)
        if source is None or row.get("query") != source["query"] or row.get("qids") != source["qids"]:
            raise SystemExit(f"{parse_id} query/qid list differs from the queue")
        if row.get("semantic_review_status") not in {"resolved", "unresolved"}:
            raise SystemExit(f"{parse_id} has invalid semantic_review_status")
        if not isinstance(row.get("events"), list) or not row["events"]:
            raise SystemExit(f"{parse_id} has no event parse")
        for event in row["events"]:
            missing = [field for field in EVENT_FIELDS if field not in event]
            if missing:
                raise SystemExit(f"{parse_id} event misses {missing}")
            if event.get("polarity") not in {"positive", "negative", "unknown"}:
                raise SystemExit(f"{parse_id} has invalid polarity")
            canonicalize_event(event)
            harmonize_event(row["query"], event)
        row["review_method"] = "codex_text_semantic_event_normalization"
        row["worker_normalization_rule_version"] = batch["rule_version"]
        row["normalization_rule_version"] = PIPELINE_VERSION
        row["ontology_version"] = "v3-ontology-1.0.0"
        row["basis_artifact"] = batch["output_path"]
        events[parse_id] = row
        counts[row["semantic_review_status"]] += 1
        for qid in row["qids"]:
            raw = raw_by_qid.get(qid)
            if raw is None or raw["query"] != row["query"]:
                raise SystemExit(f"{parse_id} has an invalid raw positive qid reference: {qid}")
            if qid in dispositions:
                raise SystemExit(f"Duplicate positive disposition: {qid}")
            dispositions[qid] = {
                "qid": qid, "parse_id": parse_id, "vid": raw["vid"], "query": raw["query"],
                "semantic_review_status": "semantic_unresolved" if row["semantic_review_status"] == "unresolved" else "resolved",
                "reason": row.get("evidence", ""), "review_method": row["review_method"],
                "reviewer": row["reviewer"], "reviewed_at": row["reviewed_at"],
                "ontology_version": row["ontology_version"],
            }
            qid_coverage += 1
        source["status"] = "completed"
        source["semantic_review_status"] = row["semantic_review_status"]
    batch["status"] = "imported"
    batch["imported_at"] = now
    batch["counts"] = dict(counts)
    assignment_doc["updated_at"] = now
    atomic_json(assignment_path, assignment_doc)
    write_jsonl(WORK / "positives/query_queue.jsonl", queue)
    write_jsonl(event_path, sorted(events.values(), key=lambda row: row["parse_id"]))
    write_jsonl(disposition_path, sorted(dispositions.values(), key=lambda row: row["qid"]))
    state_path = WORK / "state.json"
    state = read_json(state_path)
    all_statuses = Counter(row["semantic_review_status"] for row in events.values())
    state.update({
        "updated_at": now, "positive_unique_queries_normalized": len(events),
        "positive_queries_normalized": len(events),
        "positive_queries_pending": 9956 - len(events), "positive_qids_with_dispositions": len(dispositions),
        "positive_qids_pending": 16124 - len(dispositions), "positive_query_parse_counts": dict(all_statuses),
        "positive_imported_batches": sorted(item["batch_id"] for item in assignment_doc["assignments"] if item["status"] == "imported"),
    })
    atomic_json(state_path, state)
    progress = read_json(PROGRESS)
    progress.update({key: state[key] for key in (
        "updated_at", "positive_unique_queries_normalized", "positive_queries_pending",
        "positive_qids_with_dispositions", "positive_qids_pending", "positive_query_parse_counts",
        "positive_imported_batches",
    )})
    progress["positive_queries_normalized"] = len(events)
    atomic_json(PROGRESS, progress)
    print(json.dumps({"batch": args.batch, "query_counts": dict(counts), "qids_covered": qid_coverage,
                      "total_queries_normalized": len(events), "total_qids_with_dispositions": len(dispositions)},
                     ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True)
    args = parser.parse_args()
    import_batch(args)


if __name__ == "__main__":
    main()
