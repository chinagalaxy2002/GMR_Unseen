#!/usr/bin/env python3
"""Queue only post-C status deltas introduced by blind reviewer addenda."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def latest_decision(row):
    return row.get('decision', row.get('final_status'))


def main():
    out = []
    for batch in (1, 2, 3):
        tag = f'{batch:03d}'
        evidence = {x['audit_id']: x for x in read(BASE / f'staging/positive_audit_shards/batch_{tag}.jsonl')}
        a = {x['audit_id']: x for x in read(BASE / f'review/full_positive_agent_a_batch{tag}.jsonl')}
        b = {x['audit_id']: x for x in read(BASE / f'review/full_positive_agent_b_batch{tag}.jsonl')}
        c = {x['audit_id']: x for x in read(BASE / f'review/full_positive_agent_c_batch{tag}.jsonl')}
        if not (evidence.keys() == a.keys() == b.keys() == c.keys()):
            raise RuntimeError(f'batch {tag} reviewer coverage mismatch')
        for qid, item in evidence.items():
            ra, rb, rc = a[qid], b[qid], c[qid]
            if any(x.get('input_hash') != item['input_hash'] or x.get('evidence_hash') != item['evidence_hash'] for x in (ra, rb, rc)):
                raise RuntimeError(f'hash mismatch for {qid}')
            statuses = {'A': latest_decision(ra), 'B': latest_decision(rb), 'prior_C': rc.get('final_status', rc.get('decision'))}
            if len(set(statuses.values())) > 1:
                out.append({
                    'batch': tag, 'audit_id': qid, 'input_hash': item['input_hash'], 'evidence_hash': item['evidence_hash'],
                    'original_evidence': item, 'agent_a_latest': ra, 'agent_b_latest': rb, 'prior_agent_c': rc,
                    'status_delta': statuses,
                    'instruction': 'Review the frozen-v0.3 compatibility addenda and original query/evidence item-by-item. Decide the final status using the actual source text and global-support limitation; preserve prior C decision in history and cite why it stands or changes. Never treat unreviewed train-pool citations as final support.'
                })
    path = BASE / 'staging/full_positive_c_status_delta_input.jsonl'
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in out), encoding='utf-8')
    report = {'records': len(out), 'batches': {f'{b:03d}': sum(x['batch'] == f'{b:03d}' for x in out) for b in (1,2,3)},
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'status': 'ready_for_agent_c_addendum'}
    (BASE / 'reports/full_positive_c_status_delta_queue.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
