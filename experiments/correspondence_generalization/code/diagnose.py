"""Fixed capacity, fixed optimization budget stage probes; no true U reads."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import roc_auc_score,roc_curve
from torch.utils.data import DataLoader
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE/'code'),str(ROOT),str(ROOT/'training/qd_detr_gmr')]
from vendor.qd_dataset import StartEndDataset,start_end_collate,prepare_batch_inputs
from vendor.qd_train import build_dataset_config
from vendor.qd_evaluate import eval_epoch
from models.qd_detr_gmr import build_model
from diagnostic_metrics import localization

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mean(x,m):return (x*m[...,None]).sum(1)/m.sum(1)[:,None].clamp_min(1)

def extract(model,opt,path):
    ds=StartEndDataset(**build_dataset_config(opt,str(path),False,True))
    assert len(ds)==len(Path(path).read_text().splitlines())
    dl=DataLoader(ds,batch_size=16,shuffle=False,num_workers=0,collate_fn=start_end_collate)
    cap={};hooks=[]
    for n,mod in [('v',model.input_vid_proj),('t',model.input_txt_proj),('f',model.transformer)]:
        def hook(m,i,o,key=n):cap[key]=o
        hooks.append(mod.register_forward_hook(hook))
    out={};rows=[];head=[];rng=np.random.default_rng(3407);projections={}
    def project(x,key):
        if key not in projections:
            projections[key]=torch.tensor(rng.choice([-1.,1.],size=(x.shape[-1],256))/np.sqrt(x.shape[-1]),dtype=torch.float32,device=x.device)
        return x@projections[key]
    with torch.no_grad():
        for meta,batch in dl:
            x,_=prepare_batch_inputs(batch,opt.device);r=model(**x)
            vm=x['src_vid_mask'];tm=x['src_txt_mask']
            rv=mean(x['src_vid'][...,:-2],vm);rt=mean(x['src_txt'],tm)
            pv=mean(cap['v'],vm);pt=mean(cap['t'],tm);dec=cap['f'][0][-1]
            values={'raw_joint':project(torch.cat([rv,rt],-1),'joint'),'raw_video':project(rv,'video'),'raw_text':project(rt,'text'),'projection_joint':pv*pt,'projection_video':pv,'projection_text':pt,'decoder_max':dec.max(1).values,'decoder_mean':dec.mean(1)}
            for k,v in values.items():out.setdefault(k,[]).append(v.cpu().numpy())
            head.extend(r['pred_exist_logits'].cpu().numpy().tolist());rows.extend(meta)
    for h in hooks:h.remove()
    return rows,{k:np.concatenate(v) for k,v in out.items()},np.asarray(head,dtype=np.float32),len(dl)

def fit(x,y,evals,device):
    torch.manual_seed(3407)
    mu=x.mean(0);sd=x.std(0).clip(1e-5)
    tx=torch.tensor((x-mu)/sd,device=device);ty=torch.tensor(y,dtype=torch.float32,device=device)
    model=torch.nn.Linear(x.shape[1],1).to(device);optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
    gen=torch.Generator(device='cpu').manual_seed(3407);updates=0
    order_hash=hashlib.sha256()
    for epoch in range(100):
        indices=torch.randperm(len(y),generator=gen)
        order_hash.update(indices.numpy().tobytes())
        for ids in indices.split(256):
            optimizer.zero_grad();loss=torch.nn.functional.binary_cross_entropy_with_logits(model(tx[ids.to(device)]).flatten(),ty[ids.to(device)]);loss.backward();optimizer.step();updates+=1
    with torch.no_grad():scores=[model(torch.tensor((v-mu)/sd,device=device)).flatten().cpu().numpy() for v in evals]
    return scores,{'updates':updates,'row_exposures':len(y)*100,'per_row_exposures':100,'batch_order_sha256':order_hash.hexdigest(),'parameters':x.shape[1]+1,'loss_last':loss.item(),'state_dict':{k:v.cpu() for k,v in model.state_dict().items()},'standardization_mean':mu,'standardization_std':sd}

def auc(y,s):return float(roc_auc_score(y,s))
def threshold(y,s):
    f,t,th=roc_curve(y,s);return float(th[np.argmax(t-f)])
def summary(rows,s,th):
    y=np.asarray([r['exist_label'] for r in rows]);pos=y==1;neg=~pos
    by={}
    for r,z in zip(rows,s):by.setdefault(r['vid'],{0:[],1:[]})[r['exist_label']].append(float(z))
    pairs=[float(a>b)+.5*float(a==b) for v in by.values() for a in v[1] for b in v[0]]
    return {'auroc':auc(y,s),'threshold':th,'positive_frr':float((s[pos]<th).mean()),'negative_rr':float((s[neg]<th).mean()),'pairacc_all_same_video_pairs_ties_half':float(np.mean(pairs)) if pairs else None,'pair_count':len(pairs)}
def bootstrap(rows,scores):
    vids=np.array([r['vid'] for r in rows]);y=np.array([r['exist_label'] for r in rows]);unique=np.unique(vids);groups={v:np.flatnonzero(vids==v) for v in unique};rng=np.random.default_rng(3407)
    vals={k:[] for k in scores};diffs={k:[] for k in scores if k!='original_head'}
    joint_diffs={f'{j}_minus_{u}':[] for j,us in [('raw_joint',['raw_video','raw_text']),('projection_joint',['projection_video','projection_text'])] for u in us}
    for _ in range(1000):
        ix=np.concatenate([groups[v] for v in rng.choice(unique,len(unique),replace=True)])
        if len(np.unique(y[ix]))<2:continue
        av={k:auc(y[ix],s[ix]) for k,s in scores.items()}
        for k,a in av.items():vals[k].append(a)
        for k in diffs:diffs[k].append(av[k]-av['original_head'])
        for k in joint_diffs:
            j,u=k.split('_minus_');joint_diffs[k].append(av[j]-av[u])
    return {'auroc_ci95':{k:np.quantile(v,[.025,.975]).tolist() for k,v in vals.items()},'paired_gain_over_head_ci95':{k:np.quantile(v,[.025,.975]).tolist() for k,v in diffs.items()},'joint_minus_unimodal_ci95':{k:np.quantile(v,[.025,.975]).tolist() for k,v in joint_diffs.items()},'unit':'video','resamples':1000}

def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--stage',default='best');p.add_argument('--device',default='cuda:1');a=p.parse_args()
    run=a.run.resolve();assert run.is_relative_to(HERE/'runs')
    dst=run/f'diagnostic_{a.stage}';dst.mkdir(exist_ok=False)
    began=time.monotonic();source_hashes={str(p):sha(p) for p in (HERE/'code').rglob('*.py')};torch.set_num_threads(4)
    ck=run/('best.ckpt' if a.stage=='best' else f'stage_{int(a.stage):03d}.ckpt')
    c=torch.load(ck,map_location='cpu',weights_only=False);opt=c['opt'];opt.device=a.device;opt.num_workers=0;opt.results_dir=str(dst)
    model,criterion=build_model(opt);model.load_state_dict(c['model']);model.to(a.device).eval();criterion.to(a.device)
    view=Path(opt.train_path).parent;packs={}
    for n,f in [('train','train.jsonl'),('seen','val_seen.jsonl'),('pseudo','pseudo_unseen_dev.jsonl')]:packs[n]=extract(model,opt,view/f)
    scores={n:{'original_head':packs[n][2]} for n in ('seen','pseudo')};y=np.array([r['exist_label'] for r in packs['train'][0]])
    fit_records={}
    for k in packs['train'][1]:
        ss,record=fit(packs['train'][1][k],y,[packs[n][1][k] for n in ('seen','pseudo')],a.device)
        torch.save(record,dst/f'probe_{k}.pt');fit_records[k]={k:v for k,v in record.items() if k not in ('state_dict','standardization_mean','standardization_std')}
        for n,s in zip(('seen','pseudo'),ss):scores[n][k]=s
    ss,record=fit(packs['train'][2][:,None],y,[packs[n][2][:,None] for n in ('seen','pseudo')],a.device)
    torch.save(record,dst/'probe_calibration.pt')
    for n,s in zip(('seen','pseudo'),ss):scores[n]['scalar_calibration']=s
    metrics={}
    for k in scores['seen']:
        th=threshold(np.array([r['exist_label'] for r in packs['seen'][0]]),scores['seen'][k])
        metrics[k]={n:summary(packs[n][0],scores[n][k],th) for n in ('seen','pseudo')}
    for n in ('seen','pseudo'):
        np.savez(dst/f'{n}_scores.npz',**scores[n]);(dst/f'{n}_rows.json').write_text(json.dumps(packs[n][0]))
    boot=bootstrap(packs['pseudo'][0],scores['pseudo'])
    orig=metrics['original_head'];gate={}
    for k in packs['train'][1]:
        gain=metrics[k]['pseudo']['auroc']-orig['pseudo']['auroc'];loss=orig['seen']['auroc']-metrics[k]['seen']['auroc']
        gate[k]={'gain':gain,'seen_loss':loss,'readout_gain_gate_pass':gain>=.03 and loss<=.01 and boot['paired_gain_over_head_ci95'][k][0]>0,'causal_mechanism_proven':False}
    for j,us in [('raw_joint',['raw_video','raw_text']),('projection_joint',['projection_video','projection_text'])]:
        gate[j]['joint_over_unimodal_gate_pass']=all(metrics[j]['pseudo']['auroc']-metrics[u]['pseudo']['auroc']>=.03 and boot['joint_minus_unimodal_ci95'][f'{j}_minus_{u}'][0]>0 for u in us)
    official={}
    for n,f in [('seen','val_seen.jsonl'),('pseudo','pseudo_unseen_dev.jsonl')]:
        ds=StartEndDataset(**build_dataset_config(opt,str(view/f),True,True));opt.eval_split_name='val'
        official[n]=eval_epoch(None,model,ds,opt,f'{n}_official_predictions.jsonl',criterion)[0]
    loc={n:localization(dst/f'{n}_official_predictions.jsonl',packs[n][0],scores[n]['original_head'],metrics['original_head'][n]['threshold']) for n in ('seen','pseudo')}
    result={'seed':3407,'output':str(dst),'parent_provenance_sha256':sha(run/'provenance.json'),'configuration':dict(opt),'data_sha256':{n:sha(view/f) for n,f in [('train','train.jsonl'),('seen','val_seen.jsonl'),('pseudo','pseudo_unseen_dev.jsonl')]},'localization':loc,'state':'completed_stage_diagnostic','stage':a.stage,'checkpoint_epoch':c['epoch'],'checkpoint_sha256':sha(ck),'code_sha256':source_hashes[str(Path(__file__))],'executed_source_sha256':source_hashes,'protocol_sha256':sha(run/'protocol.json'),'metrics':metrics,'pseudo_video_bootstrap':boot,'gate':gate,'fit_records':fit_records,'extraction_forwards':sum(v[3] for v in packs.values()),'evaluation_forwards':sum((len(packs[n][0])+15)//16 for n in ('seen','pseudo')),'wall_seconds':time.monotonic()-began,'device':a.device,'official_gate':{'threshold':opt.exist_gate_thd,'hard':False},'limitations':['raw random projection is compression, not CLIP aligned cosine','projection product and decoder pools differ in statistics','single held action and video distribution shift','readout association alone cannot establish causality','scalar calibration has one-dimensional input; lower capacity control','official GMR metrics and separate seen-selected hard threshold must not be conflated']}
    (dst/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps({'path':str(dst),'gate':gate},indent=2))
if __name__=='__main__':main()
