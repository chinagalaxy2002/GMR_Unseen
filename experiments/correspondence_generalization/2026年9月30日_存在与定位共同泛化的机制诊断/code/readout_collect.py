"""Native precision readout from three saved best models; inference only."""
import json
from pathlib import Path
from phase2 import STAGE,HERE,dump,rows,sha

DEST=STAGE/'readout_analysis'
RUNS={'throw':HERE/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1',
      'open_close':STAGE/'runs/open_close_qd_gmr_baseline_s3407_attempt1',
      'sit':STAGE/'diagnostics/sit/baseline/evaluation_bundle'}


def main():
    import torch
    from torch.utils.data import DataLoader
    import queue_worker as w
    torch.set_num_threads(4);torch.manual_seed(3407)
    state={'state':'running','training_updates':0,'families':{}}
    dump(DEST/'state.json',state)
    for family,run in RUNS.items():
        ck=torch.load(run/'best.ckpt',map_location='cpu',weights_only=False)
        opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0
        ev,dsmod=w.modules('qd');model,_,*_=w.make_model(opt,ev,'baseline','qd')
        model.load_state_dict(ck['model']);model.eval()
        for split,view,predname in [('seen','val_seen','best_seen_predictions.jsonl'),('pseudo','pseudo','pseudo_predictions.jsonl')]:
            output=DEST/f'{family}_{split}_native.jsonl';assert not output.exists(),output
            ds=w.dataset(opt,dsmod,run/'views'/f'{view}.jsonl','qd',labels=False)
            old={str(p['qid']):p for p in rows(run/predname)};records=[];largest=0.0;match=0
            with torch.inference_mode():
                for meta,batch in DataLoader(ds,batch_size=16,num_workers=0,collate_fn=dsmod.start_end_collate):
                    inputs,_=dsmod.prepare_batch_inputs(batch,'cuda:0');out=model(**inputs)
                    logits=out['pred_exist_logits'].cpu();sigmoid=out['pred_exist_logits'].sigmoid().cpu()
                    fg=out['pred_logits'].softmax(-1)[...,0].cpu()
                    for i,r in enumerate(meta):
                        score=float(sigmoid[i]);serialized=float(f'{score:.4f}');original=old[str(r['qid'])]['pred_exist_score']
                        largest=max(largest,abs(score-original));match+=serialized==original
                        records.append({'qid':str(r['qid']),'vid':r['vid'],'exist_logit':float(logits[i]),
                            'exist_sigmoid_fp32':score,'exist_sigmoid_serialized':serialized,'original_saved_score':original,
                            'native_foreground_slot_probabilities':fg[i].tolist()})
            assert len(records)==len(ds) and largest<=.0002,(family,split,largest)
            output.write_text(''.join(json.dumps(r)+'\n' for r in records))
            state['families'][family+'/'+split]={'rows':len(records),'saved_probability_max_abs_error':largest,
                'serialized_exact_match_fraction':match/len(records),'checkpoint_epoch_zero_based':ck['epoch'],
                'checkpoint_sha256':sha(run/'best.ckpt'),'view_sha256':sha(run/'views'/f'{view}.jsonl'),
                'original_prediction_sha256':sha(run/predname),'output_sha256':sha(output)}
            dump(DEST/'state.json',state)
        del model
    state.update(state='inference_completed',source_sha256=sha(Path(__file__)))
    dump(DEST/'state.json',state)
    print(json.dumps(state))


if __name__=='__main__':main()
