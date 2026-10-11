#!/usr/bin/env python3
"""Apply completed qid-level semantic audits to the v3 source pool and splits."""
import copy
import datetime
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'data/processed/semantic_existence_v3'
RELEASE = ROOT / 'data/release/semantic_existence_v3'
AUDIT = WORK / 'full_audit_20261009'
REVISION = 'full-semantic-audit-20261009-1'


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        temp = stream.name
    os.replace(temp, path)


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        temp = stream.name
    os.replace(temp, path)


def text_forms(event):
    values = [event.get(k) for k in ('anchor_concept', 'concept', 'anchor_object', 'theme')]
    return [re.sub(r'\s+', ' ', str(v).lower().replace('_', ' ')).strip() for v in values if v]


def has_concept(event, target):
    forms = text_forms(event)
    if target == 'couch':
        return any(re.search(r'\b(couch|sofa)\b', form) for form in forms)
    if target == 'cabinet':
        return any(form == 'cabinet' or 'cabinet entry' in form or 'cabinet door' in form or 'cabinet drawer' in form
                   or 'drawer in cabinet' in form or 'door of cabinet' in form for form in forms)
    if target == 'box':
        return any(form == 'box' or 'box lid' in form or 'lid of box' in form or 'box door' in form for form in forms)
    return any(re.search(rf'\b{re.escape(target)}\b', form) for form in forms)


def active(event):
    return event.get('assertion', 'asserted') not in {'purpose', 'intended', 'negated'}


def held_event(event, spec):
    if not active(event):
        return False
    action = event.get('action_family')
    if spec['axis'] == 'action_family':
        return action in spec['held_action_families']
    for family, concept in spec['held_compositions']:
        if action != family or not has_concept(event, concept):
            continue
        role = event.get('anchor_role')
        if family == 'sit' and role in {'support_surface', 'location'}:
            return True
        if family in {'open', 'close'} and role == 'theme':
            return True
    return False


def row_held(row, spec):
    return any(held_event(event, spec) for event in row.get('events', []))


def graph(events):
    event = next((e for e in events if active(e)), events[0])
    action = event.get('action_family')
    obj = event.get('anchor_object') or event.get('theme')
    return {
        'action': action,
        'action_family': action,
        'action_class': action,
        'object': obj,
        'object_concept': event.get('concept') or event.get('anchor_concept') or obj,
        'object_role': event.get('anchor_role'),
        'location': event.get('location'),
        'source': event.get('source'),
        'goal': event.get('goal'),
        'manner': event.get('manner'),
        'assertion': event.get('assertion', 'asserted'),
        'representation': 'full_semantic_audit_primary_event_projection',
    }


def target_key(event):
    action = event.get('action_family')
    if action in {'take_out', 'pick_up'}:
        action = 'physical_take'
    if action in {'put_down', 'put_in', 'place'}:
        action = 'physical_place'
    obj = next(iter(text_forms(event)), '')
    return action, obj


def primary_event(row, spec):
    return next((e for e in row.get('events', []) if held_event(e, spec)), None)


now = datetime.datetime.now(datetime.timezone.utc).isoformat()
marker = AUDIT / 'full_application.json'
if marker.exists() and json.loads(marker.read_text()).get('revision') == REVISION:
    raise SystemExit('This full semantic audit revision is already applied.')

audit_rows = read(AUDIT / 'decisions.jsonl')
audit = {row['qid']: row for row in audit_rows}
assert len(audit) == 18661 and len(audit) == len(audit_rows), 'Audit must cover 18,661 unique qids.'
assert all(row['audit_decision'] in {'pass', 'revise', 'quarantine', 'exclude'} for row in audit.values())
positive_source = {row['qid']: row for row in read(WORK / 'master/positive_clean.jsonl')}
negative_source = {row['qid']: row for row in read(WORK / 'master/negative_clean.jsonl')}
assert len(positive_source) == 15076
assert len(negative_source) == 2869
assert {q for q, row in audit.items() if row['exist_label'] == 1} == set(positive_source)
assert {q for q, row in audit.items() if row['exist_label'] == 0} == set(negative_source) | {
    q for q, row in audit.items() if row['exist_label'] == 0 and row['audit_decision'] in {'exclude', 'quarantine'}
}

specs = json.loads((WORK / 'selection/split_specs.json').read_text())['groups']
video_splits = {row['vid']: row['split'] for row in read(WORK / 'inputs/video_splits.jsonl')}
old_neg_decisions = {row['candidate_qid']: row for row in read(WORK / 'review/decisions.jsonl')}

positive = {}
positive_quarantine = []
positive_corrections = []
for qid, old in positive_source.items():
    reviewed = audit[qid]
    if reviewed['audit_decision'] in {'quarantine', 'exclude'}:
        positive_quarantine.append(reviewed)
        continue
    row = copy.deepcopy(old)
    row['events'] = copy.deepcopy(reviewed['canonical_events'])
    row['semantic_graph'] = graph(row['events'])
    row['split'] = video_splits[row['vid']]
    row.update(exist_label=1, existence_status='present', semantic_status='audited',
               full_audit_decision=reviewed['audit_decision'], full_audit_qid=qid,
               full_audit_rule_version=reviewed['rule_version'], full_audit_reason=reviewed['reason'])
    if reviewed['audit_decision'] == 'revise':
        row['semantic_correction_revision'] = REVISION
        positive_corrections.append(reviewed)
    positive[qid] = row

negative = {}
for qid, old in negative_source.items():
    reviewed = audit[qid]
    assert reviewed['audit_decision'] in {'pass', 'revise'} and reviewed.get('relation') == 'distinct'
    row = copy.deepcopy(old)
    row['events'] = copy.deepcopy(reviewed['canonical_events'])
    row['semantic_graph'] = graph(row['events'])
    row['split'] = video_splits[row['vid']]
    row.update(exist_label=0, existence_status='absent_by_construction', semantic_status='audited',
               full_audit_decision=reviewed['audit_decision'], full_audit_qid=qid,
               full_audit_rule_version=reviewed['rule_version'], full_audit_reason=reviewed['reason'])
    negative[qid] = row

# Build all five partitions from the reviewed event lists. Train retains only seen rows.
group_rows = {}
group_negatives = {}
for group, spec in specs.items():
    pos_rows = []
    neg_rows = []
    for row in positive.values():
        is_held = row_held(row, spec)
        if row['split'] == 'train' and is_held:
            continue
        copy_row = copy.deepcopy(row)
        partition = 'U+' if is_held else 'S+'
        copy_row.update(partition=partition, semantic_status='unseen' if is_held else 'seen',
                        novelty_type='unseen' if is_held else 'seen')
        pos_rows.append(copy_row)
    for row in negative.values():
        is_held = row_held(row, spec)
        if row['split'] == 'train' and is_held:
            continue
        copy_row = copy.deepcopy(row)
        partition = 'U-' if is_held else 'S-'
        copy_row.update(partition=partition, semantic_status='unseen' if is_held else 'seen',
                        novelty_type='unseen' if is_held else 'seen')
        neg_rows.append(copy_row)
    group_negatives[group] = neg_rows
    group_rows[group] = pos_rows + neg_rows

# Keep exactly the legal shared seen-negative intersection on each train axis.
shared = {}
for axis, groups in [('action', ['A1_v3', 'A2_v3', 'A3_v3']), ('composition', ['C1_v3', 'C2_v3'])]:
    eligible = []
    for group in groups:
        train_positive_ids = {row['qid'] for row in group_rows[group] if row['exist_label'] == 1 and row['split'] == 'train'}
        eligible.append({row['qid'] for row in group_negatives[group]
                         if row['split'] == 'train' and row['partition'] == 'S-'
                         and row.get('source_qid') in train_positive_ids})
    common = set.intersection(*eligible)
    shared[axis] = sorted(common)
    for group in groups:
        group_rows[group] = [row for row in group_rows[group]
                             if row['exist_label'] == 1 or row['split'] != 'train' or row['qid'] in common]

# Build a full staged set and verify basic structural invariants before writing.
group_outputs = {}
group_summaries = {}
for group, spec in specs.items():
    rows = sorted(group_rows[group], key=lambda row: row['qid'])
    assert len({row['qid'] for row in rows}) == len(rows), f'{group}: duplicate qid'
    by_split = {split: [row for row in rows if row['split'] == split] for split in ('train', 'val', 'test')}
    assert all(row['partition'] in {'S+', 'S-'} for row in by_split['train']), f'{group}: unseen train row'
    for split, split_rows in by_split.items():
        for row in split_rows:
            expected = 'U' if row_held(row, spec) else 'S'
            assert row['partition'][0] == expected, f'{group}: partition mismatch {row["qid"]}'
    pos_by_qid = {row['qid']: row for row in rows if row['exist_label'] == 1}
    candidates = {}
    for nrow in rows:
        if nrow['exist_label'] != 0 or nrow['split'] == 'train' or nrow['partition'] != 'U-':
            continue
        prow = pos_by_qid.get(nrow.get('source_qid'))
        if not prow or prow['split'] != nrow['split'] or prow['vid'] != nrow['vid'] or prow['partition'] != 'U+':
            continue
        pe = primary_event(prow, spec)
        ne = primary_event(nrow, spec)
        if not pe or not ne or target_key(pe) == target_key(ne):
            continue
        candidates.setdefault(prow['qid'], []).append(nrow)
    pairs = []
    test_rows = []
    for source_qid, alternatives in sorted(candidates.items()):
        nrow = sorted(alternatives, key=lambda row: row['qid'])[0]
        prow = pos_by_qid[source_qid]
        pair = {'pair_id': 'pair_' + nrow['qid'], 'positive_qid': source_qid, 'negative_qid': nrow['qid'],
                'source_qid': source_qid, 'candidate_qid': nrow['qid'], 'video_id': nrow['vid'], 'vid': nrow['vid'],
                'split': nrow['split'], 'shared_source': True, 'novelty_axis': spec['axis'],
                'target_alignment': 'changed_reviewed_primary_held_event',
                'negative_verification_status': nrow.get('verification_status', 'llm_semantic_review_passed')}
        pairs.append(pair)
        if nrow['split'] == 'test':
            test_rows.extend([prow, nrow])
    counts = Counter((split, row['partition']) for split, split_rows in by_split.items() for row in split_rows)
    inventory = {'group': group, 'spec': spec,
                 'counts': {f'{split}_{part}': count for (split, part), count in sorted(counts.items())},
                 'unique_videos': len({row['vid'] for row in rows}), 'matched_u_pairs': len(pairs),
                 'revision': REVISION, 'full_audit_status': 'complete',
                 'shared_seen_negative_axis': 'action' if group.startswith('A') else 'composition'}
    statistics = {'group': group, 'rows': len(rows), **{split: len(by_split[split]) for split in by_split},
                  'partition_counts': dict(Counter(row['partition'] for row in rows)),
                  'test_matched_u_pairs': len(test_rows) // 2, 'test_matched_u_rows': len(test_rows),
                  'revision': REVISION}
    group_outputs[group] = {'rows': rows, 'splits': by_split, 'pairs': pairs, 'test_matched_rows': test_rows,
                            'inventory': inventory, 'statistics': statistics}
    group_summaries[group] = inventory

# Snapshot the negative-applied state once, then apply to processed source and release.
backup = AUDIT / 'full_application_before'
assert not backup.exists(), 'Existing full-application snapshot must not be overwritten.'
backup.mkdir()
shutil.copytree(RELEASE, backup / 'release')
for name in ('master', 'review', 'splits', 'selection'):
    shutil.copytree(WORK / name, backup / 'processed' / name)

write(WORK / 'master/positive_clean.jsonl', sorted(positive.values(), key=lambda row: row['qid']))
write(WORK / 'review/positive_full_audit_quarantine.jsonl', positive_quarantine)
write(WORK / 'review/positive_full_audit_corrections.jsonl', positive_corrections)
write(WORK / 'review/full_semantic_audit_decisions.jsonl', sorted(audit_rows, key=lambda row: row['qid']))
write(WORK / 'review/full_semantic_audit_issues.jsonl', [row for row in audit_rows if row['audit_decision'] != 'pass' or row['issues']])
dump(WORK / 'selection/shared_negative_pools_full_audit.json', shared)
write(WORK / 'selection/shared_action_seen_negative_reviewed.jsonl', [negative[q] for q in shared['action']])
write(WORK / 'selection/shared_composition_seen_negative_reviewed.jsonl', [negative[q] for q in shared['composition']])

for group, output in group_outputs.items():
    folder = WORK / 'splits' / group
    for split, rows in output['splits'].items():
        write(folder / (split + '.jsonl'), rows)
    write(folder / 'val_seen.jsonl', [row for row in output['splits']['val'] if row['partition'].startswith('S')])
    write(folder / 'matched_u_pairs.jsonl', output['pairs'])
    write(folder / 'test_matched_u.jsonl', output['test_matched_rows'])
    dump(folder / 'semantic_inventory.json', output['inventory'])
    dump(folder / 'statistics.json', output['statistics'])
dump(WORK / 'splits/summary.json', group_summaries)

# Mirror the audited source and partitions into the versioned v3 release.
shutil.copy2(WORK / 'master/positive_clean.jsonl', RELEASE / 'master/positive_clean.jsonl')
shutil.copy2(WORK / 'master/negative_clean.jsonl', RELEASE / 'master/negative_clean.jsonl')
shutil.copytree(WORK / 'splits', RELEASE / 'splits', dirs_exist_ok=True)
for name in ('full_semantic_audit_decisions.jsonl', 'full_semantic_audit_issues.jsonl',
             'positive_full_audit_quarantine.jsonl', 'positive_full_audit_corrections.jsonl'):
    shutil.copy2(WORK / 'review' / name, RELEASE / 'review' / name)
for name in ('shared_action_seen_negative_reviewed.jsonl', 'shared_composition_seen_negative_reviewed.jsonl'):
    shutil.copy2(WORK / 'selection' / name, RELEASE / 'selection' / name)

decision_counts = dict(Counter(row['audit_decision'] for row in audit_rows))
positive_counts = dict(Counter(row['audit_decision'] for row in audit_rows if row['exist_label'] == 1))
application = {'revision': REVISION, 'applied_at': now, 'audited_unique_qids': len(audit_rows),
               'audit_decisions': decision_counts, 'positive_audit_decisions': positive_counts,
               'positive_source_qids': len(positive_source), 'positive_retained_qids': len(positive),
               'positive_quarantined_qids': len(positive_quarantine), 'positive_revised_qids': len(positive_corrections),
               'retained_negative_qids': len(negative), 'shared_seen_negative_pool_counts': {k: len(v) for k, v in shared.items()},
               'backup_path': str(backup.relative_to(ROOT)), 'groups': {g: o['statistics'] for g, o in group_outputs.items()}}
dump(marker, application)
dump(RELEASE / 'full_audit_update.json', application)

info = json.loads((RELEASE / 'release_info.json').read_text())
info.update(status='full_semantic_reaudit_applied_pending_validation', full_audit_revision=REVISION,
            full_audit_qids=len(audit_rows), positive_clean_qids=len(positive), negative_clean_qids=len(negative),
            groups=group_summaries, full_audit_decisions=decision_counts)
dump(RELEASE / 'release_info.json', info)

stats = json.loads((RELEASE / 'review/review_statistics.json').read_text())
stats.update(full_semantic_audit=application, positive_full_audit_decisions=positive_counts,
             positive_quarantined_qids=len(positive_quarantine), positive_revised_qids=len(positive_corrections),
             group_statistics={g: o['statistics'] for g, o in group_outputs.items()})
dump(RELEASE / 'review/review_statistics.json', stats)

for path in (WORK / 'state.json', ROOT / 'docs/semantic_existence_v3_construction/progress.json'):
    state = json.loads(path.read_text())
    state.update(updated_at=now, state='full_semantic_reaudit_applied_pending_validation',
                 full_audit_revision=REVISION, full_audit_qids=len(audit_rows),
                 positive_clean_qids=len(positive), negative_clean_qids=len(negative),
                 full_audit_decisions=decision_counts, release_groups=group_summaries)
    dump(path, state)

print(json.dumps(application, ensure_ascii=False, indent=2))
