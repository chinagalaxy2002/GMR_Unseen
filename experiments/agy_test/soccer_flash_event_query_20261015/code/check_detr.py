"""Real Val checks: native parity, task gradients, masks, diagnostics and null GT."""
from common import ROOT,save,scope_audit
from detr_backend import options,dataset,modules,build_model,predict,native_selection_metrics,package,early_stop
from detr_event_model import EventModel
from detr_diagnostics import FeatureCapture
from diagnostics import fixed_val_panel
from evaluation import evaluate
import argparse,copy,importlib,json,sys,torch,os
from torch.utils.data import DataLoader

def main(bb,device='cpu'):
    torch.set_num_threads(2);opt=options(bb,device)
    data=dataset(opt,'val',True,True);module,_=modules(bb)
    batch=module.start_end_collate([data[i] for i in range(len(data))])
    inputs,targets=module.prepare_batch_inputs(batch[1],opt.device)
    assert len(data)==3 and sorted(len(x['relevant_windows']) for x in data.data)==[0,1,2]
    torch.manual_seed(opt.seed);base,criterion=build_model(opt)
    models=[EventModel(copy.deepcopy(base),v,bb).to(opt.device) for v in ['E0','E2']]
    results=[]
    for model in models:
        # Disable dropout only in checks to compare the unchanged localization path.
        model.train()
        for m in model.modules():
            if isinstance(m,torch.nn.Dropout):m.eval()
            if isinstance(m,torch.nn.MultiheadAttention):m.dropout=0.
        torch.manual_seed(opt.seed);out=model(**inputs);losses=criterion(out,targets)
        used={k:v for k,v in losses.items() if k in criterion.weight_dict and criterion.weight_dict[k]!=0}
        total=sum(v*criterion.weight_dict[k] for k,v in used.items())
        assert torch.isfinite(total)
        total.backward()
        if model.variant=='E0':reference={k:out[k].detach().clone() for k in ['pred_logits','pred_spans']}
        else:
            for k in reference:torch.testing.assert_close(out[k],reference[k],rtol=0,atol=0)
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.base.exist_head.parameters())
            assert any(p.grad is not None and p.grad.abs().sum()>0 for p in model.base.transformer.encoder.parameters())
            assert model.base.exist_head.context is None
        model.zero_grad(set_to_none=True)
        torch.nn.functional.binary_cross_entropy_with_logits(model(**inputs)['pred_exist_logits'],targets['exist_label']).backward()
        decoder_grad=any(p.grad is not None and bool(p.grad.abs().sum()>0) for p in model.base.transformer.decoder.parameters())
        assert decoder_grad==(model.variant=='E0'),'Existence should bypass decoder only in E2'
        assert any(p.grad is not None and bool(p.grad.abs().sum()>0) for p in model.base.transformer.encoder.parameters())
        null_index=next(i for i,r in enumerate(data.data) if not r['relevant_windows'])
        nb=module.start_end_collate([data[null_index]])
        ni,nt=module.prepare_batch_inputs(nb[1],opt.device)
        null_losses=criterion(model(**ni),nt)
        assert all(torch.isfinite(v) for k,v in null_losses.items() if k in criterion.weight_dict and criterion.weight_dict[k]!=0)
        for m in model.modules():
            if isinstance(m,torch.nn.MultiheadAttention):m.dropout=.1
        pred,pre=predict(model,data,opt,return_pre_nms=True)
        capture=FeatureCapture(fixed_val_panel(data.data),bb)
        captured,captured_pre=predict(model,data,opt,return_pre_nms=True,capture=capture)
        assert pred==captured and pre==captured_pre,'Diagnostic hooks changed predictions'
        assert len(capture.records)==len(data) and not capture.handles
        for r in capture.records.values():
            assert r['tensors']['temporal_encoder_1'].shape==(r['video_valid'],256)
            if model.variant=='E2':assert 'event_query_after_temporal_1' in r['tensors']
        # Native evaluator import uses unqualified imports in Moment's released script.
        # The package path change is confined to this check process.
        sys.path.insert(0,str(ROOT/'native_source/training'/package(bb)))
        native=importlib.import_module('training.'+package(bb)+'.evaluate')
        loader=DataLoader(data,batch_size=opt.eval_bsz,collate_fn=module.start_end_collate,num_workers=0)
        native_pred,_=native.compute_mr_results(None,model,loader,opt,None)
        comparable=[{k:v for k,v in r.items() if k!='pred_exist_logit_raw'} for r in pre]
        assert comparable==native_pred,'Custom prediction differs from native entry point'
        metrics=evaluate(pred,data.data,opt);selection=native_selection_metrics(pre,data.data,opt)
        assert 'MR-full-mAP' in selection['brief']
        results.append({'variant':model.variant,'parameters':sum(p.numel() for p in model.parameters()),
            'losses':{k:float(v.detach()) for k,v in used.items()},'decoder_receives_existence_grad':decoder_grad,
            'native_prediction_parity':True,'passive_diagnostic_parity':True,'captured_qids':list(capture.records),
            'fixture_metrics':metrics['brief'],'native_selection':selection['brief']['MR-full-mAP']})
    # Isolate each item from variable batch padding and QD's head-mask order.
    for model in models:
        model.eval()
        with torch.no_grad():
            batched=model(**inputs)
            for i in range(len(data)):
                one={k:v[i:i+1] for k,v in inputs.items()}
                single=model(**one)
                for k in ['pred_logits','pred_spans','pred_exist_logits']:
                    torch.testing.assert_close(batched[k][i:i+1],single[k],rtol=2e-4,atol=2e-5)
    assert early_stop(opt,50)==(bb=='moment') and early_stop(opt,51)
    assert not early_stop(opt,49)
    # The real loader also uses workers; verify transport and no sample drop.
    worker_loader=DataLoader(data,batch_size=2,num_workers=2,collate_fn=module.start_end_collate)
    assert [r['qid'] for batch in worker_loader for r in batch[0]]==[r['qid'] for r in data.data]
    report={'state':'PASS','backbone':bb,'device':device,'torch_version':torch.__version__,
        'fixtures':'official Val only: absent/single/multiple; no formal Test selection',
        'checks':['same-weight localization parity','finite mixed and all-negative losses','new query and encoder gradients',
            'existence bypasses decoder in E2','QD auxiliary forward excluded','passive diagnostics preserve output',
            'native entry-point prediction parity','batch/head and singleton parity','native early-stop boundary','multiprocess data loading'],
        'records':results,'outside_source':scope_audit()}
    suffix=f"_gpu{os.environ['CUDA_VISIBLE_DEVICES']}" if device.startswith('cuda') and 'CUDA_VISIBLE_DEVICES' in os.environ else ''
    save(ROOT/'tests'/f'DETR_CHECKS_{bb}_{device}{suffix}.json',report)
    print(json.dumps({'state':'PASS','backbone':bb,'records':results}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backbone',choices=['moment','qd'],required=True);p.add_argument('--device',default='cpu')
    a=p.parse_args();main(a.backbone,a.device)
