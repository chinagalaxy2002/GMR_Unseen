#!/usr/bin/env python3
"""Deterministically select candidate semantic holdouts before model evaluation."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from build_semantic_existence import OBJECT_NEIGHBORS


FAMILIES = {
    "manipulation": ("take", "put", "hold", "throw", "put_down", "take_out", "put_in"),
    "consumption": ("eat", "drink", "pour", "cook"),
    "motion": ("run", "walk", "enter", "leave", "approach"),
}


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    args = parser.parse_args()
    root = args.selection
    if (root / "frozen_selection_manifest.json").exists():
        raise SystemExit("Selection is frozen; create a new version instead of overwriting it")
    actions = {r["semantic"]: r for r in csv.DictReader((root / "action_candidates.csv").open())}
    pairs = {r["semantic"]: r for r in csv.DictReader((root / "composition_candidates.csv").open())}
    rules = {
        "schema_version": 1,
        "selection_seed": 3407,
        "source_profile": "profile_provenance.json",
        "action_candidate_min_train_positives": 100,
        "action_candidate_min_test_positives": 50,
        "action_candidate_min_test_videos": 30,
        "action_candidate_min_distinct_objects": 10,
        "action_candidate_max_top_object_share": 0.70,
        "action_group_max_largest_action_share": 0.70,
        "composition_candidate_min_train_positives": 20,
        "composition_candidate_min_test_positives": 8,
        "composition_min_remaining_train_action_positives": 30,
        "composition_min_remaining_train_object_positives": 10,
        "composition_group_min_projected_test_positives": 80,
        "composition_group_max_projected_test_positives": 220,
        "composition_group_max_largest_pair_share": 0.65,
        "formal_test_min_u_positive": 80,
        "formal_test_min_u_negative": 40,
        "formal_test_min_u_positive_videos": 50,
        "formal_test_min_matched_pairs": 20,
        "formal_test_min_matched_pair_u_positive_coverage": 0.15,
        "formal_action_max_largest_action_share": 0.70,
        "formal_composition_max_largest_pair_share": 0.65,
        "parser_qc_sample_per_semantic": 12,
        "parser_qc_min_correct_fraction": 0.90,
        "shared_seen_negative_pool_target_per_axis": 1500,
        "note": "Formal gates apply after video review, before any model test predictions. Failing groups remain recorded as feasibility failures.",
    }
    write_json(root / "selection_rules.json", rules)
    selected = []
    selection_audit = []
    for index, (family, members) in enumerate(FAMILIES.items(), start=1):
        eligible = []
        for action in members:
            r = actions.get(action)
            if not r:
                selection_audit.append({"candidate": action, "family": family, "result": "not_parsed"})
                continue
            reasons = []
            for field, threshold in (("train_positives", rules["action_candidate_min_train_positives"]),
                                     ("test_positives", rules["action_candidate_min_test_positives"]),
                                     ("test_videos", rules["action_candidate_min_test_videos"]),
                                     ("distinct_objects", rules["action_candidate_min_distinct_objects"])):
                if int(r[field]) < threshold:
                    reasons.append(f"{field}<{threshold}")
            if float(r["top_object_share"]) > rules["action_candidate_max_top_object_share"]:
                reasons.append("object_concentration")
            if reasons:
                selection_audit.append({"candidate": action, "family": family, "result": "excluded", "reasons": reasons})
            else:
                eligible.append(r)
        eligible.sort(key=lambda r: (-int(r["test_positives"]), r["semantic"]))
        chosen = eligible[:2]
        if len(chosen) != 2:
            raise SystemExit(f"Insufficient eligible actions in {family}")
        total = sum(int(r["test_positives"]) for r in chosen)
        if max(int(r["test_positives"]) for r in chosen) / total > rules["action_group_max_largest_action_share"]:
            raise SystemExit(f"Action group {family} is dominated by one action")
        spec = {"schema_version": 1, "id": f"A{index}", "axis": "action",
                "selection_family": family, "held_actions": sorted(r["semantic"] for r in chosen),
                "held_compositions": []}
        selected.append(spec)
        selection_audit += [{"candidate": r["semantic"], "family": family, "result": "selected"} for r in chosen]

    considered_actions = {action for members in FAMILIES.values() for action in members}
    selection_audit += [{"candidate": action, "family": "outside_predeclared_families",
                         "result": "not_considered", "reasons": ["outside_predeclared_families"]}
                        for action in sorted(set(actions) - considered_actions)]

    by_action = defaultdict(list)
    for key, r in pairs.items():
        reasons = []
        for field, threshold in (("train_positives", rules["composition_candidate_min_train_positives"]),
                                 ("test_positives", rules["composition_candidate_min_test_positives"]),
                                 ("remaining_train_action_positives", rules["composition_min_remaining_train_action_positives"]),
                                 ("remaining_train_object_positives", rules["composition_min_remaining_train_object_positives"])):
            if int(r[field]) < threshold:
                reasons.append(f"{field}<{threshold}")
        if not reasons:
            by_action[key.split("|", 1)[0]].append(r)
        selection_audit.append({"candidate": key, "family": "composition_candidate",
                                "result": "eligible" if not reasons else "excluded", "reasons": reasons})
    groups = []
    for action, candidates in by_action.items():
        ranked = sorted(candidates, key=lambda r: (-int(r["test_positives"]), r["semantic"]))
        if len(ranked) < 2:
            continue
        anchor = ranked[0]
        anchor_object = anchor["semantic"].split("|", 1)[1]
        linked = [r for r in ranked[1:] if r["semantic"].split("|", 1)[1]
                  in OBJECT_NEIGHBORS.get(anchor_object, [])]
        group = [anchor] + linked[:2]
        if len(group) < 2:
            continue
        total = sum(int(r["test_positives"]) for r in group)
        share = max(int(r["test_positives"]) for r in group) / total
        if (rules["composition_group_min_projected_test_positives"] <= total <=
                rules["composition_group_max_projected_test_positives"] and
                share <= rules["composition_group_max_largest_pair_share"]):
            groups.append((total, action, group))
    groups.sort(key=lambda item: (-item[0], item[1]))
    if len(groups) < 2:
        raise SystemExit("Fewer than two eligible composition groups")
    for index, (total, action, group) in enumerate(groups[:2], start=1):
        spec = {"schema_version": 1, "id": f"C{index}", "axis": "composition",
                "selection_family": action, "held_actions": [],
                "held_compositions": sorted(r["semantic"] for r in group),
                "projected_test_positives": total}
        selected.append(spec)
        selection_audit.append({"candidate": action, "family": "composition", "result": "selected_group",
                                "compositions": spec["held_compositions"]})
    write_json(root / "split_specs.json", selected)
    write_json(root / "selection_audit.json", selection_audit)
    for spec in selected:
        write_json(root / f"{spec['id']}.json", spec)
    print(json.dumps({"specs": [{"id": s["id"], "actions": s["held_actions"],
                                  "compositions": s["held_compositions"]} for s in selected]}, indent=2))


if __name__ == "__main__":
    main()
