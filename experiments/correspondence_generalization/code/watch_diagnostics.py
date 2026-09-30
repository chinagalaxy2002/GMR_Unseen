"""Continue the already-started stage-gated diagnostic, without U tuning."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
run=Path(sys.argv[1]).resolve();assert run.is_relative_to(HERE/'runs')
state={'state':'waiting_for_stage','pid':os.getpid(),'completed':[],'failures':[]}
def save():
    p=run/'diagnostics_status.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));tmp.replace(p)
def alive(pid):
    try:os.kill(pid,0);return True
    except ProcessLookupError:return False
for stage in ('1','10','30','100','best'):
    ck=run/('best.ckpt' if stage=='best' else f'stage_{int(stage):03d}.ckpt')
    state.update(state='waiting_for_stage',stage=stage);save()
    while True:
        training=json.loads((run/'status.json').read_text())
        ready=ck.exists() and (stage!='best' or training['state']=='training_complete_diagnostics_pending')
        if ready:break
        if training['state']=='failed' or not alive(training['pid']):
            state.update(state='blocked_training_incomplete',training=training);save();sys.exit(1)
        time.sleep(15)
    # A stage file can be observed during torch.save; wait until stable and loadable.
    time.sleep(3)
    state.update(state='diagnosing',stage=stage);save()
    cmd=[sys.executable,'-u',str(HERE/'code/diagnose.py'),str(run),'--stage',stage,'--device','cuda:1']
    with (run/f'diagnostic_{stage}_console.log').open('w') as log:
        ret=subprocess.call(cmd,stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy())
    if ret:state['failures'].append({'stage':stage,'returncode':ret})
    else:state['completed'].append(stage)
    save()
state['state']='completed' if not state['failures'] else 'partial_failure';save()
