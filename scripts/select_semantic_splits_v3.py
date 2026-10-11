#!/usr/bin/env python3
"""Freeze v3 semantic split definitions and summarize normalized positive inventory."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data/processed/semantic_existence_v3"
SEL = WORK / "selection"
PLAN = "docs/20261009_SEMANTIC_EXISTENCE_V3_DATA_CONSTRUCTION_PLAN.md"

SPECS = {
    "schema_version": 1,
    "release_version": "semantic_existence_v3",
    "ontology_version": "v3-ontology-1.0.0",
    "normalization_rule_version": "v3-event-normalization-1.1.0",
    "seed": 3407,
    "groups": {
        "A1_v3": {"axis": "action_family", "held_action_families": ["physical_place", "physical_take"]},
        "A2_v3": {"axis": "action_family", "held_action_families": ["drink", "pour"]},
        "A3_v3": {"axis": "action_family", "held_action_families": ["run", "walk"]},
        "C1_v3": {"axis": "action_object_composition", "held_compositions": [["sit", "bed"], ["sit", "chair"], ["sit", "couch"]]},
        "C2_v3": {"axis": "action_object_composition", "held_compositions": [["open", "box"], ["open", "cabinet"], ["close", "box"], ["close", "cabinet"]]},
    },
    "object_aliases": {"sofa": "couch", "couch": "couch", "cabinet door": "cabinet_entry"},
    "role_anchors": {"C1_v3": "support_surface/location", "C2_v3": "theme"},
    "train_policy": "S+ and S- only; remove a whole query if any event in it hits the group's held definition.",
    "split_policy": "Use persisted shared video_splits.jsonl; every qid follows its video assignment.",
}

def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def canonical_object(value):
    if value is None:
        return None
    text = " ".join(str(value).lower().replace("_", " ").split())
    if text in {"sofa", "couch"}:
        return "couch"
    if text in {"cabinet door", "cabinet entry"}:
        return "cabinet_entry"
    return text

def main():
    SEL.mkdir(parents=True, exist_ok=True)
    events = read_jsonl(WORK / "positives/events.jsonl")
    dispositions = read_jsonl(WORK / "positives/dispositions.jsonl")
    raw = read_jsonl(WORK / "positives/raw.jsonl")
    videos = read_jsonl(WORK / "inputs/video_splits.jsonl")
    qids = [row["qid"] for row in raw]
    if len(qids) != len(set(qids)):
        raise SystemExit("Positive raw qids are not unique")
    disp = {r["qid"]: r for r in dispositions}
    if set(disp) != set(qids):
        raise SystemExit(f"Disposition coverage mismatch: raw={len(qids)}, dispositions={len(disp)}")
    ev_by_parse = {r["parse_id"]: r for r in events}
    event_count = Counter(); pair_count = Counter(); unresolved = Counter(); missing_vids = []
    raw_by_qid = {row["qid"]: row for row in raw}
    for qid, row in disp.items():
        if qid not in raw_by_qid:
            continue
        if row["semantic_review_status"] != "resolved":
            unresolved[row["semantic_review_status"]] += 1
            continue
        parse = ev_by_parse.get(row["parse_id"])
        if parse is None:
            raise SystemExit(f"Missing event parse for {qid}: {row['parse_id']}")
        for event in parse["events"]:
            action = event.get("action_family")
            if not action:
                continue
            event_count[action] += 1
            obj = canonical_object(event.get("anchor_object"))
            if event.get("anchor_role") in {"support_surface", "location", "theme"} and obj:
                pair_count[(action, obj)] += 1
        if not raw_by_qid[qid].get("vid"):
            missing_vids.append(qid)
    video_map = {r["vid"]: r["split"] for r in videos}
    missing_video_assignments = sorted({row["vid"] for row in raw if row["vid"] not in video_map})
    if missing_video_assignments:
        raise SystemExit(f"Missing video split assignments for {len(missing_video_assignments)} videos")
    (SEL / "split_specs.json").write_text(json.dumps(SPECS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rules = {
        "schema_version": 1,
        "ontology_version": SPECS["ontology_version"],
        "canonicalization": {"sofa": "couch", "couch": "couch", "cabinet door access event": "cabinet_entry"},
        "action_senses": json.loads((WORK / "ontology/rules.json").read_text(encoding="utf-8"))["action_senses"],
        "event_matching": "Full event list and roles; not surface-token matching.",
        "query_filter": "Remove a whole train query if any event hits a group's held definition.",
        "composition_anchor_roles": SPECS["role_anchors"],
    }
    (SEL / "semantic_rules.json").write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    profile = {
        "positive_unique_qids": len(qids),
        "positive_event_parse_records": len(events),
        "positive_qids_with_dispositions": len(disp),
        "positive_qids_resolved": sum(r["semantic_review_status"] == "resolved" for r in disp.values()),
        "positive_qids_unresolved": sum(r["semantic_review_status"] != "resolved" for r in disp.values()),
        "positive_unresolved_status_counts": unresolved,
        "video_assignments": len(video_map),
        "action_event_counts_resolved_qid_events": dict(event_count),
        "action_anchor_counts_resolved_qid_events": {f"{a}|{o}": n for (a, o), n in sorted(pair_count.items())},
        "groups": SPECS["groups"],
        "split_assignment_sources": dict(Counter(r.get("assignment_source", "unknown") for r in videos)),
        "protocol": PLAN,
        "model_predictions_used": False,
    }
    (SEL / "data_profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Record semantic support questions without imposing a scale threshold.
    issues=[]
    for group, spec in SPECS["groups"].items():
        held = spec.get("held_action_families", [])
        for action in held:
            if event_count[action] == 0:
                issues.append({"group": group, "held_action_family": action, "status": "no_resolved_positive_support", "count": 0})
        for action, obj in spec.get("held_compositions", []):
            count=pair_count[(action,obj)]
            if count == 0:
                issues.append({"group": group, "held_composition": [action,obj], "status": "no_resolved_positive_support", "count": 0})
    (SEL / "definition_issues.json").write_text(json.dumps(issues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"positive_qids": len(qids), "resolved": profile["positive_qids_resolved"], "unresolved": profile["positive_qids_unresolved"], "video_assignments": len(video_map), "definition_issues": len(issues)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
