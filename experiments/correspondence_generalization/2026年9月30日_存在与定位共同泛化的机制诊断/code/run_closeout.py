"""Explicitly authorized evaluation-only closeout; never invokes a trainer."""
import fcntl
import json
import os
import subprocess
import sys
import traceback
from phase2 import STAGE,HERE,dump,sha

state={'state':'running','pid':os.getpid(),'training_updates':0,'new_training_epochs':0,'tasks':{}}


def save():dump(STAGE/'closeout_state.json',state)


def command(key,args,gpu=0):
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4')
    log=STAGE/'logs'/f'closeout_{key}.log'
    with log.open('x') as f:
        proc=subprocess.Popen([sys.executable,'-u',*map(str,args)],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT)
        state['tasks'][key]={'state':'running','pid':proc.pid,'gpu':gpu,'log':str(log)};save()
        ret=proc.wait()
    state['tasks'][key].update(state='completed' if ret==0 else 'failed',returncode=ret);save()
    if ret:raise RuntimeError(f'{key} failed ({ret}); preserved, no automatic retry')


def main():
    with (STAGE/'closeout.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not (STAGE/'closeout_state.json').exists(),'Inspect existing closeout; no automatic retry'
        save()
        try:
            bundle=STAGE/'diagnostics/sit/baseline/evaluation_bundle'
            command('sit_best_evaluation',[STAGE/'code/evaluate_sit.py'])
            for action in ('cpu','controlled'):
                command('sit_'+action,[STAGE/'code/phase2.py',action,'--run',bundle,'--family','sit','--method','baseline'])
            for script in ('sensitivity','latest_decomposition','gate_audit'):
                command('sit_'+script,[STAGE/'code'/f'{script}.py','--run',bundle,'--family','sit','--method','baseline'])
            failure=json.loads((STAGE/'diagnostics/sit/baseline/FAILURE_DECOMPOSITION.json').read_text())['pseudo']
            batches=16 if (failure['raw_errors_over_hard_failures'] or 0)>=.8 else 64
            for checkpoint in ('best','latest'):
                command('sit_gradient_'+checkpoint,[STAGE/'code/phase2.py','gradient','--run',bundle,'--family','sit','--method','baseline','--batches',batches,'--checkpoint',checkpoint])
            for family,run in [('sit',bundle),('open_close',STAGE/'runs/open_close_qd_gmr_baseline_s3407_attempt1')]:
                command(family+'_gradient_detail',[STAGE/'code/gradient_detail.py','--run',run,'--family',family,'--method','baseline'])
            state['state']='diagnostics_completed_summary_pending';save()
            command('cross_family_summary',[STAGE/'code/summarize.py','--closeout'])
            state['state']='summary_completed_report_pending';save()
            command('render_report',[STAGE/'code/render_report.py','--closeout'])
            freeze=json.loads((STAGE/'plan/CLOSEOUT_FREEZE.json').read_text())
            checks={p:sha(p)==expected for p,expected in freeze['protected_files_sha256'].items()}
            dump(STAGE/'report/CLOSEOUT_INTEGRITY.json',{'state':'completed','all_protected_files_unchanged':all(checks.values()),'checks':checks,'training_updates':0})
            assert all(checks.values()),'Protected asset changed; inspect integrity record'
            state['state']='evaluation_closeout_completed_decision_pending';save()
        except BaseException:
            state.update(state='failed',error=traceback.format_exc());save();raise


if __name__=='__main__':main()
