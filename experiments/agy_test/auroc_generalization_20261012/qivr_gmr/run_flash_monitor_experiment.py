#!/usr/bin/env python3
"""Fresh native FlashVTG baseline with temporal candidate and AUROC diagnostics."""
import argparse
import copy
import json
import time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
import nncore
from sklearn.metrics import roc_auc_score
from run_decoder_experiment import (ROOT, diagnostics, seed_everything, stable_subset, loader,
    preserve_rng, metric_report, calibrate)
from mechanism_monitor import save_json, append_json
from auroc_mechanism_monitor import AUROCMechanismMonitor, final_ranking_bootstrap, annotate_lengths, FlashTemporalMonitor
from response_monitor import ParameterUpdateMonitor, geometry_record, overlap_matrix, frozen_records, save_records, summarize
from training.flash_vtg_gmr import dataset as module
from models.flash_vtg_gmr.model import build_model1


def make_dataset(paths,opt,name,labels):
    clip,sf=diagnostics.registry.video_dirs(paths['dataset'])
    dataset_class=module.StartEndDataset
    if getattr(opt,'monitor_smoke',False):
        class SmallDataset(module.StartEndDataset):
            def load_data(self):
                rows=super().load_data();selected=[]
                for partition in sorted({r['partition'] for r in rows}):
                    selected.extend([r for r in rows if r['partition']==partition][:8])
                return selected
        dataset_class=SmallDataset
    data=dataset_class(dset_name=opt.dset_name,data_path=str(paths['release']/f'{name}.jsonl'),
        v_feat_dirs=[str(sf),str(clip)],q_feat_dir=str(paths['text']),q_feat_type=opt.q_feat_type,
        max_q_l=opt.max_q_l,max_v_l=opt.max_v_l,ctx_mode=opt.ctx_mode,
        normalize_v=not opt.no_norm_vfeat,normalize_t=not opt.no_norm_tfeat,
        clip_len=opt.clip_length,max_windows=opt.max_windows,span_loss_type=opt.span_loss_type,
        txt_drop_ratio=opt.txt_drop_ratio if name=='train' else 0,load_labels=labels,
        mr_only=True,keep_empty_gt=True)
    expected=diagnostics.registry.rows(paths['release']/f'{name}.jsonl')
    if not getattr(opt,'monitor_smoke',False):assert len(data)==len(expected)
    if name!='test': assert all(r['partition'] in ('S+','S-') for r in data.data)
    annotate_lengths(data,paths,opt,diagnostics.registry,module)
    return data


def candidates_from_train(outputs,metadata):
    result=[]
    for i,meta in enumerate(metadata):
        spans=outputs['pred_spans'][i].detach().cpu().numpy()
        xx=spans[:,:2];fg=spans[:,2]
        gt=meta['relevant_windows'];ov=overlap_matrix(xx,gt)
        result.append(dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],exist_label=meta['exist_label'],
            duration=meta['duration'],gt_windows=gt,slot_spans_sec=xx,slot_scores=fg,
            iou_with_gt=ov.max(1) if len(gt) else np.zeros(len(xx))))
    return result


@torch.no_grad()
def predict(model,data,opt,monitor,epoch,phase):
    model.eval(); records=[]; candidates=[]; query_rows=[]
    with preserve_rng():
        for batch_index,(metadata,batch) in enumerate(loader(data,module,1,0),1):
            monitor.begin(phase,epoch,0,batch_index)
            if hasattr(monitor,"temporal"):monitor.temporal.begin(phase,epoch,0,batch_index)
            inputs,_=module.prepare_batch_inputs(batch,opt.device)
            out=model(**inputs,targets={})
            meta=metadata[0]; raw=out['_out']['boundary'].detach().cpu().numpy().copy()
            # Match native inference: round every field to 3dp, then clip_ts and round_multiple.
            raw=np.round(np.clip(raw,0,meta['duration']),3)
            raw[:,:2]=np.round(np.clip(raw[:,:2],0,150)/opt.clip_length)*opt.clip_length
            if len(raw)<model.max_num_moment:raw=np.pad(raw,((0,model.max_num_moment-len(raw)),(0,0)))
            gt=meta['relevant_windows'];ov=overlap_matrix(raw[:,:2],gt)
            valid=np.flatnonzero(raw[:,1]>raw[:,0])
            iou=float(ov[valid[0]].max()/len(gt)) if len(gt) and len(valid) else float(not gt and not len(valid))
            logit=float(out['pred_exist_logits'][0]);score=float(np.round(logit,6))
            records.append(dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],label=meta['exist_label'],score=score,accept_iou=iou,logit=logit,probability=float(out['pred_exist_logits'][0].sigmoid())))
            candidate=dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],exist_label=meta['exist_label'],duration=meta['duration'],gt_windows=gt,
                slot_spans_sec=raw[:,:2],slot_scores=raw[:,2],iou_with_gt=ov.max(1) if gt else np.zeros(len(raw)))
            candidates.append(candidate)
            if hasattr(monitor,"temporal"):monitor.temporal.observe(out,metadata,[candidate])
            query_rows.extend(monitor.observe(out,metadata,inputs,geometry=[candidate]))
    monitor.finish(phase,epoch,query_rows)
    frozen=dict(qids=np.array([r['qid'] for r in records]),vids=np.array([r['vid'] for r in records]),partitions=np.array([r['partition'] for r in records]),
        exist_logits=np.array([r['logit'] for r in records]),exist_probabilities=np.array([r['probability'] for r in records]),labels=np.array([r['label'] for r in records]),scores=np.array([r['score'] for r in records]),accept_iou=np.array([r['accept_iou'] for r in records]))
    return frozen,candidates


def run(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    save_json(out/'STATUS.json',dict(state='preparing',started=time.time()))
    seed_everything(args.seed);torch.set_num_threads(2)
    paths=diagnostics.registry.paths(args.dataset,args.split,'flash');paths['dataset']=args.dataset
    ck=torch.load(paths['checkpoint'],map_location='cpu',weights_only=False)
    opt=SimpleNamespace(**(dict(ck['opt']) if isinstance(ck['opt'],dict) else vars(ck['opt'])))
    opt.monitor_smoke=args.smoke
    opt.device=torch.device(f'cuda:{args.gpu}' if args.gpu>=0 and torch.cuda.is_available() else 'cpu')
    opt.cfg=nncore.Config.from_file(str(paths['native']/'configs/flash_vtg_gmr/model.py'))
    opt.train_path=str(paths['release']/'train.jsonl');opt.eval_path=str(paths['release']/'val_seen.jsonl')
    model,criterion=build_model1(opt);model.to(opt.device);criterion.to(opt.device)
    assert model.use_exist_head and not hasattr(model,'qivr_head')
    train=make_dataset(paths,opt,'train',True);val=make_dataset(paths,opt,'val_seen',False)
    if args.smoke: train,val=stable_subset(train,8),stable_subset(val,4)
    probe=stable_subset(train,64);probe.txt_drop_ratio=0
    monitor_dir=out/'monitor';monitor_dir.mkdir()
    monitor=AUROCMechanismMonitor(model,monitor_dir,'flash',args.gradient_every)
    updates=ParameterUpdateMonitor(model,monitor_dir)
    temporal=FlashTemporalMonitor(model,criterion,monitor_dir,args.gradient_every);monitor.temporal=temporal
    optimizer=torch.optim.AdamW(model.parameters(),lr=opt.lr,weight_decay=opt.wd,foreach=False)
    scheduler=torch.optim.lr_scheduler.StepLR(optimizer,opt.lr_drop,gamma=.5)
    save_json(out/'CONFIG.json',dict(dataset=args.dataset,split=args.split,backbone='flash',variant='native',seed=args.seed,epochs=args.epochs,
        initialization='fresh',model_kind='baseline',qivr_head=False,native_existence_head=True,
        all_parameters_trainable=all(p.requires_grad for p in model.parameters()),
        selection='maximum Seen validation AUROC; earliest tie; diagnostic reproduction protocol',
        original_selection='historical Flash checkpoint used Seen localization; this queue explicitly uses Seen AUROC',
        optimizer='native AdamW + StepLR',batch_size=opt.bsz,learning_rate=opt.lr,
        video_feature_order=['slowfast','clip'],score='native six-decimal logit',scope='smoke only' if args.smoke else 'fresh native FlashVTG baseline',
        train_counts={p:sum(r['partition']==p for r in train.data) for p in ('S+','S-')},
        release_sha256={n:diagnostics.registry.sha(paths['release']/f'{n}.jsonl') for n in ('train','val_seen','test')},
        source_sha256={str(p.relative_to(ROOT)):diagnostics.registry.sha(p) for p in (Path(__file__).resolve(),ROOT/'src/auroc_mechanism_monitor.py',ROOT/'src/models/flash_vtg_gmr/model.py')}))
    save_json(out/'OPT.json',json.loads(json.dumps(vars(opt),default=str)));save_json(out/'probe_metadata.json',dict(qids=[str(r['qid']) for r in probe.data]))
    predict(model,probe,opt,monitor,0,'probe');initial,_=predict(model,val,opt,monitor,0,'validation')
    append_json(out/'validation.jsonl',dict(epoch=0,seen_auroc=float(roc_auc_score(initial['labels'],initial['scores'])),checkpoint_eligible=False))
    best=-1.;steps=0;best_epoch=None
    for epoch in range(1,args.epochs+1):
        started=time.time();model.train();criterion.train();updates.begin_epoch(epoch);accum={}
        for batch_index,(metadata,batch) in enumerate(loader(train,module,opt.bsz,args.workers,True,args.seed+epoch),1):
            steps+=1;monitor.begin('train',epoch,steps,batch_index)
            temporal.begin('train',epoch,steps,batch_index)
            inputs,targets=module.prepare_batch_inputs(batch,opt.device)
            targets['label']=metadata;targets['fps']=torch.full((len(metadata),),1/opt.clip_length,device=opt.device)
            outputs=model(**inputs,targets=targets)
            losses={k:v for k,v in criterion((metadata,batch),outputs,targets).items() if 'loss' in k}
            total=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
            geometry=candidates_from_train(outputs,metadata)
            temporal.observe(outputs,metadata,geometry)
            monitor.observe(outputs,metadata,inputs,geometry=geometry)
            response_rows=[]
            for j,(meta,g) in enumerate(zip(metadata,geometry)):
                row=dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],label=meta['exist_label'],existence_score=float(outputs['pred_exist_logits'][j].detach().sigmoid()),existence_logit=float(outputs['pred_exist_logits'][j].detach()))
                row.update(geometry_record(g['slot_spans_sec'],g['slot_scores'],meta['relevant_windows']));response_rows.append(row)
            append_json(monitor_dir/'train_responses.jsonl',dict(epoch=epoch,step=steps,subsets=summarize(response_rows),unit='temporal candidates; not DETR slots'))
            monitor.gradients(losses,criterion,metadata)
            optimizer.zero_grad(set_to_none=True);total.backward()
            norm=torch.nn.utils.clip_grad_norm_(model.parameters(),opt.grad_clip)
            if not torch.isfinite(total) or not torch.isfinite(norm): raise RuntimeError('Nonfinite Flash loss/gradient')
            monitor.optimization(losses,criterion,norm,opt.grad_clip,optimizer.param_groups[0]['lr'],metadata)
            optimizer.step()
            for k,v in losses.items(): accum[k]=accum.get(k,0)+float(v.detach())
            if batch_index==1 or batch_index%50==0:
                save_json(out/'STATUS.json',dict(state='training',epoch=epoch,epochs=args.epochs,batches=batch_index,global_step=steps,updated=time.time()))
                print(args.dataset,args.split,'flash',epoch,batch_index,float(total),flush=True)
            if args.smoke and batch_index>=2: break
        scheduler.step();updates.end_epoch()
        predict(model,probe,opt,monitor,epoch,'probe')
        frozen,_=predict(model,val,opt,monitor,epoch,'validation');auc=float(roc_auc_score(frozen['labels'],frozen['scores']))
        append_json(out/'validation.jsonl',dict(epoch=epoch,seen_auroc=auc,losses={k:v/batch_index for k,v in accum.items()},seconds=time.time()-started,checkpoint_eligible=True))
        if auc>best:
            best,best_epoch=auc,epoch
            torch.save(dict(model={k:v.detach().cpu().clone() for k,v in model.state_dict().items()},opt=vars(opt),epoch=epoch),out/'best.ckpt')
        if epoch%5==0 or epoch==args.epochs:
            torch.save(dict(model=model.state_dict(),optimizer=optimizer.state_dict(),scheduler=scheduler.state_dict(),epoch=epoch),out/'last.ckpt.tmp')
            (out/'last.ckpt.tmp').replace(out/'last.ckpt')
        print('Epoch complete',epoch,'Seen AUROC',auc,'seconds',time.time()-started,flush=True)
    selected=torch.load(out/'best.ckpt',map_location='cpu',weights_only=False);model.load_state_dict(selected['model'])
    frozen,_=predict(model,val,opt,monitor,best_epoch,'calibration');threshold=calibrate(frozen)
    np.savez_compressed(out/'validation_predictions.npz',**frozen,threshold=threshold)
    save_json(out/'FROZEN_CALIBRATION.json',dict(best_epoch=best_epoch,seen_validation_auc=best,threshold=threshold,selected_on='Seen validation only',selected_checkpoint_sha256=diagnostics.registry.sha(out/'best.ckpt')))
    test=make_dataset(paths,opt,'test',False)
    if args.smoke: test=stable_subset(test,4)
    frozen,candidates=predict(model,test,opt,monitor,best_epoch,'test');frozen['threshold']=np.array(threshold)
    np.savez_compressed(out/'predictions.npz',**frozen);torch.save(candidates,out/'candidate_cache.pt')
    responses=frozen_records(frozen,candidates);save_records(monitor_dir/'final_test_responses.npz',responses)
    save_json(monitor_dir/'final_test_responses.json',dict(subsets=summarize(responses)))
    baseline=dict(np.load(paths['baseline'],allow_pickle=False));lookup={str(q):i for i,q in enumerate(baseline['qids'])};order=[lookup[q] for q in frozen['qids']]
    baseline={k:v[order] if v.ndim and len(v)==len(lookup) else v for k,v in baseline.items()}
    metric_report(out,baseline,frozen,candidates,100 if args.smoke else args.bootstrap);monitor.close();temporal.close()
    final_ranking_bootstrap(out,diagnostics,frozen)
    save_json(out/'STATUS.json',dict(state='complete',epochs=args.epochs,global_steps=steps,best_epoch=best_epoch,updated=time.time()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--split',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--gpu',type=int,default=0);p.add_argument('--epochs',type=int,default=100);p.add_argument('--seed',type=int,default=3407)
    p.add_argument('--workers',type=int,default=2);p.add_argument('--gradient-every',type=int,default=50);p.add_argument('--bootstrap',type=int,default=2000);p.add_argument('--smoke',action='store_true')
    a=p.parse_args()
    if a.output.exists():p.error('Fresh output required')
    try:run(a)
    except Exception as e:
        if a.output.exists():save_json(a.output/'STATUS.json',dict(state='failed',error=repr(e),updated=time.time()))
        raise
if __name__=='__main__':main()
