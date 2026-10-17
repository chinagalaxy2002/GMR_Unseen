"""Two controlled scratch runs; Val selection, frozen best, then Test once."""
from common import ROOT,save,sha,rows,options,dataset,scope_audit
import argparse,json,time,random,os,fcntl
from pathlib import Path
import numpy as np,torch
from torch.utils.data import DataLoader
from models.flash_vtg_gmr.model import build_model1
from training.flash_vtg_gmr.dataset import start_end_collate,prepare_batch_inputs
from event_model import EventModel
from evaluation import predict,evaluate,native_selection_metrics
from diagnostics import (REFERENCE_COMMIT,gradient_sample,FeatureCapture,fixed_val_panel,write_epoch,
                         write_pool_diagnostics,append,objective_gradient_relation,parameter_updates)

def seed(value):
    random.seed(value);np.random.seed(value);torch.manual_seed(value)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(value)

def checkpoint(path,payload):
    tmp=path.with_suffix('.tmp');torch.save(payload,tmp);tmp.replace(path)

def verify_sources():
    manifest=json.loads((ROOT/'provenance/FROZEN_SOURCE.json').read_text())
    # This protocol fork intentionally changes only this runner to expose seed,
    # epoch and patience controls. Every copied upstream source remains frozen.
    instrumentation={'code/run.py','code/diagnostics.py'}
    assert all(sha(ROOT/p)==h for p,h in manifest.items() if p not in instrumentation),'Frozen source changed'
    assert json.loads((ROOT/'DATA_AUDIT.json').read_text())['state']=='PASS'
    scope_audit()

def execute(variant,device='cuda',resume=True,smoke=False,seed_value=2024,epochs=100,patience=23,run_name=None):
    verify_sources();name=run_name or f'{variant}_s{seed_value}';run=ROOT/('tests/smoke_runs' if smoke else 'runs')/name;run.mkdir(parents=True,exist_ok=True)
    lock=(run/'run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (run/'COMPLETE.json').exists():return
    opt=options(device)
    opt.seed=seed_value;opt.n_epoch=1 if smoke else epochs;opt.max_es_cnt=patience
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True
    seed(seed_value);base,criterion=build_model1(opt)
    model=EventModel(base,variant).to(opt.device);seed(seed_value)
    train=dataset(opt,'train',True,smoke);val=dataset(opt,'val',False,smoke)
    generator=torch.Generator().manual_seed(opt.seed)
    optimizer=torch.optim.AdamW(model.parameters(),lr=opt.lr,weight_decay=opt.wd,foreach=False)
    scheduler=torch.optim.lr_scheduler.StepLR(optimizer,opt.lr_drop,gamma=.5)
    # Native training starts its best score at zero. Smoke fixtures can have
    # identically zero AP; they retain a first snapshot solely to test I/O.
    start=0;best=-float('inf') if smoke else 0.0;es=0
    if resume and (run/'latest.ckpt').exists():
        ck=torch.load(run/'latest.ckpt',map_location='cpu',weights_only=False)
        assert ck.get('selection_metric')==opt.selection_metric,'Refuse checkpoint from a different selection protocol'
        model.load_state_dict(ck['model']);optimizer.load_state_dict(ck['optimizer']);scheduler.load_state_dict(ck['scheduler'])
        start=ck['epoch'];best=ck['best'];es=ck['es'];generator.set_state(ck['sampler_rng'])
        random.setstate(ck['python_rng']);np.random.set_state(ck['numpy_rng']);torch.set_rng_state(ck['torch_rng'])
        if torch.cuda.is_available():torch.cuda.set_rng_state_all(ck['cuda_rng'])
        history=[r for r in rows(run/'trace.jsonl') if r['epoch']<=start]
        (run/'trace.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in history))
    save(run/'CONFIG.json',{'variant':variant,'protocol':json.loads((ROOT/'configs/protocol.json').read_text()),
         'parameters':sum(p.numel() for p in model.parameters()),'device':str(opt.device),'seed':seed_value,
         'epochs':opt.n_epoch,'early_stop_patience':opt.max_es_cnt,
         'initialization':'scratch; fixed precomputed CLIP/SlowFast features','smoke_only':smoke})
    save(run/'DIAGNOSTIC_COVERAGE.json',{'reference_branch_commit':REFERENCE_COMMIT,
         'covered':['every-step optimization','sampled objective gradient interaction','per-epoch parameter updates',
                    'validation response/candidate evidence','score distributions','same-video ranking','selection trace',
                    'actual mean-pool causal ablation','counterfactual max ownership','frozen Test diagnostics'],
         'architecture_not_applicable':['Hungarian assignment flips','DETR decoder slots'],
         'selection_safety':'diagnostics never enter loss, checkpoint selection, or threshold selection'})
    loader=DataLoader(train,batch_size=opt.bsz,shuffle=True,num_workers=0,collate_fn=start_end_collate,generator=generator)
    trained_epochs=start
    panel=fixed_val_panel(val.data)
    save(run/'diagnostics/FIXED_VAL_PANEL.json',{'data':'Standard Val only','qids':panel,
         'selection':'first four per absent/single/multi group, sorted by qid; no score-based selection',
         'feature_every_epochs':10,'feature_first_epoch':True,'feature_on_new_best':True})
    # A restart after the final committed epoch must proceed directly to
    # freezing/evaluation, without another optimizer step or undefined epoch.
    stop_epoch=opt.n_epoch if es<=opt.max_es_cnt else start
    for epoch in range(start,stop_epoch):
        tick=time.time();model.train();criterion.train();totals={};batches=0;grad_samples=[];norms=[]
        parameters_before={n:p.detach().cpu().clone() for n,p in model.named_parameters()}
        for batch in loader:
            inputs,targets=prepare_batch_inputs(batch[1],opt.device)
            targets['label']=batch[0];targets['fps']=torch.full((len(batch[0]),),1/opt.clip_length,device=opt.device)
            output=model(**inputs,targets=targets);losses=criterion(batch,output,targets)
            losses={k:v for k,v in losses.items() if 'loss' in k and k in criterion.weight_dict}
            loss=sum(v*criterion.weight_dict[k] for k,v in losses.items())
            if not torch.isfinite(loss):raise FloatingPointError(f'Nonfinite loss epoch {epoch+1}')
            optimizer.zero_grad(set_to_none=True)
            sampled=batches==0 or (batches+1)%50==0
            if sampled and 'loss_exist' in losses:
                exist_obj=losses['loss_exist']*criterion.weight_dict['loss_exist']
                loc_obj=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k!='loss_exist')
                append(run/'diagnostics/gradients.jsonl',{'epoch':epoch+1,'batch':batches+1,
                    'pair':'existence_vs_localization',**objective_gradient_relation(model,exist_obj,loc_obj)})
            loss.backward()
            if batches==0 or (batches+1)%50==0:
                grad_samples.append({'batch':batches+1,'groups':gradient_sample(model)})
            norm=torch.nn.utils.clip_grad_norm_(model.parameters(),opt.grad_clip,error_if_nonfinite=True)
            if sampled:
                append(run/'diagnostics/optimization.jsonl',{'epoch':epoch+1,'batch':batches+1,
                    'losses':{k:float(v.detach()) for k,v in losses.items()},'total_loss':float(loss.detach()),
                    'preclip_global_norm':float(norm),'clip_threshold':opt.grad_clip,
                    'clip_coefficient':min(1.,opt.grad_clip/max(float(norm),1e-30)),'lr':optimizer.param_groups[0]['lr']})
            norms.append(float(norm));optimizer.step()
            for k,v in losses.items():totals[k]=totals.get(k,0.)+float(v.detach())
            batches+=1
            if batches%50==0:
                save(run/'STATUS.json',{'state':'training','epoch':epoch+1,'batch':batches,'updated':time.time()})
                with (run/'diagnostics/train_batches.jsonl').open('a') as f:
                    f.write(json.dumps({'epoch':epoch+1,'batch':batches,'losses':{k:float(v.detach()) for k,v in losses.items()},
                        'total_grad_norm_before_clip':float(norm),'lr':optimizer.param_groups[0]['lr']})+'\n')
        scheduler.step()
        capture=FeatureCapture(panel)
        pred,pre=predict(model,val,opt,return_pre_nms=True,capture=capture)
        metrics=evaluate(pred,val.data,opt)
        native=native_selection_metrics(pre,val.data,opt)
        score=native['brief']['MR-full-mAP'];assert np.isfinite(score)
        improved=score>best
        if improved:best=score;es=0
        else:es+=1
        record={'epoch':epoch+1,'score':score,'best':best,'improved':improved,'early_stop_count':es,
                'selection_metric':opt.selection_metric,'selection_stage':'pre-NMS',
                'seconds':time.time()-tick,'losses':{k:v/batches for k,v in totals.items()},
                'native_pre_nms_metrics':native['brief'],'val_metrics':metrics['brief']}
        train_diag={'losses':record['losses'],'gradient_samples':grad_samples,
                    'total_grad_norm_before_clip':{'mean':float(np.mean(norms)),'max':max(norms),
                                                   'fraction_clipped':float(np.mean(np.asarray(norms)>opt.grad_clip))},
                    'lr':optimizer.param_groups[0]['lr'],'batches':batches}
        keep_features=improved or epoch==0 or (epoch+1)%10==0
        write_epoch(run,epoch+1,pre,pred,val.data,opt,train_diag,metrics,native,capture,keep_features)
        append(run/'diagnostics/parameter_updates.jsonl',{'epoch':epoch+1,'modules':parameter_updates(parameters_before,model)})
        payload={'model':model.state_dict(),'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict(),
            'epoch':epoch+1,'best':best,'es':es,'sampler_rng':generator.get_state(),
            'selection_metric':opt.selection_metric,'selection_stage':'pre-NMS',
            'python_rng':random.getstate(),'numpy_rng':np.random.get_state(),'torch_rng':torch.get_rng_state(),
            'cuda_rng':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}
        if improved:
            checkpoint(run/'best.ckpt',payload)
            save(run/'selected.json',{'epoch':epoch+1,'score':score,'selection_data':'official Standard Val only',
                'metric':opt.selection_metric,'stage':'pre-NMS','strict_improvement':True})
            save(run/'validation_metrics.json',metrics)
            save(run/'validation_native_pre_nms_metrics.json',native)
            (run/'validation_predictions_pre_nms.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pre))
            (run/'validation_predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pred))
        append(run/'selection/trace.jsonl',{'epoch':epoch+1,'score':score,'previous_best':record['best'] if not improved else None,
            'improved':improved,'early_stop_count':es,'metric':opt.selection_metric,'stage':'pre-NMS','selection_data':'Val only'})
        checkpoint(run/'latest.ckpt',payload)
        trained_epochs=epoch+1
        with (run/'trace.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
        save(run/'STATUS.json',{'state':'training','epoch':epoch+1,'best':best,'selection_metric':opt.selection_metric,
                               'early_stop_count':es,'updated':time.time()})
        print(json.dumps(record),flush=True)
        if es>=opt.max_es_cnt:break
    if not (run/'best.ckpt').exists():raise RuntimeError('Native pre-NMS Val mAP never strictly exceeded initial best=0; no best checkpoint')
    ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False);model.load_state_dict(ck['model'])
    save(run/'FROZEN.json',{'checkpoint_sha256':sha(run/'best.ckpt'),'epoch':ck['epoch'],
         'selection_data':'Val only','selection_metric':opt.selection_metric,'selection_stage':'pre-NMS',
         'G_mIoU_threshold':.4,'thresholds':opt.cls_thresholds,'test_started':False,'smoke_only':smoke})
    save(run/'selection/frozen.json',{'checkpoint_sha256':sha(run/'best.ckpt'),'epoch':ck['epoch'],
         'metric':opt.selection_metric,'stage':'pre-NMS','test_started':False})
    save(run/'STATUS.json',{'state':'frozen_test','updated':time.time()})
    test=dataset(opt,'test',False,smoke);test_capture=FeatureCapture([])
    pred,pre=predict(model,test,opt,return_pre_nms=True,capture=test_capture);metrics=evaluate(pred,test.data,opt)
    (run/'test_predictions_pre_nms.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pre))
    save(run/'metrics_pre_nms.json',evaluate(pre,test.data,opt))
    (run/'test_predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pred))
    save(run/'metrics.json',metrics)
    write_pool_diagnostics(run,'test',ck['epoch'],test_capture,pre,test.data,opt)
    frozen=json.loads((run/'selection/frozen.json').read_text());frozen.update(test_started=True,test_completed=True);save(run/'selection/frozen.json',frozen)
    save(run/'COMPLETE.json',{'variant':variant,'selected_epoch':ck['epoch'],'trained_epochs':trained_epochs,'updated':time.time(),'smoke_only':smoke})
    save(run/'STATUS.json',{'state':'complete','updated':time.time()})
    scope_audit()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['E0','E2'],required=True);p.add_argument('--device',default='cuda')
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--seed',type=int,default=2024)
    p.add_argument('--epochs',type=int,default=100)
    p.add_argument('--patience',type=int,default=23)
    p.add_argument('--run-name')
    a=p.parse_args()
    name=a.run_name or f'{a.variant}_s{a.seed}'
    try:execute(a.variant,a.device,smoke=a.smoke,seed_value=a.seed,epochs=a.epochs,patience=a.patience,run_name=name)
    except Exception as exc:
        save(ROOT/('tests/smoke_runs' if a.smoke else 'runs')/name/'STATUS.json',{'state':'failed','error':repr(exc),'updated':time.time()});raise
