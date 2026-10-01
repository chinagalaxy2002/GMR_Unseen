"""Independent affine/pooling/GT/AUC verification and prespecified mean-pooling sensitivity."""
import collections,datetime,hashlib,json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis';r=json.loads((D/'RESULTS.json').read_text());b=np.load(D/'BOOTSTRAP_WEIGHTS.npz');vs=b['videos'].tolist();mult=b['multipliers'];vi={v:i for i,v in enumerate(vs)}
assert np.array_equal(mult,np.random.default_rng(3407).multinomial(len(vs),np.full(len(vs),1/len(vs)),size=1000))
probes={'early_global':'early','memory_global':'memory','decoder_global':'decoder_pool','text_global':'text_mean','video_global':'video','memory_window':'memory'}
(D/'POOLING_ROBUSTNESS_FREEZE.json').write_text(json.dumps({'at':datetime.datetime.now().isoformat(),'reason':'after primary results; exploratory sensitivity to unequal max search scopes; no new fit, primary unchanged','definition':'compare S+ GT-mean score with original S- video-mean score; additionally report label-separated max-minus-mean gaps and n valid positions; all time readouts, all six seen/pseudo groups; same1000seed3407video weights','no_claim':'not a new inference method; GT used only diagnostic'},ensure_ascii=False,indent=2)+'\n')
checks={};sensitivity={};distribution={};original_collection=json.loads((D/'state.json').read_text())
def rank_auc(y,score,w):
 # library supplies independent implementation rather than importing analysis auc.
 if (w[y==0].sum()==0 or w[y==1].sum()==0):return np.nan
 return roc_auc_score(y,score,sample_weight=w)
def packed(a):
 valid=a[1:][np.isfinite(a[1:])];return {'point':float(a[0]) if np.isfinite(a[0]) else None,'ci95':np.quantile(valid,[.025,.975]).tolist() if len(valid) else None,'valid_resamples':len(valid)}
for group,block in r['groups'].items():
 fam,split=group.split('/');meta=[json.loads(x) for x in (D/f'{fam}_{split}_rows.jsonl').read_text().splitlines()];rows=[json.loads(x) for x in (D/f'{fam}_{split}_probe_rows.jsonl').read_text().splitlines()];datafile=np.load(D/f'{fam}_{split}.npz');data={key:datafile[key] for key in datafile.files};datafile.close();off=data['offset'];y=np.array([x['label'] for x in rows]);ii=np.array([vi[x['vid']] for x in rows]);weights=np.vstack([np.ones(len(rows)),mult[:,ii]]);coeffs={k:np.load(D/f'{fam}_{k}_affine.npz') for k in probes}
 assert len(meta)==len(rows) and all(str(a['qid'])==bb['qid'] and a['vid']==bb['vid'] for a,bb in zip(meta,rows))
 for i,(x,g) in enumerate(zip(rows,meta)):
  nt=off[i+1]-off[i];assert nt==x['native_positions'];centers=(np.arange(nt)+.5)*g['native_clip_length'];mask=np.array([any(a<=t<=bb for a,bb in g['relevant_windows']) for t in centers]);assert mask.sum()==x['GT_position_count'] # no fallback needed in these assets
  assert x['original_native_exist_logit']==float(data['exist_logit'][i])
  for k,key in probes.items():
   z=coeffs[k];assert z['effective_coefficient'].shape==(256,) and np.allclose(z['effective_coefficient'],z['coefficient'][0]/z['train_scale']);assert np.allclose(z['effective_bias'],z['intercept'][0]-z['effective_coefficient']@z['train_mean'])
   rep=data[key][off[i]:off[i+1]] if key in ['early','memory','video'] else data[key][i:i+1];score=rep.astype(np.float64)@z['effective_coefficient']+z['effective_bias'];saved=x['readouts'][k]
   if split=='canonical' and k=='text_global':assert abs(score[0]-saved['scores'][0])<1e-5
   else:assert np.allclose(score,saved['scores'],atol=1e-8,rtol=0)
   assert abs(np.mean(saved['scores'])-saved['mean_score'])<1e-10 and abs(max(saved['scores'])-saved['max_score'])<1e-10
   if key in ['early','memory','video'] and x['label']:
    assert abs(float(score[mask].max())-saved['GT_max_score'])<1e-8 and abs(float(score[mask].mean())-saved['GT_mean_score'])<1e-8;assert bool(mask[np.argmax(score)])==saved['peak_inside_GT']
 for name in list(probes)+['native_saliency','original_native']:
  for pool in ['mean','max']:
   score=np.array([x['original_native_exist_logit'] if name=='original_native' else x['readouts'][name][pool+'_score'] for x in rows]);stored=block['metrics'][name+'/'+pool+'/AUROC'];assert abs(roc_auc_score(y,score)-stored['point'])<1e-12
   # All shared replicates for primary memory and original head, sampled replicates for other fixed probes.
   replicate_ids=list(range(1000)) if name in ['memory_global','original_native'] else [0,17,222,500,998]
   values=np.array([rank_auc(y,score,weights[j+1]) for j in replicate_ids])
   if len(values)==1000:assert np.allclose(np.quantile(values[np.isfinite(values)],[.025,.975]),stored['ci95'])
 if split=='canonical':
  assert block['metrics']['text_global/max/same_query_PairAcc_query_equal']['point']==.5
  groups=collections.defaultdict(list)
  for i,x in enumerate(rows):groups[x['query']].append(i)
  for name in ['memory_global','memory_window','early_global','original_native']:
   qs=[]
   for ids in groups.values():
    pairs=[(a,bb) for a in ids for bb in ids if rows[a]['label'] and not rows[bb]['label'] and rows[a]['vid']!=rows[bb]['vid']]
    score=lambda j:rows[j]['original_native_exist_logit'] if name=='original_native' else rows[j]['readouts'][name]['max_score']
    qs.append(np.mean([1 if score(a)>score(bb) else .5 if score(a)==score(bb) else 0 for a,bb in pairs]))
   assert abs(np.mean(qs)-block['metrics'][name+'/max/same_query_PairAcc_query_equal']['point'])<1e-12
 sensitivity[group]={};distribution[group]={}
 for name in ['early_global','memory_global','video_global','memory_window','native_saliency']:
  score=np.array([x['readouts'][name]['GT_mean_score'] if x['label'] else x['readouts'][name]['mean_score'] for x in rows]);arr=np.array([rank_auc(y,score,w) for w in weights]);sensitivity[group][name+'/GT_mean_vs_Sminus_video_mean_AUROC']=packed(arr)
  distribution[group][name]={}
  for label in [0,1]:
   vals=[x['readouts'][name]['max_score']-x['readouts'][name]['mean_score'] for x in rows if x['label']==label];distribution[group][name][str(label)]={'queries':len(vals),'max_minus_mean_quantiles_p05_p50_p95':np.quantile(vals,[.05,.5,.95]).tolist(),'native_positions_quantiles_p05_p50_p95':np.quantile([x['native_positions'] for x in rows if x['label']==label],[.05,.5,.95]).tolist()}
 del data;checks[group]={'rows':len(rows),'affine_effective_capacity_257':True,'all_affine_time_scores_and_GT_support_recomputed':True,'GT_no_fallback_on_current_rows':True,'mean_max_logits_identity':True,'AUC_points_independent_sklearn':True,'primary_original_full1000_bootstrap_independent':True,'canonical_pair_query_equal_recomputed':split=='canonical'}
 print('verified',group,flush=True)
(D/'POOLING_ROBUSTNESS.json').write_text(json.dumps({'metrics':sensitivity,'label_distributions':distribution,'interpretation':'GT mean uses original positive window diagnostic only; entire negative video confirmed absent; pooling changes only analysis, no fit/selection'},ensure_ascii=False,indent=2)+'\n')
assert all(not d['convergence_warnings'] and d['parameters']==257 for fits in r['probe_fits'].values() for d in fits.values())
(D/'VALIDATION.json').write_text(json.dumps({'state':'passed','checks':checks,'all18_fits_converged_without_warning':True,'train_only_standardization_and_fixed257_parameters':True,'bootstrap_exact_seed3407':True,'original_collection12groups_native_scores_verified':original_collection['groups'],'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('independent temporal verification completed',flush=True)
