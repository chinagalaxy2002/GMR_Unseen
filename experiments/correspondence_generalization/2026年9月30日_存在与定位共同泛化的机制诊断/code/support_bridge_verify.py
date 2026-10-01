"""Independent bridge checks, repair/break attribution and actual text-input mismatch audit."""
import collections,hashlib,json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
S=Path(__file__).resolve().parents[1];D=S/'support_bridge_analysis';ROOT=S.parent;REPO=ROOT.parents[1]
r=json.loads((D/'RESULTS.json').read_text());rr=[json.loads(x) for x in (D/'ROWS.jsonl').read_text().splitlines()];freeze=json.loads((D/'FREEZE.json').read_text());failed=json.loads((S/'support_bridge_analysis_failures/attempt_001/FREEZE.json').read_text());assert freeze['definitions']==failed['definitions']
audit=json.loads((D/'TEXT_FEATURE_AUDIT.json').read_text());b=np.load(D/'BOOTSTRAP_WEIGHTS.npz');vs=b['videos'].tolist();m=b['multipliers'];vi={v:i for i,v in enumerate(vs)};assert np.array_equal(m,np.random.default_rng(3407).multinomial(len(vs),np.full(len(vs),1/len(vs)),size=1000))
def summary(point,rep):
 good=rep[np.isfinite(rep)];return {'point':float(point) if np.isfinite(point) else None,'ci95':np.quantile(good,[.025,.975]).tolist() if len(good) else None,'valid_resamples':int(len(good))}
def stat(rows,values,mask):
 ii=np.array([vi[x['vid']] for x in rows]);w=m[:,ii];v=np.array(values,dtype=float);mk=np.array(mask,dtype=bool);den=w[:,mk].sum(axis=1);boot=np.divide(w[:,mk]@v[mk],den,out=np.full(1000,np.nan),where=den>0)
 return summary(v[mk].mean() if mk.any() else np.nan,boot)
checks={};attribution={};featurestats={}
for name,z in r['groups'].items():
 rows=[x for x in rr if x['family']+'/'+x['split']==name];y=np.array([x['label'] for x in rows]);idx=np.array([vi[x['vid']] for x in rows]);pos=y==1
 for x in rows:
  windows=x['raw_windows'];p=np.array([w[2] for w in windows]);cs=[]
  for i,a in enumerate(windows):
   vals=[]
   for j,bb in enumerate(windows):
    if i==j:continue
    inter=max(0,min(a[1],bb[1])-max(a[0],bb[0]));den=a[1]-a[0]+bb[1]-bb[0]-inter;vals.append(inter/den if den>0 else 0)
   cs.append(sum(vals)/len(vals))
  c=np.array(cs);scores={'foreground':p,'agreement':c,'foreground_agreement':p*c,'scalar_geometry_control':p*np.mean(c)}
  for k,s in scores.items():
   stored=x['methods'][k];assert np.allclose(s,stored['candidate_scores'],rtol=0,atol=1e-14);assert int(np.argmax(s))+1==stored['selected_original_rank'];assert abs(float(s.max())-stored['max_score'])<1e-14
   if x['label']:
    good=np.array(x['candidate_max_gt_iou'])>=.5;assert bool(good[stored['selected_original_rank']-1])==stored['raw_correct']
    if stored['mixed_candidate_PairAcc'] is not None:
     wins=[1 if a>bb else .5 if a==bb else 0 for a,g in zip(s,good) if g for bb,h in zip(s,good) if not h];assert abs(np.mean(wins)-stored['mixed_candidate_PairAcc'])<1e-12
   else:assert x['candidate_max_gt_iou'] is None and not stored['raw_correct']
  assert x['methods']['foreground']['selected_original_rank']==1 and x['methods']['scalar_geometry_control']['selected_original_rank']==1
 for k in ['original_exist','foreground','agreement','foreground_agreement','scalar_geometry_control']:
  score=np.array([x['original_exist_score'] if k=='original_exist' else x['methods'][k]['max_score'] for x in rows]);point=roc_auc_score(y,score);stored=z['metrics'][k+'/existence_AUROC'];assert abs(point-stored['point'])<1e-12
  reps=np.array([roc_auc_score(y,score,sample_weight=w) for w in m[:,idx]]);assert np.allclose(np.quantile(reps,[.025,.975]),stored['ci'])
 raw0=np.array([x['methods']['foreground']['raw_correct'] for x in rows]);attribution[name]={}
 for k in ['agreement','foreground_agreement']:
  raw=np.array([x['methods'][k]['raw_correct'] for x in rows]);repair=pos&~raw0&raw;broken=pos&raw0&~raw;missing=pos&np.array([x['label'] and max(x['candidate_max_gt_iou'])<.5 for x in rows]);assert not np.any(missing&raw)
  mask=pos;attribution[name][k]={'repairs':int(repair.sum()),'breaks':int(broken.sum()),'net_correct_change':int(repair.sum()-broken.sum()),'repair_fraction_of_Splus':stat(rows,repair,mask),'break_fraction_of_Splus':stat(rows,broken,mask),'repair_fraction_of_raw_errors':stat(rows,repair,pos&~raw0),'break_fraction_of_raw_correct':stat(rows,broken,pos&raw0),'repaired_candidate_misses':0}
  assert abs((repair.sum()-broken.sum())/pos.sum()-z['metrics'][k+'/raw_delta_vs_original']['point'])<1e-12
 checks[name]={'rows_verified':len(rows),'all_candidate_scores_and_ranks_recomputed':True,'all_gt_independent_formula_inputs_windows_only':True,'all_mixed_query_pair_scores_recomputed':True,'five_readout_AUC_full_1000_sklearn_bootstrap_matches':True,'repair_break_raw_gain_identity':True,'scalar_control_original_rank_always':True}
 fs=[]
 for group in audit[name]:
  arrays=[]
  for q in group['qids']:
   with np.load(REPO/'features/semantic_existence_v2/A1/clip_text'/f'qid{q}.npz') as zt:a=zt['last_hidden_state'].astype(np.float32)[:32]
   arrays.append(a/(np.linalg.norm(a,axis=-1,keepdims=True)+1e-5))
  shapeeq=len({a.shape for a in arrays})==1;diff=max(float(np.abs(a-arrays[0]).max()) for a in arrays) if shapeeq else None
  fs.append({'query':group['query'],'shape_equal':shapeeq,'max_abs_normalized_input_difference':diff,'exact_equal':shapeeq and all(np.array_equal(a,arrays[0]) for a in arrays)})
 assert sum(x['exact_equal'] for x in fs)==z['coverage']['exact_feature_equal_groups']
 values=[x['max_abs_normalized_input_difference'] for x in fs if x['shape_equal']];featurestats[name]={'groups':len(fs),'shape_equal_groups':sum(x['shape_equal'] for x in fs),'shape_different_groups':sum(not x['shape_equal'] for x in fs),'exact_equal_groups':sum(x['exact_equal'] for x in fs),'same_shape_max_abs_difference_quantiles_p0_p25_p50_p75_p100':np.quantile(values,[0,.25,.5,.75,1]).tolist() if values else None,'per_group':fs,'interpretation':'input difference audit only; no new text control, no causal visual-information conclusion'}
(D/'ATTRIBUTION.json').write_text(json.dumps(attribution,ensure_ascii=False,indent=2)+'\n');(D/'TEXT_INPUT_DIFFERENCES.json').write_text(json.dumps(featurestats,ensure_ascii=False,indent=2)+'\n')
(D/'VALIDATION.json').write_text(json.dumps({'state':'passed','checks':checks,'bootstrap_seed_and_common_video_matrix_exact':True,'freeze_definitions_unchanged_after_serialization_failure':True,'failed_attempt_saved':'../support_bridge_analysis_failures/attempt_001','original_internal_AUC_check_count_correction':'source field named 30, actually 5 methods x 5 weight vectors = 25 per group; independent verifier checks all1000x5 per group','verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('Full independent verification passed',len(rr),'rows')
print('Primary repair/break', {g:{k:v for k,v in x['foreground_agreement'].items() if k in ['repairs','breaks']} for g,x in attribution.items()})
print('Feature differences', {g:{k:v for k,v in x.items() if k not in ['per_group','interpretation']} for g,x in featurestats.items()})
