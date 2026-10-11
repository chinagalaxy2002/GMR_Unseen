#!/usr/bin/env python3
"""Validate the isolated-free v3 release package against its audited source."""
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/release/semantic_existence_v3'
RELEASE = ROOT / 'data/release/semantic_existence_v3_release'


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def main():
    errors = []
    if not RELEASE.exists():
        raise SystemExit(f'Missing release directory: {RELEASE}')
    if (RELEASE / 'review').exists():
        errors.append('Per-qid review records were copied into the clean release.')

    quarantine_ids = {row['candidate_qid'] for row in read(SOURCE / 'review/quarantine.jsonl')}
    audit_rows = read(SOURCE / 'review/full_semantic_audit_decisions.jsonl')
    quarantine_ids.update(row['qid'] for row in audit_rows if row['audit_decision'] == 'quarantine')
    exclude_ids = {row['candidate_qid'] for row in read(SOURCE / 'review/exclusions.jsonl')}
    exclude_ids.update(row['qid'] for row in audit_rows if row['audit_decision'] == 'exclude')
    removed_ids = quarantine_ids | exclude_ids

    master_rows = {}
    for name in ('positive_clean.jsonl', 'negative_clean.jsonl'):
        source_rows = read(SOURCE / 'master' / name)
        release_rows = read(RELEASE / 'master' / name)
        if source_rows != release_rows:
            errors.append(f'Master file differs from audited source: {name}')
        if len({row['qid'] for row in release_rows}) != len(release_rows):
            errors.append(f'Duplicate qid in master: {name}')
        for row in release_rows:
            master_rows[row['qid']] = row

    if set(master_rows) & removed_ids:
        errors.append(f'{len(set(master_rows) & removed_ids)} quarantined/excluded qids remain in master.')

    groups = {}
    train_negative_pools = {}
    for group in ('A1_v3', 'A2_v3', 'A3_v3', 'C1_v3', 'C2_v3'):
        source_dir = SOURCE / 'splits' / group
        release_dir = RELEASE / 'splits' / group
        split_rows = {}
        for split in ('train', 'val', 'test'):
            source_rows = read(source_dir / f'{split}.jsonl')
            rows = read(release_dir / f'{split}.jsonl')
            split_rows[split] = rows
            if source_rows != rows:
                errors.append(f'{group}/{split} differs from audited source.')
            qids = [row['qid'] for row in rows]
            if len(qids) != len(set(qids)):
                errors.append(f'{group}/{split} has duplicate qids.')
            if set(qids) & removed_ids:
                errors.append(f'{group}/{split} contains quarantined/excluded qids.')
            if any(row['qid'] not in master_rows for row in rows):
                errors.append(f'{group}/{split} contains qids absent from clean masters.')
            if split == 'train' and any(row['partition'] not in {'S+', 'S-'} for row in rows):
                errors.append(f'{group} train contains an unseen row.')

        for first, second in (('train', 'val'), ('train', 'test'), ('val', 'test')):
            vids_a = {row['vid'] for row in split_rows[first]}
            vids_b = {row['vid'] for row in split_rows[second]}
            if vids_a & vids_b:
                errors.append(f'{group} has video overlap between {first} and {second}.')

        val_seen = read(release_dir / 'val_seen.jsonl')
        expected_seen = [row for row in split_rows['val'] if row['partition'].startswith('S')]
        if val_seen != expected_seen:
            errors.append(f'{group}/val_seen does not match the seen validation subset.')
        train_negative_pools[group] = {row['qid'] for row in split_rows['train'] if row['exist_label'] == 0}
        stats = json.loads((release_dir / 'statistics.json').read_text())
        if stats['rows'] != sum(len(rows) for rows in split_rows.values()):
            errors.append(f'{group} statistics row count is inconsistent.')
        groups[group] = stats

    for axis_groups in (('A1_v3', 'A2_v3', 'A3_v3'), ('C1_v3', 'C2_v3')):
        pools = [train_negative_pools[group] for group in axis_groups]
        if not all(pool == pools[0] for pool in pools[1:]):
            errors.append(f'Train negative pools do not match for groups: {axis_groups}')

    if errors:
        print(json.dumps({'status': 'FAIL', 'errors': errors}, ensure_ascii=False, indent=2))
        return 1

    report = {
        'status': 'PASS',
        'validated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'positive_clean_qids': len(read(RELEASE / 'master/positive_clean.jsonl')),
        'negative_clean_qids': len(read(RELEASE / 'master/negative_clean.jsonl')),
        'quarantined_or_excluded_qids_checked': len(removed_ids),
        'quarantined_or_excluded_qids_in_clean_data': 0,
        'per_qid_review_records_in_release': False,
        'groups': groups,
    }
    (RELEASE / 'validation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    info_path = RELEASE / 'release_info.json'
    info = json.loads(info_path.read_text())
    info.update(status='clean_release_validated', validated_at=report['validated_at'], validation='PASS')
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
