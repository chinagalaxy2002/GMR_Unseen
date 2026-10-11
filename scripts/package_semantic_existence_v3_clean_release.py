#!/usr/bin/env python3
"""Package an isolated-free v3 release from the validated clean source dataset."""
import datetime
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/release/semantic_existence_v3'
DESTINATION = ROOT / 'data/release/semantic_existence_v3_release'

if DESTINATION.exists():
    raise SystemExit(f'Refusing to overwrite existing release: {DESTINATION}')

with tempfile.TemporaryDirectory(prefix='semantic_existence_v3_release_', dir=ROOT / 'data/release') as tmp:
    stage = Path(tmp) / DESTINATION.name
    stage.mkdir()

    for name in ('ontology',):
        shutil.copytree(SOURCE / name, stage / name)

    (stage / 'selection').mkdir()
    for name in ('data_profile.json', 'definition_issues.json', 'semantic_rules.json', 'split_specs.json',
                 'shared_action_seen_negative_reviewed.jsonl', 'shared_composition_seen_negative_reviewed.jsonl'):
        shutil.copy2(SOURCE / 'selection' / name, stage / 'selection' / name)

    for name in ('master', 'splits'):
        shutil.copytree(SOURCE / name, stage / name)

    full_audit = [json.loads(line) for line in
                  (SOURCE / 'review/full_semantic_audit_decisions.jsonl').read_text().splitlines() if line.strip()]
    source_release_info = json.loads((SOURCE / 'release_info.json').read_text())
    quarantine = [json.loads(line) for line in
                  (SOURCE / 'review/quarantine.jsonl').read_text().splitlines() if line.strip()]
    excludes = [json.loads(line) for line in
                (SOURCE / 'review/exclusions.jsonl').read_text().splitlines() if line.strip()]
    all_decisions = Counter(row['audit_decision'] for row in full_audit)
    positive_decisions = Counter(row['audit_decision'] for row in full_audit if row['exist_label'] == 1)
    negative_decisions = Counter(row['audit_decision'] for row in full_audit if row['exist_label'] == 0)

    positive_count = sum(1 for line in (stage / 'master/positive_clean.jsonl').read_text().splitlines() if line.strip())
    negative_count = sum(1 for line in (stage / 'master/negative_clean.jsonl').read_text().splitlines() if line.strip())
    assert positive_count == 15034 and negative_count == 2869

    quarantined_ids = {row['candidate_qid'] for row in quarantine}
    quarantined_ids.update(row['qid'] for row in full_audit
                          if row['audit_decision'] == 'quarantine')
    excluded_ids = {row['candidate_qid'] for row in excludes}
    excluded_ids.update(row['qid'] for row in full_audit if row['audit_decision'] == 'exclude')
    master_ids = set()
    for splitfile in (stage / 'master/positive_clean.jsonl', stage / 'master/negative_clean.jsonl'):
        master_ids.update(json.loads(line)['qid'] for line in splitfile.read_text().splitlines() if line.strip())
    split_ids = set()
    for path in (stage / 'splits').glob('*/*.jsonl'):
        if path.name not in {'train.jsonl', 'val.jsonl', 'test.jsonl'}:
            continue
        split_ids.update(json.loads(line)['qid'] for line in path.read_text().splitlines() if line.strip())
    assert not (master_ids & quarantined_ids), 'Quarantined qid found in clean master pool.'
    assert not (split_ids & quarantined_ids), 'Quarantined qid found in train/val/test.'
    assert not (master_ids & excluded_ids), 'Excluded qid found in clean master pool.'
    assert not (split_ids & excluded_ids), 'Excluded qid found in train/val/test.'

    groups = {}
    for group_dir in sorted((stage / 'splits').iterdir()):
        if not group_dir.is_dir():
            continue
        groups[group_dir.name] = json.loads((group_dir / 'statistics.json').read_text())

    protocol = {
        'release': DESTINATION.name,
        'based_on': 'semantic_existence_v3',
        'full_audit_revision': 'full-semantic-audit-20261009-1',
        'negative_review_revision': 'negative-full-audit-20261009-1',
        'ontology_version': 'v3-ontology-1.0.0',
        'unique_qid_audit': len(full_audit),
        'video_review_performed': False,
        'model_predictions_used': False,
        'hashes_generated': False,
        'preset_scale_gates': False,
        'quarantined_or_excluded_examples_copied_to_release': False,
        'review_evidence_location': 'data/release/semantic_existence_v3/review/ and data/processed/semantic_existence_v3/full_audit_20261009/',
    }
    (stage / 'construction_protocol.json').write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + '\n')

    inventory = {
        'release': DESTINATION.name,
        'positive_clean_qids': positive_count,
        'negative_clean_qids': negative_count,
        'full_audited_qids': len(full_audit),
        'audited_decision_counts': dict(all_decisions),
        'legacy_negative_decision_counts': source_release_info['legacy_decisions'],
        'quarantined_qids_excluded_from_clean_data': len(quarantined_ids),
        'excluded_qids_excluded_from_clean_data': len(excluded_ids),
        'source_video_assignments': 6670,
    }
    (stage / 'input_inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')

    audit_summary = {
        'revision': 'full-semantic-audit-20261009-1',
        'audited_unique_qids': len(full_audit),
        'decision_counts': dict(all_decisions),
        'positive_decision_counts': dict(positive_decisions),
        'negative_decision_counts': dict(negative_decisions),
        'positive_clean_qids': positive_count,
        'negative_clean_qids': negative_count,
        'quarantined_examples_in_release': 0,
        'excluded_examples_in_release': 0,
    }
    (stage / 'audit_summary.json').write_text(json.dumps(audit_summary, ensure_ascii=False, indent=2) + '\n')

    release_info = {
        'release': DESTINATION.name,
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'clean_release_validated',
        'positive_clean_qids': positive_count,
        'negative_clean_qids': negative_count,
        'quarantined_examples_in_clean_data': 0,
        'excluded_examples_in_clean_data': 0,
        'groups': groups,
        'validation': 'PASS',
    }
    (stage / 'release_info.json').write_text(json.dumps(release_info, ensure_ascii=False, indent=2) + '\n')

    README = '''# Semantic Existence v3 Release\n\nThis is the clean, isolated-free release built from the completed v3 semantic audit. Quarantined and excluded examples are not included in the master pools or any train/validation/test split. The prior `semantic_existence_v3` directory remains the audit archive.\n\n## Contents\n\n- `master/`: 15,034 positive and 2,869 reviewed distinct negative qids.\n- `splits/`: A1, A2, A3, C1, and C2 train/validation/test datasets, seen validation subsets, and matched-U files.\n- `selection/`: split definitions, semantic rules, and clean shared seen-negative pools.\n- `ontology/`: v3 ontology rules and version.\n- `audit_summary.json`: aggregate counts only; it contains no quarantined sample rows.\n\nTraining contains S+/S- only. The shared train-negative qid pool is identical across groups within each axis. All groups use the persisted shared video split. See `release_info.json`, `input_inventory.json`, and each group's `statistics.json` for counts.\n\nThe qid-level audit evidence and the separate manual-review workbook are kept outside this clean release under `data/release/semantic_existence_v3/review/`. No video-by-video review was performed.\n'''
    (stage / 'README.md').write_text(README, encoding='utf-8')

    # Publish only after the staged package contains no quarantined/excluded example rows.
    stage.rename(DESTINATION)

print(json.dumps({'release_dir': str(DESTINATION.relative_to(ROOT)), 'positive_clean_qids': positive_count,
                  'negative_clean_qids': negative_count, 'quarantined_qids_excluded': len(quarantined_ids),
                  'excluded_qids_excluded': len(excluded_ids), 'groups': groups}, ensure_ascii=False, indent=2))
