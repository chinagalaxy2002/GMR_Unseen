#!/usr/bin/env python3
"""Validate and merge per-qid semantic audit records, leaving releases untouched."""
import json,datetime,os,tempfile
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'data/processed/semantic_existence_v3/full_audit_20261009'
def read(p):return [json.loads(x) for x in open(p) if x.strip()]
def dump(p,value):
 with tempfile.NamedTemporaryFile(mode='w',dir=p.parent,delete=False) as f:
  json.dump(value,f,ensure_ascii=False,indent=2);n=f.name
 os.replace(n,p)
assign=json.load(open(AUDIT/'assignments.json'));collected=[];inputs={};failures=[]
for batch in assign:
 path=ROOT/batch['output_path']
 if not path.exists():continue
 try:
  rs=read(path);ins=read(ROOT/batch['input_path']);lookup={r['qid']:r for r in ins}
  assert len(rs)==len(lookup),f'{len(rs)} rows expected {len(lookup)}'
  assert len({r['qid'] for r in rs})==len(rs),'duplicate output qid'
  assert {r['qid'] for r in rs}==set(lookup),'qid mismatch'
  for r in rs:
   original=lookup[r['qid']]
   assert r['query']==original['query'],f'query mismatch {r["qid"]}'
   assert r['audit_decision'] in {'pass','revise','quarantine','exclude'},f'invalid decision {r["qid"]}'
   assert r['rule_version']=='full-audit-20261009-1','rule mismatch'
   assert r.get('reason') and r.get('event_summary'),'missing concrete summary/reason'
   assert isinstance(r['canonical_events'],list),'invalid canonical_events'
   if r['audit_decision'] in {'pass','revise'}:assert r['canonical_events'],'no events for retained row'
   assert isinstance(r['issues'],list),'invalid issues'
   for ev in r['canonical_events']:
    assert ev.get('action_family'),'missing action family'
   if not original['exist_label']:
    assert r.get('relation') in {'distinct','equivalent','source_entails_candidate','candidate_entails_source','overlap','unclear'},'missing relation'
    assert r.get('source_event_summary'),'missing source summary'
   r['batch_id']=batch['batch_id'];r['basis_artifact']=batch['output_path'];r['memberships']=original['memberships'];r['exist_label']=original['exist_label'];r['vid']=original['vid']
  collected.extend(rs);inputs.update(lookup);batch['status']='imported'
 except (AssertionError,KeyError,ValueError,TypeError) as e:failures.append({'batch':batch['batch_id'],'error':str(e)})
assert len({r['qid'] for r in collected})==len(collected),'overlapping batches'
previous={r['qid']:r for r in read(AUDIT/'decisions.jsonl')} if (AUDIT/'decisions.jsonl').exists() else {}
with open(AUDIT/'history.jsonl','a') as history:
 for r in collected:
  old=previous.get(r['qid'])
  if old and old!=r:history.write(json.dumps({'qid':r['qid'],'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'previous':old,'replacement':r},ensure_ascii=False)+'\n')
with open(AUDIT/'decisions.jsonl','w') as f:
 for r in collected:f.write(json.dumps(r,ensure_ascii=False)+'\n')
with open(AUDIT/'issues.jsonl','w') as f:
 for r in collected:
  if r['audit_decision']!='pass' or r['issues']:f.write(json.dumps(r,ensure_ascii=False)+'\n')
progress=json.load(open(AUDIT/'progress.json'))
progress.update(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewed_qids=len(collected),pending_qids=progress['total_unique_qids']-len(collected),decision_counts=dict(Counter(r['audit_decision'] for r in collected)),issue_counts=dict(Counter(i['code'] for r in collected for i in r['issues'])),imported_batches=sum(b['status']=='imported' for b in assign),import_errors=failures)
dump(AUDIT/'assignments.json',assign);dump(AUDIT/'progress.json',progress)
print(json.dumps({k:progress[k] for k in ['reviewed_qids','pending_qids','decision_counts','import_errors']},ensure_ascii=False))
