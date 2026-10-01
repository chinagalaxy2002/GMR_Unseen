"""Separate unchanged scalar gate from asymmetric saved temporal postprocessing."""
import argparse
import copy
import json
from pathlib import Path
from phase2 import STAGE, HERE, REPO, dump, hit, rows, sha


def main():
    import torch
    import queue_worker as w
    from training.qd_detr_gmr.postprocessing import PostProcessorDETR

    a=argparse.ArgumentParser();a.add_argument('--run',type=Path,required=True)
    a.add_argument('--family',required=True);a.add_argument('--method',default='baseline')
    args=a.parse_args();dest=STAGE/'diagnostics'/args.family/args.method/'GATE_POSTPROCESS_AUDIT.json'
    assert not dest.exists(),dest
    ck=torch.load(args.run/'best.ckpt',map_location='cpu',weights_only=False);opt=ck['opt']
    proc=PostProcessorDETR(clip_length=opt.clip_length,min_ts_val=0,max_ts_val=float(getattr(opt,'max_ts_val',150)),
                          min_w_l=1,max_w_l=float(getattr(opt,'max_ts_val',150)),move_window_method='left',process_func_names=('clip_ts','round_multiple'))
    result={}
    for split,gt,pred in [('pseudo','pseudo','pseudo_predictions.jsonl'),('seen','val_seen','best_seen_predictions.jsonl')]:
        rr=rows(args.run/'views'/f'{gt}.jsonl');pp={str(p['qid']):p for p in rows(args.run/pred)}
        aligned=proc([dict(qid=p['qid'],pred_relevant_windows=copy.deepcopy(p['pred_relevant_windows_pre_exist'])) for p in pp.values()])
        aligned={str(p['qid']):p for p in aligned}
        mismatches=[];changes=[];positive=0;aligned_hits=0;gated_hits=0
        for r in rr:
            qid=str(r['qid']);p=pp[qid];ap=aligned[qid]
            ac=[w[:2] for w in ap['pred_relevant_windows']];gc=[w[:2] for w in p['pred_relevant_windows']]
            if ac!=gc:mismatches.append(qid)
            if r['exist_label']:
                positive+=1
                raw=hit(p,r,'pred_relevant_windows_pre_exist');gated=hit(p,r,'pred_relevant_windows');al=hit(ap,r,'pred_relevant_windows')
                aligned_hits+=al;gated_hits+=gated
                if raw!=gated:changes.append({'qid':qid,'raw_hit':raw,'gated_hit':gated,'aligned_raw_hit':al})
        result[split]={'rows':len(rr),'positive':positive,'all_ranked_coordinate_mismatches':len(mismatches),
                       'mismatch_qids':mismatches,'raw_to_gated_hit_changes':changes,
                       'aligned_raw_R1_05_auxiliary':aligned_hits/positive,'official_gated_R1_05':gated_hits/positive,
                       'prediction_sha256':sha(args.run/pred)}
    dump(dest,{'state':'completed','training_updates':0,'results':result,
        'source_sha256':sha(Path(__file__)),
        'official_evaluator_sha256':sha(HERE/'code/vendor/qd_evaluate.py'),
        'official_postprocessor_sha256':sha(REPO/'training/qd_detr_gmr/postprocessing.py'),
        'gate_sha256':sha(REPO/'models/qd_detr_gmr/gmr_adapter.py'),
        'interpretation':'Official soft gate is a per-row nonnegative scalar. Exact positive scalar scaling preserves within-row ranking. Saved gated coordinates alone receive clip_ts/round_multiple; frozen raw endpoint remains untouched. When aligned coordinates match, hit changes are explained by temporal postprocessing rather than gate veto or reranking. Aligned raw is auxiliary only, not a replacement co-primary endpoint.'})
    print(json.dumps({'state':'completed','output':str(dest)}))


if __name__=='__main__':main()
