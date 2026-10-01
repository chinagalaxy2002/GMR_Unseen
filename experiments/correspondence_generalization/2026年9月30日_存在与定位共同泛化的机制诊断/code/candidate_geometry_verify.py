"""Independent validation of saved diagnostics and shared bootstrap; no model access."""
import collections,json,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
S=Path(__file__).resolve().parents[1];D=S/'candidate_geometry_analysis'
r=json.loads((D/'RESULTS.json').read_text()); rows=[json.loads(x) for x in (D/'CANDIDATE_ROWS.jsonl').read_text().splitlines()]
b=np.load(D/'BOOTSTRAP_WEIGHTS.npz');vs=b['videos'].tolist();m=b['multipliers'];idx={v:i for i,v in enumerate(vs)}
assert m.shape==(1000,len(vs)) and np.all(m.sum(axis=1)==len(vs))
expected=np.random.default_rng(3407).multinomial(len(vs),np.full(len(vs),1/len(vs)),size=1000);assert np.array_equal(m,expected)
checks={}; contrasts={}
def aggregate(rr,values):
 pairs=[(idx[x['vid']],v) for x,v in zip(rr,values) if v is not None];ids=np.array([x[0] for x in pairs],dtype=int);val=np.array([x[1] for x in pairs]);c=np.bincount(ids,minlength=len(vs));s=np.bincount(ids,weights=val,minlength=len(vs));good=c>0;v=np.divide(s,c,out=np.zeros(len(vs)),where=good);den=m@good.astype(float);boot=np.divide(m@v,den,out=np.full(1000,np.nan),where=den>0)
 return v[good].mean() if good.any() else np.nan,boot,len(pairs),int(good.sum())
def pack(point,boot,nq,nv):
 ok=boot[np.isfinite(boot)];return {'point':float(point),'ci95':np.quantile(ok,[.025,.975]).tolist() if len(ok) else None,'valid_resamples':len(ok),'eligible_queries':nq,'eligible_videos':nv}
for name,g in r['groups'].items():
 rr=[x for x in rows if x['family']+'/'+x['split']==name];checks[name]={'queries':len(rr),'recomputed_pairs':0,'recomputed_correlations':0}
 for x in rr:
  c=x['candidates'];scores=np.array([z['foreground_score'] for z in c]);ov=np.array([z['max_iou'] for z in c]);correct=ov>=.5
  if correct.any() and (~correct).any():
   pairs=[1 if a>bb else .5 if a==bb else 0 for a,good in zip(scores,correct) if good for bb,bad in zip(scores,correct) if not bad]
   assert abs(np.mean(pairs)-x['PairAcc'])<1e-12 and len(pairs)==x['pair_count'];checks[name]['recomputed_pairs']+=len(pairs)
  if x['spearman_score_iou'] is not None:
   rho=np.corrcoef(rankdata(scores),rankdata(ov))[0,1];assert abs(rho-x['spearman_score_iou'])<1e-12;checks[name]['recomputed_correlations']+=1
  for t in [.5,.7]:assert x['first_correct_rank'][str(t)]==next((z['rank'] for z in c if z['max_iou']>=t),None)
  for z in c:
   a=z['window'];gt=z['matched_gt'];inter=max(0,min(a[1],gt[1])-max(a[0],gt[0]));union=a[1]-a[0]+gt[1]-gt[0]-inter
   assert abs(z['max_iou']-inter/union)<1e-12
   geo=z['geometry'];assert abs(geo['end_error_seconds']-geo['start_error_seconds']-(geo['prediction_length_seconds']-geo['gt_length_seconds']))<1e-10
 for t in [.5,.7]:
  assert abs(sum(g['metrics'][f'first_rank_{k}_iou_{t}']['query_equal']['point'] for k in range(1,11))+g['metrics'][f'no_correct_candidate_iou_{t}']['query_equal']['point']-1)<1e-12
 for key,values in {'PairAcc':[x['PairAcc'] for x in rr],**{f'R_at_{k}_iou_{t}':[any(z['max_iou']>=t for z in x['candidates'][:k]) for x in rr] for k in [1,2,3,5,10] for t in [.5,.7]}}.items():
  point,boot,nq,nv=aggregate(rr,values);a=g['metrics'][key];assert abs(point-a['video_equal']['point'])<1e-12 and np.allclose(np.quantile(boot,[.025,.975]),a['video_equal']['ci95'])
  assert nq==a['eligible_queries'] and nv==a['eligible_videos']
 contrasts[name]={}
 for typ in ['top1_correct','ranking_error','candidate_miss']:
  for field in ['abs_center_error_over_gt_length','prediction_gt_length_ratio','max_iou']:
   values=[x['candidates'][x['oracle_rank']-1]['geometry'][field]-x['candidates'][0]['geometry'][field] if x['category']==typ else None for x in rr]
   contrasts[name][f'{typ}/oracle_minus_top1/{field}']=pack(*aggregate(rr,values))
 for field in ['gt_length_seconds','abs_center_error_over_gt_length','prediction_gt_length_ratio','gt_center_video_fraction','start_error_over_gt_length','end_error_over_gt_length']:
  for w in ['top1','oracle']:
   groups=[]
   for typ in ['candidate_miss','ranking_error']:
    values=[x['candidates'][0 if w=='top1' else x['oracle_rank']-1]['geometry'][field] if x['category']==typ else None for x in rr];groups.append(aggregate(rr,values))
   a,bb=groups;contrasts[name][f'candidate_miss_minus_ranking_error/{w}/{field}']={'point':float(a[0]-bb[0]),'ci95':np.quantile(a[1]-bb[1],[.025,.975]).tolist(),'valid_resamples':int(np.isfinite(a[1]-bb[1]).sum()),'group_coverage_queries_videos':[list(a[2:]),list(bb[2:])],'interpretation':'different output-defined groups, descriptive not causal'}
(D/'GEOMETRY_CONTRASTS.json').write_text(json.dumps(contrasts,ensure_ascii=False,indent=2)+'\n')
(D/'VALIDATION.json').write_text(json.dumps({'state':'passed','shared_bootstrap_seed_matrix_exact':True,'checks':checks,'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'additional_contrasts':'derived predefined geometry comparisons; same saved bootstrap; no outcome-selected cutpoints'},ensure_ascii=False,indent=2)+'\n')
print('independent validation passed',len(rows),'queries',len(vs),'shared videos')
