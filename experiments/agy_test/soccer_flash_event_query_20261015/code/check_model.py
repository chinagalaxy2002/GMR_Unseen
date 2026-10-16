"""Real Soccer fixtures: localization parity, loss/backward, null batch, eval."""
from common import ROOT,ASSETS,save,sha,rows,options,scope_audit
import json,copy,torch,argparse
from torch.utils.data import Subset
from models.flash_vtg_gmr.model import build_model1
from training.flash_vtg_gmr.dataset import StartEndDataset,start_end_collate,prepare_batch_inputs
from event_model import EventModel
from evaluation import predict,evaluate

def main(device):
    torch.set_num_threads(2);opt=options(device)
    data=rows(ROOT/'data/val.jsonl')
    chosen=[next(d for d in data if len(d['relevant_windows'])==n) for n in [0,1,2]]
    path=ROOT/'tests/fixture_val.jsonl';path.write_text(''.join(json.dumps(d)+'\n' for d in chosen))
    ds=StartEndDataset('hl',str(path),opt.v_feat_dirs,opt.t_feat_dir,max_q_l=40,max_v_l=75,
        ctx_mode='video_tef',load_labels=True,clip_len=2,max_windows=5,mr_only=True,keep_empty_gt=True)
    assert len(ds)==3
    batch=start_end_collate([ds[i] for i in range(3)]);inputs,targets=prepare_batch_inputs(batch[1],opt.device)
    targets['label']=batch[0];targets['fps']=torch.full((3,),.5,device=opt.device)
    torch.manual_seed(2024);base,criterion=build_model1(opt)
    e0=EventModel(copy.deepcopy(base),'E0').to(opt.device);e2=EventModel(copy.deepcopy(base),'E2').to(opt.device)
    results=[]
    for model in [e0,e2]:
        model.train()
        for m in model.modules():
            if isinstance(m,torch.nn.Dropout):m.eval()
            if isinstance(m,torch.nn.MultiheadAttention):m.dropout=0.
        torch.manual_seed(2024)
        out=model(**inputs,targets=targets)
        losses=criterion(batch,out,targets)
        total=sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
        assert torch.isfinite(total),losses
        total.backward()
        if model.variant=='E0':reference={k:out[k].detach().clone() for k in ['out_coord','out_class']}
        else:
            for key in reference:torch.testing.assert_close(out[key],reference[key],rtol=0,atol=0)
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.base.exist_head.parameters())
            assert any(p.grad is not None and p.grad.abs().sum()>0 for p in model.base.transformer.encoder.parameters())
            assert model.base.exist_head.context is None
        results.append({'variant':model.variant,'losses':{k:float(v.detach()) for k,v in losses.items() if k in criterion.weight_dict},
                        'parameters':sum(p.numel() for p in model.parameters())})
        # An all-negative batch must not call interval regression with empty GT.
        nb=start_end_collate([ds[0]]);ni,nt=prepare_batch_inputs(nb[1],opt.device);nt['label']=nb[0];nt['fps']=torch.full((1,),.5,device=opt.device)
        nl=criterion(nb,model(**ni,targets=nt),nt)
        assert all(torch.isfinite(v) for k,v in nl.items() if k in criterion.weight_dict)
        # Native inference assumes bs=1. Restore dropout probabilities to config.
        for m in model.modules():
            if isinstance(m,torch.nn.MultiheadAttention):m.dropout=.1
        pred=predict(model,ds,opt);metrics=evaluate(pred,ds.data,opt)
        save(ROOT/'tests'/f'{model.variant}_fixture_metrics.json',metrics)
    assert results[1]['parameters']>results[0]['parameters']
    scope=scope_audit()
    cp=ASSETS/'checkpoint/flashVTG_gmr'
    ck=torch.load(cp,map_location='cpu',weights_only=False)
    state=ck.get('model',ck.get('state_dict'));assert state is not None
    state={k.removeprefix('module.'):v for k,v in state.items()}
    base.load_state_dict(state,strict=True)
    save(ROOT/'tests'/f'MODEL_CHECKS_{device}.json',{'state':'PASS','device':device,
        'torch_version':torch.__version__,'cuda_version':torch.version.cuda,
        'official_checkpoint_sha256':sha(cp),'official_checkpoint_strict_load':True,
        'fixtures':'Official Val: absent/single/multi',
        'checks':['same-weight train localization outputs identical','finite positive and null losses',
                  'Event branch and shared encoder gradients','capture cleared after forward',
                  'native batch1 inference and official metric suite'],
        'records':results,'outside_source':scope})
    print(json.dumps(results),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--device',default='cpu');main(p.parse_args().device)
