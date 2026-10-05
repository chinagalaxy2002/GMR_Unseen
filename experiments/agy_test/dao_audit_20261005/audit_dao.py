"""Independent frozen-checkpoint and feature audit; no training."""
from pathlib import Path
import importlib.util
import json
import sys
import hashlib
from collections import defaultdict

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/agy_test/decomposed_action_object_verifier"
OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location("dao_training_audit",BASE/"train_and_eval.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
torch.set_num_threads(2)
device=torch.device('cuda:0')
SPLITS=mod.SPLITS
VISUAL=['v_sf_cand','v_sf_start','v_sf_end','v_sf_glob','v_clip_cand','v_clip_glob']
MODEL_FIELDS=VISUAL+['q_act','q_obj','h_pool','orig_logits','fg_max']

def read(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return h.hexdigest()

def calc(score,d,pairs,th=None):
    sm=np.isin(d['partitions'],['S+','S-']);um=~sm;y=d['labels']
    sa=float(roc_auc_score(y[sm],score[sm]));ua=float(roc_auc_score(y[um],score[um]))
    ix={str(q):i for i,q in enumerate(d['qids'])}
    vals=[float(score[ix[str(p['positive_qid'])]]>score[ix[str(p['negative_qid'])]])+.5*float(score[ix[str(p['positive_qid'])]]==score[ix[str(p['negative_qid'])]]) for p in pairs]
    r=dict(Seen_AUROC=sa,Unseen_AUROC=ua,Gap=sa-ua,Matched_PairAcc=float(np.mean(vals)),matched_pair_n=len(vals))
    if th is not None:
        accept=score>=th
        for pre,mask in [('Seen',sm),('Unseen',um)]:
            rej=~accept[mask];yy=y[mask]
            tp=np.sum(rej&(yy==0));fp=np.sum(rej&(yy==1));fn=np.sum(~rej&(yy==0))
            r[pre+'_RejF1']=float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.
        r.update(U_pos_FRR=float((~accept[d['partitions']=='U+']).mean()*100),U_neg_RR=float((~accept[d['partitions']=='U-']).mean()*100))
    return r

def exact_query_scores(score,d,meta):
    groups=defaultdict(list)
    for i,q in enumerate(d['qids']):
        if d['partitions'][i] in ['U+','U-']:groups[meta[str(q)]['query']].append(i)
    vals=[];counts=[]
    for q,ii in groups.items():
        pos=[i for i in ii if d['labels'][i]==1];neg=[i for i in ii if d['labels'][i]==0]
        vv=[float(score[a]>score[b])+.5*float(score[a]==score[b]) for a in pos for b in neg if d['vids'][a]!=d['vids'][b]]
        if vv:vals.append(float(np.mean(vv)));counts.append(len(vv))
    return dict(query_groups=len(vals),pair_n=sum(counts),macro=float(np.mean(vals)) if vals else None,weighted=float(np.average(vals,weights=counts)) if vals else None)

def weighted_auc_prepared(y,score,vid_indices):
    order=np.argsort(score,kind='stable');yy=y[order];ss=score[order];vv=vid_indices[order]
    starts=np.r_[0,np.flatnonzero(np.diff(ss))+1]
    def fn(counts):
        w=counts[vv];p=np.add.reduceat(w*(yy==1),starts);n=np.add.reduceat(w*(yy==0),starts)
        return float((p*(np.cumsum(n)-n/2)).sum()/(p.sum()*n.sum())) if p.sum()*n.sum() else np.nan
    return fn

report={'scope':'frozen checkpoints; no retraining; interventions are feature-level diagnostic controls','splits':{},'sha256':{}}
boot={}
for split in SPLITS:
    print('START',split,flush=True)
    npz=np.load(BASE/'features'/split/'test.npz')
    d={k:npz[k] for k in MODEL_FIELDS+['qids','vids','labels','partitions','construction_types','best_spans']}
    vnpz=np.load(BASE/'features'/split/'val.npz')
    vd={k:vnpz[k] for k in MODEL_FIELDS+['labels','partitions']}
    cpath=BASE/'runs'/split/'verifier_checkpoint.pt'
    ckpt=torch.load(cpath,map_location='cpu',weights_only=False)
    model=mod.GatedDAOVerifier().to(device)
    model.load_state_dict(ckpt['state_dict']);model.eval()
    batch={k:torch.tensor(d[k],dtype=torch.float32,device=device) for k in MODEL_FIELDS}
    vb={k:torch.tensor(vd[k],dtype=torch.float32,device=device) for k in MODEL_FIELDS}
    with torch.no_grad():
        result=model(batch);val_result=model(vb)
    sg={k:x.detach().cpu().numpy() for k,x in result.items() if x.ndim>0}
    preds=read(BASE/'runs'/split/'predictions.jsonl');pmap={str(p['qid']):p for p in preds}
    saved=np.array([pmap[str(q)]['final_logit'] for q in d['qids']])
    m=json.loads((BASE/'runs'/split/'metrics.json').read_text())
    pairs=read(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')
    meta={str(x['qid']):x for x in read(ROOT/'data/release/semantic_existence_v2'/split/'test.jsonl')}
    sv=np.isin(vd['partitions'],['S+','S-']);vals=val_result['s_exist'].cpu().numpy()
    th=mod.choose_val_seen_threshold(vals[sv],vd['labels'][sv])
    gate=torch.sigmoid(5*(batch['fg_max']-.2)).cpu().numpy()
    aa=float(result['alpha_act'].item());ao=float(result['alpha_obj'].item())
    scores={
        'baseline':d['orig_logits'],
        'full':sg['s_exist'],
        'detector_only':sg['s_det'],
        'detector_plus_action':sg['s_det']+gate*aa*sg['ev_act'],
        'detector_plus_object':sg['s_det']+gate*ao*sg['ev_obj'],
        'action_evidence_only':sg['ev_act'],
        'object_evidence_only':sg['ev_obj'],
        'negative_text_prior':-aa*sg['prior_act']-ao*sg['prior_obj'],
    }
    # Diagnostic interventions use the already trained model, not separately fit controls.
    # Local streams permutation leaves query-conditioned detector states fixed.
    rng=np.random.default_rng(3407)
    permutations=[]
    for repeat in range(5):
        order=rng.permutation(len(saved))
        # Explicitly avoid donating descriptors from the same video.
        bad=d['vids'][order]==d['vids']
        for _ in range(20):
            if not bad.any():break
            order[bad]=rng.integers(len(saved),size=int(bad.sum()))
            bad=d['vids'][order]==d['vids']
        donor=torch.tensor(order,device=device)
        shuffled={k:(x[donor] if k in VISUAL else x) for k,x in batch.items()}
        with torch.no_grad():sc=model(shuffled)['s_exist'].cpu().numpy()
        permutations.append(calc(sc,d,pairs))
        if repeat==0:scores['local_video_permuted_0']=sc
    zeros={k:(torch.zeros_like(x) if k in VISUAL+['h_pool','orig_logits'] else torch.full_like(x,.5) if k=='fg_max' else x) for k,x in batch.items()}
    with torch.no_grad():scores['zero_visual_frozen_model']=model(zeros)['s_exist'].cpu().numpy()
    r={'checks':{},'metrics':{k:calc(s,d,pairs,ckpt['threshold'] if k=='full' else None) for k,s in scores.items()},
       'exact_query_U_cross_video':{k:exact_query_scores(s,d,meta) for k,s in scores.items()},
       'local_stream_video_permutations':permutations,'alpha_action':aa,'alpha_object':ao,
       'detector_weights':{k:float(getattr(model,k).item()) for k in ['w_base','w_fg','bias']}}
    checks=r['checks']
    checks['prediction_max_abs_error']=float(np.max(np.abs(saved-sg['s_exist'])))
    checks['checkpoint_parameter_count']=sum(x.numel() for x in model.parameters())
    checks['val_seen_auc']=float(roc_auc_score(vd['labels'][sv],vals[sv]))
    checks['stored_val_seen_auc']=m['best_val_seen_auc']
    checks['threshold_replayed']=float(th);checks['threshold_stored']=float(ckpt['threshold'])
    checks['metric_max_abs_error']=max(abs(r['metrics']['full'][k]-m[k]) for k in ['Seen_AUROC','Unseen_AUROC','Gap','Matched_PairAcc','U_pos_FRR','U_neg_RR'])
    checks['prediction_unique_complete']=len(pmap)==len(preds)==len(d['qids']) and set(pmap)==set(meta)==set(d['qids'])
    checks['metadata_equal']=all(meta[str(q)]['partition']==p and int(meta[str(q)]['exist_label'])==int(y) and meta[str(q)]['vid']==v for q,p,y,v in zip(d['qids'],d['partitions'],d['labels'],d['vids']))
    tr=np.load(BASE/'features'/split/'train.npz')
    checks['train_seen_only']=bool(np.all(np.isin(tr['partitions'],['S+','S-'])))
    checks['video_overlap']={a:len(set(tr['vids'])&set(d['vids'])) for a in ['train_test']}
    checks['train_val_video_overlap']=len(set(tr['vids'])&set(vnpz['vids']))
    checks['val_test_video_overlap']=len(set(vnpz['vids'])&set(d['vids']))
    train_qids_set=set(tr['qids'])
    source_pairs=list(zip(tr['source_qids'],tr['construction_types']))
    checks['source_pair_n']={ct:sum(str(src) in train_qids_set and t==ct for src,t in source_pairs) for ct in ['action_counterfactual','object_counterfactual']}
    hq=np.load(ROOT/'experiments/agy_test/cache/hq'/split/'test.npz')
    checks['hq_spans_max_abs_error']=float(np.max(np.abs(d['best_spans']-hq['spans'][np.arange(len(saved)),hq['fg'].argmax(1)])))
    checks['center_greater_than_width_fraction']=float(np.mean(d['best_spans'][:,0]>d['best_spans'][:,1]))
    # Cached proposal localization under its actual center/width convention.
    hits=[]
    for i,q in enumerate(d['qids']):
        c,w=map(float,d['best_spans'][i]);duration=float(meta[str(q)]['duration'])
        a,b=np.clip([(c-w/2)*duration,(c+w/2)*duration],0,duration)
        best=0.
        for g,e in meta[str(q)]['relevant_windows']:
            inter=max(0.,min(b,e)-max(a,g));union=b-a+e-g-inter
            best=max(best,inter/union if union>0 else 0.)
        hits.append(best>=.5)
    up=d['partitions']=='U+';hits=np.array(hits)
    r['U_pos_raw_R1_iou05']=float(hits[up].mean())
    r['U_pos_gated_R1_iou05']=float((hits[up]&(saved[up]>=ckpt['threshold'])).mean())
    report['splits'][split]=r
    boot[split]=dict(y=d['labels'],parts=d['partitions'],vids=d['vids'],original=d['orig_logits'],final=saved)
    np.savez(OUT/(split+'_audit_scores.npz'),qids=d['qids'],vids=d['vids'],labels=d['labels'],partitions=d['partitions'],**scores)
    for path in [cpath,BASE/'features'/split/'test.npz',BASE/'features'/split/'val.npz',BASE/'features'/split/'train.npz',BASE/'runs'/split/'predictions.jsonl']:
        report['sha256'][str(path.relative_to(ROOT))]=sha(path)
    print('RESULT',split,json.dumps(r),flush=True)
    del model,batch,vb,result,val_result

# Independent weighted implementation; identical shared-video sampling scheme.
vids=sorted(set(np.concatenate([x['vids'] for x in boot.values()])))
vm={v:i for i,v in enumerate(vids)};funcs=[]
for d in boot.values():
    vi=np.array([vm[v] for v in d['vids']]);group=[]
    for pp in [['S+','S-'],['U+','U-']]:
        mask=np.isin(d['parts'],pp)
        group.append([weighted_auc_prepared(d['y'][mask],d[k][mask],vi[mask]) for k in ['original','final']])
    funcs.append(group)
rng=np.random.default_rng(20261005);deltas=np.empty((2000,5,3))
for i in range(2000):
    counts=np.bincount(rng.integers(len(vids),size=len(vids)),minlength=len(vids)).astype(float)
    for j,group in enumerate(funcs):
        ds,du=[f[1](counts)-f[0](counts) for f in group];deltas[i,j]=[ds,du,du-ds]
names=['delta_seen','delta_unseen','gap_reduction']
ci=lambda x:{n:np.nanquantile(x[:,j],[.025,.975]).tolist() for j,n in enumerate(names)}
report['bootstrap']={'repeats':2000,'video_clusters':len(vids),'macro':ci(np.nanmean(deltas,axis=1)),'per_split':{s:ci(deltas[:,i]) for i,s in enumerate(SPLITS)}}
report['macro_metrics']={method:{k:float(np.mean([x['metrics'][method][k] for x in report['splits'].values()])) for k in ['Seen_AUROC','Unseen_AUROC','Gap','Matched_PairAcc']} for method in report['splits']['A1']['metrics']}
(OUT/'audit_metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print('MACRO',json.dumps(report['macro_metrics']),flush=True)
print('BOOTSTRAP',json.dumps(report['bootstrap']),flush=True)
