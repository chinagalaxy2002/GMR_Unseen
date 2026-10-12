"""Native Flash instrumentation parity and historical Seen prediction parity."""
import tempfile
import json
from types import SimpleNamespace
from pathlib import Path
import numpy as np
import torch
import nncore
import run_flash_monitor_experiment as f
from auroc_mechanism_monitor import AUROCMechanismMonitor,FlashTemporalMonitor
from mechanism_monitor import save_json


def main():
    torch.set_num_threads(2);f.seed_everything(3407)
    paths=f.diagnostics.registry.paths('soccer','A1_soccer','flash');paths['dataset']='soccer'
    ck=torch.load(paths['checkpoint'],map_location='cpu',weights_only=False);raw=ck['opt']
    opt=SimpleNamespace(**(dict(raw) if isinstance(raw,dict) else vars(raw)))
    opt.device=torch.device('cpu');opt.monitor_smoke=True;opt.cfg=nncore.Config.from_file(str(paths['native']/'configs/flash_vtg_gmr/model.py'))
    data=f.make_dataset(paths,opt,'train',True)
    data=f.stable_subset(data,1)
    meta,batch=next(iter(f.loader(data,f.module,2,0)));inputs,targets=f.module.prepare_batch_inputs(batch,'cpu')
    targets['label']=meta;targets['fps']=torch.full((2,),1/opt.clip_length)
    model,criterion=f.build_model1(opt);model.train();rng=torch.get_rng_state().clone()
    expected=model(**inputs,targets=targets);losses=criterion((meta,batch),expected,targets)
    total=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
    params=list(model.parameters());grads=torch.autograd.grad(total,params,allow_unused=True);end=torch.get_rng_state().clone()
    torch.set_rng_state(rng)
    with tempfile.TemporaryDirectory() as temp:
        mon=AUROCMechanismMonitor(model,temp,'flash',1);temporal=FlashTemporalMonitor(model,criterion,temp,1);mon.temporal=temporal
        mon.begin('train',1,1,1);temporal.begin('train',1,1,1)
        observed=model(**inputs,targets=targets);losses=criterion((meta,batch),observed,targets)
        geometry=f.candidates_from_train(observed,meta);temporal.observe(observed,meta,geometry)
        rows=mon.observe(observed,meta,inputs,geometry=geometry);mon.gradients(losses,criterion,meta)
        for key in ('pred_exist_logits','pred_spans','out_class','out_coord'):torch.testing.assert_close(observed[key],expected[key],rtol=0,atol=0)
        total=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict);total.backward()
        assert torch.equal(end,torch.get_rng_state())
        for parameter,grad in zip(params,grads):
            if grad is None:assert parameter.grad is None
            else:torch.testing.assert_close(parameter.grad,grad,rtol=0,atol=0)
        assert temporal.targets and len(rows)==2
        assert all(len(r['leave_one_unit_out_logit_drop'])==r['valid_video_tokens'] for r in rows)
        temporal.close();mon.close()
    val=f.make_dataset(paths,opt,'val_seen',False);model.load_state_dict(ck['model'])
    with tempfile.TemporaryDirectory() as temp:
        mon=AUROCMechanismMonitor(model,temp,'flash');pred,candidates=f.predict(model,val,opt,mon,0,'validation');mon.close()
    reference={str(r['qid']):r for r in f.diagnostics.registry.rows(paths['validation'])}
    expected=np.array([reference[q]['pred_exist_logit'] for q in pred['qids']]);delta=float(abs(expected-pred['scores']).max())
    save_json(f.ROOT/"monitoring/FLASH_PARITY_DEBUG.json",dict(qids=pred["qids"].tolist(),expected=expected.tolist(),actual=pred["scores"].tolist(),opt=json.loads(json.dumps(vars(opt),default=str))))
    assert delta<=2e-5,delta
    gt={str(r['qid']):r for r in val.data};ious=[]
    for q in pred['qids']:
        rows=[r[:2] for r in reference[q]['pred_relevant_windows'] if r[1]>r[0]];truth=gt[q]['relevant_windows']
        ious.append(float(f.overlap_matrix(rows[:1],truth).max()/len(truth)) if truth and rows else float(not truth and not rows))
    iou_delta=float(abs(np.array(ious)-pred['accept_iou']).max());assert iou_delta<1e-6,iou_delta
    result=dict(passed=True,bitwise_outputs_gradients_rng=True,actual_native_targets=True,
        seen_historical_score_max_difference=delta,seen_historical_set_iou_max_difference=iou_delta,seen_queries=len(val))
    save_json(f.ROOT/'monitoring/FLASH_FULL_MONITOR_TEST_RESULTS.json',result);print(json.dumps(result))
if __name__=='__main__':main()
