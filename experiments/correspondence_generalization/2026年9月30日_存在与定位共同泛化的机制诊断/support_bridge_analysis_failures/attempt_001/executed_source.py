"""Frozen, GT-free candidate score hypotheses checked on original labels. No fitting/forward."""
import collections,datetime,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
S=Path(__file__).resolve().parents[1];ROOT=S.parent;REPO=ROOT.parents[1];D=S/'support_bridge_analysis'
FAMILIES=['throw','open_close','sit'];SPLITS=['seen','pseudo']
RUNS={'throw':ROOT/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1','open_close':S/'runs/open_close_qd_gmr_baseline_s3407_attempt1','sit':S/'diagnostics/sit/baseline/evaluation_bundle'}
METHODS=['foreground','agreement','foreground_agreement','scalar_geometry_control']
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def iou(a,b):
 inter=max(0,min(a[1],b[1])-max(a[0],b[0]));den=a[1]-a[0]+b[1]-b[0]-inter
 return inter/den if den>0 else 0.
def score_candidates(windows):
 # GT, labels, exist output, qid, split and duration are deliberately absent.
 p=np.asarray([w[2] for w in windows],dtype=float);n=len(p)
 overlap=np.array([[iou(a,b) if i!=j else 0. for j,b in enumerate(windows)] for i,a in enumerate(windows)])
 c=overlap.sum(axis=1)/(n-1) if n>1 else np.zeros(n)
 return {'foreground':p,'agreement':c,'foreground_agreement':p*c,'scalar_geometry_control':p*c.mean()},overlap

def auc(y,s,w):
 _,ii=np.unique(s,return_inverse=True);p=np.bincount(ii,weights=w*(y==1));n=np.bincount(ii,weights=w*(y==0),minlength=len(p));den=p.sum()*n.sum()
 return float(np.dot(p,np.cumsum(n)-n/2)/den) if den else np.nan

def pack(point,reps,level=.95):
 reps=np.asarray(reps);valid=reps[np.isfinite(reps)];a=(1-level)/2
 return {'point':float(point) if np.isfinite(point) else None,'ci_level':level,'ci':np.quantile(valid,[a,1-a]).tolist() if len(valid) else None,'valid_resamples':int(len(valid)),'invalid_resamples':1000-int(len(valid))}

def feature_groups(gt,protected):
 byq=collections.defaultdict(list)
 for i,x in enumerate(gt):byq[x['query']].append(i)
 groups=[];audit=[]
 for query,ids in byq.items():
  if {gt[i]['exist_label'] for i in ids}!={0,1} or len({gt[i]['vid'] for i in ids})<2:continue
  digests=[]
  for i in ids:
   path=REPO/'features/semantic_existence_v2/A1/clip_text'/f"qid{gt[i]['qid']}.npz";protected[str(path)]=sha(path)
   with np.load(path) as z:arr=z['last_hidden_state'].astype(np.float32)[:32]
   arr=arr/(np.linalg.norm(arr,axis=-1,keepdims=True)+1e-5)
   h=hashlib.sha256(str(arr.shape).encode()+arr.tobytes()).hexdigest();digests.append(h)
  equal=len(set(digests))==1
  if equal:groups.append(ids)
  audit.append({'query':query,'qids':[str(gt[i]['qid']) for i in ids],'normalized_feature_digests':digests,'same_shape_tokens_and_values':equal})
 return groups,audit

def main():
 D.mkdir(exist_ok=True);assert not (D/'FREEZE.json').exists(),'Do not overwrite completed/frozen analysis'
 old=json.loads((S/'candidate_geometry_analysis/FREEZE.json').read_text());protected=dict(old['protected_files_sha256']);assert all(sha(p)==h for p,h in protected.items())
 for p in (S/'candidate_geometry_analysis').iterdir():
  if p.is_file():protected[str(p)]=sha(p)
 source={};audits={};textgroups={};coverage={};allvid=set()
 for fam in FAMILIES:
  for split in SPLITS:
   name=fam+'/'+split;run=RUNS[fam];gp=run/'views'/('val_seen.jsonl' if split=='seen' else 'pseudo.jsonl');pp=run/('best_seen_predictions.jsonl' if split=='seen' else 'pseudo_predictions.jsonl');gt=read(gp);pred=read(pp);pd={str(x['qid']):x for x in pred}
   assert len(pd)==len(gt) and {str(x['qid']) for x in gt}==pd.keys() and all(pd[str(x['qid'])]['vid']==x['vid'] for x in gt)
   assert all(len(x['pred_relevant_windows_pre_exist'])==10 for x in pred)
   source[name]=(gt,pd);allvid.update(x['vid'] for x in gt);groups,audit=feature_groups(gt,protected);audits[name]=audit;textgroups[name]=groups
   coverage[name]={'rows':len(gt),'positive':sum(x['exist_label']==1 for x in gt),'negative':sum(x['exist_label']==0 for x in gt),'videos':len({x['vid'] for x in gt}),'exact_query_label_mixed_groups':len(audit),'exact_feature_equal_groups':len(groups),'exact_feature_equal_queries':sum(len(a) for a in groups)}
   protected[str(gp)]=sha(gp);protected[str(pp)]=sha(pp)
 runtime={cmd:subprocess.run(cmd,shell=True,capture_output=True,text=True).stdout for cmd in ['ps -eo pid,etimes,args','nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader']}
 dump('RUNTIME_BEFORE.json',{'at':now(),'snapshots':runtime})
 definitions={'purpose':'bridge existing candidate diagnostic to existence and raw localization; original S+/S- only, no new absence, no fitting','p':'foreground value carried by original saved candidate window; preserve original list order for all exact ties','c':'candidate i mean temporal IoU with other 9 predicted candidates; diagonal excluded, not GT IoU','primary_hypothesis':'s_i=p_i*c_i; hypothesis that mutual candidate geometry support can rank localization and distinguish existence jointly','controls':{'foreground':'s_i=p_i; original raw rank; max score tests original foreground existence evidence','agreement':'s_i=c_i; geometry alone to detect shape/length biases','scalar_geometry_control':'s_i=p_i*mean(c); identical per-query geometry summary but no candidate-specific weighting; all-zero ties keep original rank'},'existence_diagnostic':'max_i s_i, not installed as pred_exist_score; original threshold/gate unchanged; no threshold fitting or replacement','localization_diagnostic':'argmax s_i, exact ties select first original rank; saved coordinates unchanged; raw R1@.5 only; no new official gated candidate','pair_metrics':'mixed S+ candidate query PairAcc, then equal queries/video; same-video S+/S- pairs mean/video; feature-equal same-query cross-video PairAcc mean/query; endpoint bootstrap weights product; same video pairs excluded','feature_equal':'float32 last_hidden_state first32, normalize by norm+1e-5 exactly per vendor qd dataset; shape+values hashes identical; mask lengths implicit in shape; no canonical forward','bootstrap':'seed3407,1000 shared union original videos; global weighted AUC and original query-equal raw metrics; cluster query PairAcc->video; equal three families; zero denominator NA','uncertainty':'exploratory 95%; auxiliary97.5% paired deltas preserve major-endpoint standard but not confirmatory method test','entry_decision':'Require primary joint path: equal-family pseudo diagnostic AUROC and raw deltas lower97.5%>0, at least two families positive on both, seen primary AUROC/raw lower95%>=-.01, candidate-specific primary stronger than geometry-only raw at lower95%>0, feature-equal same-query support across at least two families with lower95%>.5. Necessary evidence only, not efficacy/gated/FRR/RR/VTG success. Failure means no new training round for this hypothesis; no posthoc formula/lambda sweep.','restrictions':'no old runs restart; training/update/forward0; U/test not read; no oracle used in actual scores; existing checkpoints/threshold/gate/outputs immutable'}
 dump('FREEZE.json',{'at':now(),'authorization':'User active goal: continue evidence-driven research and conditionally open a new experimental stage if sufficient discoveries; this bounded read-only bridge is first step','source_sha256':sha(__file__),'definitions':definitions,'coverage':coverage,'protected_files_sha256':protected,'seen_selected_best':'throw100/open_close100/sit77 logged (stopped), best fixed','formal_U_access':False,'training_updates':0,'new_forward_passes':0})
 dump('TEXT_FEATURE_AUDIT.json',audits);dump('state.json',{'state':'running','started_at':now(),'training_updates':0,'new_forward_passes':0})
 vs=sorted(allvid);vi={v:i for i,v in enumerate(vs)};mult=np.random.default_rng(3407).multinomial(len(vs),np.full(len(vs),1/len(vs)),size=1000)
 np.savez_compressed(D/'BOOTSTRAP_WEIGHTS.npz',videos=np.array(vs),multipliers=mult)
 results={};allrows=[];group_rep={};baseline=json.loads((S/'readout_analysis/RESULTS.json').read_text());checks={}
 for name,(gt,pd) in source.items():
  yy=np.array([x['exist_label'] for x in gt]);indices=np.array([vi[x['vid']] for x in gt]);exist=np.array([pd[str(x['qid'])]['pred_exist_score'] for x in gt]);sc={k:[] for k in METHODS};hits={k:[] for k in METHODS};pairs={k:[] for k in METHODS};mixedidx=[];loclabels=[]
  for z,x in enumerate(gt):
   windows=pd[str(x['qid'])]['pred_relevant_windows_pre_exist'];scores,overlap=score_candidates(windows)
   # Model-independent scoring is finished before original labels/GT enter readout.
   ov=np.array([max((iou(w,g) for g in x['relevant_windows']),default=0.) for w in windows]) if yy[z] else np.zeros(len(windows))
   good=ov>=.5;is_mix=yy[z] and good.any() and (~good).any()
   if is_mix:mixedidx.append(z)
   record={'family':name.split('/')[0],'split':name.split('/')[1],'qid':str(x['qid']),'vid':x['vid'],'label':int(yy[z]),'query':x['query'],'original_exist_score':float(exist[z]),'raw_windows':windows,'candidate_max_gt_iou':ov.tolist() if yy[z] else None,'candidate_overlap_off_diagonal':overlap.tolist(),'methods':{}}
   for k in METHODS:
    s=scores[k];rank=int(np.argmax(s));sc[k].append(float(s[rank]));hit=bool(yy[z] and ov[rank]>=.5);hits[k].append(hit)
    pair=(s[good,None]>s[None,~good])+.5*(s[good,None]==s[None,~good]) if is_mix else None
    if is_mix:pairs[k].append(float(pair.mean()))
    record['methods'][k]={'candidate_scores':s.tolist(),'selected_original_rank':rank+1,'max_score':float(s[rank]),'raw_correct':hit,'mixed_candidate_PairAcc':float(pair.mean()) if is_mix else None}
   allrows.append(record)
  sc={k:np.array(v) for k,v in sc.items()};hits={k:np.array(v) for k,v in hits.items()};scores_all={'original_exist':exist,**sc};original_raw=hits['foreground']
  weights=np.vstack([np.ones(len(gt)),mult[:,indices]]);aucs={k:np.array([auc(yy,s,w) for w in weights]) for k,s in scores_all.items()};pos=yy==1
  raw={k:np.divide(weights[:,pos]@h[pos],weights[:,pos].sum(axis=1),out=np.full(1001,np.nan),where=weights[:,pos].sum(axis=1)>0) for k,h in hits.items()}
  # Independent library AUC comparison includes randomly weighted clusters and ties.
  for k in scores_all:
   for b in [0,1,19,211,900]:assert abs(aucs[k][b]-roc_auc_score(yy,scores_all[k],sample_weight=weights[b]))<1e-12
  fam,split=name.split('/');oldmetric=baseline['families'][fam][split]['metrics']
  checks[name]={'original_AUROC_reproduced':abs(aucs['original_exist'][0]-oldmetric['original_AUROC']['point'])<1e-12,'original_raw_reproduced':abs(raw['foreground'][0]-oldmetric['raw_R1_05']['point'])<1e-12,'scalar_control_rank_identical':all(hits['scalar_geometry_control']==original_raw),'weighted_AUC_sklearn_30_checks_passed':True};assert all(checks[name].values())
  byv=collections.defaultdict(list)
  for i,x in enumerate(gt):byv[x['vid']].append(i)
  vp=[(v,[i for i in ids if yy[i]==1],[i for i in ids if yy[i]==0]) for v,ids in byv.items() if {yy[i] for i in ids}=={0,1}]
  qp=[]
  for ids in textgroups[name]:
   pp=[i for i in ids if yy[i]];nn=[i for i in ids if not yy[i]];edges=[(i,j) for i in pp for j in nn if gt[i]['vid']!=gt[j]['vid']]
   if edges:qp.append(edges)
  coverage[name].update(mixed_label_videos=len(vp),same_video_pairs=sum(len(p)*len(n) for _,p,n in vp),feature_equal_query_groups_with_pairs=len(qp),feature_equal_cross_video_pairs=sum(len(e) for e in qp),mixed_candidate_queries=len(mixedidx),mixed_candidate_videos=len({gt[i]['vid'] for i in mixedidx}))
  metrics={};rep={}
  def store(key,arr,level=.95):metrics[key]=pack(arr[0],arr[1:],level);rep[key]=arr
  for k in scores_all:
   store(k+'/existence_AUROC',aucs[k]);store(k+'/existence_delta_vs_original',aucs[k]-aucs['original_exist']);store(k+'/existence_delta_vs_original_975',aucs[k]-aucs['original_exist'],.975)
   if k in METHODS:
    store(k+'/raw_R1_05',raw[k]);store(k+'/raw_delta_vs_original',raw[k]-raw['foreground']);store(k+'/raw_delta_vs_original_975',raw[k]-raw['foreground'],.975)
    # S+ candidate pair summaries; no candidate-pair weighted sampling.
    ii=indices[mixedidx];cnt=np.bincount(ii,minlength=len(vs));sm=np.bincount(ii,weights=np.asarray(pairs[k]),minlength=len(vs));eligible=cnt>0;vm=np.divide(sm,cnt,out=np.zeros_like(sm),where=eligible);wb=np.vstack([np.ones(len(vs)),mult]);den=wb@eligible.astype(float);arr=np.divide(wb@vm,den,out=np.full(1001,np.nan),where=den>0);store(k+'/mixed_candidate_PairAcc_video_equal',arr)
   # Same-video original labels: aggregate pair comparisons within each video first.
   val=[];ids=[]
   for v,p,n in vp:
    a=scores_all[k][p,None];b=scores_all[k][None,n];val.append(float(((a>b)+.5*(a==b)).mean()));ids.append(vi[v])
   wb=np.vstack([np.ones(len(vs)),mult]);den=wb[:,ids].sum(axis=1);arr=np.divide(wb[:,ids]@np.array(val),den,out=np.full(1001,np.nan),where=den>0);store(k+'/same_video_PairAcc_video_equal',arr)
   # Identical actual cached text input, cross-video; per exact query group equal.
   qnum=np.zeros(1001);qden=np.zeros(1001)
   for edges in qp:
    ei=np.array([[vi[gt[i]['vid']],vi[gt[j]['vid']]] for i,j in edges]);v=np.array([float(scores_all[k][i]>scores_all[k][j])+.5*float(scores_all[k][i]==scores_all[k][j]) for i,j in edges]);ew=wb[:,ei[:,0]]*wb[:,ei[:,1]];dd=ew.sum(axis=1);available=dd>0
    qnum+=np.divide(ew@v,dd,out=np.zeros(1001),where=available);qden+=available
   qa=np.divide(qnum,qden,out=np.full(1001,np.nan),where=qden>0);store(k+'/same_query_exact_feature_PairAcc_query_equal',qa)
  for endpoint in ['existence_AUROC','raw_R1_05']:
   sourcearr=aucs if endpoint=='existence_AUROC' else raw
   for ctrl in ['foreground','agreement','scalar_geometry_control']:
    store('primary_minus_'+ctrl+'/'+endpoint,sourcearr['foreground_agreement']-sourcearr[ctrl])
  results[name]={'coverage':coverage[name],'metrics':metrics};group_rep[name]=rep
  print('bridge completed',name,flush=True)
 equal={};eqreps={}
 for split in SPLITS:
  equal[split]={};eqreps[split]={}
  for key in results['throw/'+split]['metrics']:
   arr=np.mean([group_rep[f+'/'+split][key] for f in FAMILIES],axis=0);level=.975 if key.endswith('_975') else .95
   equal[split][key]=pack(arr[0],arr[1:],level);eqreps[split][key]=arr
 # Necessary exploratory entry evidence, NOT a final efficacy verdict; no hidden fallback.
 primary='foreground_agreement';ps=equal['pseudo'];ss=equal['seen']
 def lower(x):return x['ci'][0] if x['ci'] is not None else -float('inf')
 entry={'equal_pseudo_AUROC_lower975_positive':lower(ps[primary+'/existence_delta_vs_original_975'])>0,'equal_pseudo_raw_lower975_positive':lower(ps[primary+'/raw_delta_vs_original_975'])>0,'at_least_two_families_joint_positive':sum(results[f+'/pseudo']['metrics'][primary+'/existence_delta_vs_original']['point']>0 and results[f+'/pseudo']['metrics'][primary+'/raw_delta_vs_original']['point']>0 for f in FAMILIES)>=2,'seen_AUROC_lower95_not_worse_than_minus_01':lower(ss[primary+'/existence_delta_vs_original'])>=-.01,'seen_raw_lower95_not_worse_than_minus_01':lower(ss[primary+'/raw_delta_vs_original'])>=-.01,'candidate_specific_stronger_than_geometry_only_raw':lower(ps['primary_minus_agreement/raw_R1_05'])>0,'two_families_exact_text_visual_support':sum(lower(results[f+'/pseudo']['metrics'][primary+'/same_query_exact_feature_PairAcc_query_equal'])>.5 for f in FAMILIES)>=2}
 dump('RESULTS.json',{'state':'completed','groups':results,'equal_family':equal,'entry_evidence_checks':entry,'entry_evidence_supported':all(entry.values()),'entry_is_not_joint_success':True,'training_updates':0,'new_forward_passes':0,'reproduction_checks':checks,'video_union':len(vs),'primary':primary,'limitations':definitions})
 (D/'ROWS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n' for x in allrows));dump('COVERAGE.json',coverage)
 final={p:sha(p)==h for p,h in protected.items()};assert all(final.values())
 dump('INTEGRITY.json',{'at':now(),'protected_files':len(protected),'all_unchanged':all(final.values()),'checks':final,'source_matches_freeze':True,'reproduction_checks':checks})
 dump('state.json',{'state':'completed','completed_at':now(),'rows':len(allrows),'protected_files':len(protected),'training_updates':0,'new_forward_passes':0,'new_round_entry_supported':all(entry.values())})
 print('ENTRY',entry,flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  if D.exists():dump('state.json',{'state':'failed','error':repr(e),'at':now(),'training_updates':0})
  raise
