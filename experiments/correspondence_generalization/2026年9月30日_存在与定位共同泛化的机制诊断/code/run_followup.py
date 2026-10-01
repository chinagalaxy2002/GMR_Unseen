"""Supplement existing live queue; never trains, restarts or overwrites it."""
import fcntl
import json
import os
import subprocess
import sys
import time
import traceback
from phase2 import STAGE, HERE, dump

PY=sys.executable
state={'state':'running','pid':os.getpid(),'training_started':False,'training_updates':0,'tasks':{}}


def save():dump(STAGE/'followup_state.json',state)


def command(script,run,family,method,gpu,artifact):
    key=f'{family}_{method}_{script}'
    output=STAGE/'diagnostics'/family/method/artifact
    if output.exists():
        assert json.loads(output.read_text())['state']=='completed'
        state['tasks'][key]={'state':'existing_completed','artifact':str(output)};save();return
    # Do not retry incomplete sensitivity/latest outputs silently.
    if script=='sensitivity' and (output.parent/'INPUT_SENSITIVITY_MANIFEST.json').exists():
        raise RuntimeError(f'Incomplete sensitivity: {output.parent}')
    if script=='latest_decomposition' and (output.parent/'latest_predictions').exists():
        raise RuntimeError(f'Incomplete latest audit: {output.parent}')
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4')
    log=STAGE/'logs'/f'{key}.log'
    with log.open('a') as f:
        p=subprocess.Popen([PY,'-u',str(STAGE/'code'/f'{script}.py'),'--run',str(run),'--family',family,'--method',method],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT)
        state['tasks'][key]={'state':'running','pid':p.pid,'gpu':gpu,'log':str(log)};save()
        ret=p.wait()
    state['tasks'][key].update(state='completed' if ret==0 else 'failed',returncode=ret);save()
    if ret:raise RuntimeError(f'{key} failed ({ret}); no retry')


def supplements(run,family,method,gpu):
    for script,artifact in [('sensitivity','INPUT_SENSITIVITY.json'),('latest_decomposition','LATEST_FAILURE_DECOMPOSITION.json'),('gate_audit','GATE_POSTPROCESS_AUDIT.json')]:
        command(script,run,family,method,gpu,artifact)


def main():
    with (STAGE/'followup.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);save()
        try:
            for method in ('baseline','adapter'):
                supplements(HERE/'runs/autonomous_queue_20260930_strict/jobs'/f'dev_A1_qd_gmr_{method}_s3407_attempt1','throw',method,0)
            pending={'open_close':0,'sit':1}
            while pending:
                queue=json.loads((STAGE/'queue_state.json').read_text())
                if queue['state']=='failed':raise RuntimeError('Main queue failed; inspect preserved records')
                for family,gpu in list(pending.items()):
                    key=family+'_baseline_D2_latest'
                    if queue['tasks'].get(key,{}).get('state')=='completed':
                        supplements(STAGE/'runs'/f'{family}_qd_gmr_baseline_s3407_attempt1',family,'baseline',gpu)
                        del pending[family]
                state['waiting_families']=list(pending);save()
                if pending:time.sleep(15)
            # Main scheduler may still be finalizing after the last completed subprocess.
            while json.loads((STAGE/'queue_state.json').read_text())['state']=='running':time.sleep(2)
            env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
            with (STAGE/'logs/cross_family_summary.log').open('a') as f:
                ret=subprocess.call([PY,'-u',str(STAGE/'code/summarize.py')],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT)
            if ret:raise RuntimeError(f'Cross-family summary failed ({ret}); no retry')
            state['state']='supplemental_diagnostics_completed_decision_pending';save()
        except BaseException:
            state.update(state='failed',error=traceback.format_exc());save();raise


if __name__=='__main__':main()
