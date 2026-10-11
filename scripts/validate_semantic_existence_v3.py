#!/usr/bin/env python3
"""Semantic and split integrity validation for the v3 release candidate."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; W=ROOT/'data/processed/semantic_existence_v3'; OUT=W/'splits'
def read(p): return [json.loads(x) for x in open(p) if x.strip()]
def fail(msg): raise SystemExit('FAIL: '+msg)
errors=[]; decisions={r['candidate_qid']:r for r in read(W/'review/decisions.jsonl')}
if len(decisions)!=6976: errors.append(f'decision coverage {len(decisions)} != 6976')
if any(r['decision'] not in {'keep','exclude','quarantine'} for r in decisions.values()):errors.append('pending/unknown decision')
if any(r['decision']=='keep' and r['relation']!='distinct' for r in decisions.values()):errors.append('keep without distinct relation')
assign={r['vid']:r['split'] for r in read(W/'inputs/video_splits.jsonl')}
for group in json.load(open(OUT/'summary.json')):
 d=OUT/group; data={n:read(d/f'{n}.jsonl') for n in ['train','val','test']}
 ids={n:{r['qid'] for r in rs} for n,rs in data.items()}
 vids={n:{r['vid'] for r in rs} for n,rs in data.items()}
 for a,b in [('train','val'),('train','test'),('val','test')]:
  if vids[a]&vids[b]: errors.append(f'{group}: video overlap {a}/{b}: {len(vids[a]&vids[b])}')
 for split,rows in data.items():
  if len(ids[split])!=len(rows):errors.append(f'{group} {split}: duplicate qid')
  for r in rows:
   if assign.get(r['vid'])!=split:errors.append(f'{group}: split mismatch {r["qid"]}')
   if split=='train' and r['partition'] not in {'S+','S-'}:errors.append(f'{group}: unseen in train {r["qid"]}')
   if r['exist_label']==0:
    q=r['qid']; dv=decisions.get(q)
    if not dv or dv['decision']!='keep' or dv['relation']!='distinct':errors.append(f'{group}: released negative not adjudicated keep {q}')
    if dv and (dv['source_qid']!=r['source_qid'] or dv['vid']!=r['vid']):errors.append(f'{group}: source mismatch {q}')
 # validate matched references, same video/partition and U axis
 positives={r['qid']:r for rs in data.values() for r in rs if r['exist_label']==1}
 negatives={r['qid']:r for rs in data.values() for r in rs if r['exist_label']==0}
 for p in read(d/'matched_u_pairs.jsonl'):
  a=positives.get(p['source_qid']); b=negatives.get(p['candidate_qid'])
  if not a or not b or a['vid']!=b['vid'] or a['vid']!=p['vid'] or a['partition']!='U+' or b['partition']!='U-':errors.append(f'{group}: bad matched pair {p}')
# verify clean pools
a=read(W/'master/positive_clean.jsonl'); b=read(W/'master/negative_clean.jsonl')
if len({x['qid'] for x in a})!=len(a):errors.append('duplicate positive master qid')
if len({x['qid'] for x in b})!=len(b):errors.append('duplicate negative master qid')
if errors:
 for e in errors[:30]:print(e)
 print('total errors',len(errors));sys.exit(1)
print(json.dumps({'status':'PASS','reviewed_legacy_qids':len(decisions),'released_clean_positive_qids':len(a),'released_clean_negative_qids':len(b),'groups':{g:json.load(open(OUT/g/'statistics.json')) for g in json.load(open(OUT/'summary.json'))}},ensure_ascii=False,indent=2))
