"""Training-side multi-family diagnostics; never reads official U/test."""
import argparse, collections, hashlib, json, os, re, subprocess, sys, time, traceback
from pathlib import Path
STAGE=Path(__file__).resolve().parents[1]; HERE=STAGE.parent; REPO=HERE.parents[1]
sys.path.insert(0,str(HERE/'code'))
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def prepare():
 source=REPO/'data/release/semantic_existence_v2/A1/train.jsonl';seen=REPO/'features/semantic_existence_v2/A1/val_seen.jsonl'
 defs={'open_close':(['open','close'],r'\b(?:open|opens|opening|opened|close|closes|closing|closed|shut|shuts|shutting)\b'),'sit':(['sit'],r'\b(?:sit|sits|sitting|sat|seat|seats|seated|seating)\b')}
 manifest={'seed':3407,'families':['throw','open_close','sit'],'selection':'original training coverage only; no U/test or method outcomes','source_train_sha256':sha(source),'views':{'throw':str(HERE/'runs/pseudo_unseen_a1_throw_strict')}}
 for family,(actions,pattern) in defs.items():
  dest=STAGE/'views'/family
  if dest.exists():
   old=json.loads((dest/'view_manifest.json').read_text());assert old['source_train_sha256']==sha(source);manifest['views'][family]=str(dest);continue
  dest.mkdir(parents=True);original=[(json.loads(l),l) for l in source.read_bytes().splitlines(keepends=True)];rx=re.compile(pattern,re.I)
  dev=[(r,l) for r,l in original if (r.get('semantic_graph') or {}).get('action_base') in actions];excluded={r['vid'] for r,l in original if (r.get('semantic_graph') or {}).get('action_base') in actions or rx.search(r['query'])}
  train=[(r,l) for r,l in original if r['vid'] not in excluded];val=[(json.loads(l),l) for l in seen.read_bytes().splitlines(keepends=True) if (json.loads(l).get('semantic_graph') or {}).get('action_base') not in actions and not rx.search(json.loads(l)['query'])]
  assert not {r['vid'] for r,l in train}&{r['vid'] for r,l in dev};assert all(not rx.search(r['query']) for r,l in train)
  derived={}
  for name,data in [('train.jsonl',train),('pseudo_unseen_dev.jsonl',dev),('val_seen.jsonl',val)]:
   assert data;dest.joinpath(name).write_bytes(b''.join(l for r,l in data));derived[name]={'sha256':sha(dest/name),'rows':len(data),'labels':dict(collections.Counter(str(r['exist_label']) for r,l in data)),'videos':len({r['vid'] for r,l in data})}
  dump(dest/'view_manifest.json',{'seed':3407,'family':family,'actions':actions,'lexical_pattern':pattern,'excluded_video_count':len(excluded),'source_train_sha256':sha(source),'source_seen_sha256':sha(seen),'derived':derived,'isolation':'annotated primary action and lexical family, not complete conceptual isolation','original_rows_unchanged':True,'train_dev_video_overlap':0});manifest['views'][family]=str(dest)
 dump(STAGE/'diagnostics/FAMILY_MANIFEST.json',manifest);return manifest

def iou(a,b):
 inter=max(0,min(a[1],b[1])-max(a[0],b[0]));return inter/max(a[1]-a[0]+b[1]-b[0]-inter,1e-8)
def hit(p,r,key):
 w=sorted(p.get(key,[]),key=lambda x:x[2],reverse=True);return max((iou(w[0],g) for g in r['relevant_windows']),default=0)>=.5 if w else False

def diagnose_cpu(run,family,method):
 import numpy as np
 from sklearn.metrics import roc_auc_score
 out=STAGE/'diagnostics'/family/method;th=json.loads((run/'threshold_frozen.json').read_text())['threshold'];all_results={}
 for split,gtfile,predfile in [('pseudo','views/pseudo.jsonl','pseudo_predictions.jsonl'),('seen','views/val_seen.jsonl','best_seen_predictions.jsonl')]:
  rr=rows(run/gtfile);pp={str(p['qid']):p for p in rows(run/predfile)};assert all(str(r['qid']) in pp for r in rr)
  counts=collections.Counter();by_video=collections.defaultdict(lambda:{0:[],1:[]});by_query=collections.defaultdict(lambda:{0:[],1:[]});scores=[];labels=[]
  for r in rr:
   p=pp[str(r['qid'])];s=p['pred_exist_score'];accept=s>=th;y=r['exist_label'];scores.append(s);labels.append(y);by_video[r['vid']][y].append(s);by_query[r['query']][y].append((s,r['vid'],r['qid']))
   if y:
    raw=hit(p,r,'pred_relevant_windows_pre_exist');gated=hit(p,r,'pred_relevant_windows');counts['positive']+=1;counts['raw_correct' if raw else 'raw_incorrect']+=1;counts['raw_correct_accepted' if raw and accept else 'raw_correct_rejected' if raw else 'raw_incorrect']+=0 if not raw else 1
    counts['positive_rejected']+=int(not accept);counts['official_gated_correct']+=int(gated);counts['raw_correct_gated_wrong']+=int(raw and not gated);counts['raw_wrong_gated_correct']+=int(not raw and gated);counts['official_empty']+=int(not p['pred_relevant_windows'])
   else:counts['negative']+=1;counts['negative_accepted']+=int(accept)
  pos=counts['positive'];neg=counts['negative'];correct=counts['raw_correct'];fail=counts['raw_incorrect']+counts['raw_correct_rejected'];assert counts['raw_incorrect']+counts['raw_correct_accepted']+counts['raw_correct_rejected']==pos
  same=[float(a>b)+.5*float(a==b) for v in by_video.values() for a in v[1] for b in v[0]]
  query_pairs=[(a[0],b[0]) for v in by_query.values() for a in v[1] for b in v[0] if a[1]!=b[1]]
  qs=[float(a>b)+.5*float(a==b) for a,b in query_pairs]
  auc=float(roc_auc_score(labels,scores));totalpairs=pos*neg;same_sum=sum(same);cross=(auc*totalpairs-same_sum)/(totalpairs-len(same)) if totalpairs>len(same) else None
  # A matching query string alone is insufficient: audit actual cached feature tensors.
  consistent=0;eligible=0
  for query,v in by_query.items():
   if not v[0] or not v[1]:continue
   eligible+=1;digests=[]
   for s,vid,qid in v[0]+v[1]:
    f=REPO/'features/semantic_existence_v2/A1/clip_text'/f'qid{qid}.npz';pack=np.load(f);arr=pack['last_hidden_state'];arr=arr[:32];arr=arr/np.maximum(np.linalg.norm(arr,axis=-1,keepdims=True),1e-5);digests.append(hashlib.sha256(arr.tobytes()).hexdigest())
   consistent+=int(len(set(digests))==1)
  metrics={'AUROC':auc,'raw_R1_05':correct/pos,'gated_R1_05':counts['official_gated_correct']/pos,'FRR':counts['positive_rejected']/pos,'RR':1-counts['negative_accepted']/neg,'counts':dict(counts),'raw_correct_rejected_over_positives':counts['raw_correct_rejected']/pos,'raw_correct_rejected_over_raw_correct':counts['raw_correct_rejected']/correct if correct else None,'raw_errors_over_hard_failures':counts['raw_incorrect']/fail if fail else None,'threshold':th,'threshold_source':'seen validation only','unit':'original rows; pair combinations correlated','training_updates':0,'same_video_pairacc':float(np.mean(same)) if same else None,'same_video_pairs':len(same),'cross_video_pairacc':cross,'exact_query_cross_video_pairacc':float(np.mean(qs)) if qs else None,'exact_query_cross_video_pairs':len(qs),'exact_query_groups':eligible,'exact_query_feature_consistent_groups':consistent,'mixed_label_videos':sum(bool(v[0] and v[1]) for v in by_video.values()),'input_feature_audit':'normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control','source_hashes':{gtfile:sha(run/gtfile),predfile:sha(run/predfile)}}
  all_results[split]=metrics
 dump(out/'FAILURE_DECOMPOSITION.json',all_results);dump(out/'VISUAL_INCREMENT.json',{split:{k:v for k,v in d.items() if 'pair' in k or 'query' in k or 'video' in k} for split,d in all_results.items()});return all_results

def controlled_query(run,family,method):
 import torch, numpy as np
 from torch.utils.data import DataLoader
 import queue_worker as w
 torch.set_num_threads(4);torch.manual_seed(3407)
 ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0;ev,dsmod=w.modules('qd');model,criterion,*_=w.make_model(opt,ev,method,'qd');model.load_state_dict(ck['model']);model.eval()
 ds=w.dataset(opt,dsmod,run/'views/pseudo.jsonl','qd');groups=collections.defaultdict(list)
 for r in ds.data:groups[r['query']].append(r)
 eligible={q:rr for q,rr in groups.items() if {r['exist_label'] for r in rr}=={0,1} and len({r['vid'] for r in rr})>1}
 mapping={str(r['qid']):str(min(rr,key=lambda r:str(r['qid']))['qid']) for rr in eligible.values() for r in rr};original=ds._get_query_feat_by_qid
 ds._get_query_feat_by_qid=lambda qid:original(mapping[str(qid)])
 ds.data=[r for r in ds.data if r['query'] in eligible];scores={}
 with torch.no_grad():
  for meta,batch in DataLoader(ds,batch_size=16,num_workers=0,collate_fn=dsmod.start_end_collate):
   inputs,targets=dsmod.prepare_batch_inputs(batch,'cuda:0');out=model(**inputs);ss=out['pred_exist_logits'].sigmoid().cpu().tolist();scores.update({str(r['qid']):s for r,s in zip(meta,ss)})
 pairs=[]
 for rr in eligible.values():
  for a in rr:
   for b in rr:
    if a['exist_label']==1 and b['exist_label']==0 and a['vid']!=b['vid']:
     x=scores[str(a['qid'])];y=scores[str(b['qid'])];pairs.append((float(x>y)+.5*float(x==y),a['vid'],b['vid']))
 unique=sorted({v for _,a,b in pairs for v in [a,b]});rng=np.random.default_rng(3407);samples=[]
 for _ in range(1000):
  weights=collections.Counter(rng.choice(unique,len(unique),replace=True)) if unique else {};den=sum(weights[a]*weights[b] for _,a,b in pairs)
  if den:samples.append(sum(x*weights[a]*weights[b] for x,a,b in pairs)/den)
 dump(STAGE/'diagnostics'/family/method/'CONTROLLED_QUERY.json',{'state':'completed','training_updates':0,'query_groups':len(eligible),'rows':len(ds),'pairs':len(pairs),'pairacc':float(np.mean([x for x,a,b in pairs])) if pairs else None,'video_endpoint_bootstrap_ci95':np.quantile(samples,[.025,.975]).tolist() if samples else None,'text_input':'same normalized cached feature and mask per identical query, canonical lexicographically smallest qid; original video and labels unchanged','pure_text_pairacc_control':.5,'checkpoint_sha256':sha(run/'best.ckpt'),'scores':scores,'limitations':'original labels only; sparse correlated pairs, endpoint video bootstrap; not a causal proof or full-sample metric'})

def gradient(run,family,method,batches,checkpoint="best"):
 import torch, numpy as np
 from torch.utils.data import DataLoader
 import queue_worker as w
 torch.set_num_threads(4);torch.manual_seed(3407)
 checkpoint_path=run/(checkpoint+'.ckpt');ck=torch.load(checkpoint_path,map_location='cpu',weights_only=False);opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0;ev,dsmod=w.modules('qd');model,criterion,*_=w.make_model(opt,ev,method,'qd');model.load_state_dict(ck['model']);model.eval();criterion.eval()
 ds=w.dataset(opt,dsmod,run/'views/train.jsonl','qd');ds.data=[r for r in ds.data if r['exist_label']==1]
 gen=torch.Generator().manual_seed(3407);order=torch.randperm(len(ds),generator=gen).tolist();dl=DataLoader(ds,batch_sampler=[order[i:i+16] for i in range(0,min(len(order),batches*16),16)],num_workers=0,collate_fn=dsmod.start_end_collate)
 blocks=collections.defaultdict(list)
 for name,param in model.named_parameters():
  if 'correspondence_adapter' in name:key='adapter'
  elif 'input_vid_proj' in name or 'input_txt_proj' in name:key='input_projection'
  elif 'decoder' in name:key='decoder'
  elif 'transformer' in name:key='interaction'
  else:continue
  blocks[key].append(param)
 params=[p for ps in blocks.values() for p in ps];values=collections.defaultdict(list);norms=collections.defaultdict(list);qids=[]
 for meta,batch in dl:
  inputs,targets=dsmod.prepare_batch_inputs(batch,'cuda:0');out=model(**inputs);ld=criterion(out,targets);weighted={k:v*criterion.weight_dict[k] for k,v in ld.items() if k in criterion.weight_dict};losses={'exist':weighted['loss_exist'],'loc':sum(v for k,v in weighted.items() if k!='loss_exist' and k!='loss_saliency'),'saliency':weighted.get('loss_saliency')};grads={k:torch.autograd.grad(v,params,retain_graph=True,allow_unused=True) for k,v in losses.items() if isinstance(v,torch.Tensor) and v.requires_grad}
  offset=0
  for block,ps in blocks.items():
   for other in ['loc','saliency']:
    if other not in grads:continue
    aa=grads['exist'][offset:offset+len(ps)];bb=grads[other][offset:offset+len(ps)];pairs=[(a.flatten(),b.flatten()) for a,b in zip(aa,bb) if a is not None and b is not None]
    if not pairs:values[block+'|'+other].append(None);continue
    a=torch.cat([a for a,b in pairs]);b=torch.cat([b for a,b in pairs]);norms[block+'|'+other].append({'exist_norm':float(a.norm()),'other_norm':float(b.norm())});den=a.norm()*b.norm();values[block+'|'+other].append(float(torch.dot(a,b)/den) if den>0 else None)
   offset+=len(ps)
  qids.append([str(r['qid']) for r in meta])
 summary={}
 for k,vs in values.items():
  good=[v for v in vs if v is not None];summary[k]={'valid_batches':len(good),'invalid_batches':len(vs)-len(good),'median_cosine':float(np.median(good)) if good else None,'negative_fraction':float(np.mean(np.array(good)<0)) if good else None,'cosines':vs,'gradient_norms':norms[k]}
 dump(STAGE/'diagnostics'/family/method/('GRADIENT_RELATIONS_'+checkpoint+'.json'),{'checkpoint':str(checkpoint_path),'checkpoint_sha256':sha(checkpoint_path),'checkpoint_epoch_zero_based':ck['epoch'],'executed_source_sha256':sha(Path(__file__)),'training_updates':0,'mode':'eval; local geometry only, not causal evidence','qids':qids,'loss_weights':criterion.weight_dict,'blocks':summary,'state':'completed','interpretation':'cross-checkpoint and cross-family evidence required; duplicated best/latest epoch is not independent evidence'})

def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','cpu','controlled','gradient']);a.add_argument('--run',type=Path);a.add_argument('--family',default='throw');a.add_argument('--method',default='baseline');a.add_argument('--batches',type=int,default=16);a.add_argument('--checkpoint',choices=['best','latest'],default='best');args=a.parse_args()
 if args.action=='prepare':prepare()
 elif args.action=='cpu':diagnose_cpu(args.run,args.family,args.method)
 elif args.action=='controlled':controlled_query(args.run,args.family,args.method)
 else:gradient(args.run,args.family,args.method,args.batches,args.checkpoint)
if __name__=='__main__':main()
