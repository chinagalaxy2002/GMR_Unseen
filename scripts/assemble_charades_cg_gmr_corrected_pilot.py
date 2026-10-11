#!/usr/bin/env python3
"""Assemble corrected pilot A/B/C histories without promoting it to release."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(relative):
    path = BASE / relative
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def main():
    evidence = {x['candidate']['candidate_id']: x for x in read('staging/corrected_pilot_v3_evidence.jsonl')}
    a = {x['candidate_id']: x for x in read('review/corrected_pilot_v3_agent_a.jsonl')}
    b = {x['candidate_id']: x for x in read('review/corrected_pilot_v3_agent_b.jsonl')}
    cpath = BASE / 'review/corrected_pilot_v3_agent_c.jsonl'
    c = {x['candidate_id']: x for x in read('review/corrected_pilot_v3_agent_c.jsonl')} if cpath.exists() else {}
    scores = {x['candidate_id']: x for x in read('staging/corrected_pilot_v3_clip_scores.jsonl')}
    ids = set(evidence)
    if set(a) != ids or set(b) != ids:
        raise SystemExit(f'A/B coverage mismatch: inputs={len(ids)}, A={len(a)}, B={len(b)}')
    for role, reviews in (('A', a), ('B', b)):
        if any(reviews[cid].get('input_hash') != evidence[cid]['candidate']['input_hash'] for cid in ids):
            raise SystemExit(f'{role} input hash mismatch')
        if any(reviews[cid].get('decision') not in {'keep', 'exclude', 'quarantine', 'retry'} for cid in ids):
            raise SystemExit(f'{role} contains pending or invalid decisions')

    histories = []
    disagreements = set()
    for cid in sorted(ids):
        inp, ra, rb = evidence[cid], a[cid], b[cid]
        disagreement = any(ra.get(k) != rb.get(k) for k in ('decision', 'audited_partition', 'construction_valid'))
        if disagreement:
            disagreements.add(cid)
        rc = c.get(cid)
        if disagreement and rc is None:
            final, partition, resolution = 'pending', 'uncertain', 'awaiting_agent_c'
        elif disagreement:
            final = rc.get('decision', rc.get('final_status', 'quarantine'))
            partition = rc.get('audited_partition', 'uncertain')
            resolution = 'agent_c_adjudicated'
        else:
            final, partition, resolution = ra['decision'], ra.get('audited_partition', 'uncertain'), 'A_B_agreement'
        score = scores.get(cid)
        if final == 'keep' and inp['candidate']['construction_type'] == 'cross_video' and not (score and score.get('in_lowest_half')):
            final, resolution = 'exclude', 'outside_matching_subset_clip_lower_half'
        if final == 'keep' and (ra['decision'] == 'retry' or rb['decision'] == 'retry'):
            final, resolution = 'retry', 'review_evidence_read_failure'
        histories.append({
            'sample_id': cid,
            'input_hash': inp['candidate']['input_hash'],
            'candidate_input': inp['candidate'],
            'donor_positive_evidence': inp['donor_positive'],
            'same_video_positive_evidence': inp['same_video_positive_evidence'],
            'candidate_generation_metadata': score,
            'review_history': {'A': ra, 'B': rb, 'C': rc},
            'review_resolution': resolution,
            'final_status': final,
            'audited_partition': partition,
            'evidence_level': 'text_audited' if final == 'keep' else None,
            'absence_claim': 'not video reviewed; constructed from query text and supplied annotations only' if final == 'keep' else None,
            'release_eligibility': 'process_only_pilot'
        })

    if set(c) != disagreements:
        if disagreements and set(c) != disagreements:
            print(f'Agent C coverage pending: expected {len(disagreements)}, have {len(c)}')
    out = BASE / 'review/corrected_pilot_v3_review_history.jsonl'
    out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in histories), encoding='utf-8')
    counts = Counter(x['final_status'] for x in histories)
    summary = {'records': len(histories), 'status_counts': dict(counts), 'A_B_disagreements': len(disagreements),
               'C_records': len(c), 'pending_or_retry': sum(x['final_status'] in {'pending', 'retry'} for x in histories),
               'status': 'process-only; never promote pilot rows automatically'}
    (BASE / 'reports/corrected_pilot_v3_review_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary['pending_or_retry']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
