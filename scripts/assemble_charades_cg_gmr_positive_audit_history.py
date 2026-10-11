#!/usr/bin/env python3
"""Assemble only fully reviewed positive-audit batches; never auto-promote pilots."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, required=True)
    args = parser.parse_args()
    tag = f'{args.batch:03d}'
    evidence = read(BASE / f'staging/positive_audit_shards/batch_{tag}.jsonl')
    a = read(BASE / f'review/full_positive_agent_a_batch{tag}.jsonl')
    b = read(BASE / f'review/full_positive_agent_b_batch{tag}.jsonl')
    c_path = BASE / f'review/full_positive_agent_c_batch{tag}.jsonl'
    if not c_path.exists():
        raise SystemExit(f'Agent C output missing for batch {tag}')
    c = read(c_path)
    c_input_path = BASE / f'staging/full_positive_agent_c_batch{tag}_input.jsonl'
    if c_input_path.exists():
        c_input = read(c_input_path)
        if {x['audit_id'] for x in c_input} != {x['audit_id'] for x in c}:
            raise RuntimeError('Agent C output IDs do not exactly cover the C queue')
        c_in_map = {x['audit_id']: x for x in c_input}
        for row in c:
            queued = c_in_map[row['audit_id']]
            if row.get('input_hash') != queued.get('input_hash') or row.get('evidence_hash') != queued.get('evidence_hash'):
                raise RuntimeError(f'Agent C output does not match C queue hashes: {row["audit_id"]}')
    delta_path = BASE / 'review/full_positive_c_status_delta.jsonl'
    deltas = {x['audit_id']: x for x in read(delta_path)} if delta_path.exists() else {}
    maps = [{r['audit_id']: r for r in group} for group in (a, b, c)]
    if any(len(m) != len(evidence) for m in maps[:2]):
        raise RuntimeError('A/B must each cover the complete batch exactly')
    if len(maps[2]) > len(evidence):
        raise RuntimeError('Agent C contains unexpected extra records')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import prepare_charades_cg_gmr_positive_c_queue as compare
    result = []
    for item in evidence:
        qid = item['audit_id']
        ra, rb = (m[qid] for m in maps[:2])
        rc = maps[2].get(qid)
        for reviewer, row in (('A', ra), ('B', rb)) + ((('C', rc),) if rc else ()):
            if row.get('input_hash') != item['input_hash'] or row.get('evidence_hash') != item['evidence_hash']:
                raise RuntimeError(f'{reviewer} hash mismatch for {qid}')
        if rc:
            status = rc.get('final_status', rc.get('decision'))
            resolution = 'agent_c_item_level_adjudication'
            if rc.get('reviewer') not in {'Agent C', 'C', 'agent_c'} and 'C' not in str(rc.get('reviewer', '')):
                raise RuntimeError(f'C reviewer provenance missing for {qid}')
        else:
            same = (compare.decision(ra) == compare.decision(rb)
                    and compare.part(ra) == compare.part(rb)
                    and compare.latest_semantic_decision(ra, 'A') == compare.latest_semantic_decision(rb, 'B')
                    and compare.event_signature(ra, 'A') == compare.event_signature(rb, 'B')
                    and compare.final_support_resolved(ra, 'A') == compare.final_support_resolved(rb, 'B'))
            if not same:
                raise RuntimeError(f'missing C decision for unresolved A/B disagreement: {qid}')
            status = compare.decision(ra)
            resolution = 'A_B_agreement_on_required_fields'
        if status not in {'keep', 'exclude', 'quarantine'}:
            raise RuntimeError(f'no terminal review decision for {qid}: {status}')
        delta = deltas.get(qid) if deltas.get(qid, {}).get('batch') == tag else None
        if delta:
            if delta.get('input_hash') != item['input_hash'] or delta.get('evidence_hash') != item['evidence_hash']:
                raise RuntimeError(f'C status-delta hash mismatch for {qid}')
            status = delta.get('final_status_after_delta', status)
            resolution = 'agent_c_status_delta_after_blind_compatibility_addendum'
        result.append({
            'audit_id': qid, 'input_hash': item['input_hash'], 'evidence_hash': item['evidence_hash'],
            'source_instance': item['source_row'], 'original_evidence_bundle': item,
            'review_history': {'A': ra, 'B': rb, 'C': rc, 'C_status_delta': delta},
            'final_status': status,
            'audited_partition': (delta.get('audited_partition', 'undetermined') if delta else
                                  (rc.get('audited_partition', 'undetermined') if rc else compare.part(ra))),
            'semantic_parse': rc.get('semantic_parse') if rc else (ra.get('audit_v0_3', {}).get('semantic_review') or ra.get('semantic_events')),
            'training_support_check': rc.get('training_support_check') if rc else (ra.get('member_support_evidence') or ra.get('audit_v0_3', {}).get('training_positive_support')),
            'exposure_check': rc.get('exposure_check') if rc else (ra.get('audit_v0_3', {}).get('exposure_check') or ra.get('exposure_check')),
            'source_window_quality': rc.get('source_window_quality') if rc else (ra.get('window_flag') or ra.get('source_window_quality')),
            'final_reason': (delta.get('reason') if delta else (rc.get('reason') if rc else ra.get('reason'))),
            'visual_inspection': rc.get('video_visual_inspection', False) if rc else False,
            'video_presence_claim': rc.get('video_presence_claim', 'none') if rc else 'none',
            'review_resolution': resolution,
        })
    out = BASE / f'review/full_positive_audit_history_batch{tag}.jsonl'
    out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in result), encoding='utf-8')
    report = {
        'batch': tag, 'records': len(result), 'unique_audit_ids': len({x['audit_id'] for x in result}),
        'status_counts': dict(Counter(x['final_status'] for x in result)),
        'partition_counts': dict(Counter(str(x['audited_partition']) for x in result)),
        'pending_or_retry': sum(x['final_status'] in {'pending', 'retry'} for x in result),
        'visual_inspection_count': sum(bool(x['visual_inspection']) for x in result),
        'C_rows': len(maps[2]), 'A_B_agreement_rows': len(result) - len(maps[2]),
        'history_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
        'release_eligible': False,
        'reason': 'Batch-level review history only; global support/exposure reconciliation and all remaining rows are incomplete.'
    }
    (BASE / f'reports/full_positive_audit_history_batch{tag}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
