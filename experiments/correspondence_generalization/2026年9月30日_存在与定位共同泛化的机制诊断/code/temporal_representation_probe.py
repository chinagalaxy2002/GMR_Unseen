"""Matched affine probes on frozen representations; fit only original train rows."""
import collections,datetime,hashlib,json,warnings
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import roc_auc_score
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis'
FAMS=['throw','open_close','sit'];PROBES={'early_global':'early','memory_global':'memory','decoder_global':'decoder_pool','text_global':'text_mean','video_global':'video','memory_window':'memory'}
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def dump(n,x):
 p=D/n;tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=lambda z:z.item() if isinstance(z,np.generic) else str(z),allow_nan=False)+'\n');tmp.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(r):
 n=r['native_video_positions'];clip=r['native_clip_length'];centers=(np.arange(n)+.5)*clip;mask=np.zeros(n,dtype=bool)
 for a,b in r['relevant_windows']:mask|=(centers>=a)&(centers<=b)
 fallback=False
 if not mask.any() and r['exist_label']:
  for a,b in r['relevant_windows']:mask|=(np.minimum((np.arange(n)+1)*clip,b)>np.maximum(np.arange(n)*clip,a))
  fallback=bool(mask.any())
 return mask,fallback

def summaries(data,rows,key,window=False):
 if key in ['text_mean','decoder_pool']:return np.array(data[key],dtype=np.float64),np.ones(len(rows),dtype=bool)
 seq=data[key];off=data['offset'];xs=[];valid=[]
 for i,r in enumerate(rows):
  a=seq[off[i]:off[i+1]]
  if window and r['exist_label']:
   mask,_=inside(r);valid.append(mask.any());xs.append(a[mask].mean(0) if mask.any() else np.zeros(a.shape[1]))
  else:valid.append(True);xs.append(a.mean(0))
 return np.array(xs,dtype=np.float64),np.array(valid)
def collect_predictions(fam,split,models):
 rows=read(D/f'{fam}_{split}_rows.jsonl');data=np.load(D/f'{fam}_{split}.npz');off=data['offset'];sequences={k:data[k] for k in ['early','memory','video']};summ={key:summaries(data,rows,key)[0] for key in ['text_mean','decoder_pool']};records=[]
 for i,r in enumerate(rows):
  x={'family':fam,'split':split,'qid':str(r['qid']),'vid':r['vid'],'query':r['query'],'label':int(r['exist_label']),'original_native_exist_logit':float(data['exist_logit'][i]),'native_positions':r['native_video_positions'],'duration':r['duration'],'canonical_qid':r['canonical_qid'],'readouts':{}}
  mask,fallback=inside(r);x.update(GT_position_count=int(mask.sum()),GT_position_fraction=float(mask.mean()) if r['exist_label'] else None,GT_position_overlap_fallback=fallback)
  for probe,key in PROBES.items():
   model=models[probe];w=model['effective_coefficient'];bias=model['effective_bias']
   if key in sequences:a=sequences[key][off[i]:off[i+1]].astype(np.float64)@w+bias
   else:a=np.array([float(summ[key][i]@w+bias)])
   maxscore=float(a.max());entry={'mean_score':float(a.mean()),'max_score':maxscore,'scores':a.tolist(),'is_temporal':key in sequences}
   if key in sequences and r['exist_label'] and mask.any():
    peak=int(np.argmax(a));entry.update(GT_max_score=float(a[mask].max()),GT_mean_score=float(a[mask].mean()),peak_inside_GT=bool(mask[peak]),peak_time_seconds=(peak+.5)*r['native_clip_length'],GT_max_percentile=float(np.mean(a[mask].max()>a)+.5*np.mean(a[mask].max()==a)),GT_max_minus_all_max=float(a[mask].max()-maxscore))
   x['readouts'][probe]=entry
  a=data['saliency'][off[i]:off[i+1]].astype(np.float64);e={'mean_score':float(a.mean()),'max_score':float(a.max()),'scores':a.tolist(),'is_temporal':True}
  if r['exist_label'] and mask.any():e.update(GT_max_score=float(a[mask].max()),GT_mean_score=float(a[mask].mean()),peak_inside_GT=bool(mask[int(np.argmax(a))]),GT_max_percentile=float(np.mean(a[mask].max()>a)+.5*np.mean(a[mask].max()==a)),GT_max_minus_all_max=float(a[mask].max()-a.max()))
  x['readouts']['native_saliency']=e;records.append(x)
 if split=='canonical':
  # Pure text exact-tie reference: remove only batch-GEMM floating-point variation.
  groups=collections.defaultdict(list)
  for x in records:groups[x['canonical_qid']].append(x)
  for ids in groups.values():
   scores=[x['readouts']['text_global']['max_score'] for x in ids];assert max(scores)-min(scores)<1e-5
   reference=ids[0]['readouts']['text_global']['max_score']
   for x in ids:x['readouts']['text_global']={'mean_score':reference,'max_score':reference,'scores':[reference],'is_temporal':False,'numerical_exact_tie_reference':True}
 (D/f'{fam}_{split}_probe_rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n' for x in records));data.close();return records

def auc(y,s,w):
 _,ii=np.unique(s,return_inverse=True);p=np.bincount(ii,weights=w*(y==1));n=np.bincount(ii,weights=w*(y==0),minlength=len(p));den=p.sum()*n.sum();return np.dot(p,np.cumsum(n)-n/2)/den if den else np.nan

def pack(arr,level=.95):
 valid=arr[1:][np.isfinite(arr[1:])];alpha=(1-level)/2
 return {'point':float(arr[0]) if np.isfinite(arr[0]) else None,'ci95':np.quantile(valid,[alpha,1-alpha]).tolist() if len(valid) else None,'valid_resamples':len(valid),'invalid_resamples':1000-len(valid)}
def mean_stat(values,weights):
 vals=np.array([np.nan if x is None else float(x) for x in values]);ok=np.isfinite(vals);den=weights[:,ok].sum(axis=1)
 return np.divide(weights[:,ok]@vals[ok],den,out=np.full(len(weights),np.nan),where=den>0)

def metrics(records,mult,vi,canonical=False):
 yy=np.array([x['label'] for x in records]);idx=np.array([vi[x['vid']] for x in records]);weights=np.vstack([np.ones(len(records)),mult[:,idx]]);base=np.array([x['original_native_exist_logit'] for x in records]);result={};rep={}
 def store(key,arr):result[key]=pack(arr);rep[key]=arr
 orig=np.array([auc(yy,base,w) for w in weights]);store('original_native/AUROC',orig)
 # Video-pair control, every available video equal after pair summaries.
 byv=collections.defaultdict(list)
 for i,x in enumerate(records):byv[x['vid']].append(i)
 groups=[(v,[i for i in ids if yy[i]],[i for i in ids if not yy[i]]) for v,ids in byv.items() if {yy[i] for i in ids}=={0,1}]
 qgroups=collections.defaultdict(list)
 if canonical:
  for i,x in enumerate(records):qgroups[x['query']].append(i)
 wvideo=np.vstack([np.ones(len(vi)),mult]);counts={}
 for name in list(PROBES)+['native_saliency','original_native']:
  for pool in ['mean','max']:
   score=base if name=='original_native' else np.array([x['readouts'][name][pool+'_score'] for x in records]);arr=np.array([auc(yy,score,w) for w in weights]);store(name+'/'+pool+'/AUROC',arr);store(name+'/'+pool+'/delta_AUROC_vs_native_exist',arr-orig)
   for j in [0,5,551]:assert abs(arr[j]-roc_auc_score(yy,score,sample_weight=weights[j]))<1e-12
   vals=[];ids=[]
   for v,p,n in groups:
    aa=score[p,None];bb=score[None,n];vals.append(float(((aa>bb)+.5*(aa==bb)).mean()));ids.append(vi[v])
   den=wvideo[:,ids].sum(axis=1);pa=np.divide(wvideo[:,ids]@np.array(vals),den,out=np.full(1001,np.nan),where=den>0);store(name+'/'+pool+'/same_video_PairAcc_video_equal',pa)
   if canonical:
    numerator=np.zeros(1001);denom=np.zeros(1001);countpairs=0
    for ids in qgroups.values():
     edges=[(i,j) for i in ids for j in ids if yy[i] and not yy[j] and records[i]['vid']!=records[j]['vid']]
     if not edges:continue
     countpairs+=len(edges);ii=np.array([[vi[records[i]['vid']],vi[records[j]['vid']]] for i,j in edges]);v=np.array([float(score[i]>score[j])+.5*float(score[i]==score[j]) for i,j in edges]);ew=wvideo[:,ii[:,0]]*wvideo[:,ii[:,1]];d=ew.sum(axis=1);ok=d>0;numerator+=np.divide(ew@v,d,out=np.zeros(1001),where=ok);denom+=ok
    store(name+'/'+pool+'/same_query_PairAcc_query_equal',np.divide(numerator,denom,out=np.full(1001,np.nan),where=denom>0));counts['same_query_pairs']=countpairs
  for field in ['peak_inside_GT','GT_max_percentile','GT_max_minus_all_max','GT_mean_score']:
   store(name+'/'+field,mean_stat([x['readouts'].get(name,{}).get(field) for x in records],weights))
  gt=np.array([x['readouts'].get(name,{}).get('GT_max_score',np.nan) if x['label'] else (x['original_native_exist_logit'] if name=='original_native' else x['readouts'][name]['max_score']) for x in records]);ok=np.isfinite(gt)
  store(name+'/GT_window_max_vs_Sminus_video_max_AUROC',np.array([auc(yy[ok],gt[ok],w[ok]) for w in weights]));counts[name+'/GTmax_eligible_Splus']=int(sum(ok&(yy==1)))
 store('GT_duration_position_fraction',mean_stat([x['GT_position_fraction'] for x in records],weights))
 for name in ['early_global','memory_global','memory_window','video_global','native_saliency']:
  store(name+'/peak_minus_duration_chance',rep[name+'/peak_inside_GT']-rep['GT_duration_position_fraction'])
 counts.update(rows=len(records),positive=int(yy.sum()),negative=int(sum(yy==0)),videos=len(set(idx)),mixed_label_videos=len(groups),same_query_groups=len(qgroups),GT_fallback_Splus=sum(x['GT_position_overlap_fallback'] for x in records),GT_no_valid_positions_Splus=sum(x['label'] and x['GT_position_count']==0 for x in records))
 return result,rep,counts

def main():
 st=json.loads((D/'state.json').read_text());assert st['state']=='collection_completed';assert not (D/'RESULTS.json').exists(),'no overwrite'
 freeze=json.loads((D/'FREEZE.json').read_text());dump('PROBE_CODE_FREEZE.json',{'at':now(),'source_sha256':sha(__file__),'definitions_match_collection_freeze':True,'evaluation_outputs_not_yet_created':True})
 data={};fits={}
 for fam in FAMS:
  arrays=np.load(D/f'{fam}_train.npz');rr=read(D/f'{fam}_train_rows.jsonl');yy=np.array([x['exist_label'] for x in rr]);models={};fits[fam]={}
  for name,key in PROBES.items():
   x,valid=summaries(arrays,rr,key,window=name=='memory_window');scaler=StandardScaler().fit(x[valid]);z=scaler.transform(x[valid]);model=LogisticRegression(C=1.,penalty='l2',class_weight='balanced',solver='lbfgs',max_iter=1000,tol=1e-6,random_state=3407)
   with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always',ConvergenceWarning);model.fit(z,yy[valid])
   convergence=[str(e.message) for e in caught if issubclass(e.category,ConvergenceWarning)]
   effective=model.coef_[0]/scaler.scale_;bias=float(model.intercept_[0]-effective@scaler.mean_);models[name]={'effective_coefficient':effective,'effective_bias':bias}
   np.savez(D/f'{fam}_{name}_affine.npz',coefficient=model.coef_,intercept=model.intercept_,train_mean=scaler.mean_,train_scale=scaler.scale_,effective_coefficient=effective,effective_bias=bias)
   fits[fam][name]={'parameters':257,'train_queries':int(valid.sum()),'excluded_train_positive_no_GT_position':int((~valid).sum()),'fit_iterations':int(model.n_iter_[0]),'convergence_warnings':convergence,'train_summary_AUROC':roc_auc_score(yy[valid],model.decision_function(z)),'standardizer_train_only':True,'probe_original_label_fit':True,'GT_window_supervision':name=='memory_window'}
   assert np.allclose(x[valid]@effective+bias,model.decision_function(z),atol=1e-8);print('probe fitted',fam,name,fits[fam][name]['fit_iterations'],flush=True)
  arrays.close();dump('PROBE_FITS.json',fits)
  for split in ['seen','pseudo','canonical']:data[fam+'/'+split]=collect_predictions(fam,split,models)
 vs=sorted({x['vid'] for rr in data.values() for x in rr});vi={v:i for i,v in enumerate(vs)};mult=np.random.default_rng(3407).multinomial(len(vs),np.full(len(vs),1/len(vs)),size=1000);np.savez_compressed(D/'BOOTSTRAP_WEIGHTS.npz',videos=np.array(vs),multipliers=mult)
 result={};reps={}
 for group,rr in data.items():
  m,rep,coverage=metrics(rr,mult,vi,group.endswith('canonical'));result[group]={'metrics':m,'coverage':coverage};reps[group]=rep;print('evaluated',group,flush=True)
 equal={};difference={}
 for split in ['seen','pseudo','canonical']:
  equal[split]={k:pack(np.mean([reps[f+'/'+split][k] for f in FAMS],axis=0)) for k in reps['throw/'+split]}
 for fam in FAMS+['equal_family']:
  if fam=='equal_family':difference[fam]={k:pack(np.mean([reps[f+'/pseudo'][k]-reps[f+'/seen'][k] for f in FAMS],axis=0)) for k in reps['throw/seen']}
  else:difference[fam]={k:pack(reps[fam+'/pseudo'][k]-reps[fam+'/seen'][k]) for k in reps[fam+'/seen']}
 dump('RESULTS.json',{'state':'completed','groups':result,'equal_family':equal,'pseudo_minus_seen_descriptive':difference,'probe_fits':fits,'shared_video_union':len(vs),'original_model_updates':0,'fitted_probe_parameters':6*257*3,'saliency_weight':{f:freeze['options'][f]['lw_saliency'] for f in FAMS},'limits':'exploratory affine accessibility; no representation absence proof, no formalGMR/VTG efficacy, no fitted U or pseudo labels'})
 st.update(state='probe_analysis_completed',probe_fits=18,fitted_probe_parameters=4626,original_model_updates=0,finished_probe_at=now());dump('state.json',st);print('temporal probe analysis complete',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:dump('PROBE_FAILURE.json',{'at':now(),'error':repr(e)});raise
