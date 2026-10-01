"""Audit complete-block norms and unused/zero gradients on frozen D2 batches."""
import argparse
import collections
import json
from pathlib import Path
from phase2 import STAGE, dump, sha


def main():
    import numpy as np
    import torch
    from torch.utils.data import DataLoader
    import queue_worker as w

    a=argparse.ArgumentParser();a.add_argument('--run',type=Path,required=True)
    a.add_argument('--family',required=True);a.add_argument('--method',default='baseline');args=a.parse_args()
    dest=STAGE/'diagnostics'/args.family/args.method
    output=dest/'GRADIENT_DETAIL.json';assert not output.exists(),output
    torch.set_num_threads(4);results={};cache={}
    for checkpoint in ('best','latest'):
        original=json.loads((dest/f'GRADIENT_RELATIONS_{checkpoint}.json').read_text())
        ckpath=args.run/f'{checkpoint}.ckpt'
        assert sha(ckpath)==original['checkpoint_sha256'], 'Checkpoint changed since D2'
        ck=torch.load(ckpath,map_location='cpu',weights_only=False)
        tensor_hash=w.hashlib.sha256()
        for key,value in sorted(ck['model'].items()):
            tensor_hash.update(key.encode());tensor_hash.update(value.cpu().numpy().tobytes())
        key=tensor_hash.hexdigest()
        if key in cache:
            results[checkpoint]={**cache[key],'reused_identical_model_from':'best','independent_checkpoint_evidence':False}
            continue
        torch.manual_seed(3407)
        opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0
        ev,dsmod=w.modules('qd');model,criterion,*_=w.make_model(opt,ev,args.method,'qd')
        model.load_state_dict(ck['model']);model.eval();criterion.eval()
        ds=w.dataset(opt,dsmod,args.run/'views/train.jsonl','qd')
        lookup={str(r['qid']):i for i,r in enumerate(ds.data)}
        batches=[[lookup[q] for q in batch] for batch in original['qids']]
        assert all(ds.data[i]['exist_label']==1 for batch in batches for i in batch)
        blocks=collections.defaultdict(list)
        for name,param in model.named_parameters():
            if 'correspondence_adapter' in name:block='adapter'
            elif 'input_vid_proj' in name or 'input_txt_proj' in name:block='input_projection'
            elif 'decoder' in name:block='decoder'
            elif 'transformer' in name:block='interaction'
            else:continue
            blocks[block].append(param)
        params=[p for ps in blocks.values() for p in ps];records=collections.defaultdict(list);observed_loss_keys=set()
        for meta,batch in DataLoader(ds,batch_sampler=batches,num_workers=0,collate_fn=dsmod.start_end_collate):
            inputs,targets=dsmod.prepare_batch_inputs(batch,'cuda:0')
            weighted={k:v*criterion.weight_dict[k] for k,v in criterion(model(**inputs),targets).items() if k in criterion.weight_dict}
            loc_keys=[k for k in weighted if k.startswith(('loss_label','loss_span','loss_giou'))]
            other_keys=[k for k in weighted if k not in loc_keys and k not in ('loss_exist','loss_saliency')]
            assert not other_keys, f'Unexpected non-location keys: {other_keys}'
            observed_loss_keys.update(weighted)
            losses={'exist':weighted['loss_exist'],'loc':sum(weighted[k] for k in loc_keys)}
            if 'loss_saliency' in weighted:losses['saliency']=weighted['loss_saliency']
            grads={k:torch.autograd.grad(v,params,retain_graph=True,allow_unused=True) for k,v in losses.items() if isinstance(v,torch.Tensor) and v.requires_grad}
            offset=0
            for block,ps in blocks.items():
                for task in ('exist','loc','saliency'):
                    gg=grads.get(task)
                    if gg is None:
                        records[block+'|'+task].append({'available':False,'reason':'loss absent or no differentiable loss'});continue
                    gs=gg[offset:offset+len(ps)];used=[g for g in gs if g is not None]
                    nonfinite=sum(not bool(torch.isfinite(g).all()) for g in used)
                    records[block+'|'+task].append({'available':True,'tensor_count':len(ps),'unused_tensor_fraction':sum(g is None for g in gs)/len(ps),
                        'zero_among_used_tensor_fraction':sum(not bool(torch.count_nonzero(g)) for g in used)/len(used) if used else None,
                        'nonfinite_used_tensors':nonfinite,'full_block_norm':float(torch.sqrt(sum(g.square().sum() for g in used))) if used and not nonfinite else None})
                for other in ('loc','saliency'):
                    if other not in grads:continue
                    aa=grads['exist'][offset:offset+len(ps)];bb=grads[other][offset:offset+len(ps)]
                    # Treat unused entries as structural zeros; norms include all task-active parameters.
                    an=sum(g.square().sum() for g in aa if g is not None);bn=sum(g.square().sum() for g in bb if g is not None)
                    dot=sum((a*b).sum() for a,b in zip(aa,bb) if a is not None and b is not None)
                    den=torch.sqrt(an*bn) if isinstance(an,torch.Tensor) and isinstance(bn,torch.Tensor) else None
                    cosine=float(dot/den) if den is not None and den>0 and torch.isfinite(den) else None
                    records[block+'|exist_vs_'+other].append({'full_block_cosine':cosine})
                offset+=len(ps)
        summary={}
        for block,rr in records.items():
            if 'exist_vs' in block:
                good=[r['full_block_cosine'] for r in rr if r['full_block_cosine'] is not None and np.isfinite(r['full_block_cosine'])]
                summary[block]={'valid_batches':len(good),'invalid_batches':len(rr)-len(good),'median_cosine':float(np.median(good)) if good else None,'negative_fraction':float(np.mean(np.asarray(good)<0)) if good else None}
            else:
                good=[r for r in rr if r.get('available')]
                summary[block]={'available_batches':len(good),'unavailable_batches':len(rr)-len(good),'nonfinite_tensors':sum(r['nonfinite_used_tensors'] for r in good),
                    'mean_unused_tensor_fraction':float(np.mean([r['unused_tensor_fraction'] for r in good])) if good else None,
                    'median_full_block_norm':float(np.median([r['full_block_norm'] for r in good if r['full_block_norm'] is not None])) if any(r['full_block_norm'] is not None for r in good) else None}
        result={'checkpoint_epoch_zero_based':ck['epoch'],'checkpoint_sha256':sha(ckpath),'model_tensor_sha256':key,
            'original_diagnostic_sha256':sha(dest/f'GRADIENT_RELATIONS_{checkpoint}.json'),'qids':original['qids'],'batches':len(batches),
            'observed_weighted_loss_keys':sorted(observed_loss_keys),'loss_weights':criterion.weight_dict,'summary':summary,'batch_records':records,
            'reused_identical_model_from':None,'independent_checkpoint_evidence':True}
        results[checkpoint]=result;cache[key]=result
    dump(output,{'state':'completed','training_updates':0,'source_sha256':sha(Path(__file__)),'checkpoints':results,
        'interpretation':'S+ only, eval mode local geometry; unused tensors treated as zero in full-block cosine. Original norms used only the jointly differentiable tensor intersection; detail fixes interpretation without overwriting original output. Inactive saliency is unavailable, not agreement. No S- localization gradient is inferred.'})
    print(json.dumps({'state':'completed','output':str(output)}))


if __name__=='__main__':main()
