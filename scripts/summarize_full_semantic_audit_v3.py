#!/usr/bin/env python3
"""Trace reviewed event corrections to every group's released memberships."""
import json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'data/processed/semantic_existence_v3/full_audit_20261009';REL=ROOT/'data/release/semantic_existence_v3'
rows=[json.loads(x) for x in open(AUDIT/'decisions.jsonl') if x.strip()]
specs=json.load(open(REL/'selection/split_specs.json'))['groups'];changes=[];purpose=[];invalid=[]
video_splits={r['vid']:r['split'] for r in (json.loads(x) for x in open(ROOT/'data/processed/semantic_existence_v3/inputs/video_splits.jsonl'))}
def hit(ev,spec):
 action=ev['action_family']; anchor=(ev.get('anchor_object') or '').lower().replace('sofa','couch'); tokens=set(re.findall(r'[a-z]+',anchor))
 if spec['axis']=='action_family':return action in spec['held_action_families']
 for a,o in spec['held_compositions']:
  if a==action and o in tokens:
   if a=='sit':return ev.get('anchor_role') in {'support_surface','location'}
   return ev.get('anchor_role')=='theme'
 return False
for r in rows:
 if r['audit_decision'] in {'exclude','quarantine'}:
  invalid.append({'qid':r['qid'],'query':r['query'],'decision':r['audit_decision'],'issues':r['issues'],'reason':r['reason'],'memberships':r['memberships'],'relation':r.get('relation')})
 for group,spec in specs.items():
  present=any(m['group']==group for m in r['memberships'])
  if not present and r['audit_decision'] in {'pass','revise'}:
   active=[ev for ev in r['canonical_events'] if ev.get('assertion','asserted') not in {'negated','purpose','intended'}]
   held=any(hit(e,spec) for e in active)
   held_purpose=any(hit(e,spec) for e in r['canonical_events'])
   split=video_splits[r['vid']]
   if split!='train' or not held_purpose:
    changes.append({'qid':r['qid'],'query':r['query'],'group':group,'split':split,'current_partition':None,'reviewed_expected_partition':('U' if held else 'S')+('+' if r['exist_label'] else '-'),'code':'missing_seen_train_query' if split=='train' else 'missing_evaluation_query','canonical_events':r['canonical_events'],'worker_decision':r['audit_decision'],'basis_artifact':r['basis_artifact']})
 for m in r['memberships']:
  spec=specs[m['group']]
  active=[ev for ev in r['canonical_events'] if ev.get('assertion','asserted') not in {'negated','purpose','intended'}]
  held=any(hit(e,spec) for e in active);held_all=any(hit(e,spec) for e in r['canonical_events'])
  expected=('U' if held else 'S')+('+' if r['exist_label'] else '-')
  if held_all!=held:purpose.append({'qid':r['qid'],'query':r['query'],'group':m['group'],'current_partition':m['partition'],'note':'held semantic content only in purpose/intended event; policy needs explicit treatment','events':r['canonical_events']})
  if expected!=m['partition']:
   changes.append({'qid':r['qid'],'query':r['query'],'group':m['group'],'split':m['split'],'current_partition':m['partition'],'reviewed_expected_partition':expected,'code':'train_held_event_leak' if m['split']=='train' and held else 'semantic_partition_mismatch','canonical_events':r['canonical_events'],'worker_decision':r['audit_decision'],'basis_artifact':r['basis_artifact']})
with open(AUDIT/'partition_findings.jsonl','w') as f:
 for r in changes:f.write(json.dumps(r,ensure_ascii=False)+'\n')
with open(AUDIT/'purpose_scope_findings.jsonl','w') as f:
 for r in purpose:f.write(json.dumps(r,ensure_ascii=False)+'\n')
summary={'state':'provisional' if len(rows)<18661 else 'all_qids_reviewed_pending_primary_synthesis','reviewed_qids':len(rows),'nonpass_qids':sum(r['audit_decision']!='pass' for r in rows),'audit_decisions':dict(Counter(r['audit_decision'] for r in rows)),'partition_findings':len(changes),'partition_findings_by_group':dict(Counter(r['group'] for r in changes)),'train_leak_occurrences':sum(r['code']=='train_held_event_leak' for r in changes),'train_leak_unique_qids':len({r['qid'] for r in changes if r['code']=='train_held_event_leak'}),'purpose_scope_findings':len(purpose),'release_modified':False,'note':'Canonical event judgments are individual reviewer outputs; findings remain recommendations until primary synthesis.'}
json.dump(summary,open(AUDIT/'finding_summary.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
