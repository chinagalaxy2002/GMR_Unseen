#!/usr/bin/env python3
"""Build v3 groups from adjudicated clean pools and the persisted video split."""
import json, glob, re, os, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'data/processed/semantic_existence_v3'
REL2=ROOT/'data/release/semantic_existence_v2'
OUT=WORK/'splits'

def read(path):
 with open(path) as f:
  for line in f:
   if line.strip(): yield json.loads(line)
def write(path, rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
  temp=f.name
 os.replace(temp,path)
def canon(s):
 s=(s or '').lower().replace('sofa','couch')
 s=re.sub(r'[^a-z0-9 ]',' ',s)
 return re.sub(r'\s+',' ',s).strip()
def action(r):
 g=r.get('semantic_graph') or {}; a=(g.get('action_class') or g.get('action_base') or g.get('action') or '').lower()
 if a in {'put','put_down','put_in','put_on','put_back','place'}: return 'physical_place'
 if a in {'take','take_out','pick_up','pick-up'}: return 'physical_take'
 return a
def anchor(r):
 g=r.get('semantic_graph') or {}
 return canon(g.get('object_concept') or g.get('object') or g.get('location') or '')
def is_held(r, spec):
 if r.get('events'):
  return any(is_held({'semantic_graph':{'action_class':ev.get('action_family',''),'object':ev.get('anchor_object') or ev.get('theme') or ev.get('location') or ''}},spec) for ev in r['events'])
 a=action(r); o=anchor(r)
 if spec['axis']=='action_family': return a in spec['held_action_families']
 for ha,ho in spec['held_compositions']:
  if a==ha and (ho in o or (ho=='couch' and 'sofa' in o)): return True
 return False
# Gather all legacy released qids; validate cross-group consistency.
legacy={}
for p in REL2.glob('*/*.jsonl'):
 if p.name not in {'train.jsonl','val.jsonl','test.jsonl'}: continue
 for r in read(p): legacy.setdefault(r['qid'],r)
# Positive normalized event records indexed to qid and existing source qids.
rawpos={r['qid']:r for r in read(WORK/'positives/raw.jsonl')}
events={}
for e in read(WORK/'positives/events.jsonl'):
 for q in e.get('qids',[]): events[q]=e
pos_dis={r['qid']:r for r in read(WORK/'positives/dispositions.jsonl')}
dec={r['candidate_qid']:r for r in read(WORK/'review/decisions.jsonl')}
correction_path=WORK/'review/semantic_overrides.jsonl'
semantic_overrides={r['qid']:r for r in read(correction_path)} if correction_path.exists() else {}
vidsplit={r['vid']:r['split'] for r in read(WORK/'inputs/video_splits.jsonl')}
specs=json.load(open(WORK/'selection/split_specs.json'))['groups']
# Restore source-positive queries with event normalization metadata.
positives=[]
for q,e in events.items():
 if q not in rawpos or pos_dis.get(q,{}).get('semantic_review_status')!='resolved': continue
 r=dict(rawpos[q]); r['events']=e['events']; r['semantic_status']='resolved'; r['construction_type']='original_positive'
 if e.get('semantic_correction_revision'): r['semantic_correction_revision']=e['semantic_correction_revision']
 r['source_qid']=q; positives.append(r)
# Clean negative pool uses only qids whose complete-event review is keep/distinct.
negatives=[]
for q,d in dec.items():
 if d['decision']!='keep' or d['relation']!='distinct' or q not in legacy: continue
 r=dict(legacy[q]); r['source_qid']=d['source_qid']; r['construction_type']='legacy_adjudicated_negative'; r['review_decision']=q
 if q in semantic_overrides:
  correction=semantic_overrides[q]
  if correction['query']!=r['query']: raise ValueError(f'Semantic override query mismatch: {q}')
  r['events']=correction['events']
  r['semantic_graph']=correction['semantic_graph']
  r['semantic_correction_revision']=correction['revision']
 negatives.append(r)
# Deduplicate by qid and assign one video split to every row.
positives=list({r['qid']:r for r in positives}.values()); negatives=list({r['qid']:r for r in negatives}.values())
for r in positives+negatives:
 r['split']=vidsplit.get(r['vid'],r.get('source_split') or 'train')
for r in positives+negatives:
 if r['split'] not in {'train','val','test'}: raise ValueError(r)
# Per group: use complete reviewed events when available; legacy graphs are fallback.
summary={}
for group,spec in specs.items():
 rows=[]
 for r in positives:
  evs=r.get('events',[])
  # v3 normalized events carry action_family and anchors; adapt to split predicates.
  testrow=dict(r); testrow['semantic_graph']={'action_class':evs[0].get('action_family','') if evs else '', 'object': ' '.join(str(x.get('anchor_object') or x.get('theme') or x.get('location') or '') for x in evs)}
  # use any event hit, not only first event
  held=False
  for ev in evs:
   testrow['semantic_graph']={'action_class':ev.get('action_family',''),'object':ev.get('anchor_object') or ev.get('theme') or ev.get('location') or ''}
   if is_held(testrow,spec): held=True; break
  held_test=held and r['split'] in {'val','test'}
  if held and r['split']=='train': continue
  if held_test:
   partition='U+'; status='unseen'
  else:
   partition='S+'; status='seen'
  o=dict(r); o.update(partition=partition,exist_label=1,existence_status='present',semantic_status=status,novelty_type='unseen' if held else 'seen')
  rows.append(o)
 for r in negatives:
  held=is_held(r,spec)
  # train only includes seen negatives; test/val retain held and seen rows
  if held and r['split']=='train': continue
  if r['split']=='train' and not held: partition='S-'
  elif held: partition='U-'
  else: partition='S-'
  o=dict(r); o.update(partition=partition,exist_label=0,existence_status='absent',semantic_status='unseen' if held else 'seen',novelty_type='unseen' if held else 'seen')
  rows.append(o)
 # stable qid order, unique.
 rows=list({r['qid']:r for r in rows}.values())
 d=OUT/group; d.mkdir(parents=True,exist_ok=True)
 train=[r for r in rows if r['split']=='train' and r['partition'] in {'S+','S-'}]
 val=[r for r in rows if r['split']=='val']; test=[r for r in rows if r['split']=='test']
 write(d/'train.jsonl',train); write(d/'val.jsonl',val); write(d/'test.jsonl',test)
 write(d/'val_seen.jsonl',[r for r in val if r['partition'] in {'S+','S-'}])
 # Exact matched pairs use source links and same video, one candidate per source.
 posmap={r['qid']:r for r in rows if r['exist_label']==1}; negmap={r['qid']:r for r in rows if r['exist_label']==0}
 pairs=[]
 for n in sorted(negatives,key=lambda x:x['qid']):
  p=posmap.get(n.get('source_qid'))
  nn=negmap.get(n['qid'])
  if p and nn and p['vid']==nn['vid'] and p['split']==nn['split'] and p['partition'][0]==nn['partition'][0]:
   pairs.append({'source_qid':p['qid'],'candidate_qid':nn['qid'],'vid':p['vid'],'split':p['split'],'partition':p['partition'][0],'positive_query':p['query'],'negative_query':nn['query']})
 write(d/'matched_u_pairs.jsonl',[p for p in pairs if p['partition']=='U'])
 write(d/'test_matched_u.jsonl',[p for p in pairs if p['split']=='test' and p['partition']=='U'])
 from collections import Counter
 cnt=Counter((r['split'],r['partition']) for r in rows)
 inv={'group':group,'spec':spec,'counts':{f'{s}_{p}':n for (s,p),n in sorted(cnt.items())},'unique_videos':len({r['vid'] for r in rows}),'matched_u_pairs':sum(p['partition']=='U' for p in pairs)}
 json.dump(inv,open(d/'semantic_inventory.json','w'),ensure_ascii=False,indent=2)
 json.dump({'group':group,'rows':len(rows),'train':len(train),'val':len(val),'test':len(test),'partition_counts':dict(Counter(r['partition'] for r in rows))},open(d/'statistics.json','w'),ensure_ascii=False,indent=2)
 summary[group]=inv
write(WORK/'master/positive_clean.jsonl',positives); write(WORK/'master/negative_clean.jsonl',negatives)
json.dump(summary,open(OUT/'summary.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({'positive_clean':len(positives),'negative_clean':len(negatives),'groups':{k:v['counts'] for k,v in summary.items()}},ensure_ascii=False,indent=2))
