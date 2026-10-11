#!/usr/bin/env python3
"""Assemble complete, traceable pilot review histories after independent audits."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def write(path, values):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in values), encoding='utf-8')


def candidate_history():
    evidence = {x['candidate']['candidate_id']: x for x in read(BASE / 'staging/pilot_evidence.jsonl')}
    a = {x['candidate_id']: x for x in read(BASE / 'review/pilot_agent_a.jsonl')}
    b = {x['candidate_id']: x for x in read(BASE / 'review/pilot_agent_b_v2.jsonl')}
    cpath = BASE / 'review/pilot_agent_c.jsonl'
    c = {x['candidate_id']: x for x in read(cpath)} if cpath.exists() else {}
    scores = {x['candidate_id']: x for x in read(BASE / 'staging/pilot_clip_scores.jsonl')}
    result = []
    for cid in sorted(evidence):
        inp, ra, rb = evidence[cid], a[cid], b[cid]
        rc = c.get(cid)
        same = all(ra.get(k) == rb.get(k) for k in ('decision', 'audited_partition', 'construction_valid'))
        if same:
            status = ra['decision']
            partition = ra.get('audited_partition')
            resolution = 'A_B_agreement'
        elif rc:
            status = rc.get('decision', rc.get('final_status', 'quarantine'))
            partition = rc.get('audited_partition', 'uncertain')
            resolution = 'agent_c_adjudicated'
        else:
            status, partition, resolution = 'pending', 'uncertain', 'awaiting_agent_c'
        clip = scores.get(cid)
        if status == 'keep' and inp['candidate']['construction_type'] == 'cross_video' and not (clip and clip.get('in_lowest_half')):
            status, resolution = 'exclude', 'outside_clip_lower_half'
        result.append({'sample_id': cid, 'input_hash': inp['candidate']['input_hash'],
                       'candidate_input': inp['candidate'],
                       'source_positive_evidence': inp['donor_positive'],
                       'same_video_positive_evidence': inp['same_video_positive_evidence'],
                       'candidate_generation_metadata': clip,
                       'review_history': {'A': ra, 'B': rb, 'C': rc},
                       'review_resolution': resolution, 'final_status': status,
                       'audited_partition': partition, 'evidence_level': 'text_audited' if status == 'keep' else None,
                       'absence_claim': 'not video reviewed; based on text and supplied annotations only' if status == 'keep' else None})
    write(BASE / 'review/pilot_candidate_review_history.jsonl', result)
    return result


def positive_history():
    evidence = {x['sample_id']: x for x in read(BASE / 'staging/positive_audit_pilot.jsonl')}
    a = {x['sample_id']: x for x in read(BASE / 'review/positive_pilot_agent_a.jsonl')}
    b = {x['sample_id']: x for x in read(BASE / 'review/positive_pilot_agent_b.jsonl')}
    cpath = BASE / 'review/positive_pilot_agent_c.jsonl'
    c = {x['sample_id']: x for x in read(cpath)} if cpath.exists() else {}
    result = []
    for sid in sorted(evidence):
        ra, rb = a[sid], b[sid]
        rc = c.get(sid)
        same = ra.get('decision') == rb.get('decision') and ra.get('audited_partition') == rb.get('audited_partition')
        if same:
            status = ra['decision']
            partition = ra.get('audited_partition', 'undetermined')
            resolution = 'A_B_agreement'
        elif rc:
            status = rc.get('decision', 'quarantine')
            partition = rc.get('audited_partition', 'undetermined')
            resolution = 'agent_c_adjudicated'
        else:
            status, partition, resolution = 'pending', 'undetermined', 'awaiting_agent_c'
        result.append({'sample_id': sid, 'input_hash': evidence[sid]['input_hash'],
                       'source_evidence': evidence[sid], 'review_history': {'A': ra, 'B': rb, 'C': rc},
                       'final_status': status, 'audited_partition': partition,
                       'review_resolution': resolution})
    write(BASE / 'review/positive_pilot_review_history.jsonl', result)
    return result


def main():
    c = candidate_history()
    p = positive_history()
    from collections import Counter
    print(json.dumps({'candidate_pilot': dict(Counter(x['final_status'] for x in c)),
                      'positive_pilot': dict(Counter(x['final_status'] for x in p)),
                      'candidate_pending': sum(x['final_status'] == 'pending' for x in c),
                      'positive_pending': sum(x['final_status'] == 'pending' for x in p)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
