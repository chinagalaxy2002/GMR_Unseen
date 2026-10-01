"""D3 latest checkpoint audit, isolated predictions and seen-only threshold."""
import argparse
import collections
import json
import shutil
import sys
from pathlib import Path

from phase2 import STAGE, HERE, dump, rows, sha, hit


def main():
    import numpy as np
    import torch
    import queue_worker as w
    from sklearn.metrics import roc_auc_score

    a = argparse.ArgumentParser()
    a.add_argument('--run',type=Path,required=True)
    a.add_argument('--family',required=True)
    a.add_argument('--method',default='baseline')
    args=a.parse_args()
    output=STAGE/'diagnostics'/args.family/args.method/'LATEST_FAILURE_DECOMPOSITION.json'
    assert not output.exists(), output
    latest=args.run/'latest.ckpt'
    best=args.run/'best.ckpt'
    torch.set_num_threads(4)
    torch.manual_seed(3407)
    ck=torch.load(latest,map_location='cpu',weights_only=False)
    bestck=torch.load(best,map_location='cpu',weights_only=False)
    same=all(torch.equal(v,bestck['model'][k]) for k,v in ck['model'].items())
    del bestck
    dest=output.parent/'latest_predictions'
    dest.mkdir(exist_ok=False)
    if same:
        shutil.copyfile(args.run/'pseudo_predictions.jsonl',dest/'pseudo_predictions.jsonl')
        shutil.copyfile(args.run/'best_seen_predictions.jsonl',dest/'seen_predictions.jsonl')
    else:
        opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0;opt.results_dir=str(dest)
        ev,dsmod=w.modules('qd')
        model,criterion,*_=w.make_model(opt,ev,args.method,'qd')
        model.load_state_dict(ck['model']);model.eval()
        with torch.no_grad():
            for split,source in [('pseudo','pseudo'),('seen','val_seen')]:
                w.official_eval(model,criterion,opt,ev,dsmod,args.run/'views'/f'{source}.jsonl',f'{split}_predictions.jsonl','qd')
    seen=rows(args.run/'views/val_seen.jsonl')
    threshold=w.existence_summary(seen,rows(dest/'seen_predictions.jsonl'))['threshold']
    results={}
    for split,source in [('pseudo','pseudo'),('seen','val_seen')]:
        rr=rows(args.run/'views'/f'{source}.jsonl')
        pp={str(p['qid']):p for p in rows(dest/f'{split}_predictions.jsonl')}
        assert len(rr)==len(pp)
        counts=collections.Counter();ys=[];ss=[]
        for r in rr:
            p=pp[str(r['qid'])];score=p['pred_exist_score'];accept=score>=threshold
            ys.append(r['exist_label']);ss.append(score)
            if r['exist_label']:
                raw=hit(p,r,'pred_relevant_windows_pre_exist');gated=hit(p,r,'pred_relevant_windows')
                counts['positive']+=1
                counts['raw_correct' if raw else 'raw_incorrect']+=1
                if raw:counts['raw_correct_accepted' if accept else 'raw_correct_rejected']+=1
                counts['positive_rejected']+=not accept
                counts['official_gated_correct']+=gated
                counts['raw_correct_gated_wrong']+=raw and not gated
                counts['raw_wrong_gated_correct']+=not raw and gated
                counts['official_empty']+=not p['pred_relevant_windows']
            else:
                counts['negative']+=1;counts['negative_accepted']+=accept
        pos=counts['positive'];neg=counts['negative'];correct=counts['raw_correct']
        fail=counts['raw_incorrect']+counts['raw_correct_rejected']
        results[split]={'AUROC':float(roc_auc_score(ys,ss)), 'raw_R1_05':correct/pos,
            'gated_R1_05':counts['official_gated_correct']/pos, 'FRR':counts['positive_rejected']/pos,
            'RR':1-counts['negative_accepted']/neg, 'counts':dict(counts),
            'raw_correct_rejected_over_raw_correct':counts['raw_correct_rejected']/correct if correct else None,
            'raw_errors_over_hard_failures':counts['raw_incorrect']/fail if fail else None,
            'threshold':threshold,'threshold_source':'latest checkpoint seen validation only; Youden J, diagnostic only',
            'source_prediction_sha256':sha(dest/f'{split}_predictions.jsonl')}
    dump(output,{'state':'completed','training_updates':0,'checkpoint_epoch_zero_based':ck['epoch'],
        'checkpoint_sha256':sha(latest),'source_sha256':sha(Path(__file__)),
        'same_model_tensors_as_best':same,'predictions_reused_from_best':same,'results':results,
        'limitations':'Latest comparison is descriptive, not an alternative pseudo-based checkpoint selection or full training trajectory; unchanged official gate, diagnostic threshold fitted on latest seen only.'})
    print(json.dumps({'state':'completed','output':str(output),'same_model_tensors_as_best':same}))


if __name__=='__main__':main()
