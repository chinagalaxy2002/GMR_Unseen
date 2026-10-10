#!/usr/bin/env python3
"""Deterministic Semantic-Existence v4 composition pipeline.

All negatives made here are candidates. Only inherited v3 rows retain their
original label and provenance; this package never claims visual verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "data/release/semantic_existence_v3_release"
WORK = ROOT / "data/processed/semantic_existence_v4_comp/work"
RELEASE = ROOT / "data/release/semantic_existence_v4_comp"
SEED = 3407
ALIASES = {"sofa": "couch", "cabinet door": "cabinet_entry"}
ACTION_ALIASES = {"sit_down":"sit"}
STOP = set("a an the person someone somebody they he she it is are was were be being to of in on at by with from into onto out over under and or then while as for their his her this that another some any".split())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict], sort_key="qid") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: tuple(str(r.get(k, "")) for k in (sort_key if isinstance(sort_key, tuple) else (sort_key,))))
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    if not isinstance(value, str):
        return None
    text = re.sub(r"\s+", " ", value.strip().lower())
    if not text or text in {"unknown", "unspecified", "none", "null"}:
        return None
    text=ALIASES.get(text,text)
    # Explicit object subtype closure for the support-surface target concept.
    # Preserve the original surface value in the source event; only the v4 key
    # collapses simple chair modifiers/plurals to the chair concept.
    if re.fullmatch(r"(?:[a-z]+\s+)*chairs?", text) and not re.search(r"\b(?:leg|back|arm)\s+chair\b", text):
        return "chair"
    spaced=text.replace("_", " ")
    if re.search(r"\bcabinet\b.*\bdoors?\b|\bcupboard\b.*\bdoors?\b",text):
        return "cabinet_entry"
    # v4 ontology extension: ordinary door subtypes share a door concept;
    # cabinet entry events and doorways remain distinct.
    if "doorway" not in spaced and re.search(r"\bdoors?\b(?:$|\s+(?:of|to)\b)",spaced):
        return "door"
    return text


def canonical_action(value):
    value=canonical(value)
    return ACTION_ALIASES.get(value,value)


def event_compositions(event: dict) -> list[dict]:
    """Return only explicit action-role-filler relations; never guess direction."""
    action = canonical_action(event.get("action_family"))
    if not action:
        return []
    values = []
    # Explicit source/goal fields take precedence over a generic primary anchor.
    for role in ("source", "goal", "support_surface", "instrument", "theme", "location", "target", "agent"):
        filler = canonical(event.get(role))
        if filler:
            values.append((role, filler, "explicit_role_field"))
    role = canonical(event.get("anchor_role"))
    filler = canonical(event.get("anchor_object"))
    if role and filler:
        values.append((role, filler, "anchor_role_object"))
    # v3's sit representation may store the support only in location.
    if action in {"sit", "sit_down"} and not any(r == "support_surface" for r, _, _ in values):
        surface = canonical(event.get("support_surface") or event.get("location"))
        if surface:
            values.append(("support_surface", surface, "sit_support_normalization"))
    out, seen = [], set()
    for role, filler, evidence in values:
        if role in {"theme", "source", "goal", "support_surface", "instrument", "location", "target", "agent"}:
            key = (action, role, filler)
            if key not in seen:
                out.append({"action_family": action, "role": role, "filler": filler,
                            "composition_key": "|".join(key), "evidence": evidence,
                            "assertion": canonical(event.get("assertion")) or "unspecified"})
                seen.add(key)
    return out


def row_compositions(row: dict) -> list[dict]:
    events = row.get("events")
    if not isinstance(events, list) or not events:
        return []
    out=[comp for event in events if isinstance(event, dict) for comp in event_compositions(event)]
    # v4 parse repair: an explicit sit-on/in-chair phrase establishes a support edge
    # even when the v3 primary projection attached a different nearby location.
    sit_assertions=[canonical(e.get("assertion")) or "unspecified" for e in events if isinstance(e,dict) and canonical_action(e.get("action_family"))=="sit"]
    if sit_assertions and re.search(r"\b(?:sit|sits|sitting|sat)(?:\s+down)?\s+(?:on|in)\s+(?:the\s+|a\s+|an\s+|their\s+)?chair\b",row.get("query",""),re.I):
        out.append({"action_family":"sit","role":"support_surface","filler":"chair",
                    "composition_key":"sit|support_surface|chair","evidence":"v4_explicit_query_relation_repair",
                    "assertion":sit_assertions[0]})
    # v3 sometimes anchors an appliance/room instead of the explicitly named
    # door part. Recover only a direct action-to-door phrase; cabinet/cupboard
    # doors stay under the separate cabinet-entry ontology concept.
    query=row.get("query","")
    if not re.search(r"\b(?:cabinet|cabitnet|cupboard|wardrobe)\b.{0,30}\bdoor\b",query,re.I):
        for action in {canonical_action(e.get("action_family")) for e in events if isinstance(e,dict)}:
            if action not in {"open","close"}: continue
            action_pattern={"open":r"open(?:s|ed|ing)?","close":r"clos(?:e|es|ed|ing)"}[action]
            if re.search(rf"\b{action_pattern}\b(?:\W+\w+){{0,5}}\W+doors?\b",query,re.I):
                assertion=next((canonical(e.get("assertion")) or "unspecified" for e in events
                                if isinstance(e,dict) and canonical_action(e.get("action_family"))==action),"unspecified")
                out.append({"action_family":action,"role":"theme","filler":"door",
                            "composition_key":f"{action}|theme|door","evidence":"v4_explicit_query_door_relation",
                            "assertion":assertion})
    dedup={c["composition_key"]:c for c in out}
    return list(dedup.values())


def row_asserted_hits(row: dict, held_keys: set[str]) -> bool:
    for event in row.get("events",[]) if isinstance(row.get("events"),list) else []:
        for c in event_compositions(event):
            if c["composition_key"] in held_keys and c.get("assertion")=="asserted":
                return True
    if "sit|support_surface|chair" in held_keys and re.search(r"\b(?:sit|sits|sitting|sat)(?:\s+down)?\s+(?:on|in)\s+(?:the\s+|a\s+|an\s+|their\s+)?chair\b",row.get("query",""),re.I):
        return any(isinstance(e,dict) and canonical_action(e.get("action_family"))=="sit" and canonical(e.get("assertion"))=="asserted" for e in row.get("events",[]))
    for key in held_keys:
        action,role,filler=key.split("|",2)
        if role=="theme" and filler=="door" and key in {c["composition_key"] for c in row_compositions(row)}:
            if any(isinstance(e,dict) and canonical_action(e.get("action_family"))==action and canonical(e.get("assertion"))=="asserted" for e in row.get("events",[])):
                return True
    return False


def row_target_assertions(row: dict, held_keys: set[str]) -> set[str]:
    return {c.get("assertion","unspecified") for c in row_compositions(row) if c["composition_key"] in held_keys}


def row_has_unresolved_event(row: dict) -> bool:
    events = row.get("events")
    return not isinstance(events, list) or not events or any(
        not isinstance(event, dict) or not event_compositions(event) for event in events
    )


def row_ambiguous_door_exposure(row: dict, held_keys: set[str]) -> bool:
    """Conservatively quarantine cabinet/cupboard-door scope when holding generic door."""
    query=row.get("query","")
    if not re.search(r"\b(?:cabinet|cabitnet|cupboard|wardrobe)\b.{0,30}\bdoor\b",query,re.I):
        return False
    return any(row_mentions_door_action(query,key.split("|",1)[0]) for key in held_keys if key.endswith("|theme|door"))


def row_mentions_door_action(query: str, action: str) -> bool:
    pattern={"open":r"open(?:s|ed|ing)?","close":r"clos(?:e|es|ed|ing)"}.get(action)
    if not pattern: return False
    if re.search(rf"\b{pattern}\b(?:\W+\w+){{0,5}}\W+doors?\b",query,re.I):
        return True
    # Resultative English such as “pushes the door open” explicitly asserts
    # an opening outcome, but v3 may annotate only the causative push action.
    if action=="open" and re.search(r"\bpush(?:es|ed|ing)?\b(?:\W+\w+){0,3}\W+doors?\b(?:\W+\w+){0,2}\W+open\b",query,re.I):
        return True
    return False


def row_unresolved_door_graph_mismatch(row: dict, held_keys: set[str]) -> bool:
    query=row.get("query","")
    for key in held_keys:
        action,role,filler=key.split("|",2)
        if role=="theme" and filler=="door" and row_mentions_door_action(query,action):
            if key not in {c["composition_key"] for c in row_compositions(row)}:
                return True
    return False


def load_masters():
    positives = read_jsonl(V3 / "master/positive_clean.jsonl")
    negatives = read_jsonl(V3 / "master/negative_clean.jsonl")
    return positives, negatives


def negative_provenance_problems(row: dict, positives_by_qid: dict) -> list[str]:
    source=positives_by_qid.get(row.get("source_qid"))
    problems=[]
    if source is None:
        problems.append("source_qid_not_in_clean_positive_master")
    else:
        if source.get("vid")!=row.get("vid"): problems.append("source_video_mismatch")
        if row.get("source_query") and source.get("query")!=row.get("source_query"): problems.append("source_sentence_mismatch")
        if row.get("source_windows") and source.get("relevant_windows")!=row.get("source_windows"): problems.append("source_windows_mismatch")
    if not row.get("review_decision") or not row.get("verification_status"):
        problems.append("missing_inherited_review_provenance")
    return problems


def reconstruct_assignments():
    by_group = {}
    for group_dir in sorted((V3 / "splits").glob("*_v3")):
        assignment = {}
        for part in ("train", "val", "test"):
            for row in read_jsonl(group_dir / f"{part}.jsonl"):
                vid = row["vid"]
                if vid in assignment and assignment[vid] != part:
                    raise ValueError(f"{group_dir.name}: video {vid} occurs in multiple source partitions")
                assignment[vid] = part
        by_group[group_dir.name] = assignment
    if set(by_group) != {"A1_v3", "A2_v3", "A3_v3", "C1_v3", "C2_v3"}:
        raise ValueError(f"Expected five v3 groups, found {sorted(by_group)}")
    union = {}
    for group, assignment in by_group.items():
        for vid, part in assignment.items():
            if vid in union and union[vid] != part:
                raise ValueError(f"v3 group assignment conflict for {vid}: {union[vid]} vs {part} in {group}")
            union[vid] = part
    # The clean masters independently cover all rows used by v4 and must agree.
    master_assignment = {}
    for row in load_masters()[0] + load_masters()[1]:
        vid, part = row["vid"], row.get("split")
        if part not in {"train", "val", "test"}:
            raise ValueError(f"Missing source split for qid {row.get('qid')}")
        if vid in master_assignment and master_assignment[vid] != part:
            raise ValueError(f"Master assignment conflict for video {vid}")
        master_assignment[vid] = part
        if vid not in union or union[vid] != part:
            raise ValueError(f"Master/video split not reconstructed from v3 groups: {vid}={part}")
    # Some videos are absent from one or more groups because all rows were filtered,
    # but each video's observed assignment is stable across every appearance.
    info = read_json(V3 / "input_inventory.json")
    return union, by_group, {"represented_videos": len(union), "clean_master_videos": len(master_assignment),
                             "source_inventory_video_assignments": info.get("source_video_assignments"),
                             "unrepresented_source_assignments": max(0, int(info.get("source_video_assignments", len(union))) - len(union)),
                             "partition_counts": dict(Counter(union.values())),
                             "per_group_video_counts": {g: len(v) for g, v in by_group.items()}}


def inventory():
    positives, negatives = load_masters()
    assignment, by_group, assign_stats = reconstruct_assignments()
    rows = positives + negatives
    events = []
    row_event_counts = Counter()
    relation_counts = Counter()
    status = Counter()
    for row in rows:
        evs = row.get("events", [])
        row_event_counts[len(evs)] += 1
        if not evs:
            status["missing_event_list"] += 1
        for index, event in enumerate(evs):
            comps = event_compositions(event)
            if not comps:
                status["unresolved_event_representation"] += 1
            relation_counts.update(c["role"] for c in comps)
            events.append({"qid": row["qid"], "vid": row["vid"], "source_split": row["split"],
                           "exist_label": row["exist_label"], "query": row["query"], "event_index": index,
                           "event": event, "compositions": comps})
    write_jsonl(WORK / "audit/event_inventory.jsonl", events, ("qid", "event_index"))
    doc = {"source_release": "semantic_existence_v3_release", "positive_qids": len(positives),
           "negative_qids": len(negatives), "unique_qids": len(rows), "unique_videos_in_clean_masters": len({r['vid'] for r in rows}),
           "event_count": len(events), "multi_event_qids": sum(count for n, count in row_event_counts.items() if n > 1),
           "event_count_distribution": dict(row_event_counts), "composition_role_coverage": dict(relation_counts),
           "events_without_explicit_composition": dict(status), "video_assignment": assign_stats,
           "semantic_graph_policy": "projection only; full events array is authoritative"}
    write_json(WORK / "audit/inventory_summary.json", doc)
    return doc


def profile():
    positives, negatives = load_masters()
    assignment, _, _ = reconstruct_assignments()
    pos_profiles=[]
    for row in positives:
        comps=row_compositions(row)
        pos_profiles.append((row,comps,{c["composition_key"] for c in comps},row_has_unresolved_event(row)))
    test_keys = defaultdict(list)
    train_keys = defaultdict(list)
    for row,comps,keys,unresolved in pos_profiles:
        split=assignment[row["vid"]]
        if unresolved: continue
        if split in {"test","train"}:
            dest=test_keys if split=="test" else train_keys
            for c in comps:
                if split=="test" and row["exist_label"]==1 and not row_asserted_hits(row,{c["composition_key"]}): continue
                dest[c["composition_key"]].append((row,c))
    negatives_by_key = defaultdict(list)
    positive_by_qid={r["qid"]:r for r in positives}
    for row in negatives:
        if negative_provenance_problems(row,positive_by_qid): continue
        if row_has_unresolved_event(row): continue
        for c in row_compositions(row):
            if assignment.get(row["vid"]) == "test":
                negatives_by_key[c["composition_key"]].append((row, c))
    universe = sorted(set(test_keys) | set(train_keys))
    candidates = []
    for key in universe:
        action, role, filler = key.split("|", 2)
        t = test_keys.get(key, [])
        safe_train=[(r,comps) for r,comps,row_keys,unresolved in pos_profiles
                    if assignment[r["vid"]]=="train" and not unresolved and key not in row_keys
                    and not row_ambiguous_door_exposure(r,{key})]
        action_alt=[(r,c) for r,comps in safe_train for c in comps if c["action_family"]==action]
        filler_alt=[(r,c) for r,comps in safe_train for c in comps if c["filler"]==filler]
        role_filler_alt = [(r, c) for r, c in filler_alt if c["role"] == role and c["action_family"] != action]
        action_alternatives = sorted({c["filler"] for _, c in action_alt if c["role"] == role})
        n_videos = len({r["vid"] for r, _ in t})
        leakage_train = len(train_keys.get(key, []))
        action_alt_qids = len({r["qid"] for r, _ in action_alt})
        filler_alt_qids = len({r["qid"] for r, _ in filler_alt})
        strict_eligible = (role in {"theme", "goal", "source", "support_surface", "location", "instrument"} and
                           len(t) >= 50 and n_videos >= 35 and action_alt_qids >= 20 and
                           filler_alt_qids >= 10 and len(action_alternatives) >= 2)
        candidates.append({"composition_key": key, "action_family": action, "role": role, "filler": filler,
                           "test_positive_qids": len({r["qid"] for r, _ in t}), "test_positive_videos": n_videos,
                           "training_positive_action_qids_outside_target": action_alt_qids,
                           "training_positive_filler_qids_outside_target": filler_alt_qids,
                           "training_role_filler_other_action_qids": len({r["qid"] for r, _ in role_filler_alt}),
                           "alternative_action_fillers_same_role": action_alternatives,
                           "exact_training_positive_events": leakage_train,
                           "inherited_test_negative_qids": len({r["qid"] for r, _ in negatives_by_key.get(key, [])}),
                           "inherited_test_negative_videos": len({r["vid"] for r, _ in negatives_by_key.get(key, [])}),
                           "eligible_initial_thresholds": strict_eligible,
                           "eligibility": {"test_positive_at_least_50": len(t) >= 50,
                                           "positive_videos_at_least_35": n_videos >= 35,
                                           "action_constituent_at_least_20": action_alt_qids >= 20,
                                           "filler_constituent_at_least_10": filler_alt_qids >= 10,
                                           "two_alternative_fillers_same_role": len(action_alternatives) >= 2,
                                           "primary_composition_role": role in {"theme", "goal", "source", "support_surface", "location", "instrument"},
                                           "exact_training_exposure_removed_by_builder": leakage_train}})
    candidates.sort(key=lambda c: (-c["eligible_initial_thresholds"], -c["test_positive_qids"], c["composition_key"]))
    write_jsonl(WORK / "selection/composition_candidates.jsonl", candidates, "composition_key")
    summary = {"source": "v3 original positive test rows only", "model_scores_used": False, "seed": SEED,
               "thresholds": {"test_positive_qids": 50, "distinct_test_videos": 35,
                              "training_action_outside_target": 20, "training_filler_outside_target": 10,
                              "alternative_fillers_same_action_role": 2},
               "candidate_count": len(candidates), "eligible_count": sum(c["eligible_initial_thresholds"] for c in candidates),
               "roles_with_test_candidates": dict(Counter(c["role"] for c in candidates if c["test_positive_qids"])),
               "eligible_by_role": dict(Counter(c["role"] for c in candidates if c["eligible_initial_thresholds"])),
               "top_candidates": [c for c in candidates if c["eligible_initial_thresholds"]][:100]}
    write_json(WORK / "selection/coverage_report.json", summary)
    # Select no more than six keys, one per action initially, role/filler variety.
    eligible = [c for c in candidates if c["eligible_initial_thresholds"] and c["inherited_test_negative_qids"] >= 30]
    selected, seen_actions, seen_roles, seen_fillers = [], set(), set(), set()
    for c in eligible:
        if c["action_family"] in seen_actions:
            continue
        selected.append(c); seen_actions.add(c["action_family"]); seen_roles.add(c["role"]); seen_fillers.add(c["filler"])
        if len(selected) == 6:
            break
    for c in eligible:
        if len(selected) >= 6:
            break
        if c["composition_key"] in {s["composition_key"] for s in selected}:
            continue
        if c["role"] not in seen_roles or c["filler"] not in seen_fillers:
            selected.append(c); seen_roles.add(c["role"]); seen_fillers.add(c["filler"])
    selected_keys = {s["composition_key"] for s in selected}
    specs = {"schema_version": 1, "release": "semantic_existence_v4_comp", "seed": SEED,
             "selection_frozen_before_model_evaluation": True, "selection_criteria": summary["thresholds"],
             "primary_negative_support_screen": {"inherited_test_negative_qids_preferred_minimum": 30,
                                                   "selected_group_count": len(selected),
                                                   "roles_allowed": ["theme", "goal", "source", "support_surface", "location", "instrument"]},
             "groups": {"CG%02d_%s" % (i + 1, re.sub(r'[^a-z0-9]+', '_', c['action_family'] + '_' + c['role'] + '_' + c['filler']).strip('_')):
                        {"axis": "action_role_filler_composition", "held_compositions": [c["composition_key"]],
                         "action_family": c["action_family"], "role": c["role"], "filler": c["filler"],
                         "selection_counts": c, "status": "selected"} for i, c in enumerate(selected)},
             "rejected_near_misses": [{**c, "rejection_reason": ("below_initial_coverage_thresholds" if not c["eligible_initial_thresholds"] else
                                 "below_preferred_inherited_negative_support" if c["inherited_test_negative_qids"] < 30 else
                                 "not_selected_under_diversity_and_six_group_cap")}
                                  for c in candidates if c["composition_key"] not in selected_keys]}
    write_json(WORK / "selection/proposed_groups.json", specs)
    return specs


def group_key_set(spec):
    return set(spec["held_compositions"])


def row_hits(row, keys):
    return bool({c["composition_key"] for c in row_compositions(row)} & keys)


def content_words(text):
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    irregular = {"opened":"open", "opening":"open", "opens":"open", "closed":"close", "closing":"close",
                 "closes":"close", "sat":"sit", "sits":"sit", "sitting":"sit", "ran":"run", "runs":"run",
                 "running":"run", "walked":"walk", "walking":"walk", "walks":"walk", "putting":"put",
                 "puts":"put", "placed":"place", "placing":"place", "takes":"take", "taking":"take",
                 "went":"go", "inches":"inch", "leading":"lead", "reopening":"reopen"}
    return {irregular.get(w, re.sub(r"ies$", "y", re.sub(r"s$", "", w))) for w in words if w not in STOP and len(w) > 1}


def numeric_summary(values):
    values=sorted(values)
    if not values: return {"n":0,"min":None,"median":None,"mean":None,"max":None}
    n=len(values)
    med=(values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2)
    return {"n":n,"min":values[0],"median":med,"mean":sum(values)/n,"max":values[-1]}


def assign_row(row, part, status):
    r = dict(row)
    r["partition"] = part
    r["semantic_status"] = status
    r["novelty_type"] = "compositional" if status == "unseen" else "seen"
    r["source_qid"] = r.get("source_qid") or r["qid"]
    return r


def partition_source_rows(rows: list[dict], split: str, held_keys: set[str]):
    """Deterministically derive one video split's labeled rows and quarantine records."""
    kept, removed, unresolved = [], [], []
    for row in sorted(rows, key=lambda r:r["qid"]):
        held = row_hits(row, held_keys)
        if row_ambiguous_door_exposure(row,held_keys):
            (removed if split=="train" else unresolved).append(
                {"qid":row["qid"],"vid":row["vid"],"exist_label":row["exist_label"],"source_split":split,
                 "reason":"ambiguous_cabinet_door_scope_quarantined","matched_keys":[]})
            continue
        if row_unresolved_door_graph_mismatch(row,held_keys):
            (removed if split=="train" else unresolved).append(
                {"qid":row["qid"],"vid":row["vid"],"exist_label":row["exist_label"],"source_split":split,
                 "reason":"held_query_semantics_not_resolved_in_event_graph","matched_keys":[]})
            continue
        if row_has_unresolved_event(row):
            unresolved.append({"qid":row["qid"],"vid":row["vid"],"source_split":split,
                               "reason":"one_or_more_events_without_explicit_action_role_filler"})
            if split=="train":
                removed.append({"qid":row["qid"],"vid":row["vid"],"exist_label":row["exist_label"],
                                "reason":"unresolved_event_semantics_quarantined","matched_keys":[]})
            continue
        if split=="train" and held:
            removed.append({"qid":row["qid"],"vid":row["vid"],"exist_label":row["exist_label"],
                            "reason":"full_event_list_exposes_held_composition",
                            "matched_keys":sorted(held_keys & {c["composition_key"] for c in row_compositions(row)})})
            continue
        target_assertions=row_target_assertions(row,held_keys)
        if held and row["exist_label"]==1 and not row_asserted_hits(row,held_keys):
            unresolved.append({"qid":row["qid"],"vid":row["vid"],"source_split":split,
                               "reason":"held_positive_event_not_explicitly_asserted"})
            continue
        if held and row["exist_label"]==0 and target_assertions & {"purpose","intended","attempted","negated","background"}:
            unresolved.append({"qid":row["qid"],"vid":row["vid"],"source_split":split,
                               "reason":"negative_query_target_event_scope_ambiguous"})
            continue
        quadrant=("U" if held else "S")+("+" if row["exist_label"] else "-")
        kept.append(assign_row(row,quadrant,"unseen" if held else "seen"))
    return kept,removed,unresolved


def build_splits(specs=None):
    specs = specs or read_json(WORK / "selection/proposed_groups.json")
    positives, negatives = load_masters()
    assignment, _, _ = reconstruct_assignments()
    source_by_qid = {r["qid"]: r for r in positives + negatives}
    positive_by_qid = {r["qid"]: r for r in positives}
    ineligible_negatives = []
    eligible_negatives = []
    for row in negatives:
        source = positive_by_qid.get(row.get("source_qid"))
        problems = []
        if source is None:
            problems.append("source_qid_not_in_clean_positive_master")
        else:
            if source.get("vid") != row.get("vid"):
                problems.append("source_video_mismatch")
            if row.get("source_query") and source.get("query") != row.get("source_query"):
                problems.append("source_sentence_mismatch")
            if row.get("source_windows") and source.get("relevant_windows") != row.get("source_windows"):
                problems.append("source_windows_mismatch")
        if not row.get("review_decision") or not row.get("verification_status"):
            problems.append("missing_inherited_review_provenance")
        if problems:
            ineligible_negatives.append({"qid":row["qid"],"source_qid":row.get("source_qid"),"vid":row.get("vid"),"problems":problems})
        else:
            eligible_negatives.append(row)
    write_jsonl(WORK / "audit/ineligible_inherited_negatives.jsonl", ineligible_negatives)
    for group, spec in specs["groups"].items():
        keys = group_key_set(spec)
        splits = {p: [] for p in ("train", "val", "test")}
        removed = []
        unresolved = []
        source_rows=positives+eligible_negatives
        for split in ("train","val","test"):
            these=[row for row in source_rows if assignment[row["vid"]]==split]
            kept,excluded,unknown=partition_source_rows(these,split,keys)
            splits[split].extend(kept); removed.extend(excluded); unresolved.extend(unknown)
        out = WORK / "splits" / group
        for part, rows in splits.items():
            write_jsonl(out / f"{part}.jsonl", rows)
        write_jsonl(out / "val_seen.jsonl", [r for r in splits["val"] if r["partition"].startswith("S")])
        write_jsonl(out / "val_unseen_diagnostic.jsonl", [r for r in splits["val"] if r["partition"].startswith("U")])
        write_jsonl(out / "train_exclusions.jsonl", removed)
        unresolved_rows=[]
        source_lookup={r["qid"]:r for r in positives+eligible_negatives}
        for item in unresolved:
            original=dict(source_lookup[item["qid"]])
            original.update({"partition":"UNRESOLVED","semantic_status":"unresolved","novelty_type":"unresolved",
                             "unresolved_reason":item["reason"]})
            unresolved_rows.append(original)
        full_views={r["qid"]:r for r in splits["val"]+[r for r in unresolved_rows if r["split"]=="val"]}
        for row in positives+negatives:
            if assignment[row["vid"]] in {"val","test"} and row["qid"] not in full_views and (row["exist_label"]==0 and row not in eligible_negatives):
                quarantined=dict(row); quarantined.update({"partition":"QUARANTINED","semantic_status":"unresolved",
                    "novelty_type":"unresolved","unresolved_reason":"ineligible_inherited_negative_provenance"})
                if assignment[row["vid"]]=="val": full_views[row["qid"]]=quarantined
                else: unresolved_rows.append(quarantined)
        write_jsonl(out / "unresolved_semantics.jsonl", unresolved_rows)
        write_jsonl(out / "val_full.jsonl", list(full_views.values()))
        write_jsonl(out / "test_unresolved.jsonl", [r for r in unresolved_rows if r["split"]=="test"])
        held_key=sorted(keys)[0]
        matched_pairs=inherited_matched_pairs(splits["test"],"test",held_key)
        matched_qids={qid for pair in matched_pairs for qid in (pair["positive_qid"],pair["negative_qid"])}
        write_jsonl(out / "matched_u_pairs.jsonl", matched_pairs, "pair_id")
        write_jsonl(out / "test_matched_u.jsonl", [r for r in splits["test"] if r["qid"] in matched_qids])
        trainpos = [r for r in splits["train"] if r["exist_label"] == 1]
        train_vocab = set().union(*(content_words(r["query"]) for r in splits["train"])) if splits["train"] else set()
        lex = {}
        for part in ("val", "test"):
            for q in ("U+", "U-"):
                rows = [r for r in splits[part] if r["partition"] == q]
                all_seen, violations = [], []
                for r in rows:
                    missing = sorted(content_words(r["query"]) - train_vocab)
                    if not missing: all_seen.append(r["qid"])
                    else: violations.append({"qid": r["qid"], "missing_content_lemmas": missing})
                lex[f"{part}_{q}"] = {"n": len(rows), "strict_lexical_seen_n": len(all_seen),
                                      "strict_lexical_seen_pct": (100 * len(all_seen) / len(rows) if rows else None),
                                      "violations": violations}
        lexical_test_rows=[r for r in splits["test"] if content_words(r["query"]).issubset(train_vocab)]
        write_jsonl(out / "test_lexical_seen.jsonl", lexical_test_rows)
        write_jsonl(out / "test_lexical_seen_u.jsonl", [r for r in lexical_test_rows if r["partition"].startswith("U")])
        target_removed=[x for x in removed if x["reason"]=="full_event_list_exposes_held_composition"]
        unresolved_removed=[x for x in removed if x["reason"] in {"unresolved_event_semantics_quarantined","ambiguous_cabinet_door_scope_quarantined","held_query_semantics_not_resolved_in_event_graph"}]
        stats = {"group": group, "held_compositions": sorted(keys), "counts": {p: dict(Counter(r["partition"] for r in rows)) for p, rows in splits.items()},
                 "rows": {p: len(rows) for p, rows in splits.items()},
                 "videos": {p: len({r["vid"] for r in rows}) for p, rows in splits.items()},
                 "train_excluded_qids": len(removed), "train_excluded_positive": sum(x["exist_label"] == 1 for x in target_removed),
                 "train_excluded_negative": sum(x["exist_label"] == 0 for x in target_removed),
                 "train_target_excluded_qids": len(target_removed),
                 "train_ambiguous_door_scope_quarantined_qids": sum(x["reason"]=="ambiguous_cabinet_door_scope_quarantined" for x in removed),
                 "train_query_graph_mismatch_quarantined_qids": sum(x["reason"]=="held_query_semantics_not_resolved_in_event_graph" for x in removed),
                 "train_unresolved_quarantined_qids": len(unresolved_removed),
                 "unresolved_rows_quarantined": len(unresolved),
                 "unresolved_train_rows_quarantined": sum(x["source_split"] == "train" for x in unresolved),
                 "ineligible_inherited_negatives_excluded": len(ineligible_negatives),
                 "lexical_coverage": lex, "matched_inherited_pairs": len(matched_pairs),
                 "negative_provenance": "inherited v3 rows retain original review metadata; no video review is claimed"}
        exclusion_reasons=defaultdict(list)
        for item in removed: exclusion_reasons[item["reason"]].append(item)
        stats["train_exclusions_by_reason"]={reason:{"qids":len(items),"positive_qids":sum(x["exist_label"]==1 for x in items),
                                                        "negative_qids":sum(x["exist_label"]==0 for x in items)}
                                              for reason,items in sorted(exclusion_reasons.items())}
        stats["condition_videos"] = {part:{q:len({r["vid"] for r in rows if r["partition"]==q})
                                            for q in ("S+","S-","U+","U-")} for part,rows in splits.items()}
        stats["condition_qids"] = {part:{q:sum(r["partition"]==q for r in rows)
                                          for q in ("S+","S-","U+","U-")} for part,rows in splits.items()}
        stats["query_word_length"] = {part:{label:numeric_summary([len(r["query"].split()) for r in rows if r["exist_label"]==label])
                                             for label in (1,0)} for part,rows in splits.items()}
        stats["positive_window_duration_seconds"] = {part:numeric_summary([b-a for r in rows if r["exist_label"] for a,b in r["relevant_windows"]])
                                                       for part,rows in splits.items()}
        for part,rows in splits.items():
            comp_counts=Counter(c["composition_key"] for r in rows for c in row_compositions(r))
            action_counts=Counter(c["action_family"] for r in rows for c in row_compositions(r))
            filler_counts=Counter(c["filler"] for r in rows for c in row_compositions(r))
            video_counts=Counter(r["vid"] for r in rows)
            stats.setdefault("distributions",{})[part]={"top_compositions":comp_counts.most_common(20),
                "top_actions":action_counts.most_common(20),"top_fillers":filler_counts.most_common(20),
                "top_video_query_counts":video_counts.most_common(10),
                "max_queries_per_video":max(video_counts.values(),default=0),
                "positive_negative_mean_word_length_difference":(stats["query_word_length"][part][1]["mean"]-stats["query_word_length"][part][0]["mean"])
                    if stats["query_word_length"][part][1]["mean"] is not None and stats["query_word_length"][part][0]["mean"] is not None else None,
                "original_annotation_rows":len(rows),"generated_annotation_rows":0}
        write_json(out / "statistics.json", stats)
        write_json(out / "split_spec_provenance.json", {"seed": SEED, "spec": spec, "source_release": str(V3.relative_to(ROOT)),
                    "assignment_source": "union of the five v3 split files, checked against clean masters",
                    "excluded_training_rows": len(removed), "selection_frozen_before_model_evaluation": True})
        write_json(out / "semantic_inventory.json", {"group": group, "held_compositions": sorted(keys),
                    "action_constituent_training_examples": sum(1 for r in trainpos for c in row_compositions(r) if c['action_family'] == spec['action_family'] and c['composition_key'] not in keys),
                    "filler_constituent_training_examples": sum(1 for r in trainpos for c in row_compositions(r) if c['filler'] == spec['filler'] and c['composition_key'] not in keys),
                    "roles": [spec["role"]], "event_parsing_coverage": "v3 supplied event lists; incomplete/missing roles remain unresolved"})
        # Retain source references and detect missing qids instead of silently dropping them.
        for r in splits["train"] + splits["val"] + splits["test"]:
            if r["qid"] not in source_by_qid:
                raise ValueError(f"source qid is absent from clean master: {r['qid']}")
    return specs


def tfidf_similarity(a: str, b: str) -> float:
    """Small deterministic cosine surrogate; it is not CLIP similarity."""
    ta, tb = Counter(content_words(a)), Counter(content_words(b))
    if not ta or not tb:
        return 0.0
    vocab = ta.keys() | tb.keys()
    na = math.sqrt(sum(ta[x] ** 2 for x in vocab)); nb = math.sqrt(sum(tb[x] ** 2 for x in vocab))
    return sum(ta[x] * tb[x] for x in vocab) / (na * nb) if na and nb else 0.0


def candidate_id(strategy, group, source_qid, target_vid, candidate_query):
    raw = "|".join((strategy, group, source_qid, target_vid, candidate_query))
    return "cand_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def valid_reassignment(source_row: dict, target_video: dict, target_annotations: list[dict], target_key: str) -> tuple[bool, str]:
    """Check a source-positive to target-video reassignment without asserting absence."""
    if source_row.get("split") != target_video.get("split"):
        return False, "cross_split_reassignment"
    if source_row.get("vid") == target_video.get("vid"):
        return False, "identical_source_target_video"
    if target_key not in {c["composition_key"] for c in row_compositions(source_row)}:
        return False, "source_does_not_express_target_composition"
    if any(target_key in {c["composition_key"] for c in row_compositions(r)} for r in target_annotations):
        return False, "known_positive_annotation_conflict"
    return True, "candidate_only_absence_unverified"


def valid_matched_pair(pair: dict, rows_by_qid: dict) -> tuple[bool, str]:
    pos = rows_by_qid.get(pair.get("positive_qid"))
    neg = rows_by_qid.get(pair.get("negative_qid"))
    if pos is None or neg is None:
        return False, "missing_pair_qid_reference"
    if pos.get("exist_label") != 1 or neg.get("exist_label") != 0:
        return False, "incorrect_pair_labels"
    if pos.get("vid") != neg.get("vid"):
        return False, "pair_video_mismatch"
    if pos.get("split") != neg.get("split"):
        return False, "pair_split_mismatch"
    if pair.get("target_composition") and pair["target_composition"] not in {c["composition_key"] for c in row_compositions(pos)}:
        return False, "positive_does_not_express_pair_composition"
    if pair.get("target_composition") and pair["target_composition"] not in {c["composition_key"] for c in row_compositions(neg)}:
        return False, "negative_does_not_express_pair_composition"
    return True, "valid_same_video_pair"


def inherited_matched_pairs(rows: list[dict], split: str, held_key: str) -> list[dict]:
    """Pair original same-video U+/U- rows only when both annotations express the key."""
    by_video=defaultdict(lambda:{"U+":[],"U-":[]})
    for row in rows:
        if row.get("partition") in {"U+","U-"} and held_key in {c["composition_key"] for c in row_compositions(row)}:
            by_video[row["vid"]][row["partition"]].append(row)
    pairs=[]
    for vid,classes in sorted(by_video.items()):
        positives=sorted(classes["U+"],key=lambda r:r["qid"])
        negatives=sorted(classes["U-"],key=lambda r:r["qid"])
        for pos,neg in zip(positives,negatives):
            pair_id="pair_"+hashlib.sha256(f"{split}|{held_key}|{pos['qid']}|{neg['qid']}".encode()).hexdigest()[:16]
            pairs.append({"pair_id":pair_id,"positive_qid":pos["qid"],"negative_qid":neg["qid"],
                          "vid":vid,"split":split,"target_composition":held_key,
                          "generation_strategy":"inherited_v3_same_video_annotations",
                          "video_absence_verified":False,"provenance":"both labels inherited from v3"})
    return pairs


def generate_negatives(specs=None):
    specs = specs or read_json(WORK / "selection/proposed_groups.json")
    positives, negatives = load_masters()
    assignment, _, _ = reconstruct_assignments()
    by_vid = defaultdict(list)
    for r in positives: by_vid[r["vid"]].append(r)
    for group, spec in specs["groups"].items():
        keys = group_key_set(spec)
        test_positives = [r for r in positives if assignment[r["vid"]] == "test" and row_hits(r, keys)
                          and row_asserted_hits(r, keys) and not row_has_unresolved_event(r)]
        positives_test_by_vid = {vid: sorted(rows, key=lambda x: x["qid"]) for vid, rows in by_vid.items() if assignment.get(vid) == "test"}
        rows, review = [], []
        target_usage = {"conservative_in_domain_reassignment": Counter(), "hard_in_domain_reassignment": Counter()}
        for source in sorted(test_positives, key=lambda r: r["qid"]):
            key = sorted(keys & {c["composition_key"] for c in row_compositions(source)})[0]
            possible = []
            for target_vid, target_rows in positives_test_by_vid.items():
                target_stub = {"vid": target_vid, "split": "test"}
                ok, reason = valid_reassignment(source, target_stub, target_rows, key)
                if not ok:
                    continue
                # Require the same group key in source; this preserves the target exactly.
                sim = max((tfidf_similarity(source["query"], t["query"]) for t in target_rows), default=0.0)
                overlap = max((len(content_words(source["query"]) & content_words(t["query"]))
                               for t in target_rows), default=0)
                possible.append((sim, -overlap, target_vid, target_rows))
            if len(possible) < 2:
                continue
            possible.sort(key=lambda x: (x[0], x[1], x[2]))
            low_count = max(1, math.ceil(len(possible) * 0.25))
            low_pool = possible[:low_count]
            min_low_use = min(target_usage["conservative_in_domain_reassignment"][x[2]] for x in low_pool)
            low_balanced = [x for x in low_pool if target_usage["conservative_in_domain_reassignment"][x[2]] == min_low_use]
            conservative = min(low_balanced, key=lambda x: hashlib.sha256(f"{source['qid']}|{x[2]}".encode()).hexdigest())
            hard_pool = sorted(possible, key=lambda x: (x[1], -x[0], x[2]))[:low_count]
            max_hard_use = min(target_usage["hard_in_domain_reassignment"][x[2]] for x in hard_pool)
            hard_balanced = [x for x in hard_pool if target_usage["hard_in_domain_reassignment"][x[2]] == max_hard_use]
            hard = min(hard_balanced, key=lambda x: (-x[0], hashlib.sha256(f"{source['qid']}|{x[2]}".encode()).hexdigest()))
            strata = {"conservative_in_domain_reassignment": conservative,
                      "hard_in_domain_reassignment": hard}
            for strategy, (sim, neg_overlap, target_vid, target_rows) in strata.items():
                target_usage[strategy][target_vid] += 1
                qid = candidate_id(strategy, group, source["qid"], target_vid, source["query"])
                conflict = any(key in {c["composition_key"] for c in row_compositions(t)} for t in target_rows)
                cand = {"qid": qid, "vid": target_vid, "target_video": target_vid, "source_video": source["vid"],
                        "source_qid": source["qid"], "original_qid": source["qid"], "original_sentence": source["query"],
                        "query": source["query"], "candidate_sentence": source["query"], "duration": target_rows[0]["duration"],
                        "relevant_windows": [], "exist_label": 0, "partition": "candidate_U-", "semantic_status": "unseen",
                        "novelty_type": "compositional", "semantic_graph": source.get("semantic_graph", {}),
                        "events": source.get("events", []), "target_composition": key, "generation_strategy": strategy,
                        "changed_components": [], "semantic_review_result": "pending_independent_review",
                        "conflict_check_result": "pass_annotation_nonmatch" if not conflict else "conflict",
                        "evidence_limitations": "No raw video; no visual absence verification. Token cosine is a text-only surrogate, not CLIP.",
                        "similarity_method": "token_cosine_surrogate", "similarity_score": round(sim, 8),
                        "component_overlap": -neg_overlap, "source_split": "test", "target_split": "test",
                        "construction_type": "unverified_negative_candidate"}
                if conflict:
                    cand["conflict_check_result"] = "reject_same_video_positive_annotation"
                rows.append(cand)
                review.append({"candidate_qid": qid, "decision": "quarantine", "reviewer": "independent_pipeline_audit",
                               "reason": "Text annotations can reject direct conflicts but cannot establish absence without video evidence.",
                               "video_absence_verified": False})
        # Cross-video reassignment has no source-positive/target-negative matched pair by design.
        out = WORK / "negatives" / group
        write_jsonl(out / "reassignment_candidates.jsonl", rows)
        write_jsonl(out / "review_queue.jsonl", review)
        write_jsonl(out / "matched_candidate_pairs.jsonl", [])
        # Conservative, deterministic counterfactual candidate: only use an explicit alternative
        # filler already attached to the same action+role in real positives; never call it gold.
        cf = []
        training_context = defaultdict(set)
        for r in positives:
            if assignment[r["vid"]] != "train": continue
            for c in row_compositions(r): training_context[(c["action_family"], c["role"])].add(c["filler"])
        for source in sorted(test_positives, key=lambda r: r["qid"]):
            comps = [c for c in row_compositions(source) if c["composition_key"] in keys]
            if not comps: continue
            c = comps[0]
            alternatives = sorted(training_context[(c["action_family"], c["role"])] - {c["filler"]})
            if not alternatives: continue
            # We cannot safely edit the sentence without a parser-backed role span; preserve as review-needed.
            cf.append({"source_qid": source["qid"], "source_video": source["vid"], "target_video": source["vid"],
                       "original_sentence": source["query"], "candidate_sentence": None,
                       "target_composition": c["composition_key"], "generation_strategy": "structure_preserving_counterfactual",
                       "allowed_alternative_fillers_seen_in_train": alternatives,
                       "changed_components": [], "semantic_review_result": "not_generated_role_span_required",
                       "conflict_check_result": "not_run", "evidence_limitations": "No counterfactual text fabricated: v3 events do not provide sentence spans for role-safe edits.",
                       "status": "no_candidate_generated"})
        write_jsonl(out / "counterfactual_candidates.jsonl", cf)
    return


def import_reviews(review_path: Path):
    # Review import accepts structured audit decisions but cannot promote to absence label.
    records = read_jsonl(review_path)
    valid = {"accept_candidate", "quarantine", "reject"}
    if any(r.get("decision") not in valid for r in records):
        raise ValueError("Review decisions must be accept_candidate, quarantine, or reject")
    out = WORK / "audit/independent_review.jsonl"
    write_jsonl(out, records, "candidate_qid")
    decisions={r["candidate_qid"]:r["decision"] for r in records}
    for candidate_path in sorted((WORK/"negatives").glob("*/reassignment_candidates.jsonl")):
        candidates=read_jsonl(candidate_path)
        for row in candidates:
            if row["qid"] in decisions:
                row["semantic_review_result"]=decisions[row["qid"]]
        write_jsonl(candidate_path,candidates)
    return out


def export_review_queue():
    records=[]
    for cand_path in sorted((WORK/"negatives").glob("*/reassignment_candidates.jsonl")):
        group=cand_path.parent.name
        for r in read_jsonl(cand_path):
            records.append({"candidate_qid":r["qid"],"group":group,"source_qid":r["source_qid"],
                "source_video":r["source_video"],"target_video":r["target_video"],
                "original_sentence":r["original_sentence"],"candidate_sentence":r["candidate_sentence"],
                "target_composition":r["target_composition"],"generation_strategy":r["generation_strategy"],
                "candidate_events":r.get("events",[]),"annotation_conflict_check":r["conflict_check_result"],
                "similarity_method":r["similarity_method"],"similarity_score":r["similarity_score"],
                "video_absence_verified":False,"decision":"","reviewer":"","reason":""})
    out=WORK/"audit/candidate_review_template.jsonl"
    write_jsonl(out,records,"candidate_qid")
    return out


def validate_group(group_dir: Path, spec: dict, assignment: dict, source_by_qid: dict):
    errors = []
    splits = {p: read_jsonl(group_dir / f"{p}.jsonl") for p in ("train", "val", "test")}
    ids, videos = {}, {}
    keys = group_key_set(spec)
    for part, rows in splits.items():
        videos[part] = set()
        qids = set()
        if rows != sorted(rows, key=lambda r: r.get("qid", "")):
            errors.append(f"nondeterministic row order in {part}")
        for r in rows:
            qid = r.get("qid"); vid = r.get("vid")
            if qid in qids: errors.append(f"duplicate qid in {part}: {qid}")
            qids.add(qid)
            fingerprint = json.dumps({k:r.get(k) for k in ("vid","query","relevant_windows","exist_label")}, sort_keys=True)
            if qid in ids and ids[qid] != fingerprint: errors.append(f"conflicting duplicate qid: {qid}")
            ids[qid] = fingerprint
            if qid not in source_by_qid: errors.append(f"missing source qid: {qid}")
            elif r.get("source_qid") not in source_by_qid:
                errors.append(f"missing source_qid reference: {qid}->{r.get('source_qid')}")
            elif any(r.get(k) != source_by_qid[qid].get(k) for k in ("vid", "query", "duration", "relevant_windows", "exist_label")):
                errors.append(f"source annotation content changed: {qid}")
            if vid not in assignment or assignment[vid] != part: errors.append(f"source split mismatch: {qid}/{vid}/{part}")
            videos[part].add(vid)
            windows = r.get("relevant_windows", [])
            if r["exist_label"] and (not windows or any(len(w)!=2 or w[0] < 0 or w[1] <= w[0] or w[1] > r["duration"] + 1e-4 for w in windows)):
                errors.append(f"invalid positive windows: {qid}")
            if not r["exist_label"] and windows: errors.append(f"negative has windows: {qid}")
            if r["partition"] != (("U" if row_hits(r, keys) else "S") + ("+" if r["exist_label"] else "-")):
                errors.append(f"incorrect quadrant: {qid}")
            if part == "train" and row_hits(r, keys): errors.append(f"held composition train exposure: {qid}")
            if part == "train" and r["partition"] not in {"S+","S-"}: errors.append(f"unseen train label: {qid}")
            if not r.get("source_qid"): errors.append(f"missing provenance: {qid}")
    for a,b in (("train","val"),("train","test"),("val","test")):
        if videos[a] & videos[b]: errors.append(f"video overlap {a}/{b}")
    seen = read_jsonl(group_dir / "val_seen.jsonl")
    if seen != [r for r in splits["val"] if r["partition"].startswith("S")]: errors.append("val_seen mismatch")
    # Full-list leakage and constituent exposure.
    tr = [r for r in splits["train"] if r["exist_label"]]
    if not any(any(c["action_family"] == spec["action_family"] and c["composition_key"] not in keys for c in row_compositions(r)) for r in tr):
        errors.append("held action constituent missing from train")
    if not any(any(c["filler"] == spec["filler"] and c["composition_key"] not in keys for c in row_compositions(r)) for r in tr):
        errors.append("held filler constituent missing from train")
    pair_path = group_dir / "matched_u_pairs.jsonl"
    pairs = read_jsonl(pair_path)
    pair_rows = {r["qid"]: r for rows in splits.values() for r in rows}
    for pair in pairs:
        valid, reason = valid_matched_pair(pair, pair_rows)
        if not valid: errors.append(f"invalid matched pair {pair.get('pair_id')}: {reason}")
    matched_rows=read_jsonl(group_dir/"test_matched_u.jsonl")
    expected_matched={qid for pair in pairs for qid in (pair.get("positive_qid"),pair.get("negative_qid"))}
    if {r.get("qid") for r in matched_rows}!=expected_matched:
        errors.append("test_matched_u qids do not match pair references")
    return errors, {p: dict(Counter(r["partition"] for r in rows)) for p, rows in splits.items()}, {p:len(v) for p,v in videos.items()}


def validate_release():
    specs = read_json(RELEASE / "selection/proposed_groups.json")
    assignment, by_group, assignment_stats = reconstruct_assignments()
    positives, negatives = load_masters()
    source_by_qid = {r["qid"]:r for r in positives + negatives}
    errors = []
    source_qids=[r["qid"] for r in positives+negatives]
    if len(source_qids)!=len(set(source_qids)): errors.append("duplicate qids in source masters")
    if specs.get("selection_frozen_before_model_evaluation") is not True or not specs.get("groups"):
        errors.append("split specifications are missing or not marked frozen")
    if specs.get("seed") != SEED:
        errors.append(f"unexpected or missing frozen selection seed: {specs.get('seed')}")
    if not (RELEASE/"selection/split_specs.json").exists() or read_json(RELEASE/"selection/split_specs.json") != specs:
        errors.append("frozen split specifications are missing or differ from selected specifications")
    held_keys=[key for spec in specs.get("groups",{}).values() for key in spec.get("held_compositions",[])]
    if len(held_keys)!=len(set(held_keys)): errors.append("held composition keys overlap across frozen groups")
    all_candidate_ids=set()
    for group in specs.get("groups",{}):
        candidate_path=RELEASE/"negative_candidates"/group/"reassignment_candidates.jsonl"
        if candidate_path.exists():
            all_candidate_ids.update(r.get("qid") for r in read_jsonl(candidate_path))
    audit_path=RELEASE/"audit/independent_review.jsonl"
    if audit_path.exists():
        audit_ids=[r.get("candidate_qid") for r in read_jsonl(audit_path)]
        if len(audit_ids)!=len(set(audit_ids)): errors.append("duplicate independent audit candidate records")
        if set(audit_ids)!=all_candidate_ids: errors.append("independent audit qids differ from candidate qids")
    groups = {}
    for group,spec in specs["groups"].items():
        gd=RELEASE/"splits"/group
        e,c,v=validate_group(gd,spec,assignment,source_by_qid)
        errors.extend(f"{group}: {x}" for x in e)
        groups[group]={"errors":e,"counts":c,"videos":v}
        gd=RELEASE/"splits"/group
        full_val=read_jsonl(gd/"val_full.jsonl")
        expected_val={r["qid"] for r in positives+negatives if assignment[r["vid"]]=="val"}
        if {r.get("qid") for r in full_val} != expected_val:
            errors.append(f"{group}: val_full does not conserve all original validation qids")
        unresolved_test=read_jsonl(gd/"test_unresolved.jsonl")
        labeled_test={r["qid"] for r in read_jsonl(gd/"test.jsonl")}
        expected_unresolved_test={r["qid"] for r in positives+negatives if assignment[r["vid"]]=="test" and r["qid"] not in labeled_test}
        if {r.get("qid") for r in unresolved_test} != expected_unresolved_test:
            errors.append(f"{group}: test_unresolved does not conserve excluded original test qids")
        train_rows=read_jsonl(gd/"train.jsonl")
        train_exclusions=read_jsonl(gd/"train_exclusions.jsonl")
        unresolved_rows=read_jsonl(gd/"unresolved_semantics.jsonl")
        ineligible_path=RELEASE/"audit/ineligible_inherited_negatives.jsonl"
        ineligible={r["qid"] for r in read_jsonl(ineligible_path)} if ineligible_path.exists() else set()
        train_dispositions={r["qid"] for r in train_rows}|{r["qid"] for r in train_exclusions}
        train_dispositions|={r["qid"] for r in unresolved_rows if r.get("source_split")=="train" or r.get("split")=="train"}
        train_dispositions|={r["qid"] for r in positives+negatives if r["split"]=="train" and r["qid"] in ineligible}
        expected_train={r["qid"] for r in positives+negatives if r["split"]=="train"}
        if train_dispositions != expected_train:
            errors.append(f"{group}: training qid disposition does not conserve all original train rows")
        source_rows={r["qid"]:r for r in positives+negatives}
        for r in full_val:
            src=source_rows.get(r.get("qid"))
            if src is None or any(r.get(k)!=src.get(k) for k in ("vid","query","duration","relevant_windows","exist_label")):
                errors.append(f"{group}: val_full changed/missing original source content for {r.get('qid')}")
        candidates=read_jsonl(RELEASE/"negative_candidates"/group/"reassignment_candidates.jsonl")
        candidate_ids=[r.get("qid") for r in candidates]
        if len(candidate_ids)!=len(set(candidate_ids)):
            errors.append(f"{group}: duplicate candidate qids")
        for r in candidates:
            if r.get("construction_type") != "unverified_negative_candidate": errors.append(f"candidate mislabeled verified: {r.get('qid')}")
            if r.get("source_split") != r.get("target_split"): errors.append(f"cross-split reassignment: {r.get('qid')}")
            if r.get("relevant_windows"): errors.append(f"candidate has fabricated windows: {r.get('qid')}")
            if r.get("source_qid") not in source_by_qid: errors.append(f"candidate source qid missing: {r.get('qid')}")
            if r.get("target_video") != r.get("vid"): errors.append(f"candidate target video mismatch: {r.get('qid')}")
            src=source_by_qid.get(r.get("source_qid"))
            if src and (src.get("vid")!=r.get("source_video") or src.get("query")!=r.get("original_sentence")):
                errors.append(f"candidate source provenance mismatch: {r.get('qid')}")
            if src and (r.get("query")!=src.get("query") or r.get("events")!=src.get("events")):
                errors.append(f"candidate sentence/event provenance mismatch: {r.get('qid')}")
            if assignment.get(r.get("target_video"))!=r.get("target_split") or assignment.get(r.get("source_video"))!=r.get("source_split"):
                errors.append(f"candidate video assignment mismatch: {r.get('qid')}")
            if r.get("source_split") != "test" or r.get("target_split") != "test":
                errors.append(f"candidate reassignment is not test-to-test: {r.get('qid')}")
            held=r.get("target_composition")
            if held not in group_key_set(spec):
                errors.append(f"candidate composition does not match frozen group: {r.get('qid')}")
            if held not in {c["composition_key"] for c in row_compositions(r)}:
                errors.append(f"candidate changed held composition: {r.get('qid')}")
            if r.get("semantic_review_result") not in {"pending_independent_review", "accept_candidate", "quarantine", "reject"}:
                errors.append(f"candidate missing audit status: {r.get('qid')}")
        audit_path=RELEASE/"audit/independent_review.jsonl"
        if audit_path.exists():
            audit_records=read_jsonl(audit_path)
            reviewed={r.get("candidate_qid") for r in audit_records}
            missing={r.get("qid") for r in candidates}-reviewed
            if missing: errors.append(f"{len(missing)} candidates missing independent review records in {group}")
            by_candidate={r.get("candidate_qid"):r for r in audit_records}
            for r in candidates:
                review=by_candidate.get(r["qid"])
                if review and r.get("semantic_review_result")!=review.get("decision"):
                    errors.append(f"candidate semantic review status mismatch: {r['qid']}")
    # Source release regression check: hash inventory created before any processing.
    input_hashes=read_json(RELEASE/"input_inventory.json")["sha256"]
    for rel, expected in input_hashes.items():
        if digest(ROOT/rel) != expected: errors.append(f"v3 input changed since inventory: {rel}")
    stage1=read_json(RELEASE/"audit/data_inventory.json").get("source_hashes_sha256",{})
    stage1_paths={"positive_clean.jsonl":V3/"master/positive_clean.jsonl",
                  "negative_clean.jsonl":V3/"master/negative_clean.jsonl",
                  "rules.json":V3/"ontology/rules.json",
                  "split_specs.json":V3/"selection/split_specs.json"}
    for name,expected in stage1.items():
        path=stage1_paths.get(name)
        if path is None or digest(path)!=expected:
            errors.append(f"v3 Stage-1 regression hash mismatch: {name}")
    manifest=read_json(RELEASE/"manifest.json")
    for rel, expected in manifest.get("sha256",{}).items():
        if digest(RELEASE/rel) != expected: errors.append(f"release hash mismatch: {rel}")
    gates={"video_disjointness":"PASS" if not any("video overlap" in x for x in errors) else "FAIL",
           "source_annotation_preservation":"PASS" if not any("source annotation content changed" in x for x in errors) else "FAIL",
           "train_qid_conservation":"PASS" if not any("training qid disposition" in x for x in errors) else "FAIL",
           "validation_view_conservation":"PASS" if not any("val_full does not conserve" in x for x in errors) else "FAIL",
           "full_event_train_leakage":"PASS" if not any("held composition train exposure" in x for x in errors) else "FAIL",
           "ambiguous_scope_quarantine":"PASS" if not any("ambiguous_cabinet_door_scope_quarantined" in x for x in errors) else "FAIL",
           "quadrant_assignment":"PASS" if not any("incorrect quadrant" in x for x in errors) else "FAIL",
           "positive_timestamp_validity":"PASS" if not any("invalid positive windows" in x for x in errors) else "FAIL",
           "negative_window_emptiness":"PASS" if not any("negative has windows" in x for x in errors) else "FAIL",
           "source_and_candidate_provenance":"PASS" if not any("source_qid" in x or "source_video" in x for x in errors) else "FAIL",
           "frozen_group_candidate_identity":"PASS" if not any("candidate composition does not match frozen group" in x or "candidate changed held composition" in x for x in errors) else "FAIL",
           "cross_split_reassignment":"PASS" if not any("cross-split reassignment" in x or "video assignment mismatch" in x for x in errors) else "FAIL",
           "independent_audit_completeness":"PASS" if not any("independent review" in x or "audit records" in x or "audit qids" in x for x in errors) else "FAIL",
           "candidate_not_promoted_to_gold":"PASS" if not any("candidate mislabeled verified" in x for x in errors) else "FAIL",
           "matched_pair_integrity":"PASS" if not any("invalid matched pair" in x for x in errors) else "FAIL",
           "split_order_determinism":"PASS" if not any("nondeterministic row order" in x for x in errors) else "FAIL",
           "frozen_specification_integrity":"PASS" if not any("split specifications" in x or "frozen selection seed" in x for x in errors) else "FAIL",
           "source_input_hashes":"PASS" if not any("v3 input changed" in x for x in errors) else "FAIL",
           "v3_stage1_regression_hashes":"PASS" if not any("Stage-1 regression hash mismatch" in x for x in errors) else "FAIL",
           "release_hashes":"PASS" if not any("release hash mismatch" in x for x in errors) else "FAIL"}
    report={"status":"PASS" if not errors else "FAIL", "errors":errors,"gates":gates,"assignment":assignment_stats,"groups":groups,
            "candidate_negative_rows_are_labels":False,"v3_regression_hashes_checked":len(stage1),
            "v3_package_input_hashes_checked":len(input_hashes)}
    write_json(RELEASE/"validation_report.json",report)
    if errors: raise SystemExit(json.dumps(report,ensure_ascii=False,indent=2))
    return report


def package():
    specs=read_json(WORK/"selection/proposed_groups.json")
    # Start from deterministic clean package tree without touching v3.
    for name in ("ontology","selection","splits","negative_candidates","audit","statistics"):
        (RELEASE/name).mkdir(parents=True,exist_ok=True)
    shutil.copy2(V3/"ontology/rules.json", RELEASE/"ontology/v3_rules.json")
    shutil.copy2(V3/"ontology/rules.json", RELEASE/"ontology/rules.json")
    write_json(RELEASE/"ontology/v4_proposed_changes.json",{"status":"explicit v4 normalization extensions; not a modification of frozen v3 rules",
        "action_aliases":{"sit_down":"sit"},
        "object_aliases":{"ordinary door subtype descriptions":"door","chair subtype descriptions":"chair","cabinet/cupboard door access events":"cabinet_entry"},
        "preserved_distinctions":["doorway is not door","cabinet_entry is not generic door","source and goal remain distinct"],
        "query_relation_repair":["sit on/in chair maps to support_surface=chair only when a sit event is present and explicit phrase is present","direct open/close + door phrases recover theme=door when the event list anchors a different part/object"],
        "ambiguous_scope_policy":["cabinet/cupboard door rows are quarantined for generic-door folds when the source annotation does not resolve the relation"],
        "reason":"Independent audit found sit_down leakage, chair subtype fragmentation, and door part/whole omissions in v3 event projections."})
    for f in ("composition_candidates.jsonl","coverage_report.json","proposed_groups.json"):
        shutil.copy2(WORK/"selection"/f, RELEASE/"selection"/f)
    shutil.copy2(WORK/"selection/proposed_groups.json",RELEASE/"selection/split_specs.json")
    write_json(RELEASE/"selection/semantic_rules.json",{"schema_version":1,"ontology_version":"v3-ontology-1.0.0+v4-explicit-extension",
        "composition_key":"canonical_action_family|explicit_semantic_role|canonical_filler",
        "alias_rules":{"sofa":"couch","cabinet door":"cabinet_entry","ordinary door subtypes":"door","chair subtype fillers":"chair","sit_down":"sit"},
        "leakage_rule":"exclude whole train query if any event in events matches any held composition; quarantine rows with event lacking an explicit relation",
        "role_direction":"source and goal remain separate; no relation inferred from surface tokens"})
    (RELEASE/"master").mkdir(parents=True,exist_ok=True)
    shutil.copy2(V3/"master/positive_clean.jsonl",RELEASE/"master/positive_clean.jsonl")
    shutil.copy2(V3/"master/negative_clean.jsonl",RELEASE/"master/negative_clean.jsonl")
    for group in specs["groups"]:
        shutil.copytree(WORK/"splits"/group, RELEASE/"splits"/group, dirs_exist_ok=True)
        shutil.copytree(WORK/"negatives"/group, RELEASE/"negative_candidates"/group, dirs_exist_ok=True)
    shutil.copy2(WORK/"audit/independent_review.jsonl", RELEASE/"audit/independent_review.jsonl") if (WORK/"audit/independent_review.jsonl").exists() else write_jsonl(RELEASE/"audit/independent_review.jsonl", [])
    # Preserve original negative records separately for provenance inspection.
    shutil.copy2(V3/"master/negative_clean.jsonl", RELEASE/"negative_candidates/inherited_v3_negative_source.jsonl")
    for name in ("data_inventory.json","exposure_inventory.json","schema_report.md"):
        source=WORK/"audit"/name
        if source.exists(): shutil.copy2(source,RELEASE/"audit"/name)
    ineligible=WORK/"audit/ineligible_inherited_negatives.jsonl"
    if ineligible.exists(): shutil.copy2(ineligible,RELEASE/"audit/ineligible_inherited_negatives.jsonl")
    for name in ("negative_feasibility_review.json","negative_feasibility_review.md"):
        source=WORK/"audit"/name
        if source.exists(): shutil.copy2(source,RELEASE/"audit"/name)
    for name in ("quality_report.md","independent_review_summary.json","final_independent_train_leakage_audit_v4_20261010.md","final_independent_train_leakage_audit_v4_20261010.json"):
        source=WORK/"audit"/name
        if source.exists(): shutil.copy2(source,RELEASE/"audit"/name)
    input_files=["README.md","release_info.json","construction_protocol.json","audit_summary.json","input_inventory.json","validation_report.json","ontology/rules.json","selection/semantic_rules.json","selection/split_specs.json","selection/data_profile.json","splits/summary.json","master/positive_clean.jsonl","master/negative_clean.jsonl"]
    input_files += [f"splits/{group}/{part}.jsonl" for group in ("A1_v3","A2_v3","A3_v3","C1_v3","C2_v3") for part in ("train","val","test")]
    input_doc={"source_release":"data/release/semantic_existence_v3_release","sha256":{str((V3/f).relative_to(ROOT)):digest(V3/f) for f in input_files},"files_checked":input_files}
    write_json(RELEASE/"input_inventory.json",input_doc)
    # Source provenance and evidence boundaries.
    protocol={"release":"semantic_existence_v4_comp","source":"semantic_existence_v3_release only","seed":SEED,
              "video_assignment":"reconstructed from all five v3 group split files and cross-checked against clean masters",
              "selection":"deterministic coverage criteria, frozen before any model evaluation", "visual_review_performed":False,
              "new_negative_candidates_are_gold_labels":False,"similarity":"token cosine surrogate; not CLIP",
              "v3_negative_status":"inherited text-reviewed annotations; source v3 records say no per-video review",
              "counterfactual_policy":"no sentence edits emitted where role-specific surface spans cannot be established safely",
              "independent_audit":"separate audit pass; candidate text does not establish video absence",
              "related_negative_aware_vmr_method":{"reference":"Moment of Untruth: Dealing with Negative Queries in Video Moment Retrieval",
                  "url":"https://openaccess.thecvf.com/content/WACV2025/html/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.html",
                  "adaptation":"cross-video in-domain reassignment is separately identified; role-sensitive counterfactual editing is a distinct proposed extension and was not claimed as the paper's method"}}
    write_json(RELEASE/"construction_protocol.json",protocol)
    # stats aggregate
    agg={g:read_json(RELEASE/"splits"/g/"statistics.json") for g in specs["groups"]}
    write_json(RELEASE/"statistics/group_statistics.json",agg)
    info={"release":"semantic_existence_v4_comp","status":"provisional_candidate_release_with_inherited_v3_annotation_views",
          "groups":list(specs["groups"]),"selected_groups":len(specs["groups"]),"seed":SEED,
          "negative_candidate_status":"not gold labels; requires video verification"}
    write_json(RELEASE/"release_info.json",info)
    readme=("# Semantic-Existence v4 Comp (provisional)\n\n"
            "This package contains composition holdout annotation views built only from `semantic_existence_v3_release`, plus separate unverified negative candidate sidecars. It is not a video-verified gold release. Existing v3 negative labels retain their v3 provenance; the v3 audit reports text semantic review and no per-video review. New reassignment candidates are never merged into annotation labels.\n\n"
            "Training contains S+/S− only and removes a complete query when any event in its full `events` list matches the held composition. Test positives and windows are original v3 annotations. Video splits are reconstructed and checked across five v3 groups.\n\n"
            "Run `python scripts/semantic_comp_v4/pipeline.py validate` from the repository root. Rebuild with `inventory`, `profile`, `build`, `negatives`, then `package` and `validate`. See `FINAL_REPORT.md` for counts, limits, and exact commands.\n")
    (RELEASE/"README.md").write_text(readme,encoding="utf-8")
    refresh_manifest()
    return


def refresh_manifest():
    files = sorted(p for p in RELEASE.rglob("*") if p.is_file() and p.name not in {"manifest.json", "validation_report.json"})
    write_json(RELEASE/"manifest.json", {"algorithm":"sha256", "sha256":{str(p.relative_to(RELEASE)):digest(p) for p in files}})


def summarize():
    specs=read_json(RELEASE/"selection/proposed_groups.json")
    audits=read_jsonl(RELEASE/"audit/independent_review.jsonl") if (RELEASE/"audit/independent_review.jsonl").exists() else []
    audit_by_qid={r.get("candidate_qid"):r for r in audits}
    roles=read_json(RELEASE/"audit/data_inventory.json").get("semantic_roles",{}) if (RELEASE/"audit/data_inventory.json").exists() else {}
    lines=["# Semantic-Existence v4 Comp — Final Report","", "**Status: provisional candidate release with inherited v3 annotation views. New negative candidates are not gold labels and require visual verification.**", "",
           "## Composition groups", "", "| Group | Held composition | Test U+ qids / videos | Inherited test U− qids / videos | Exact target train exclusions (positive / negative) | Ambiguous door exclusions | Query/event mismatch quarantines | Strict lexical-seen U+ |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    summary={}; totals=Counter()
    for g,s in specs["groups"].items():
        st=read_json(RELEASE/"splits"/g/"statistics.json")
        t=st["counts"]["test"]
        cand=read_jsonl(RELEASE/"negative_candidates"/g/"reassignment_candidates.jsonl")
        cf=read_jsonl(RELEASE/"negative_candidates"/g/"counterfactual_candidates.jsonl")
        methods=Counter(r["generation_strategy"] for r in cand)
        decisions=Counter(audit_by_qid.get(r["qid"],{}).get("decision","missing") for r in cand)
        uplus=t.get("U+",0); uneg=t.get("U-",0)
        lex=st["lexical_coverage"]["test_U+"]
        uv=st["condition_videos"]["test"]["U+"]; nv=st["condition_videos"]["test"]["U-"]
        lines.append(f"| {g} | `{s['held_compositions'][0]}` | {uplus} / {uv} | {uneg} / {nv} | {st['train_excluded_positive']} / {st['train_excluded_negative']} | {st['train_ambiguous_door_scope_quarantined_qids']} | {st['train_query_graph_mismatch_quarantined_qids']} | {lex['strict_lexical_seen_n']}/{lex['n']} ({lex['strict_lexical_seen_pct'] or 0:.1f}%) |")
        totals.update(methods); totals.update({f"audit_{k}":v for k,v in decisions.items()})
        summary[g]={"stats":st,"reassignment_candidates":len(cand),"counterfactual_records":len(cf),"counterfactual_sentences_generated":sum(bool(r.get("candidate_sentence")) for r in cf),"candidate_decisions":dict(decisions)}
    lines += ["", "## Full partition coverage", "", "| Group | Split | S+ qids / videos | S− qids / videos | U+ qids / videos | U− qids / videos | Strict lexical-seen U− |", "|---|---|---:|---:|---:|---:|---:|"]
    for g,s in specs["groups"].items():
        st=summary[g]["stats"]
        for part in ("train","val","test"):
            vals=[f"{st['condition_qids'][part][q]} / {st['condition_videos'][part][q]}" for q in ("S+","S-","U+","U-")]
            lex=st["lexical_coverage"].get(f"{part}_U-",{"strict_lexical_seen_n":0,"n":0,"strict_lexical_seen_pct":None})
            pct=f" ({lex['strict_lexical_seen_pct']:.1f}%)" if lex.get("strict_lexical_seen_pct") is not None else ""
            lines.append(f"| {g} | {part} | {vals[0]} | {vals[1]} | {vals[2]} | {vals[3]} | {lex['strict_lexical_seen_n']}/{lex['n']}{pct} |")
    lines += ["", "## Independent negative candidate audit", "", "| Group | Conservative reassignment | Hard reassignment | Counterfactual sentences generated | Accepted structurally | Quarantined | Rejected | Matched candidate pairs |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for g,s in specs["groups"].items():
        x=summary[g]; d=x["candidate_decisions"]
        methods=Counter(r["generation_strategy"] for r in read_jsonl(RELEASE/"negative_candidates"/g/"reassignment_candidates.jsonl"))
        lines.append(f"| {g} | {methods['conservative_in_domain_reassignment']} | {methods['hard_in_domain_reassignment']} | {x['counterfactual_sentences_generated']} | {d.get('accept_candidate',0)} | {d.get('quarantine',0)+d.get('missing',0)} | {d.get('reject',0)} | 0 |")
    total_cand=sum(x["reassignment_candidates"] for x in summary.values())
    inherited_pairs=sum(x["stats"]["matched_inherited_pairs"] for x in summary.values())
    lines += ["", f"The pipeline generated **{total_cand}** cross-video reassignment candidates ({totals['conservative_in_domain_reassignment']} conservative and {totals['hard_in_domain_reassignment']} hard). It generated **0** counterfactual sentences because v3 annotations do not include reliable sentence-role spans for minimal edits that preserve these target keys. Newly generated candidate matched pairs: **0**. The release includes **{inherited_pairs}** inherited same-video U+/U− pair from original annotations (CG01); it retains the original qids and labels. The independent audit records structural decisions only; every accepted candidate still requires video review before it can become an absence label.", "",
              "## Feasibility, roles, and constituents", "", f"The deterministic profile found **{sum(c['eligible_initial_thresholds'] for c in read_jsonl(RELEASE/'selection/composition_candidates.jsonl'))}** keys meeting the initial positive-support and constituent screens. The frozen primary set contains **{len(specs['groups'])}** groups after the preferred inherited-negative support screen (30 test negative qids) and diversity rules. Exact candidates and rejection reasons are in `selection/composition_candidates.jsonl` and `selection/split_specs.json`.", "",
              "| Group | Action positive training qids outside target | Filler training qids outside target | Exact train qids removed for target | Test original U+ | Inherited test U− |", "|---|---:|---:|---:|---:|---:|"]
    for g,s in specs["groups"].items():
        inv=read_json(RELEASE/"splits"/g/"semantic_inventory.json"); st=summary[g]["stats"]
        lines.append(f"| {g} | {inv['action_constituent_training_examples']} | {inv['filler_constituent_training_examples']} | {st['train_excluded_positive']} positive + {st['train_excluded_negative']} negative target-exposure qids; {st['train_ambiguous_door_scope_quarantined_qids']} ambiguous door qids; {st['train_query_graph_mismatch_quarantined_qids']} query/event mismatch qids; {st['unresolved_train_rows_quarantined']} unresolved-event qids | {st['counts']['test'].get('U+',0)} | {st['counts']['test'].get('U-',0)} |")
    role_rows=[]
    for role,data in roles.items():
        role_rows.append(f"| {role} | {data.get('events',0)} | {len(data.get('action_families',{}))} |")
    lines += ["", "Semantic roles supported by the v3 event inventory:", "", "| Role | Event records | Action families |", "|---|---:|---:|"]+role_rows+["",
              "The main feasible groups use theme and support_surface. Goal, source, instrument, location, target, and agent are represented but much sparser or more heterogeneous; patient appears only once and was not suitable for a primary group. Agent-as-filler groups mostly encode generic person/actor variation rather than event composition.", "",
              "## Video allocation and semantic coverage", "", "All 6,507 videos represented in the clean v3 masters map consistently across all five v3 groups: 4,707 train, 498 validation, and 1,302 test. The v3 input inventory lists 6,670 assignments; the other 163 are absent from the available release and are outside v4. No video was moved between partitions. Original positive query text and windows are retained.", "",
              "The builder checks every event in `events`, including multi-event rows; `semantic_graph` is only a primary-event projection. Queries with any event lacking an explicit action-role-filler composition are quarantined from labeled views and listed in each group's `unresolved_semantics.jsonl`. Independent semantic review also prompted conservative train removal for direct door wording that conflicts with the event graph and for ambiguous cabinet-door scope. Exact train exclusion qids and reasons are in `train_exclusions.jsonl`.", "",
              "Strict lexical-seen coverage is calculated over content lemmas from all downstream training queries (S+ and S−). Exact missing lemmas for every U+/U− row are recorded in `statistics.json`; percentages are descriptive and lexicalization uses a deterministic lightweight lemma map, not a linguistic parser.", "",
              "## Negative provenance and validation status", "", "v3 contributes inherited negatives only when the source qid resolves to a clean positive with matching video, sentence, windows, and review provenance. These remain inherited text-reviewed labels; v3 says it performed no per-video review. Three inherited negative rows with unresolved source qids were quarantined globally and are documented under `audit/ineligible_inherited_negatives.jsonl`. Newly reassigned candidates are stored separately and have empty windows; neither low text similarity nor no annotation conflict establishes visual absence. Similarity is token cosine as a lightweight surrogate, not CLIP. This adapts the cross-video in-domain reassignment motivation from [Moment of Untruth](https://openaccess.thecvf.com/content/WACV2025/html/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.html); the paper's method and our proposed role-sensitive counterfactual extension are kept separate. OOD negatives are not included.", "",
              "| Validation gate | Result |", "|---|---|"]
    vr=read_json(RELEASE/"validation_report.json") if (RELEASE/"validation_report.json").exists() else {"gates":{}}
    for name,result in vr.get("gates",{}).items(): lines.append(f"| {name.replace('_',' ')} | {result} |")
    lines += ["", "The validation report also contains per-group counts and any explicit errors. The v4 input inventory hashes all 28 source files used for construction, including the 15 split JSONLs. Four Stage-1 baseline hashes (clean positive/negative masters, ontology rules, and split specs) separately confirm those v3 files remained unchanged; package artifact hashes are checked against `manifest.json`.", "",
              "## Feasibility limits and next steps", "", "The main supported families are action–theme/object and action–support-surface. Action–goal and action–source are profile-only because typed roles are sparse and current inherited negative test support is inadequate; instrument and agent-patient relations are also too sparse or ambiguous for primary groups. Temporal order and state-transition compositions are exploratory only. Synonym substitution is not used as a generation method.", "",
              "Principal limitations: only three groups pass the available coverage and inherited-negative screen; two use the filler `door`, which reflects source-data concentration; strict lexical coverage is not 100%; annotations do not provide visual absence evidence; exact role equivalence is limited by the frozen v3 ontology; and 163 source assignments cannot be reconstructed from the release. No model was trained and no performance claim is made.", "",
              "If raw Charades videos become available, review reassignment candidates individually or in a documented video-review protocol, then import qid-level decisions without changing the frozen composition specs. If an additional video dataset becomes available, map its roles to this ontology, verify that action and filler constituents are familiar under comparable training conditions, and use its videos only under a separately versioned assignment and annotation protocol.", "",
              "## Release contents and commands", "", "Usable immediately for annotation experiments: frozen train/validation/test views with original positive windows and inherited v3 negative provenance. Candidate-only files require future video verification. The deliverable is a **mixture of labeled inherited annotation views and separately labeled provisional negative candidates**, not a video-verified gold benchmark.", "",
              "Generated outputs: `data/processed/semantic_existence_v4_comp/work/` (inventory, profile, candidate generation, exclusions, review queue); `data/release/semantic_existence_v4_comp/` (frozen specs, group splits, candidate sidecars, audit, statistics, hashes, this report); `scripts/semantic_comp_v4/` (pipeline and integration tests).", "",
              "Exact commands from repository root:", "", "```bash", "python scripts/semantic_comp_v4/pipeline.py inventory", "python scripts/semantic_comp_v4/pipeline.py profile", "python scripts/semantic_comp_v4/pipeline.py build", "python scripts/semantic_comp_v4/pipeline.py negatives", "python scripts/semantic_comp_v4/pipeline.py export-review", "python scripts/semantic_comp_v4/pipeline.py import-review data/processed/semantic_existence_v4_comp/work/audit/independent_review.jsonl", "python scripts/semantic_comp_v4/test_pipeline.py", "python scripts/semantic_comp_v4/pipeline.py package", "python scripts/semantic_comp_v4/pipeline.py validate", "python scripts/semantic_comp_v4/pipeline.py report", "python scripts/semantic_comp_v4/pipeline.py validate", "```", "", "The CLI also accepts `--repo-root`, `--v3-release`, `--work-dir`, and `--output-release` before the subcommand for alternate checkout and output paths.", ""]
    (RELEASE/"FINAL_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    all_decisions=Counter()
    for x in summary.values(): all_decisions.update(x["candidate_decisions"])
    write_json(RELEASE/"statistics/negative_statistics.json",{"total_candidates":total_cand,"candidate_matched_pairs":0,
        "counterfactual_sentences_generated":0,"candidate_decisions":dict(all_decisions),
        "per_group":{g:{"reassignment_candidates":x["reassignment_candidates"],"counterfactual_records":x["counterfactual_records"],"counterfactual_sentences_generated":x["counterfactual_sentences_generated"],"candidate_decisions":x["candidate_decisions"]} for g,x in summary.items()}})
    refresh_manifest()
    return summary


def main():
    global ROOT,V3,WORK,RELEASE
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path,default=ROOT,help="repository root (default: detected from this script)")
    p.add_argument("--v3-release",type=Path,default=None,help="v3 release directory (default: <repo-root>/data/release/semantic_existence_v3_release)")
    p.add_argument("--work-dir",type=Path,default=None,help="processed output directory (default: <repo-root>/data/processed/semantic_existence_v4_comp/work)")
    p.add_argument("--output-release",type=Path,default=None,help="release output directory (default: <repo-root>/data/release/semantic_existence_v4_comp)")
    sub=p.add_subparsers(dest="cmd",required=True)
    for name in ("inventory","profile","select","build","negatives","export-review","package","validate","report"):
        sub.add_parser(name)
    imp=sub.add_parser("import-review"); imp.add_argument("review_jsonl",type=Path)
    a=p.parse_args()
    ROOT=a.repo_root.resolve()
    V3=(a.v3_release or ROOT/"data/release/semantic_existence_v3_release").resolve()
    WORK=(a.work_dir or ROOT/"data/processed/semantic_existence_v4_comp/work").resolve()
    RELEASE=(a.output_release or ROOT/"data/release/semantic_existence_v4_comp").resolve()
    if a.cmd=="inventory": print(json.dumps(inventory(),ensure_ascii=False,indent=2))
    elif a.cmd in {"profile","select"}:
        s=profile(); print(json.dumps({"selected_groups":list(s["groups"]),
            "eligible_count":sum(c["eligible_initial_thresholds"] for c in read_jsonl(WORK/"selection/composition_candidates.jsonl")),
            "group_count":len(s["groups"])},ensure_ascii=False,indent=2))
    elif a.cmd=="build": build_splits()
    elif a.cmd=="negatives": generate_negatives()
    elif a.cmd=="export-review": print(export_review_queue())
    elif a.cmd=="package": package()
    elif a.cmd=="validate": print(json.dumps(validate_release(),ensure_ascii=False,indent=2))
    elif a.cmd=="report": print(json.dumps(summarize(),ensure_ascii=False,indent=2))
    elif a.cmd=="import-review": print(import_reviews(a.review_jsonl))

if __name__=="__main__": main()
