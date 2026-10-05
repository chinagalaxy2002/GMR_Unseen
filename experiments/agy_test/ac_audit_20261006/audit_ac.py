"""Audit AC artifacts without changing originals. P0 is replayed because it was not saved."""
from pathlib import Path
from collections import defaultdict, Counter
import json
import os
import sys
import importlib.util
import numpy as np
import torch
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/agy_test/aligned_calibration_verifier'
OUT=Path(__file__).resolve().parent
SPLITS=['A1','A2_alt','A3','C1','C2_alt']
VIDEO=Path(os.environ.get('AC_VIDEO_CLIP_DIR', '/home/guoxiangyu/paper/新建文件夹/charades/vid_clip'))
sys.dont_write_bytecode=True
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location('ac_training_audit',BASE/'train_and_eval.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
torch.set_num_threads(2)
dev=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

def read(path):return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
def write(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def norm(x):return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-12)
def auc(y,s):return float(roc_auc_score(y,s)) if len(np.unique(y))==2 else None

def pair_indices(d,split):
    ix={str(q):i for i,q in enumerate(d['qids'])};pp=read(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')
    assert all(str(p['positive_qid']) in ix and str(p['negative_qid']) in ix for p in pp)
    return np.array([(ix[str(p['positive_qid'])],ix[str(p['negative_qid'])]) for p in pp])

def exact_pairs(d):
    groups=defaultdict(list)
    for i,q in enumerate(d['queries']):
        if d['partitions'][i] in ['U+','U-']:groups[str(q)].append(i)
    pairs=[];sizes=[]
    for ii in groups.values():
        pp=[(a,b) for a in ii for b in ii if d['labels'][a]==1 and d['labels'][b]==0 and d['vids'][a]!=d['vids'][b]]
        if pp:pairs.extend(pp);sizes.append(len(pp))
    return np.array(pairs,int).reshape(-1,2),sizes

def pairacc(s,pp):
    if not len(pp):return None
    a,b=s[pp[:,0]],s[pp[:,1]];return float(np.mean((a>b)+.5*(a==b)))

def metrics(s,d,pp,ep,th=None):
    r={}
    for name,parts in [('Seen',['S+','S-']),('Unseen',['U+','U-'])]:
        mask=np.isin(d['partitions'],parts);y=d['labels'][mask];sc=s[mask]
        r[name+'_AUROC']=auc(y,sc)
        if th is not None:
            reject=sc<th;tp=np.sum(reject&(y==0));fp=np.sum(reject&(y==1));fn=np.sum(~reject&(y==0))
            r[name+'_RejF1']=float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.
            r[name+'_BalancedAccuracy']=float(.5*((~reject[y==1]).mean()+reject[y==0].mean()))
    r['Gap']=r['Seen_AUROC']-r['Unseen_AUROC'];r['Matched_PairAcc']=pairacc(s,pp);r['Exact_query_cross_video_PairAcc']=pairacc(s,ep)
    if th is not None:
        r['U_pos_FRR']=float(np.mean(s[d['partitions']=='U+']<th)*100)
        r['U_neg_RR']=float(np.mean(s[d['partitions']=='U-']<th)*100)
    return r

def weighted_auc(y,s,indices):
    order=np.argsort(s,kind='stable');yy=y[order];ss=s[order];vv=indices[order];starts=np.r_[0,np.flatnonzero(np.diff(ss))+1]
    def calculate(counts):
        w=counts[vv];p=np.add.reduceat(w*(yy==1),starts);n=np.add.reduceat(w*(yy==0),starts)
        return float((p*(np.cumsum(n)-.5*n)).sum()/(p.sum()*n.sum())) if p.sum()*n.sum() else np.nan
    return calculate

report={'scope':'Frozen P1 audit, deterministic original P0 replay, no new-method fitting. Original artifacts unchanged.',
        'subsets':{},'splits':{}}
all_text=defaultdict(list);boot={};video_cache={}
for split in SPLITS:
    data={};metas={}
    for subset in ['train','val','test']:
        z=np.load(BASE/'aligned_features'/split/(subset+'.npz'));d={k:z[k] for k in z.files};data[subset]=d
        meta={str(x['qid']):x for x in read(ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl'))};metas[subset]=meta
        assert len(d['qids'])==len(set(d['qids']))==len(meta)
        assert all(int(d['labels'][i])==int(meta[str(q)]['exist_label']) and str(d['vids'][i])==str(meta[str(q)]['vid']) and str(d['queries'][i])==meta[str(q)]['query'].strip() for i,q in enumerate(d['qids']))
        q=d['q_proj_sent'];v=d['v_clip_cand'];vg=d['v_clip_glob'];ref=d['train_reference'];refscore=q@ref
        raw=(q*v).sum(-1);rawglob=(q*vg).sum(-1)
        check={'n':len(q),'partitions':dict(Counter(d['partitions'].tolist())),
               'distance_label_AUROC':auc(d['labels'],np.linalg.norm(d['q_proj_act']-d['q_proj_obj'],axis=1)),
               'q_norm_max_error':float(np.max(np.abs(np.linalg.norm(q,axis=1)-1))),
               'raw_cos_max_error':float(np.max(np.abs(raw-d['raw_cos_cand_sent']))),
               'centered_cos_max_error':float(np.max(np.abs(raw-refscore-d['sim_cand_sent']))),
               'centered_glob_max_error':float(np.max(np.abs(rawglob-refscore-d['sim_glob_sent'])))}
        hq=np.load(ROOT/'experiments/agy_test/cache/hq'/split/(subset+'.npz'));hfg=hq['fg'];sp=hq['spans'][np.arange(len(q)),hfg.argmax(1)]
        expected=np.clip(np.stack([sp[:,0]-sp[:,1]/2,sp[:,0]+sp[:,1]/2],axis=1),0,1)
        check['cxw_max_error']=float(np.max(np.abs(expected-d['best_spans'])))
        check['orig_logit_max_error']=float(np.max(np.abs(hq['orig_logits']-d['orig_logits'])))
        for i,query in enumerate(d['queries']):
            all_text[(split,str(query))].append(tuple(d[k][i].tobytes() for k in ['q_proj_sent','q_proj_act','q_proj_obj']))
        report['subsets'][split+'/'+subset]=check
    tr,va,te=[data[x] for x in ['train','val','test']]
    assert set(tr['partitions'])<=set(['S+','S-'])
    overlap={a+'_'+b:len(set(data[a]['vids'])&set(data[b]['vids'])) for a,b in [('train','val'),('train','test'),('val','test')]}
    assert not any(overlap.values())
    uvtrain=sorted(set(tr['vids']));vecs=[]
    for vid in uvtrain:
        with np.load(VIDEO/(str(vid)+'.npz')) as z:vecs.append(norm(z['features'].astype(np.float32).mean(0)))
    unnormalized_reference=np.mean(vecs,axis=0);actual_ref=norm(unnormalized_reference)
    referror=float(np.max(np.abs(actual_ref-tr['train_reference'])))
    assert referror<1e-6
    pp=pair_indices(te,split);ep,sizes=exact_pairs(te)
    b={k:v for k,v in mod.to_tensor_dict(te,dev).items() if k!='labels'}
    vb={k:v for k,v in mod.to_tensor_dict(va,dev).items() if k!='labels'}
    ckpt=torch.load(BASE/'runs'/split/'ac_verifier_checkpoint.pt',map_location='cpu',weights_only=False)
    model=mod.AlignedCalibrationVerifier().to(dev);model.load_state_dict(ckpt['state_dict']);model.eval()
    with torch.no_grad():res=model(b);vres=model(vb)
    sg={k:v.cpu().numpy() for k,v in res.items()};sv=np.isin(va['partitions'],['S+','S-']);valscore=vres['s_exist'].cpu().numpy()
    th=mod.choose_val_seen_threshold(valscore[sv],va['labels'][sv]);base_th=mod.choose_val_seen_threshold(va['orig_logits'][sv],va['labels'][sv])
    assert abs(th-ckpt['threshold'])<1e-4
    aa=float(sg['alpha_cand']);ag=float(sg['alpha_glob']);scale=float(model.scale_sim.detach().cpu());gate=sg['gate'];refscore=te['q_proj_sent']@te['train_reference']
    scores={'baseline':te['orig_logits'],'full':sg['s_exist'],'P1_detector_only':sg['s_det'],
            'P1_reference_term_only':sg['s_det']-gate*scale*(aa+ag)*refscore,
            'P1_raw_cosine_no_reference':sg['s_det']+gate*scale*(aa*te['raw_cos_cand_sent']+ag*te['raw_cos_glob_sent']),
            'centered_CLIP_evidence_only':sg['v_evidence'],'reference_text_score_only':-refscore}
    # Reproduce original flawed score shuffle precisely.
    order=np.random.default_rng(3407).permutation(len(te['labels']))
    shuffled=dict(b);shuffled['sim_cand_sent']=b['sim_cand_sent'][order];shuffled['sim_glob_sent']=b['sim_glob_sent'][order]
    with torch.no_grad():scores['original_score_shuffle']=model(shuffled)['s_exist'].cpu().numpy()
    # Replay original P0 (not stored by the source pipeline), only Seen training/selection.
    mod.set_seed(3407);p0=mod.DetectorAdapter().to(dev);opt=torch.optim.AdamW(p0.parameters(),lr=1e-3,weight_decay=1e-4)
    tb=mod.to_tensor_dict(tr,dev);weight=torch.tensor([np.sum(tr['labels']==0)/np.sum(tr['labels']==1)],device=dev)
    lossfn=torch.nn.BCEWithLogitsLoss(pos_weight=weight);best_auc=-1.;best_state=None;best_epoch=0
    for epoch in range(1,31):
        p0.train();opt.zero_grad();st=p0(tb['orig_logits'],tb['fg_max'],tb['h_pool']);loss=lossfn(st,tb['labels']);loss.backward();opt.step();p0.eval()
        with torch.no_grad():vs=p0(vb['orig_logits'],vb['fg_max'],vb['h_pool']).cpu().numpy()
        a=auc(va['labels'][sv],vs[sv])
        if a>best_auc:best_auc=a;best_state={k:v.cpu().clone() for k,v in p0.state_dict().items()};best_epoch=epoch
    p0.load_state_dict(best_state);p0.eval()
    with torch.no_grad():scores['P0_replayed']=p0(b['orig_logits'],b['fg_max'],b['h_pool']).cpu().numpy()
    torch.save({'state_dict':best_state,'best_epoch':best_epoch,'seed':3407,'scope':'original P0 replay'},OUT/(split+'_P0_replayed.pt'))
    # Keep query, original proposal coordinates, detector states and reference fixed;
    # coherently replace videos, including both queries in each matched pair.
    vids=te['vids'];uv,vi=np.unique(vids,return_inverse=True);q=te['q_proj_sent']
    for vid in uv:
        if str(vid) not in video_cache:
            with np.load(VIDEO/(str(vid)+'.npz')) as z:video_cache[str(vid)]=z['features'].astype(np.float32)
    rng=np.random.default_rng(3407);permmetrics=[]
    for repeat in range(5):
        perm=rng.permutation(len(uv))
        if np.any(perm==np.arange(len(uv))):perm=np.roll(np.arange(len(uv)),int(rng.integers(1,len(uv))))
        assert not np.any(perm==np.arange(len(uv)))
        donor_cand=np.empty_like(q);donor_glob=np.empty_like(q)
        donor_globals={str(v):norm(video_cache[str(v)].mean(0)) for v in uv}
        for i in range(len(q)):
            donor=str(uv[perm[vi[i]]]);f=video_cache[donor];T=len(f);s,e=te['best_spans'][i]
            st=max(0,min(T-1,int(np.floor(s*T))));ed=min(T,max(st+1,int(np.ceil(e*T))))
            donor_cand[i]=norm(f[st:ed].mean(0));donor_glob[i]=donor_globals[donor]
        sc=sg['s_det']+gate*scale*(aa*((q*donor_cand).sum(-1)-refscore)+ag*((q*donor_glob).sum(-1)-refscore))
        scores['query_fixed_video_shuffle_'+str(repeat)]=sc
        permmetrics.append(metrics(sc,te,pp,ep))
    m={k:metrics(s,te,pp,ep,th if k=='full' else base_th if k=='baseline' else None) for k,s in scores.items()}
    published=json.loads((BASE/'runs'/split/'metrics.json').read_text())
    metricerrors={k:float(m['full'][k]-published[k]) for k in ['Seen_AUROC','Unseen_AUROC','Gap','Matched_PairAcc','U_pos_FRR','U_neg_RR']}
    p0errors={k:float(m['P0_replayed'][k]-published['p0_detector_adapter'][k]) for k in ['Seen_AUROC','Unseen_AUROC','Gap','Matched_PairAcc']}
    # Proposal-only localization diagnostic at the Seen-selected thresholds.
    def localization(mask):
        ids=np.flatnonzero(mask);good=[]
        for i in ids:
            r=metas['test'][str(te['qids'][i])];s,e=te['best_spans'][i]*float(r['duration']);gt=r['relevant_windows']
            good.append(max(max(0,min(e,b)-max(s,a))/max(1e-12,max(e,b)-min(s,a)) for a,b in gt)>=.5)
        good=np.array(good);return {'n':len(ids),'raw_R1':float(good.mean()),'baseline_gate_R1':float(np.mean(good&(scores['baseline'][ids]>=base_th))),
            'P1_gate_R1':float(np.mean(good&(scores['full'][ids]>=th)))}
    r={'checks':{'prediction_metrics_errors':metricerrors,'P0_replay_metrics_errors':p0errors,'threshold_abs_error':abs(th-ckpt['threshold']),
                 'video_overlap':overlap,'train_reference_max_error':referror,'unnormalized_reference_norm':float(np.linalg.norm(unnormalized_reference)),
                 'checkpoint_parameters':sum(v.numel() for v in model.parameters()),'P0_best_epoch_replayed':best_epoch,
                 'exact_query_groups':len(sizes),'exact_query_pair_n':len(ep)},
       'weights':{'alpha_cand':aa,'alpha_global':ag,'scale_sim':scale},'metrics':m,
       'query_fixed_video_permutations':permmetrics,'U_pos_localization':localization(te['partitions']=='U+')}
    report['splits'][split]=r
    np.savez_compressed(OUT/(split+'_audit_scores.npz'),qids=te['qids'],vids=vids,labels=te['labels'],partitions=te['partitions'],**scores)
    with (OUT/(split+'_predictions.jsonl')).open('w') as f:
        for i,qid in enumerate(te['qids']):
            f.write(json.dumps({'qid':str(qid),'vid':str(vids[i]),'partition':str(te['partitions'][i]),'label':int(te['labels'][i]),
                'baseline_logit':float(scores['baseline'][i]),'P0_replayed_logit':float(scores['P0_replayed'][i]),'P1_logit':float(scores['full'][i])})+'\n')
    boot[split]={'y':te['labels'],'vids':vids,'parts':te['partitions'],'scores':scores}
    print('SPLIT',split,json.dumps(r,ensure_ascii=False),flush=True)
report['same_query_within_split_mismatch_groups']=sum(len(set(v))>1 for v in all_text.values())
write('audit_metrics.json',report)

# Independent paired video bootstrap, joint counts across the five splits.
uv=sorted(set(np.concatenate([d['vids'] for d in boot.values()])));vmap={v:i for i,v in enumerate(uv)}
contrasts={'full_vs_baseline':('full','baseline'),'full_vs_P0':('full','P0_replayed'),
    'full_vs_own_detector':('full','P1_detector_only'),'full_vs_reference_only':('full','P1_reference_term_only'),
    'full_vs_raw_no_reference':('full','P1_raw_cosine_no_reference'),
    'full_vs_original_score_shuffle':('full','original_score_shuffle')}
for i in range(5):contrasts['full_vs_query_fixed_video_shuffle_'+str(i)]=('full','query_fixed_video_shuffle_'+str(i))
prepared={}
for split,d in boot.items():
    ix=np.array([vmap[v] for v in d['vids']]);prepared[split]={}
    for k,s in d['scores'].items():
        funcs=[]
        for parts in [['S+','S-'],['U+','U-']]:
            mask=np.isin(d['parts'],parts);funcs.append(weighted_auc(d['y'][mask],s[mask],ix[mask]))
        prepared[split][k]=funcs
samples={k:np.empty((2000,5,3)) for k in contrasts};rng=np.random.default_rng(20261005)
for b in range(2000):
    counts=np.bincount(rng.integers(len(uv),size=len(uv)),minlength=len(uv))
    for si,split in enumerate(SPLITS):
        values={k:[f(counts) for f in fs] for k,fs in prepared[split].items()}
        for k,(a,c) in contrasts.items():
            ds=values[a][0]-values[c][0];du=values[a][1]-values[c][1];samples[k][b,si]=[ds,du,du-ds]
names=['delta_seen','delta_unseen','gap_reduction']
def ci(arr):return {k:np.nanquantile(arr[:,i],[.025,.975]).tolist() for i,k in enumerate(names)}
bs={'repeats':2000,'video_clusters':len(uv),'seed':20261005,'contrasts':{}}
for k,a in samples.items():
    bs['contrasts'][k]={'macro':ci(a.mean(1)),'per_split':{s:ci(a[:,i]) for i,s in enumerate(SPLITS)},
        'action_splits_macro':ci(a[:,:3].mean(1)),'without_C1':ci(a[:,[0,1,2,4]].mean(1))}
summary=json.loads((BASE/'benchmark_summary.json').read_text())
bs['published_macro_CI_max_abs_error']=float(max(np.max(np.abs(np.array(bs['contrasts']['full_vs_baseline']['macro'][k])-summary['bootstrap_95ci'][k])) for k in names))
write('bootstrap.json',bs)
print('BOOTSTRAP',json.dumps(bs['contrasts']['full_vs_baseline']['macro']),flush=True)
