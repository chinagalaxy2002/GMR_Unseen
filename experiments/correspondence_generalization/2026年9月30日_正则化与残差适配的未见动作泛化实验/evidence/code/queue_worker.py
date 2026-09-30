"""Budget-audited worker for QD/Moment/Flash GMR and independent positive VTG.
A config-only old checkpoint supplies historical options; its weights are never
loaded into a training model. All original files are read-only.
"""
import argparse,copy,hashlib,importlib,json,math,os,random,shutil,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
import torch
from easydict import EasyDict
from torch.utils.data import DataLoader
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
if str(ROOT) not in sys.path:sys.path[:0]=[str(HERE/'code'),str(ROOT),str(ROOT/'training/qd_detr_gmr')]
from methods import attach,window_mass_loss
from diagnostic_metrics import iou
from calibration import fit as fit_calibration, transform as transform_calibration
from sklearn.metrics import roc_auc_score,roc_curve

EXECUTED_WORKER_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def dump(p,v):
    tmp=Path(str(p)+'.tmp');tmp.write_text(json.dumps(v,indent=2,default=str));tmp.replace(p)
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def config_template(backbone,split):
    base=ROOT/'results/semantic_existence/multi_split_v2'/split/backbone
    path=sorted(base.rglob('model_best.ckpt' if backbone=='flash' else 'best.ckpt'))[0]
    ck=torch.load(path,map_location='cpu',weights_only=False);opt=ck['opt'];opt=EasyDict(copy.deepcopy(dict(opt) if isinstance(opt,dict) else vars(opt)));del ck
    return opt,path

def modules(backbone):
    if backbone=='moment':sys.path.insert(0,str(ROOT/'training/moment_detr_gmr'))
    ev=importlib.import_module(f'vendor.{backbone}_evaluate')
    ds=importlib.import_module(f'vendor.{backbone}_dataset')
    return ev,ds

def dataset(opt,mod,path,backbone,labels=True):
    kw=dict(dset_name=opt.dset_name,data_path=str(path),v_feat_dirs=opt.v_feat_dirs,q_feat_dir=opt.t_feat_dir,q_feat_type='last_hidden_state',max_q_l=opt.max_q_l,max_v_l=opt.max_v_l,ctx_mode=opt.ctx_mode,clip_len=opt.clip_length,max_windows=opt.max_windows,span_loss_type=opt.span_loss_type,load_labels=labels,mr_only=True,keep_empty_gt=bool(opt.use_exist_head))
    if backbone=='flash':kw.update(data_ratio=1.,normalize_v=not opt.no_norm_vfeat,normalize_t=not opt.no_norm_tfeat,txt_drop_ratio=opt.txt_drop_ratio if labels else 0,dset_domain=opt.dset_domain)
    if backbone=='moment':kw['domain']=None;kw['v_feat_types']=opt.v_feat_types
    d=mod.StartEndDataset(**kw);assert len(d)==len(rows(path)), 'Missing features or unwanted row filter'
    return d

def configure(a,run):
    opt,template=config_template(a.backbone,a.split);opt.seed=a.seed;opt.n_epoch=100;opt.max_es_cnt=-1;opt.num_workers=0
    opt.device=torch.device('cuda:0') if a.backbone=='flash' else 'cuda:0'
    opt.use_exist_head=a.track=='gmr';opt.results_dir=str(run);opt.train_log_filepath=str(run/'train.log');opt.eval_log_filepath=str(run/'val.log');opt.ckpt_filepath=str(run/'best.ckpt');opt.eval_split_name='val';opt.mr_only=True
    opt.resume=None;opt.resume_adapter=None;opt.resume_all=False;opt.start_epoch=0;opt.debug=False
    opt.model_ema=False
    opt.txt_drop_ratio=0;opt.train_path=str(run/'views/train.jsonl');opt.eval_path=str(run/'views/val_seen.jsonl')
    opt.t_feat_dir=str(ROOT/'features/semantic_existence_v2'/a.split/'clip_text')
    video=Path('/home/guoxiangyu/paper/新建文件夹/charades')
    opt.v_feat_dirs=[str(video/k) for k in (('vid_slowfast','vid_clip') if a.backbone=='flash' else ('vid_clip','vid_slowfast'))]
    if a.method=='regularized':opt.wd=.001;opt.dropout=.2
    if a.backbone=='flash':opt.config=str(HERE/'code/configs/flash_model.py');opt.cfg=None;opt.nms_thd=-1;opt.eval_full_only=True;opt.tensorboard_log_dir=str(run/'tensorboard')
    return opt,template

def make_model(opt,ev,method,backbone):
    model,criterion,_,_=ev.setup_model(opt)
    captured,handles=attach(model,method);model.to(opt.device)
    kw={'foreach':False} if backbone=='flash' else {}
    optim=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=opt.lr,weight_decay=opt.wd,**kw)
    sched=torch.optim.lr_scheduler.StepLR(optim,opt.lr_drop,gamma=.5 if backbone=='flash' else .1)
    return model,criterion,optim,sched,captured,handles

def official_eval(model,criterion,opt,ev,dsmod,path,name,backbone,smoke=False):
    data=dataset(opt,dsmod,path,backbone,True)
    if smoke:
        data.data=data.data[:min(16,len(data.data))]
        if hasattr(data,'preloaded_data'):data.preloaded_data=data.preloaded_data[:len(data.data)]
    if backbone=='flash':return ev.eval_epoch(model,data,opt,name,None,criterion,None)[0]
    return ev.eval_epoch(None,model,data,opt,name,criterion)[0]

def existence_summary(gt,pred,threshold=None):
    pp={str(p['qid']):p for p in pred};assert all(str(r['qid']) in pp for r in gt)
    y=np.array([r['exist_label'] for r in gt]);s=np.array([pp[str(r['qid'])]['pred_exist_score'] for r in gt])
    if threshold is None:
        f,t,th=roc_curve(y,s);threshold=float(th[np.argmax(t-f)])
    by={}
    for r,z in zip(gt,s):by.setdefault(r['vid'],{0:[],1:[]})[int(r['exist_label'])].append(z)
    pair=[float(p>n)+.5*float(p==n) for v in by.values() for p in v[1] for n in v[0]]
    result={'auroc':float(roc_auc_score(y,s)),'threshold':threshold,'positive_frr':float((s[y==1]<threshold).mean()),'negative_rr':float((s[y==0]<threshold).mean()),'same_video_all_pairs_pairacc':float(np.mean(pair)) if pair else None,'same_video_pair_count':len(pair),'ties':.5}
    for key in ('pred_relevant_windows_pre_exist','pred_relevant_windows'):
        vals=[];accepted=[]
        for r,z in zip(gt,s):
            if r['exist_label']!=1:continue
            w=pp[str(r['qid'])].get(key,pp[str(r['qid'])]['pred_relevant_windows']);w=sorted(w,key=lambda v:v[2],reverse=True)
            vals.append(max((iou(w[0],g) for g in r['relevant_windows']),default=0) if w else 0);accepted.append(z>=threshold)
        v=np.array(vals);ac=np.array(accepted);label='raw' if key.endswith('pre_exist') else 'official_gated'
        result[label]={f'R1@{t}':float((v>=t).mean()) for t in (.5,.7)}
        if label=='raw':result['diagnostic_hard']={f'R1@{t}':float(((v>=t)&ac).mean()) for t in (.5,.7)};result['raw_correct_positive_frr']={str(t):float((~ac[v>=t]).mean()) if (v>=t).any() else None for t in (.5,.7)}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--backbone',choices=['qd','moment','flash'],required=True);p.add_argument('--split',default='A1');p.add_argument('--track',choices=['gmr','vtg'],default='gmr');p.add_argument('--method',choices=['baseline','regularized','adapter','window'],default='baseline');p.add_argument('--seed',type=int,default=3407);p.add_argument('--development',action='store_true');p.add_argument('--action',choices=['train','evaluate'],default='train');p.add_argument('--smoke',action='store_true');a=p.parse_args()
    a.skip_budget_audit=os.environ.get('CORRESPONDENCE_SKIP_BUDGET_AUDIT')=='1'
    assert a.seed==3407,'User disabled multi-seed experiments; only 3407 is authorized'
    run=a.run.resolve();assert run.is_relative_to(HERE/'runs');start=time.monotonic()
    if a.action=='evaluate':
        assert not a.development
        checkpoint=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);opt=checkpoint['opt'];ev,dsmod=modules(a.backbone)
        # Evaluation is allowed only after the queue froze selection.
        assert (run.parents[0]/'SELECTION_FROZEN.json').exists() or (run.parents[1]/'SELECTION_FROZEN.json').exists()
        opt.device=torch.device('cuda:0') if a.backbone=='flash' else 'cuda:0'
        opt.results_dir=str(run/'test');Path(opt.results_dir).mkdir(exist_ok=False)
        model,criterion,_,_,_,_=make_model(opt,ev,a.method,a.backbone);model.load_state_dict(checkpoint['model']);model.eval()
        inference_count=[0]
        def count_inference(m,i):inference_count[0]+=1
        model.register_forward_pre_hook(count_inference)
        src=ROOT/'data/release/semantic_existence_v2'/a.split/'test.jsonl';dst=run/'views/test.jsonl'
        raw=src.read_text().splitlines(keepends=True)
        dst.write_text(''.join(l for l in raw if a.track=='gmr' or json.loads(l)['exist_label']==1))
        test_assets={}
        for r in rows(dst):
            for f in [Path(opt.t_feat_dir)/f"qid{r['qid']}.npz"]+[Path(f)/f"{Path(r['vid']).stem}.npz" for f in opt.v_feat_dirs]:
                if str(f) not in test_assets:assert f.is_file();test_assets[str(f)]=sha(f)
        dump(run/'test/provenance.json',{'assets_sha256':test_assets,'data_sha256':sha(dst),'source_data_sha256':sha(src),'checkpoint_sha256':sha(run/'best.ckpt'),'configuration':dict(opt),'seed':a.seed,'code_sha256':EXECUTED_WORKER_SHA,'parent_provenance_sha256':sha(run/'provenance.json'),'selection_sha256':sha(run.parent/'SELECTION_FROZEN.json'),'output':str(run/'test')})
        metrics=official_eval(model,criterion,opt,ev,dsmod,dst,'test_predictions.jsonl',a.backbone)
        result={'official_metrics':metrics,'test_data_sha256':sha(dst),'source_test_sha256':sha(src),'checkpoint_sha256':sha(run/'best.ckpt'),'seed':a.seed,'code_sha256':EXECUTED_WORKER_SHA,'wall_seconds':time.monotonic()-start,'output':str(run/'test')}
        if a.track=='gmr':
            preds=rows(run/'test/test_predictions.jsonl');validation=rows(run/'best_seen_predictions.jsonl');vr=rows(run/'views/val_seen.jsonl');th=json.loads((run/'threshold_frozen.json').read_text())['threshold'];rr=rows(dst);result['quadrants']={}
            for prefix,parts in [('seen',('S+','S-')),('unseen',('U+','U-'))]:
                subset=[r for r in rr if r['partition'] in parts];result['quadrants'][prefix]=existence_summary(subset,preds,th)
            result['auroc_gap']=result['quadrants']['seen']['auroc']-result['quadrants']['unseen']['auroc'];result['official_gate_threshold']=float(opt.exist_gate_thd);result['diagnostic_threshold_source']='seen validation Youden J; frozen before test'
            cal=json.loads((run/'calibration_frozen.json').read_text());cp=[dict(p,pred_exist_score=float(transform_calibration([p['pred_exist_score']],cal)[0])) for p in preds];ct=float(transform_calibration([th],cal)[0]);result['monotone_calibration_control']={prefix:existence_summary([r for r in rr if r['partition'] in parts],cp,ct) for prefix,parts in [('seen',('S+','S-')),('unseen',('U+','U-'))]};result['monotone_calibration_fit']=cal
            pairsrc=ROOT/'data/release/semantic_existence_v2'/a.split/'matched_u_pairs.jsonl'
            pp={str(r['qid']):r for r in preds};pair=[]
            for r in rows(pairsrc):
                x=pp[str(r['positive_qid'])]['pred_exist_score'];y=pp[str(r['negative_qid'])]['pred_exist_score'];pair.append(float(x>y)+.5*float(x==y))
            result['matched_u_pairacc']=float(np.mean(pair));result['matched_u_pairs_sha256']=sha(pairsrc)
        else:
            rr=rows(dst);pp={str(r['qid']):r for r in rows(run/'test/test_predictions.jsonl')};result['positive_vtg']={}
            for part in ('S+','U+'):
                vals=[]
                for r in rr:
                    if r['partition']!=part:continue
                    w=pp[str(r['qid'])]['pred_relevant_windows'];w=sorted(w,key=lambda z:z[2],reverse=True);vals.append(max((iou(w[0],g) for g in r['relevant_windows']),default=0) if w else 0)
                v=np.array(vals);result['positive_vtg'][part]={'n':len(v),'R1@0.5':float((v>=.5).mean()),'R1@0.7':float((v>=.7).mean()),'miou':float(v.mean())}
        result['inference_forwards']=inference_count[0];result['training_updates']=0;result['training_row_exposures']=0;result['gpu_peak_bytes']=torch.cuda.max_memory_allocated();dump(run/'test/report.json',result);return
    run.mkdir(exist_ok=False,parents=True);(run/'views').mkdir();state={'state':'preflight','pid':os.getpid(),'args':vars(a),'start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};dump(run/'status.json',state)
    try:
        random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed);torch.cuda.manual_seed_all(a.seed);torch.set_num_threads(4)
        opt,template=configure(a,run);ev,dsmod=modules(a.backbone)
        source=HERE/'runs'/json.loads((HERE/'code/configs/execution_queue.json').read_text())['development_view'] if a.development else ROOT/'data/release/semantic_existence_v2'/a.split
        if not a.development:
            frozen=json.loads((HERE/'runs/stage0/manifest.json').read_text())['splits'][a.split]['train_sha256']
            assert sha(source/'train.jsonl')==frozen,'Frozen training source changed'
        sources={'train':source/'train.jsonl','val_seen':source/'val_seen.jsonl' if a.development else ROOT/'features/semantic_existence_v2'/a.split/'val_seen.jsonl'}
        for n,src in sources.items():
            raw=src.read_text().splitlines(keepends=True);(run/f'views/{n}.jsonl').write_text(''.join(l for l in raw if a.track=='gmr' or json.loads(l)['exist_label']==1))
        if a.development:shutil.copyfile(source/'pseudo_unseen_dev.jsonl',run/'views/pseudo.jsonl')
        assets={str(src):sha(src) for src in sources.values()};assets[str(template)]=sha(template)
        for n in ('train','val_seen'):
            for r in rows(run/f'views/{n}.jsonl'):
                ps=[Path(opt.t_feat_dir)/f"qid{r['qid']}.npz"]+[Path(f)/f"{Path(r['vid']).stem}.npz" for f in opt.v_feat_dirs]
                for f in ps:
                    if str(f) not in assets:assert f.is_file();assets[str(f)]=sha(f)
        if a.development:
            for r in rows(run/'views/pseudo.jsonl'):
                for f in [Path(opt.t_feat_dir)/f"qid{r['qid']}.npz"]+[Path(f)/f"{Path(r['vid']).stem}.npz" for f in opt.v_feat_dirs]:
                    if str(f) not in assets:assert f.is_file();assets[str(f)]=sha(f)
        global_path=HERE/'runs'/json.loads((HERE/'code/configs/execution_queue.json').read_text())['output_name']/'FROZEN_ASSETS.json'
        if global_path.exists():
            global_assets=json.loads(global_path.read_text())['assets_sha256']
            for path,hash_value in assets.items():
                if path in global_assets:assert hash_value==global_assets[path],f'Frozen asset changed: {path}'
        readonly_sources={str(f):sha(f) for path in ('models','training','configs') for f in (ROOT/path).rglob('*') if f.is_file() and f.suffix in ('.py','.yml')}
        if global_path.exists():
            for path,hash_value in readonly_sources.items():
                assert global_assets.get(path)==hash_value,f'Frozen source changed: {path}'
        dump(run/'provenance.json',{'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'assets_sha256':assets,'code_sha256':{str(f):sha(f) for f in (HERE/'code').rglob('*') if f.is_file() and f.suffix in ('.py','.json')},'readonly_source_sha256':readonly_sources,'views_sha256':{f.name:sha(f) for f in (run/'views').glob('*.jsonl')},'seed':a.seed,'config':dict(opt),'config_template_only':str(template),'initial_weights':'random from scratch; template weights never loaded','output':str(run),'sampler':'CPU torch.Generator seed; full permutation per epoch; no drop_last; shared across methods','torch':torch.__version__,'device':torch.cuda.get_device_name(0),'physical_gpu':os.environ.get('CUDA_VISIBLE_DEVICES')})
        trainset=dataset(opt,dsmod,opt.train_path,a.backbone);valset=dataset(opt,dsmod,opt.eval_path,a.backbone)
        model,criterion,optim,scheduler,captured,handles=make_model(opt,ev,a.method,a.backbone)
        forward_counts={'training':0,'inference':0}
        def count_forward(module,inputs):forward_counts['training' if module.training else 'inference']+=1
        model.register_forward_pre_hook(count_forward)
        if not a.skip_budget_audit:
            h=hashlib.sha256()
            for k,v in model.state_dict().items():
                if 'correspondence_adapter' not in k:h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
            dump(run/'budget.json',{'parameters':sum(p.numel() for p in model.parameters()),'original_parameter_initialization_sha256':h.hexdigest(),'epochs':100,'expected_rows':len(trainset)*100,'expected_updates':math.ceil(len(trainset)/opt.bsz)*100,'batch_size':opt.bsz,'candidate_loss_weight':.1 if a.method=='window' else 0,'forwards_per_update':1,'label_budget':'unchanged; original selected span labels only; no teacher','scheduler':'historical Flash StepLR.step(last_loss) retained' if a.backbone=='flash' else 'historical StepLR.step()'})
        gen=torch.Generator().manual_seed(a.seed);best=0.;best_epoch=None;state['state']='training';dump(run/'status.json',state)
        with (run/'batches.jsonl').open('w') as ledger:
            for epoch in range(1 if a.smoke else 100):
                model.train();criterion.train();beg=time.monotonic();order=torch.randperm(len(trainset),generator=gen).tolist();batches=[order[i:i+opt.bsz] for i in range(0,len(order),opt.bsz)];loader=DataLoader(trainset,batch_sampler=batches,num_workers=0,collate_fn=dsmod.start_end_collate);seen=[];loss_total=0.;updates=0
                for i,(meta,batch) in enumerate(loader):
                    inputs,targets=dsmod.prepare_batch_inputs(batch,opt.device)
                    if a.backbone=='flash':targets['label']=meta;targets['fps']=torch.full((len(meta),),1/opt.clip_length,device=opt.device);out=model(**inputs,targets=targets);ld=criterion((meta,batch),out,targets);ld={k:v for k,v in ld.items() if 'loss' in k}
                    else:out=model(**inputs);ld=criterion(out,targets)
                    loss=sum(ld[k]*criterion.weight_dict[k] for k in ld if k in criterion.weight_dict)
                    if a.method=='window':loss=loss+.1*window_mass_loss(captured,inputs,targets)
                    if not torch.isfinite(loss):raise RuntimeError('nonfinite loss')
                    optim.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),opt.grad_clip) if opt.grad_clip>0 else None;optim.step()
                    qids=[str(r['qid']) for r in meta];seen.extend(qids);updates+=1;loss_total+=float(loss.detach())
                    if not a.skip_budget_audit:
                        ledger.write(json.dumps({'epoch':epoch+1,'batch':i,'qids':qids,'training_forwards':1,'updates':1})+'\n');ledger.flush()
                    if a.smoke and i>=2:break
                if not a.smoke and not a.skip_budget_audit:assert len(seen)==len(trainset) and len(set(seen))==len(trainset)
                scheduler.step(loss.detach()) if a.backbone=='flash' else scheduler.step()
                torch.cuda.synchronize();record={'epoch':epoch+1,'updates':updates,'rows':len(seen),'order_sha256':None if a.skip_budget_audit else hashlib.sha256(json.dumps(seen).encode()).hexdigest(),'each_row_once':None if a.skip_budget_audit else not a.smoke,'budget_audit_enabled':not a.skip_budget_audit,'loss':loss_total/updates,'train_wall_seconds':time.monotonic()-beg,'gpu_peak_bytes':torch.cuda.max_memory_allocated()}
                with (run/'epochs.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
                metrics=official_eval(model,criterion,opt,ev,dsmod,opt.eval_path,'latest_seen_predictions.jsonl',a.backbone,a.smoke)
                brief=metrics['brief'];score=(brief['MR-full-R1@0.7']+brief['MR-full-R1@0.5'])/2 if a.backbone=='flash' else brief.get('MR-full-mAP',0.)
                ck={'model':model.state_dict(),'optimizer':optim.state_dict(),'lr_scheduler':scheduler.state_dict(),'epoch':epoch,'opt':opt,'method':a.method,'sampler_generator_state':gen.get_state(),'python_rng':random.getstate(),'numpy_rng':np.random.get_state(),'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all()}
                torch.save(ck,run/'latest.ckpt')
                if score>best or (a.smoke and best_epoch is None):
                    best=float(score);best_epoch=epoch;torch.save(ck,run/'best.ckpt');shutil.copyfile(run/'latest_seen_predictions.jsonl',run/'best_seen_predictions.jsonl');dump(run/'selection.json',{'source':'seen validation only','score_name':'mean R1@.5/.7' if a.backbone=='flash' else 'MR-full-mAP','score':best,'epoch':epoch})
                state.update(epoch=epoch+1,updates_total=(epoch*math.ceil(len(trainset)/opt.bsz)+updates),best_epoch=best_epoch);dump(run/'status.json',state)
        assert (run/'best.ckpt').exists(),'Original seen selection never produced a positive score'
        ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);model.load_state_dict(ck['model']);model.eval()
        result={'state':'completed_smoke' if a.smoke else 'completed','args':vars(a),'seen_selection':json.loads((run/'selection.json').read_text()),'wall_seconds':time.monotonic()-start,'output':str(run),'code_sha256':EXECUTED_WORKER_SHA}
        if a.track=='gmr' and not a.smoke:
            result['seen']=existence_summary(rows(run/'views/val_seen.jsonl'),rows(run/'best_seen_predictions.jsonl'))
            dump(run/'threshold_frozen.json',{'threshold':result['seen']['threshold'],'source':'seen validation only; Youden J','before_true_U':True})
            cal=fit_calibration(rows(run/'views/val_seen.jsonl'),rows(run/'best_seen_predictions.jsonl'));dump(run/'calibration_frozen.json',cal)
        if a.development and not a.smoke:
            result['pseudo_official']=official_eval(model,criterion,opt,ev,dsmod,run/'views/pseudo.jsonl','pseudo_predictions.jsonl',a.backbone)
            vsummary=existence_summary(rows(run/'views/val_seen.jsonl'),rows(run/'best_seen_predictions.jsonl'));result['seen']=vsummary;result['pseudo']=existence_summary(rows(run/'views/pseudo.jsonl'),rows(run/'pseudo_predictions.jsonl'),vsummary['threshold'])
        result['forward_counts']=forward_counts;result['gpu_peak_bytes']=torch.cuda.max_memory_allocated();result['accurate_total_flops']='unmeasured; do not infer from one batch';dump(run/'result.json',result);state.update(state=result['state'],wall_seconds=time.monotonic()-start);dump(run/'status.json',state)
    except BaseException:
        state.update(state='failed',error=traceback.format_exc());dump(run/'status.json',state);raise
if __name__=='__main__':main()
