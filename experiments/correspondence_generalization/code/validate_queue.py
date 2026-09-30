"""Actual integration checks on training/seen rows only; no U selection."""
import importlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'code'))
results={};tests=[('qd','gmr','baseline'),('qd','gmr','regularized'),('moment','vtg','adapter'),('flash','gmr','window')]
for b,track,method in tests:
    name=f'queue_strict_verified_{b}_{track}_{method}';run=HERE/'runs'/name
    if (run/'result.json').exists():result=json.loads((run/'result.json').read_text());assert result['state']=='completed_smoke';results[name]=result;continue
    if run.exists():run=run.with_name(run.name+'_retry'+str(int(time.time())))
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(HERE/'cache/runtime'),TORCH_HOME=str(HERE/'cache/runtime/torch'),TMPDIR=str(HERE/'cache/runtime'))
    with (HERE/'runs'/f'{name}_console.log').open('w') as log:
        ret=subprocess.call([sys.executable,str(HERE/'code/queue_worker.py'),str(run),'--backbone',b,'--track',track,'--method',method,'--development','--smoke'],stdout=log,stderr=subprocess.STDOUT,env=env,cwd=HERE)
    assert ret==0,f'{name} failed; see console log';results[name]=json.loads((run/'result.json').read_text())
q0=HERE/'runs/queue_strict_verified_qd_gmr_baseline';q1=HERE/'runs/queue_strict_verified_qd_gmr_regularized'
for fname,key in [('budget.json','original_parameter_initialization_sha256'),('epochs.jsonl','order_sha256')]:
    aa=json.loads((q0/fname).read_text());bb=json.loads((q1/fname).read_text());assert aa[key]==bb[key],f'paired mismatch: {key}'
for name,r in results.items():assert r['forward_counts']['training']==3
for k in ('queue_strict_verified_moment_vtg_adapter',):
    # Verify head absence using serialized state keys; no inference on U.
    import torch
    ck=torch.load(Path(results[k]['output'])/'best.ckpt',map_location='cpu',weights_only=False);assert not any('exist_head' in v for v in ck['model'])
import execution_queue as q
for enabled,n in ((False,75),(True,100)):
    tasks=q.formal_tasks({'strongest_simple':'regularized','candidate_formal_enabled':enabled});assert len(tasks)==n and len({t['id'] for t in tasks})==n and {t['seed'] for t in tasks}=={3407}
(ROOT:=HERE/'runs/autonomous_queue_20260930_strict').mkdir(exist_ok=True)
(ROOT/'INTEGRATION_CHECKS.json').write_text(json.dumps({'state':'passed','single_seed':3407,'task_counts_without_with_candidate':[75,100],'paired_initialization_and_sample_order':True,'actual_smoke_results':results,'true_U_accessed':False},indent=2,default=str));print(ROOT/'INTEGRATION_CHECKS.json')
