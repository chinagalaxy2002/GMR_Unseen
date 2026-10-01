"""Two new holdout baselines and ordered diagnostics; no automatic complex methods."""
import concurrent.futures,fcntl,json,os,subprocess,sys,time,traceback
from pathlib import Path
from threading import RLock
STAGE=Path(__file__).resolve().parents[1];HERE=STAGE.parent;PY=sys.executable
sys.path.insert(0,str(STAGE/'code'));from phase2 import dump,diagnose_cpu
lock=RLock();state={'state':'running','pid':os.getpid(),'tasks':{},'seed':3407,'conditional_interventions':'not_started; requires cross-family diagnostic decision'}
def save():
 with lock:dump(STAGE/'queue_state.json',state)
def command(args,gpu,key):
 env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),CORRESPONDENCE_SKIP_BUDGET_AUDIT='1',PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(HERE/'cache/runtime/pycache'),TMPDIR=str(HERE/'cache/runtime'))
 log=STAGE/'logs'/f'{key}.log';log.parent.mkdir(exist_ok=True)
 with log.open('a') as f:
  proc=subprocess.Popen([PY,'-u',*map(str,args)],cwd=HERE,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  with lock:state['tasks'][key]={'state':'running','pid':proc.pid,'gpu':gpu,'log':str(log)};save()
  ret=proc.wait()
 with lock:state['tasks'][key].update(state='completed' if ret==0 else 'failed',returncode=ret);save()
 if ret:raise RuntimeError(f'{key} failed ({ret}); records retained, no automatic retry')
def diagnostics(run,family,method,gpu):
 key=f'{family}_{method}'
 diagnose_cpu(run,family,method) # D3, then D1 from saved predictions
 command([STAGE/'code/phase2.py','controlled','--run',run,'--family',family,'--method',method],gpu,key+'_D1_controlled')
 d=json.loads((STAGE/'diagnostics'/family/method/'FAILURE_DECOMPOSITION.json').read_text())['pseudo'];batches=16 if (d['raw_errors_over_hard_failures'] or 0)>=.8 else 64
 for checkpoint in ['best','latest']:
  command([STAGE/'code/phase2.py','gradient','--run',run,'--family',family,'--method',method,'--batches',batches,'--checkpoint',checkpoint],gpu,key+'_D2_'+checkpoint)
def family_job(family,gpu):
 run=STAGE/'runs'/f'{family}_qd_gmr_baseline_s3407_attempt1'
 if not (run/'result.json').exists():
  if run.exists():raise RuntimeError(f'Incomplete existing run {run}; inspect before recovery')
  command([STAGE/'code/development_worker.py',run,'--backbone','qd','--split','A1','--track','gmr','--method','baseline','--seed','3407','--development','--development-view',STAGE/'views'/family],gpu,family+'_baseline_train')
 else:assert json.loads((run/'result.json').read_text())['state']=='completed'
 diagnostics(run,family,'baseline',gpu)
def throw_job():
 for method in ['baseline','adapter']:
  diagnostics(HERE/'runs/autonomous_queue_20260930_strict/jobs'/f'dev_A1_qd_gmr_{method}_s3407_attempt1','throw',method,0)
def main():
 with (STAGE/'queue.lock').open('w') as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);save()
  try:
   # GPU0: one baseline plus throw diagnostics; GPU1: one baseline. <=2 per GPU.
   with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures=[pool.submit(family_job,'open_close',0),pool.submit(family_job,'sit',1),pool.submit(throw_job)]
    for future in futures:future.result()
   state['state']='diagnostics_completed_decision_pending';save()
  except BaseException:
   state.update(state='failed',error=traceback.format_exc());save();raise
if __name__=='__main__':main()
