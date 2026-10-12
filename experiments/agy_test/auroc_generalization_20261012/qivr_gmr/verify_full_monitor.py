"""Bitwise output/gradient/RNG parity of full native DETR instrumentation."""
import copy
import importlib
import tempfile
import torch
import numpy as np
import run_decoder_experiment as e
from auroc_mechanism_monitor import AUROCMechanismMonitor, ObjectiveSplitMonitor, auc_pairs, score_report
from mechanism_monitor import save_json


def main():
    torch.set_num_threads(2);results=[]
    assert auc_pairs(np.array([1.,2.]),np.array([1.,0.]))['auroc']==.875
    for bb in ('moment','qd'):
        p=e.diagnostics.registry.paths('soccer','A1_soccer',bb);p['dataset']='soccer'
        opt=copy.deepcopy(torch.load(p['checkpoint'],map_location='cpu',weights_only=False)['opt']);opt.device='cpu'
        pkg='moment_detr_gmr' if bb=='moment' else 'qd_detr_gmr'
        module=importlib.import_module('training.'+pkg+'.dataset')
        build=importlib.import_module('models.'+pkg+('.moment_detr' if bb=='moment' else '.model')).build_model
        data=e.make_dataset(p,opt,module,'train',True)
        data.data=[next(r for r in data.data if len(r['relevant_windows'])>=2),next(r for r in data.data if not r['relevant_windows'])]
        meta,batch=next(iter(e.loader(data,module,2,0)));inputs,targets=module.prepare_batch_inputs(batch,'cpu')
        for no_sa in (False,True):
            e.seed_everything(3407);model,criterion=build(opt);model.train()
            for layer in model.transformer.decoder.layers:layer.rm_self_attn_decoder=no_sa
            start=torch.get_rng_state().clone();expected=model(**inputs);losses=criterion(expected,targets)
            total=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
            params=list(model.parameters());grads=torch.autograd.grad(total,params,allow_unused=True);end=torch.get_rng_state().clone()
            torch.set_rng_state(start)
            with tempfile.TemporaryDirectory() as temp:
                monitor=AUROCMechanismMonitor(model,temp,bb,1);obj=ObjectiveSplitMonitor(criterion,temp)
                monitor.begin('train',1,1,1);obj.begin();out=model(**inputs);losses=criterion(out,targets)
                obj.observe(meta,1,1,losses);rows=monitor.observe(out,meta,inputs,obj.matches[0][2],targets=targets)
                monitor.gradients(losses,criterion,meta)
                observed=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
                observed.backward()
                for key in ('pred_exist_logits','pred_spans','pred_logits'):torch.testing.assert_close(out[key],expected[key],rtol=0,atol=0)
                assert torch.equal(end,torch.get_rng_state())
                for param,grad in zip(params,grads):
                    if grad is None:assert param.grad is None
                    else:torch.testing.assert_close(param.grad,grad,rtol=0,atol=0)
                assert all(len(r['leave_one_unit_out_logit_drop'])==opt.num_queries for r in rows)
                assert rows[0]['correct_units'] is not None and rows[1]['correct_units'] is None
                import json
                split=json.loads((monitor.output/'objective_split.jsonl').read_text())
                contributions={}
                for part in split['subsets'].values():
                    for key,v in part['weighted_contributions'].items():contributions[key]=contributions.get(key,0)+v
                for key,v in contributions.items():np.testing.assert_allclose(v,float(losses[key])*criterion.weight_dict[key],rtol=1e-6,atol=1e-6)
                monitor.close();obj.close()
            results.append(dict(backbone=bb,no_sa=no_sa,bitwise_outputs_gradients_rng=True,exact_native_loss_split=True))
    save_json(e.ROOT/'monitoring/FULL_MONITOR_TEST_RESULTS.json',dict(passed=True,tests=results))
    print(results)
if __name__=='__main__':main()
