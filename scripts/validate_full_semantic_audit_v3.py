#!/usr/bin/env python3
"""Validate that a full qid audit is reflected in the v3 source pool and splits."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'data/processed/semantic_existence_v3'
RELEASE = ROOT / 'data/release/semantic_existence_v3'
AUDIT = WORK / 'full_audit_20261009'


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def forms(event):
    return [re.sub(r'\s+', ' ', str(event.get(key)).lower().replace('_', ' ')).strip()
            for key in ('anchor_concept', 'concept', 'anchor_object', 'theme') if event.get(key)]


def has_concept(event, target):
    values = forms(event)
    if target == 'couch':
        return any(re.search(r'\b(couch|sofa)\b', value) for value in values)
    if target == 'cabinet':
        return any(value == 'cabinet' or any(term in value for term in
                   ('cabinet entry', 'cabinet door', 'cabinet drawer', 'drawer in cabinet', 'door of cabinet'))
                   for value in values)
    if target == 'box':
        return any(value == 'box' or any(term in value for term in
                   ('box lid', 'lid of box', 'box door')) for value in values)
    return any(re.search(rf'\b{re.escape(target)}\b', value) for value in values)


def held_event(event, spec):
    if event.get('assertion', 'asserted') in {'purpose', 'intended', 'negated'}:
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


def main():
    errors = []
    decisions = read(AUDIT / 'decisions.jsonl')
    audit = {row['qid']: row for row in decisions}
    if len(audit) != 18661 or len(decisions) != len(audit):
        errors.append(f'audit qid coverage/uniqueness: {len(audit)} unique / {len(decisions)} rows')

    clean_pos = {row['qid']: row for row in read(RELEASE / 'master/positive_clean.jsonl')}
    clean_neg = {row['qid']: row for row in read(RELEASE / 'master/negative_clean.jsonl')}
    expected_pos = {qid for qid, row in audit.items()
                    if row['exist_label'] == 1 and row['audit_decision'] in {'pass', 'revise'}}
    expected_neg = {qid for qid, row in audit.items()
                    if row['exist_label'] == 0 and row['audit_decision'] in {'pass', 'revise'}
                    and row.get('relation') == 'distinct'}
    if set(clean_pos) != expected_pos:
        errors.append(f'positive master qid mismatch: {len(set(clean_pos) ^ expected_pos)}')
    if set(clean_neg) != expected_neg:
        errors.append(f'negative master qid mismatch: {len(set(clean_neg) ^ expected_neg)}')
    for qid, row in {**clean_pos, **clean_neg}.items():
        if row.get('events') != audit[qid].get('canonical_events'):
            errors.append(f'master events differ from audit: {qid}')

    specs = json.loads((WORK / 'selection/split_specs.json').read_text())['groups']
    video_split = {row['vid']: row['split'] for row in read(WORK / 'inputs/video_splits.jsonl')}
    all_clean = {**clean_pos, **clean_neg}
    group_stats = {}
    train_negative_pools = {}
    for group, spec in specs.items():
        folder = RELEASE / 'splits' / group
        split_rows = {split: read(folder / f'{split}.jsonl') for split in ('train', 'val', 'test')}
        rows = [row for split in split_rows.values() for row in split]
        qid_rows = {row['qid']: row for row in rows}
        if len(qid_rows) != len(rows):
            errors.append(f'{group}: duplicate qid across splits')
        for left, right in (('train', 'val'), ('train', 'test'), ('val', 'test')):
            vleft = {row['vid'] for row in split_rows[left]}
            vright = {row['vid'] for row in split_rows[right]}
            if vleft & vright:
                errors.append(f'{group}: video overlap {left}/{right}')
        expected_eval = {}
        expected_train_pos = set()
        for qid, source in all_clean.items():
            is_held = any(held_event(event, spec) for event in source.get('events', []))
            if source['split'] == 'train':
                if not is_held and source['exist_label'] == 1:
                    expected_train_pos.add(qid)
                continue
            expected_eval[qid] = ('U' if is_held else 'S') + ('+' if source['exist_label'] else '-')
        actual_eval = {row['qid']: row for split in ('val', 'test') for row in split_rows[split]}
        if set(actual_eval) != set(expected_eval):
            errors.append(f'{group}: eval qid membership mismatch {len(set(actual_eval) ^ set(expected_eval))}')
        for qid, row in actual_eval.items():
            if row['partition'] != expected_eval[qid]:
                errors.append(f'{group}: eval partition mismatch {qid}')
        actual_train_pos = {row['qid'] for row in split_rows['train'] if row['exist_label'] == 1}
        if actual_train_pos != expected_train_pos:
            errors.append(f'{group}: train positive membership mismatch {len(actual_train_pos ^ expected_train_pos)}')
        if any(row['partition'] not in {'S+', 'S-'} for row in split_rows['train']):
            errors.append(f'{group}: unseen row in train')
        for row in rows:
            if video_split.get(row['vid']) != row['split']:
                errors.append(f'{group}: video split mismatch {row["qid"]}')
            if row['events'] != all_clean[row['qid']]['events']:
                errors.append(f'{group}: events differ from master {row["qid"]}')
        if read(folder / 'val_seen.jsonl') != [row for row in split_rows['val'] if row['partition'].startswith('S')]:
            errors.append(f'{group}: val_seen mismatch')

        train_negative_pools[group] = {row['qid'] for row in split_rows['train'] if row['exist_label'] == 0}
        pairs = read(folder / 'matched_u_pairs.jsonl')
        test_pairs = [pair for pair in pairs if pair['split'] == 'test']
        matched_test = read(folder / 'test_matched_u.jsonl')
        if len(matched_test) != 2 * len(test_pairs):
            errors.append(f'{group}: test matched-U expanded rows mismatch')
        for pair in pairs:
            positive = qid_rows.get(pair['positive_qid'])
            negative = qid_rows.get(pair['negative_qid'])
            if (not positive or not negative or positive['exist_label'] != 1 or negative['exist_label'] != 0
                    or positive['partition'] != 'U+' or negative['partition'] != 'U-'
                    or positive['vid'] != negative['vid'] or positive['split'] != negative['split']):
                errors.append(f'{group}: invalid matched-U pair {pair.get("pair_id", pair)}')
        stats = json.loads((folder / 'statistics.json').read_text())
        if stats['rows'] != len(rows) or any(stats[s] != len(split_rows[s]) for s in split_rows):
            errors.append(f'{group}: statistics mismatch')
        group_stats[group] = stats

    for groups in (('A1_v3', 'A2_v3', 'A3_v3'), ('C1_v3', 'C2_v3')):
        pools = [train_negative_pools[group] for group in groups]
        if not all(pool == pools[0] for pool in pools[1:]):
            errors.append(f'shared train negative pool mismatch: {groups}')

    if errors:
        print(json.dumps({'status': 'FAIL', 'error_count': len(errors), 'errors': errors[:100]}, ensure_ascii=False, indent=2))
        return 1
    report = {'status': 'PASS', 'validated_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
              'audit_qids': len(audit), 'positive_clean_qids': len(clean_pos), 'negative_clean_qids': len(clean_neg),
              'groups': group_stats, 'checks': ['audit coverage and uniqueness', 'master membership from final decisions',
              'master events match canonical audit events', 'held-rule split membership and labels', 'train contains S only',
              'video split consistency and disjointness', 'shared train S- pools by axis', 'matched-U pair references',
              'val_seen and statistics consistency']}
    (AUDIT / 'post_application_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
