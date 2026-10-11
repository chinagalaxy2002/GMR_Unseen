"""Shared, dependency-free parsing and schema helpers for Soccer-GMR unseen release."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


WORLD_CUP_SOURCE = "worldcup2022"
EXPECTED_SOURCE_COUNTS = {
    "train": {"positive": 5535, "negative": 8669, "total": 14204, "videos": 1875},
    "val": {"positive": 705, "negative": 1080, "total": 1785, "videos": 207},
    "test": {"positive": 952, "negative": 1327, "total": 2279, "videos": 374},
}
EXPECTED_CLEAN_COUNTS = {
    "train": {"positive": 5470, "negative": 8534, "total": 14004, "quarantine": 200},
    "val": {"positive": 695, "negative": 1060, "total": 1755, "quarantine": 30},
    "test": {"positive": 940, "negative": 1306, "total": 2246, "quarantine": 33},
}

ACTION_GROUPS = {
    "A1_soccer": {"axis": "action", "held_actions": ["dribble"]},
    "A2_soccer": {"axis": "action", "held_actions": ["shot"]},
    "A3_soccer": {"axis": "action", "held_actions": ["interception"]},
}
COMPOSITION_ACTIONS = {
    "C1_soccer": ["block", "clearance"],
    "C2_soccer": ["dribble", "interception"],
}
EXPECTED_COMPOSITION_TEAMS = {
    "C1_soccer": {
        "block": ["Croatia", "Argentina", "Morocco", "France", "Australia", "Netherlands", "Poland", "South Korea"],
        "clearance": ["Croatia", "Argentina", "Morocco", "France", "Senegal", "Poland", "Ghana", "Netherlands"],
    },
    "C2_soccer": {
        "dribble": ["France", "Morocco", "Croatia", "Argentina", "Senegal", "Ghana", "Brazil", "Netherlands"],
        "interception": ["France", "Morocco", "Croatia", "Argentina", "Saudi Arabia", "Ghana", "Japan", "South Korea"],
    },
}

# Include all known WorldCup and source-corpus event names so a text/metadata
# disagreement is surfaced instead of coerced into one of the eight labels.
EVENT_ALIASES = {
    "bad behaviour": ["bad behaviour", "bad behavior"],
    "block": ["block"],
    "clearance": ["clearance"],
    "dribble": ["dribble"],
    "foul committed": ["foul committed"],
    "interception": ["interception"],
    "shot": ["shot"],
    "substitution": ["substitution"],
    "header": ["header", "heading action"],
    "goal": ["scoring moment", "goal is scored", "goal"],
    "corner kick": ["corner kick", "corner-kick"],
    "goal kick": ["goal kick", "goal-kick"],
    "shot off target": ["shot off target"],
    "save": ["save"],
    "lead to corner": ["lead to corner"],
    "yellow card": ["yellow card"],
    "injury": ["injury"],
    "defense": ["defense", "defence"],
    "offense": ["offense", "offence"],
    "red card": ["red card"],
    "throw in": ["throw in", "throw-in"],
    "sliding tackle": ["sliding tackle", "sliding-tackle"],
    "free kick": ["free kick", "free-kick"],
    "penalty kick": ["penalty kick", "penalty-kick"],
    "offside": ["offside"],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_no}")
            rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[-_]+", " ", value.casefold())).strip()


def normalize_vid(vid: str) -> str:
    return re.sub(r"\.[^./]+$", "", vid)


def normalize_action(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = norm_text(value).rstrip(".!?")
    return normalized or None


def worldcup_teams(rows: list[dict[str, Any]]) -> list[str]:
    names: set[str] = set()
    for row in rows:
        match = row.get("match_info")
        teams = match.get("teams") if isinstance(match, dict) else None
        if isinstance(teams, str):
            names.update(part.strip() for part in re.split(r"\s+vs\s+", teams, flags=re.I) if part.strip())
    return sorted(names, key=str.casefold)


def _event_pattern() -> re.Pattern[str]:
    aliases: list[tuple[str, str]] = []
    for canonical, forms in EVENT_ALIASES.items():
        aliases.extend((norm_text(form), canonical) for form in forms)
    aliases.sort(key=lambda item: (-len(item[0]), item[0]))
    alternatives = "|".join(re.escape(alias) for alias, _ in aliases)
    return re.compile(rf"(?<![a-z0-9])({alternatives})(?![a-z0-9])", re.I)


_EVENT_PATTERN = _event_pattern()
_ALIAS_LOOKUP = {norm_text(alias): canonical for canonical, forms in EVENT_ALIASES.items() for alias in forms}
_ACTOR_SUFFIX = re.compile(r"\s+by\s+players\s+from\s+(.+?)\s*[.!?]*$", re.I)


def parse_query(query: Any, match_info: Any, team_names: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "semantic_action": None,
        "semantic_actor": None,
        "actor_specified": False,
        "parse_reasons": [],
        "event_mentions": [],
    }
    if not isinstance(query, str):
        result["parse_reasons"].append("query_not_string")
        return result
    body = query.strip()
    actor_match = _ACTOR_SUFFIX.search(body)
    if actor_match:
        actor_raw = actor_match.group(1).strip().rstrip(".!?").strip()
        result["actor_specified"] = True
        team_lookup = {name.casefold(): name for name in team_names}
        actor = team_lookup.get(actor_raw.casefold())
        if actor is None:
            result["parse_reasons"].append("unrecognized_actor_suffix")
        else:
            result["semantic_actor"] = actor
            match_teams = match_info.get("teams") if isinstance(match_info, dict) else None
            participants = {part.strip().casefold() for part in re.split(r"\s+vs\s+", match_teams, flags=re.I)} if isinstance(match_teams, str) else set()
            if actor.casefold() not in participants:
                result["parse_reasons"].append("actor_not_in_match_metadata")
        body = body[:actor_match.start()].strip()
    elif re.search(r"\bby\s+players\s+from\b", body, re.I):
        result["parse_reasons"].append("malformed_actor_suffix")

    mentions: list[str] = []
    for match in _EVENT_PATTERN.finditer(norm_text(body)):
        alias = norm_text(match.group(1))
        mentions.append(_ALIAS_LOOKUP[alias])
    result["event_mentions"] = mentions
    unique = sorted(set(mentions))
    if not unique:
        result["parse_reasons"].append("unparseable_event")
    elif len(unique) > 1:
        result["parse_reasons"].append("multiple_events_in_query")
    else:
        result["semantic_action"] = unique[0]
    return result


def window_validation_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    duration = row.get("duration")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        reasons.append("invalid_duration")
        return reasons
    windows = row.get("relevant_windows")
    if not isinstance(windows, list):
        return ["relevant_windows_not_list"]
    for index, window in enumerate(windows):
        if not isinstance(window, (list, tuple)) or len(window) != 2:
            reasons.append(f"invalid_window_structure:{index}")
            continue
        start, end = window
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in (start, end)):
            reasons.append(f"invalid_window_number:{index}")
            continue
        if not (0 <= start < end <= duration):
            reasons.append(f"window_out_of_bounds:{index}")
    return reasons


def derive_cleaning(rows: list[dict[str, Any]], team_names: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return enriched clean and quarantined rows, evaluating conflicts before removal."""
    enriched: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        parsed = parse_query(source.get("query"), source.get("match_info"), team_names)
        action_type = normalize_action(source.get("action_type"))
        reasons = list(parsed["parse_reasons"])
        if parsed["semantic_action"] is not None and parsed["semantic_action"] != action_type:
            reasons.append("query_action_type_mismatch")
        if action_type is None:
            reasons.append("invalid_action_type")
        reasons.extend(window_validation_reasons(source))
        row.update({key: parsed[key] for key in ("semantic_action", "semantic_actor", "actor_specified", "event_mentions")})
        row["normalized_action_type"] = action_type
        row["quarantine_reasons"] = reasons
        row["exist_label"] = int(bool(source.get("relevant_windows")))
        row["_norm_vid"] = normalize_vid(str(source.get("vid", "")))
        enriched.append(row)

    by_actor: dict[tuple[str, str, str | None], list[dict[str, Any]]] = defaultdict(list)
    by_vid_action: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_vid_query: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in enriched:
        action = row.get("semantic_action") or row.get("normalized_action_type") or ""
        by_actor[(row["_norm_vid"], action, row.get("semantic_actor"))].append(row)
        by_vid_action[(row["_norm_vid"], action)].append(row)
        by_vid_query[(row["_norm_vid"], str(row.get("query", "")))].append(row)

    for group in by_actor.values():
        labels = {row["exist_label"] for row in group}
        if labels == {0, 1}:
            for row in group:
                row["quarantine_reasons"].append("same_video_event_actor_positive_negative_conflict")
    for group in by_vid_action.values():
        if any(row["exist_label"] == 1 for row in group):
            for row in group:
                if row["exist_label"] == 0 and not row.get("actor_specified"):
                    row["quarantine_reasons"].append("generic_negative_conflicts_with_video_event_positive")
    for group in by_vid_query.values():
        if len(group) > 1:
            for row in group:
                row["quarantine_reasons"].append("duplicate_video_query_group")

    clean: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    for row in enriched:
        row["quarantine_reasons"] = sorted(set(row["quarantine_reasons"]))
        row.pop("_norm_vid", None)
        (quarantine if row["quarantine_reasons"] else clean).append(row)
    return clean, quarantine


def composition_candidates(clean_train: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, list[str]]]]:
    counts: dict[tuple[str, str], dict[int, int]] = defaultdict(lambda: {0: 0, 1: 0})
    for row in clean_train:
        actor = row.get("semantic_actor")
        action = row.get("semantic_action")
        if actor is not None and action is not None:
            counts[(action, actor)][int(row["exist_label"])] += 1
    rows: list[dict[str, Any]] = []
    selected: dict[str, dict[str, list[str]]] = {group: {} for group in COMPOSITION_ACTIONS}
    rank_by_pair: dict[tuple[str, str], int] = {}
    for action in sorted({a for a, _ in counts}):
        eligible = [
            (actor, values)
            for (candidate_action, actor), values in counts.items()
            if candidate_action == action and values[1] >= 10 and values[0] >= 10
        ]
        eligible.sort(key=lambda item: (-min(item[1][1], item[1][0]), -item[1][1], -item[1][0], item[0]))
        rank_by_pair.update({(action, actor): index + 1 for index, (actor, _) in enumerate(eligible)})
        for group_name, actions in COMPOSITION_ACTIONS.items():
            if action in actions:
                selected[group_name][action] = [actor for actor, _ in eligible[:8]]
    for (action, actor), values in sorted(counts.items()):
        rank = rank_by_pair.get((action, actor))
        rows.append({
            "action": action,
            "team": actor,
            "train_positive": values[1],
            "train_negative": values[0],
            "eligible": rank is not None,
            "eligible_rank": rank,
            "selected_C1_soccer": actor in selected.get("C1_soccer", {}).get(action, []),
            "selected_C2_soccer": actor in selected.get("C2_soccer", {}).get(action, []),
        })
    return rows, selected


def partition_row(row: dict[str, Any], group: str, held_actions: list[str], held_combinations: set[tuple[str, str]]) -> dict[str, Any]:
    action = row.get("semantic_action")
    actor = row.get("semantic_actor")
    if group in ACTION_GROUPS:
        unseen = action in held_actions
        novelty = "action" if unseen else "none"
        axis = "action"
    else:
        unseen = actor is not None and (action, actor) in held_combinations
        novelty = "action_actor_composition" if unseen else "none"
        axis = "action_actor_composition"
    result = dict(row)
    result.pop("quarantine_reasons", None)
    result["source_qid"] = row.get("qid")
    result["source_split"] = row.get("source_split")
    result["semantic_status"] = "unseen" if unseen else "seen"
    result["partition"] = ("U" if unseen else "S") + ("+" if row["exist_label"] else "-")
    result["novelty_type"] = novelty
    result["semantic_axis"] = axis
    result["construction_type"] = "original_soccer_gmr_annotation"
    result["verification_status"] = "source_annotation_inherited_not_video_reviewed"
    return result


def train_exclusion_reason(row: dict[str, Any], group: str, held_actions: list[str], held_combinations: set[tuple[str, str]]) -> str | None:
    action = row.get("semantic_action")
    actor = row.get("semantic_actor")
    if group in ACTION_GROUPS:
        return "held_out_action" if action in held_actions else None
    if actor is not None and (action, actor) in held_combinations:
        return "held_out_action_actor_combination"
    if actor is None and action in held_actions:
        return "generic_actor_query_for_held_action"
    return None

