"""Bounded process concurrency, NOT agent delegation or an old queue."""
from common import *
import subprocess, time

def main():
    status('event_fits','running',max_parallel=4,max_per_gpu=2)
    pending=[(f,k) for f in FAMILIES for k in MODULES if not (BASE/f'runs/minimal_validation/{f}_{k}.pt').exists()]
    active=[];failures=[];completed=[]
    while pending or active:
        for gpu in [0,1]:
            while pending and sum(x['gpu']==gpu for x in active)<2:
                f,k=pending.pop(0);log=BASE/f'runs/minimal_validation/{f}_{k}_fit.log'
                stream=log.open('a')
                cmd=[sys.executable,'-B',str(BASE/'code/event_modules.py'),'fit','--family',f,'--module',k,'--device',f'cuda:{gpu}']
                proc=subprocess.Popen(cmd,cwd=BASE,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'2'})
                active.append({'gpu':gpu,'family':f,'module':k,'process':proc,'stream':stream,'pid':proc.pid,'started':now()})
                print('launched',f,k,'GPU',gpu,'pid',proc.pid,flush=True)
        time.sleep(1)
        for task in list(active):
            rc=task['process'].poll()
            if rc is not None:
                task['stream'].close();active.remove(task)
                rec={k:v for k,v in task.items() if k not in ['process','stream']};rec.update(returncode=rc,finished=now())
                (completed if rc==0 else failures).append(rec)
                print('finished',task['family'],task['module'],rc,flush=True)
        dump('runs/minimal_validation/FIT_SCHEDULER.json',{'pending':pending,'active':[{k:v for k,v in x.items() if k not in ['process','stream']} for x in active],'completed':completed,'failures':failures,'max_per_gpu':2,'max_parallel':4})
        if failures:
            for task in active:
                task['process'].terminate();task['stream'].close()
            status('event_fits','failed',failures=failures);raise RuntimeError('Fit failed; preserve logs and do not automatically restart.')
    status('event_fits','completed',fits=len(completed),max_parallel=4,max_per_gpu=2)

if __name__=='__main__':
    main()
