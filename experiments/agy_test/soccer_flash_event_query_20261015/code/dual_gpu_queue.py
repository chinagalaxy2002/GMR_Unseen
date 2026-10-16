"""Adopt the running Flash pair, then Moment pair, then QD pair; one job/GPU."""
from common import ROOT,save,sha,scope_audit
from queue_status import main as report
import argparse,fcntl,json,os,subprocess,sys,time

def read(path,default=None):return json.loads(path.read_text()) if path.exists() else default

def process(pid):
    try:
        p=ROOT.__class__('/proc')/str(pid);s=(p/'stat').read_text().rsplit(') ',1)[1].split()
        return {'pid':int(pid),'state':s[0],'starttime':s[19],
            'argv':[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\0') if x]}
    except FileNotFoundError:return None

def alive(job):
    if not job.get('pid'):return False
    p=process(job['pid'])
    if not p or p['state']=='Z' or p['starttime']!=job.get('starttime'):return False
    expected=str(ROOT/'code'/('run.py' if job['backbone']=='flash' else 'run_detr.py'))
    return (expected in p['argv'] and '--variant' in p['argv'] and job['variant'] in p['argv']
        and (job['backbone']=='flash' or ('--backbone' in p['argv'] and job['backbone'] in p['argv'])))

def validate_ready():
    manifest=read(ROOT/'provenance/DETR_FROZEN_SOURCE.json')
    assert manifest and all(sha(ROOT/p)==h for p,h in manifest.items()),'DETR source hash mismatch'
    for bb in ['moment','qd']:
        assert read(ROOT/'tests'/f'DETR_CHECKS_{bb}_cpu.json',{}) .get('state')=='PASS'
        assert read(ROOT/'tests'/f'DETR_RESUME_CHECKS_{bb}.json',{}).get('state')=='PASS'
        for variant in ['E0','E2']:
            done=read(ROOT/'tests/detr_smoke_runs'/f'{bb}_{variant}'/'COMPLETE.json',{})
            assert done.get('smoke_only') is True
    scope_audit()

def gpu_free(gpu):
    info=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.free','--format=csv,noheader,nounits'],text=True)
    return any(int(idx.strip())==gpu and int(mem.strip())>=4096 for idx,mem in (line.split(',') for line in info.splitlines()))

def main():
    lock=(ROOT/'dual_gpu_queue.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    plan=read(ROOT/'QUEUE_PLAN.json');assert plan and plan['ready'] is True
    validate_ready()
    jobs=plan['jobs'];children={};handles={}
    # Recover supervisor state so a restart adopts children instead of duplicating them.
    previous=read(ROOT/'QUEUE_STATUS.json',{})
    for job in jobs:
        prior=next((r for r in previous.get('jobs',[]) if r['id']==job['id']),{})
        if prior.get('pid'):job.update({k:prior[k] for k in ['pid','starttime'] if k in prior})
    for job in jobs:
        if job.get('pid') and not job.get('starttime'):
            p=process(job['pid'])
            if p:job['starttime']=p['starttime']
    last_report=0
    while True:
        for job in jobs:
            run=ROOT/job['run'];status=read(run/'STATUS.json',{})
            child=children.get(job['id'])
            if child is not None and child.poll() is not None:
                handles.pop(job['id']).close();del children[job['id']]
            if alive(job):
                p=process(job['pid']);job['state']='paused' if p['state'] in ('T','t') else 'running'
            elif (run/'COMPLETE.json').exists():job['state']='complete'
            elif job.get('pid') or status.get('state')=='failed':
                job['state']='failed';job['error']=status.get('error','Process exited without COMPLETE.json')
            else:job['state']='pending'
        failed=any(j['state']=='failed' for j in jobs)
        active_stage=next((bb for bb in ['flash','moment','qd'] if not all(j['state']=='complete' for j in jobs if j['backbone']==bb)),None)
        if not failed and active_stage in ('moment','qd'):
            for job in jobs:
                if job['backbone']!=active_stage or job['state']!='pending':continue
                gpu=job['gpu']
                if any(j['gpu']==gpu and j['state'] in ('running','paused') for j in jobs):continue
                if not gpu_free(gpu):continue
                validate_ready()
                env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE='1')
                handle=(ROOT/'logs'/f"{job['id']}.log").open('a')
                argv=[sys.executable,'-B',str(ROOT/'code/run_detr.py'),'--backbone',job['backbone'],'--variant',job['variant'],'--preflight']
                child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT,start_new_session=True)
                p=process(child.pid);assert p
                children[job['id']]=child;handles[job['id']]=handle
                job.update(pid=child.pid,starttime=p['starttime'],state='running',launched=time.time())
        complete=all(j['state']=='complete' for j in jobs)
        save(ROOT/'QUEUE_STATUS.json',{'state':'complete' if complete else ('failed' if failed else 'running'),
            'updated':time.time(),'supervisor_pid':os.getpid(),'jobs':jobs,'active_stage':active_stage,
            'policy':'both Flash jobs finish before Moment pair; both Moment jobs finish before QD pair; E0 GPU0/E2 GPU1',
            'running':[j for j in jobs if j['state'] in ('running','paused')],
            'pending':[j['id'] for j in jobs if j['state']=='pending']})
        if time.time()-last_report>=60 or complete or failed:report(quiet=True);last_report=time.time()
        if complete or (failed and not any(j['state'] in ('running','paused') for j in jobs)):return
        time.sleep(15)

if __name__=='__main__':main()
