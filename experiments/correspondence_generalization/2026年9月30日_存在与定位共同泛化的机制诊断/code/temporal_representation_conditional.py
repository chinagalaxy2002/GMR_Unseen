"""Post-primary conditional same-text GT-mean evidence; diagnostic, not inference."""
import json,collections,datetime
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis'
(D/'CONDITIONAL_SUPPORT_FREEZE.json').write_text(json.dumps({'at':datetime.datetime.now().isoformat(),'reason':'post-primary GT-mean sensitivity showed conditional support; test same-actual-text query-equal controls, never inference','definition':'S+ original GT-mean score vs S- full-video mean; same query cross-video pairs, query-equal; same saved common video bootstrap1000seed3407; no fit or original result change'},indent=2)+'\n')
b=np.load(D/'BOOTSTRAP_WEIGHTS.npz');vi={v:i for i,v in enumerate(b['videos'].tolist())};mul=b['multipliers'];results={}
for fam in ['throw','open_close','sit']:
 rows=[json.loads(t) for t in (D/f'{fam}_canonical_probe_rows.jsonl').read_text().splitlines()];qs=collections.defaultdict(list)
 for i,x in enumerate(rows):qs[x['query']].append(i)
 results[fam]={}
 for name in ['early_global','memory_global','memory_window','video_global']:
  summary=[]
  for ids in qs.values():
   pairs=[(a,c) for a in ids for c in ids if rows[a]['label'] and not rows[c]['label'] and rows[a]['vid']!=rows[c]['vid']];a=np.array([p[0] for p in pairs]);c=np.array([p[1] for p in pairs]);pa=np.array([rows[i]['readouts'][name]['GT_mean_score'] for i in a]);ne=np.array([rows[i]['readouts'][name]['mean_score'] for i in c]);acc=(pa>ne)+.5*(pa==ne);weights=np.vstack([np.ones(len(pairs)),mul[:,[vi[rows[i]['vid']] for i in a]]*mul[:,[vi[rows[i]['vid']] for i in c]]]);den=weights.sum(1);summary.append(np.divide(weights@acc,den,out=np.full(1001,np.nan),where=den>0))
  vals=np.nanmean(summary,axis=0);good=vals[1:][np.isfinite(vals[1:])];results[fam][name]={'point':float(vals[0]),'ci95':np.quantile(good,[.025,.975]).tolist(),'valid_resamples':len(good),'query_groups':len(summary)}
(D/'CONDITIONAL_SUPPORT.json').write_text(json.dumps({'metrics':results,'limits':'GT-dependent positive evidence localization and additional original GT-supervised probe; unequal semantic control coverage; not no-GT absolute support or proposed method performance'},indent=2)+'\n');print(json.dumps(results))
