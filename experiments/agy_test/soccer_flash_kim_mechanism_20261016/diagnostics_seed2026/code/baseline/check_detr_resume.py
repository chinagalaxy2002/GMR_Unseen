"""Restart after an already committed final fixture epoch: no extra updates."""
from common import ROOT,save,sha,rows
from run_detr import execute
import argparse,json

def main(bb):
    checked=[]
    for variant in ['E0','E2']:
        run=ROOT/'tests/detr_smoke_runs'/f'{bb}_{variant}'
        assert json.loads((run/'COMPLETE.json').read_text())['smoke_only']
        before={name:sha(run/name) for name in ['best.ckpt','latest.ckpt','test_predictions.jsonl','trace.jsonl']}
        done=run/'COMPLETE.json';archive=run/'COMPLETE_before_resume.json';done.replace(archive)
        try:execute(variant,bb,'cpu',resume=True,smoke=True)
        except Exception:
            if not done.exists():archive.replace(done)
            raise
        after={name:sha(run/name) for name in before}
        assert before==after,(before,after)
        assert len(rows(run/'trace.jsonl'))==1
        assert json.loads(done.read_text())['trained_epochs']==1
        checked.append({'variant':variant,'no_extra_optimizer_steps':True,'predictions_identical':True,
                        'checkpoint_and_trace_hashes_unchanged':True})
    save(ROOT/'tests'/f'DETR_RESUME_CHECKS_{bb}.json',{'state':'PASS','backbone':bb,'checks':checked,
         'data':'three official Val fixtures reused only for code validation'})
    print(json.dumps({'state':'PASS','backbone':bb,'checks':checked}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backbone',choices=['moment','qd'],required=True);main(p.parse_args().backbone)
