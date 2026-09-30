"""Persistent, resumable execution queue. Launch once under tmux.
Conditional skips are scientific decisions from frozen gates, not silent success.
"""
import concurrent.futures,fcntl,hashlib,json,os,shutil,subprocess,sys,threading,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
CFG=HERE/'code/configs/execution_queue.json'
ROOT=HERE/'runs/autonomous_queue_20260930';ROOT.mkdir(exist_ok=True);(ROOT/'jobs').mkdir(exist_ok=True)
config=json.loads(CFG.read_text());assert config['seeds']==[3407], 'Only seed 3407 is authorized';lock=threading.RLock();state_path=ROOT/'queue_state.json'
state=json.loads(state_path.read_text()) if state_path.exists() else {'state':'initializing','tasks':{},'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'queue_config_sha256':hashlib.sha256(CFG.read_bytes()).hexdigest(),'output':str(ROOT)}
assert state['queue_config_sha256']==hashlib.sha256(CFG.read_bytes()).hexdigest(),'Queue configuration changed after launch'

def save():
    with lock:
        tmp=state_path.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));tmp.replace(state_path)
def alive(pid):
    try:os.kill(pid,0);return True
    except ProcessLookupError:return False

def env(gpu):
    e=os.environ.copy();e.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(HERE/'cache/runtime'),TORCH_HOME=str(HERE/'cache/runtime/torch'),TMPDIR=str(HERE/'cache/runtime'));return e

def call(cmd,log,gpu):
    with Path(log).open('a') as f:
        p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env(gpu),cwd=HERE,start_new_session=True)
        return p.wait()

def task_id(phase,backbone,split,track,method,seed):return f'{phase}_{split}_{backbone}_{track}_{method}_s{seed}'
def wait_resource(gpu):
    while True:
        used=int(subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
        if used<512 and shutil.disk_usage(HERE).free>20*(1<<30):return
        with lock:state['resource_wait']={'gpu':gpu,'memory_used_mb':used,'disk_free_bytes':shutil.disk_usage(HERE).free};save()
        time.sleep(30)

def job(task,gpu):
    ident=task['id'];record=state['tasks'][ident]
    if record['state'] in ('completed','skipped'):return record.get('run')
    if record.get('state')=='running' and record.get('pid') and alive(record['pid']):
        while alive(record['pid']):time.sleep(15)
    if record.get('run') and (Path(record['run'])/'result.json').exists():
        previous=json.loads((Path(record['run'])/'result.json').read_text())
        if previous['state']=='completed':record['state']='completed';save();return record['run']
    attempts=record.setdefault('attempts',[])
    if record.get('run') and Path(record['run']).exists() and not any(v['run']==record['run'] for v in attempts):
        attempts.append({'run':record['run'],'returncode':'process ended before queue recorded exit'})
    for attempt in range(len(attempts),2):
        run=ROOT/'jobs'/f'{ident}_attempt{attempt+1}';record.update(state='running',gpu=gpu,run=str(run));save()
        wait_resource(gpu)
        cmd=[sys.executable,'-u',str(HERE/'code/queue_worker.py'),str(run),'--backbone',task['backbone'],'--split',task['split'],'--track',task['track'],'--method',task['method'],'--seed',str(task['seed'])]
        if task['phase']=='dev':cmd.append('--development')
        log=ROOT/f'{ident}_attempt{attempt+1}_console.log'
        with log.open('w') as f:
            proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env(gpu),cwd=HERE,start_new_session=True);record['pid']=proc.pid;save();ret=proc.wait()
        item={'run':str(run),'returncode':ret};attempts.append(item)
        if ret==0 and (run/'result.json').exists():
            r=json.loads((run/'result.json').read_text())
            if r['state']=='completed':record.update(state='completed',run=str(run));save();return str(run)
        record.update(state='retrying' if attempt==0 else 'failed',reason=f'worker returncode={ret} or incomplete result');save()
    record['state']='failed';save();return None

def enqueue(tasks):
    for t in tasks:state['tasks'].setdefault(t['id'],dict(t,state='pending',attempts=[]))
    save()
def parallel(tasks):
    # One worker thread owns each GPU; tasks from its lane run sequentially.
    enqueue(tasks)
    def lane(gpu,items):
        for t in items:job(t,gpu)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(lane,gpu,tasks[gpu::2]) for gpu in (0,1)]
        for f in fs:f.result()

def make(phase,b,s,t,m,seed):return {'id':task_id(phase,b,s,t,m,seed),'phase':phase,'backbone':b,'split':s,'track':t,'method':m,'seed':seed}

def ensure_diagnostic():
    run=HERE/'runs'/state.get('diagnostic_run',config['initial_diagnostic_run'])
    state.update(state='waiting_initial_diagnostic',diagnostic_run=run.name);save()
    while True:
        tr=json.loads((run/'status.json').read_text())
        if tr['state']=='training_complete_diagnostics_pending':break
        if tr['state']=='failed' or not alive(tr['pid']):
            # Historical run lacks complete RNG checkpoints for exact continuation;
            # restart from scratch once in a new run rather than inventing a resume.
            if state.get('diagnostic_restart'):raise RuntimeError('Diagnostic failed after one from-scratch recovery')
            retry=HERE/'runs'/'qd_throw_diagnostic_queue_recovery';state['diagnostic_restart']=True;state['diagnostic_run']=retry.name;save()
            code=call([sys.executable,'-u',str(HERE/'code/run_development.py'),str(retry)],ROOT/'diagnostic_recovery_console.log',0)
            if code:raise RuntimeError('Diagnostic recovery failed')
            run=retry;continue
        time.sleep(15)
    # Adopt existing watcher if alive; execute any missing stages after it exits.
    while (run/'diagnostics_status.json').exists():
        ds=json.loads((run/'diagnostics_status.json').read_text())
        if ds['state'] in ('completed','partial_failure','blocked_training_incomplete') or not alive(ds['pid']):break
        time.sleep(15)
    for stage in ('1','10','30','100','best'):
        if (run/f'diagnostic_{stage}/metrics.json').exists():continue
        dest=run/f'diagnostic_{stage}'
        if dest.exists():dest.rename(run/f'diagnostic_{stage}_failed_before_queue')
        if call([sys.executable,'-u',str(HERE/'code/diagnose.py'),str(run),'--stage',stage,'--device','cuda:0'],ROOT/f'diagnostic_{stage}_console.log',1):raise RuntimeError(f'Stage {stage} diagnostic failed')
    supported=[]
    for stage in ('100','best'):
        m=json.loads((run/f'diagnostic_{stage}/metrics.json').read_text())
        supported.append(any(v.get('readout_gain_gate_pass') and v.get('joint_over_unimodal_gate_pass') for v in m['gate'].values()))
    decision={'window_candidate_association_gate':all(supported),'stages':supported,'diagnostic_run':str(run),'causality_proven':False,'teacher_branch':'skipped; provenance/information gate unverified'}
    (ROOT/'MECHANISM_GATE.json').write_text(json.dumps(decision,indent=2));return decision

def freeze_selection(decision):
    tasks=[make('dev','qd','A1','gmr',m,3407) for m in config['development_controls']]
    if decision['window_candidate_association_gate']:tasks.append(make('dev','qd','A1','gmr','window',3407))
    else:
        skip=make('dev','qd','A1','gmr','window',3407);enqueue([skip]);state['tasks'][skip['id']].update(state='skipped',reason='Frozen joint-over-unimodal mechanism gate failed');save()
    state['state']='development_controls';save();parallel(tasks)
    results={}
    for t in tasks:
        r=state['tasks'][t['id']]
        if r['state']=='completed':results[t['method']]=json.loads((Path(r['run'])/'result.json').read_text())
    if 'baseline' not in results:raise RuntimeError('Canonical paired development baseline failed')
    base=results['baseline'];simple=[k for k in ('regularized','adapter') if k in results]
    eligible=[k for k in simple if results[k]['seen']['auroc']>=base['seen']['auroc']-.01]
    strongest=max(eligible or simple,key=lambda k:results[k]['pseudo']['auroc']) if simple else None
    if strongest is None:raise RuntimeError('Both simple development controls failed')
    candidate=False
    if 'window' in results:
        c=results['window'];ref=results[strongest]
        candidate=c['pseudo']['auroc']>=ref['pseudo']['auroc']+.03 and c['seen']['auroc']>=ref['seen']['auroc']-.01 and c['pseudo']['positive_frr']<=ref['pseudo']['positive_frr']+.03 and c['pseudo']['negative_rr']>=ref['pseudo']['negative_rr']-.03
    frozen={'strongest_simple':strongest,'candidate_formal_enabled':candidate,'candidate_method':'window' if candidate else None,'mechanism_decision':decision,'development_results':results,'selection_uses_true_U':False,'note':'Strongest simple can remain a negative control if gains fail; no efficacy or novelty presumed.','frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'config_sha256':state['queue_config_sha256']}
    (ROOT/'jobs/SELECTION_FROZEN.json').write_text(json.dumps(frozen,indent=2,default=str));(ROOT/'SELECTION_FROZEN.json').write_text(json.dumps(frozen,indent=2,default=str));return frozen

def formal_tasks(frozen):
    tasks=[]
    for track,backbones in [('gmr',config['gmr_backbones']),('vtg',config['positive_vtg_backbones'])]:
        for split in config['splits']:
            for b in backbones:
                for method in ['baseline','regularized','adapter']+(['window'] if frozen['candidate_formal_enabled'] else []):
                    seeds=config['seeds']
                    for seed in seeds:tasks.append(make('formal',b,split,track,method,seed))
    return tasks

def audit_pair_budgets(tasks):
    groups={}
    for t in tasks:
        rec=state['tasks'][t['id']]
        if rec['state']!='completed':continue
        run=Path(rec['run']);ee=[json.loads(l) for l in (run/'epochs.jsonl').read_text().splitlines()];budget=json.loads((run/'budget.json').read_text())
        assert len(ee)==100 and sum(x['updates'] for x in ee)==budget['expected_updates'] and sum(x['rows'] for x in ee)==budget['expected_rows']
        key=(t['backbone'],t['split'],t['track'],t['seed']);order=[e['order_sha256'] for e in ee]
        signature=(order,json.loads((run/'provenance.json').read_text())['views_sha256']['train.jsonl'],budget['original_parameter_initialization_sha256'])
        if key in groups:assert signature==groups[key],f'Paired budget/initialization mismatch {t["id"]}'
        else:groups[key]=signature
    (ROOT/'BUDGET_AUDIT.json').write_text(json.dumps({'paired_groups':len(groups),'passed':True,'full_epochs':100},indent=2))

def evaluate(tasks):
    state['state']='formal_evaluation';save()
    valid=[t for t in tasks if state['tasks'][t['id']]['state']=='completed']
    def lane(gpu,items):
        for t in items:
            r=state['tasks'][t['id']];run=Path(r['run']);ident=t['id']+'_evaluate';er=state['tasks'].setdefault(ident,dict(t,state='pending',phase='evaluation',attempts=[]))
            if er['state']=='completed':continue
            if (run/'test/report.json').exists():er.update(state='completed',run=str(run));save();continue
            if (run/'test').exists():
                backup=run/f'test_failed_{int(time.time())}';(run/'test').rename(backup)
            cmd=[sys.executable,'-u',str(HERE/'code/queue_worker.py'),str(run),'--backbone',t['backbone'],'--split',t['split'],'--track',t['track'],'--method',t['method'],'--seed',str(t['seed']),'--action','evaluate']
            for attempt in range(2):
                wait_resource(gpu)
                er.update(state='running',gpu=gpu,run=str(run));save()
                ret=call(cmd,ROOT/f'{ident}_attempt{attempt+1}_console.log',gpu)
                er.setdefault('attempts',[]).append({'returncode':ret,'attempt':attempt+1})
                if ret==0 and (run/'test/report.json').exists():break
                if (run/'test').exists():(run/'test').rename(run/f'test_failed_retry{attempt+1}_{int(time.time())}')
            er.update(state='completed' if ret==0 and (run/'test/report.json').exists() else 'failed',returncode=ret);save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fs=[pool.submit(lane,g,valid[g::2]) for g in (0,1)]
        for f in fs:f.result()

def main():
    fd=open(ROOT/'queue.lock','w');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state.update(pid=os.getpid(),state='starting');save()
    all_formal=formal_tasks({'strongest_simple':'regularized','candidate_formal_enabled':True})
    all_dev=[make('dev','qd','A1','gmr',m,3407) for m in ('baseline','regularized','adapter','window')]
    enqueue(all_dev+all_formal)
    for t in all_formal:
        ident=t['id']+'_evaluate';state['tasks'].setdefault(ident,dict(t,id=ident,phase='evaluation',state='waiting_training',attempts=[]))
    for name in ('teacher_l2','teacher_kl'):
        state['tasks'].setdefault(name,{'id':name,'phase':'gate','state':'skipped','reason':'Reference identity and same-information budget gate unverified; no teacher added'})
    save()
    try:
        if not (ROOT/'FROZEN_ASSETS.json').exists():
            if call([sys.executable,'-u',str(HERE/'code/freeze_queue_assets.py'),str(ROOT)],ROOT/'asset_freeze_console.log',0):raise RuntimeError('Frozen asset audit failed')
        decision=json.loads((ROOT/'MECHANISM_GATE.json').read_text()) if (ROOT/'MECHANISM_GATE.json').exists() else ensure_diagnostic()
        frozen=json.loads((ROOT/'SELECTION_FROZEN.json').read_text()) if (ROOT/'SELECTION_FROZEN.json').exists() else freeze_selection(decision)
        tasks=formal_tasks(frozen)
        chosen={t['id'] for t in tasks}
        for t in all_formal:
            if t['id'] not in chosen:
                for ident in (t['id'],t['id']+'_evaluate'):state['tasks'][ident].update(state='skipped',reason='Candidate failed mechanism or development gate; no unsupported formal run')
        state['state']='formal_training';save();parallel(tasks);audit_pair_budgets(tasks)
        for t in tasks:
            if state['tasks'][t['id']]['state']!='completed':state['tasks'][t['id']+'_evaluate'].update(state='skipped',reason='Training failed; no reliable checkpoint')
        save();evaluate(tasks)
        state['state']='aggregation';save()
        ret=call([sys.executable,'-u',str(HERE/'code/aggregate_queue.py'),str(ROOT)],ROOT/'aggregation_console.log',0)
        state.update(state='completed' if ret==0 and not any(v['state']=='failed' for v in state['tasks'].values()) else 'completed_with_failures',aggregation_returncode=ret,finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));save()
    except BaseException:state.update(state='failed',error=traceback.format_exc());save();raise
if __name__=='__main__':main()
