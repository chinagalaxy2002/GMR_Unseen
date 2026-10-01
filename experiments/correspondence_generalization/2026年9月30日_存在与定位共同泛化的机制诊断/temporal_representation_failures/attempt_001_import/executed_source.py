"""Frozen-checkpoint representation extraction; no optimizer, backward, or old outputs written."""
import collections,datetime,hashlib,json,sys,subprocess
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parents[1];ROOT=S.parent;REPO=ROOT.parents[1];D=S/'temporal_representation_analysis'
sys.path[:0]=[str(ROOT/'code'),str(REPO)]
RUNS={'throw':ROOT/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1','open_close':S/'runs/open_close_qd_gmr_baseline_s3407_attempt1','sit':S/'diagnostics/sit/baseline/evaluation_bundle'}
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def dump(n,x):
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=lambda z:z.item() if isinstance(z,np.generic) else str(z),allow_nan=False)+'\n');tmp.replace(p)
def main():
 import torch
 from torch.utils.data import DataLoader
 import queue_worker as w
 from models.qd_detr_gmr import build_model
 torch.set_num_threads(4);torch.manual_seed(3407);np.random.seed(3407)
 D.mkdir(exist_ok=True);assert not (D/'FREEZE.json').exists(),'do not overwrite frozen run'
 old=json.loads((S/'support_bridge_analysis/FREEZE.json').read_text());protected=dict(old['protected_files_sha256']);assert all(sha(p)==h for p,h in protected.items())
 for dirname in ['support_bridge_analysis','candidate_geometry_analysis','readout_analysis']:
  for p in (S/dirname).iterdir():
   if p.is_file():protected[str(p)]=sha(p)
 inputs={};canonical={};opts={};assets=set();coverage={}
 for fam,run in RUNS.items():
  ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);opt=ck['opt'];assert opt.hidden_dim==256 and opt.max_q_l==32
  opts[fam]={k:getattr(opt,k,None) for k in ['hidden_dim','max_q_l','max_v_l','clip_length','max_ts_val','lw_saliency','exist_pool']};opts[fam]['epoch']=ck['epoch'];del ck
  for split,filename in [('train','train'),('seen','val_seen'),('pseudo','pseudo')]:
   gp=run/'views'/f'{filename}.jsonl';gt=read(gp);inputs[fam+'/'+split]=str(gp);protected[str(gp)]=sha(gp);assets.update(REPO/'features/semantic_existence_v2/A1/clip_text'/f"qid{x['qid']}.npz" for x in gt)
   for x in gt:
    for name in ['vid_clip','vid_slowfast']:assets.add(Path('/home/guoxiangyu/paper/新建文件夹/charades')/name/f"{x['vid']}.npz")
   coverage[fam+'/'+split]={'rows':len(gt),'positive':sum(x['exist_label']==1 for x in gt),'negative':sum(x['exist_label']==0 for x in gt),'videos':len({x['vid'] for x in gt})}
   if split=='pseudo':
    byq=collections.defaultdict(list)
    for x in gt:byq[x['query']].append(x)
    groups=[rr for rr in byq.values() if {x['exist_label'] for x in rr}=={0,1} and len({x['vid'] for x in rr})>1];canonical[fam]={str(x['qid']):str(min(rr,key=lambda x:str(x['qid']))['qid']) for rr in groups for x in rr}
  train=read(inputs[fam+'/train']);seen=read(inputs[fam+'/seen']);pseudo=read(inputs[fam+'/pseudo']);assert not {x['vid'] for x in train}&{x['vid'] for x in pseudo};assert not {str(x['qid']) for x in train}&{str(x['qid']) for x in seen}
  for p in [run/'best.ckpt',run/'latest.ckpt',run/'threshold_frozen.json']:protected[str(p)]=sha(p)
 print('hashing',len(assets),'input feature assets',flush=True)
 for p in sorted(assets):assert p.exists(),p;protected[str(p)]=sha(p)
 for p in [REPO/'models/qd_detr_gmr/model.py',REPO/'models/qd_detr_gmr/transformer.py',ROOT/'code/vendor/qd_dataset.py',ROOT/'code/queue_worker.py'] :protected[str(p)]=sha(p)
 definitions={'authorization':'user proposed zero-new-backbone representation diagnostic with matched small readout; fitting probes allowed, full-model training not authorized','hypotheses':['S+ GT windows hold elevated absolute support','video-wide time support distinguishes original S+/S-','seen to pseudo contrast locates readout accessibility vs representation limits'], 'representations':{'early':'t2v_encoder output valid video tokens after global prefix, before temporal encoder','memory':'transformer memory_local valid time tokens before decoder','video':'input_vid_proj valid tokens; pure visual+TEF control','text':'input_txt_proj valid text tokens pooled mean; pure text control','decoder':'hs[-1] pooled exactly as original exist_head'},'capacity':'six probes per family, each affine256+1=257 parameters, no hidden layers; standardization train-only','probe_fits':{'early_global':'linear logistic on full-video mean early, original video existence labels only','memory_global':'linear logistic on full-video mean memory, original existence labels only','decoder_global':'same linear logistic on original existence pooled decoder states','text_global':'same linear logistic on projected text mean','video_global':'same linear logistic on projected input video mean','memory_window':'same linear logistic; S+ train summary mean over original GT-covered positions, S- full-video mean; GT outside S+ never negative; separately marks additional temporal supervision'},'fit':'sklearn LogisticRegression(C=1,penalty=l2,class_weight=balanced,solver=lbfgs,max_iter=1000,tol=1e-6,random_state=3407), all original train rows, no grid, no seen/pseudo/U fitting or model selection','readout':'a_t=w*z(h_t)+b no time softmax; both mean and max_t as fixed pooled diagnostics. Train global probe on mean, compare mean/max without picking best. Window probe uses train GT summary only; inference max/mean does not use GT','GT_positions':'centers (t+.5)*native clip_length in any original GT interval; if no centers but bin overlaps a positive GT, deterministic overlapping clips fallback. No center/overlap => unavailable window probe row and reported; inference never sees GT','metrics':'video existence global weighted AUROC; S+ in-window-max vs all original S- full-video-max AUROC; per-S+ peak-in-GT and percentile rank of GT support relative to own sequence; no outside-window absence labels. native saliency untrained(weight0) auxiliary; original exist/raw/gated unchanged','comparison':'same affine capacity; memory_global vs original existence uses same video labels and target; memory_window gain is supervised accessibility, not proof original head faulty. Readout failure is capacity/optimization-limited, not proof information absent','bootstrap':'shared original-video union across six eval groups/canonical;1000 seed3407, exploratory95% and paired probe-original AUROC deltas. No candidate training success or confirmation','controls':'same-query canonical text feature+mask from lexicographic qid as prior CONTROLLED_QUERY; exact same text input, new frozen forward; do not index-join decoder slot scores to saved windows; pure text scores must tie within each controlled group','restrictions':'original model eval, requires_grad false,inference_mode; original parameter updates0; probe parameter fits separately counted; no resume training, no teacher/window, no new data/absence, no officialU/test, no changed threshold/gate/checkpoint'}
 dump('FREEZE.json',{'at':now(),'definitions':definitions,'source_sha256':sha(__file__),'inputs':inputs,'options':opts,'coverage':coverage,'canonical_qid_map':canonical,'protected_files_sha256':protected,'feature_assets':len(assets),'original_model_updates':0,'new_backbone_models':0,'probe_parameter_fitting':'separately accounted, six x257/family'})
 dump('RUNTIME_BEFORE.json',{'at':now(),'ps':subprocess.run(['ps','-eo','pid,etimes,args'],capture_output=True,text=True).stdout,'GPU':subprocess.run(['nvidia-smi'],capture_output=True,text=True).stdout})
 state={'state':'collecting','pid':__import__('os').getpid(),'started_at':now(),'original_model_updates':0,'probe_parameter_updates':0,'groups':{}};dump('state.json',state)
 for fam,run in RUNS.items():
  ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0;ev,dsmod=w.modules('qd');model,criterion=build_model(opt);model.load_state_dict(ck['model']);model.to('cuda:0').eval();model.requires_grad_(False)
  before={k:hashlib.sha256(v.cpu().numpy().tobytes()).hexdigest() for k,v in model.state_dict().items()};captured={}
  def save(key):
   def hook(m,args,out):captured[key]=out
   return hook
  handles=[model.transformer.register_forward_hook(save('transformer')),model.transformer.t2v_encoder.register_forward_hook(save('early')),model.input_vid_proj.register_forward_hook(save('video')),model.input_txt_proj.register_forward_hook(save('text'))]
  for split in ['train','seen','pseudo','canonical']:
   name=fam+'/'+split;output=D/f'{fam}_{split}.npz';assert not output.exists()
   gp=inputs[fam+'/pseudo' if split=='canonical' else name];ds=w.dataset(opt,dsmod,gp,'qd',labels=False)
   if split=='canonical':
    mapping=canonical[fam];original=ds._get_query_feat_by_qid;ds._get_query_feat_by_qid=lambda qid:original(mapping[str(qid)]);ds.data=[x for x in ds.data if str(x['qid']) in mapping]
   oldpred={str(x['qid']):x for x in read(run/('best_seen_predictions.jsonl' if split=='seen' else 'pseudo_predictions.jsonl'))} if split in ['seen','pseudo'] else None
   oldcanon=json.loads((S/f'diagnostics/{fam}/baseline/CONTROLLED_QUERY.json').read_text())['scores'] if split=='canonical' else None
   arrays={k:[] for k in ['early','memory','video','text_mean','decoder_pool','saliency','exist_logit']};metadata=[];offset=[0];exact=0;canonical_maxerr=0.
   with torch.inference_mode():
    for batchno,(meta,batch) in enumerate(DataLoader(ds,batch_size=16,num_workers=0,collate_fn=dsmod.start_end_collate)):
     inp,_=dsmod.prepare_batch_inputs(batch,'cuda:0');out=model(**inp);hs,_,memory,glob=captured['transformer'];early=captured['early'].transpose(0,1);length=inp['src_vid'].shape[1];assert early.shape[1]>=length+1;pool=hs[-1].mean(dim=1) if model.exist_pool=='mean' else hs[-1].max(dim=1).values
     for i,x in enumerate(meta):
      n=int(inp['src_vid_mask'][i].sum());nt=int(inp['src_txt_mask'][i].sum());qid=str(x['qid']);exist=float(out['pred_exist_logits'][i]);sig=float(out['pred_exist_logits'][i].sigmoid());
      if oldpred is not None:exact+=float(f'{sig:.4f}')==oldpred[qid]['pred_exist_score']
      if oldcanon is not None:canonical_maxerr=max(canonical_maxerr,abs(sig-oldcanon[qid]))
      for k,t in [('early',early[i,1:n+1]),('memory',memory[i,:n]),('video',captured['video'][i,:n]),('saliency',out['saliency_scores'][i,:n])]:arrays[k].append(t.cpu().numpy().astype(np.float32))
      arrays['text_mean'].append(captured['text'][i,:nt].mean(0).cpu().numpy());arrays['decoder_pool'].append(pool[i].cpu().numpy());arrays['exist_logit'].append(exist);metadata.append({**x,'native_video_positions':n,'native_clip_length':opt.clip_length,'canonical_qid':canonical[fam][qid] if split=='canonical' else None});offset.append(offset[-1]+n)
     if batchno%100==0:state['active']={'family':fam,'split':split,'rows_done':len(metadata),'rows_total':len(ds),'at':now()};dump('state.json',state);print(name,len(metadata),'/',len(ds),flush=True)
   payload={k:np.concatenate(arrays[k],axis=0) if k in ['early','memory','video','saliency'] else np.stack(arrays[k]) for k in arrays};payload['offset']=np.array(offset,dtype=np.int64)
   np.savez_compressed(output,**payload);(D/f'{fam}_{split}_rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in metadata))
   if oldpred is not None:assert exact==len(metadata),(name,exact,len(metadata))
   if oldcanon is not None:assert canonical_maxerr<1e-5,(name,canonical_maxerr)
   state['groups'][name]={'rows':len(metadata),'time_positions':offset[-1],'saved_exist_exact_matches':exact if oldpred is not None else None,'canonical_original_score_max_abs_difference':canonical_maxerr if oldcanon is not None else None,'output_sha256':sha(output),'metadata_sha256':sha(D/f'{fam}_{split}_rows.jsonl')};dump('state.json',state)
  after={k:hashlib.sha256(v.cpu().numpy().tobytes()).hexdigest() for k,v in model.state_dict().items()};assert before==after
  state.setdefault('model_state_unchanged',{})[fam]=True
  for h in handles:h.remove()
  del model,ck,criterion;torch.cuda.empty_cache()
 checks={p:sha(p)==h for p,h in protected.items()};assert all(checks.values());dump('COLLECTION_INTEGRITY.json',{'all_original_assets_unchanged':True,'protected_paths':len(checks),'checks':checks,'model_state_unchanged':state['model_state_unchanged'],'original_model_updates':0})
 state.update(state='collection_completed',finished_collection_at=now(),active=None);dump('state.json',state);print('all frozen representations collected',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  if D.exists():dump('FAILURE.json',{'at':now(),'error':repr(e),'original_model_updates':0})
  raise
