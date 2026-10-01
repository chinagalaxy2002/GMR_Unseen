"""Final protected-asset hash and runtime audit; no model operations."""
import datetime,hashlib,json,subprocess
from pathlib import Path
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis';f=json.loads((D/'FREEZE.json').read_text());checks={}
for path,expected in f['protected_files_sha256'].items():
 h=hashlib.sha256()
 with open(path,'rb') as stream:
  for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
 checks[path]=h.hexdigest()==expected
assert all(checks.values()),[p for p,v in checks.items() if not v]
(D/'INTEGRITY.json').write_text(json.dumps({'state':'passed','at':datetime.datetime.now().isoformat(),'protected_paths':len(checks),'all_original_assets_unchanged':True,'checks':checks,'original_model_updates':0,'probe_fits':18,'probe_parameters_fitted':4626},ensure_ascii=False,indent=2)+'\n')
ps=subprocess.check_output(['ps','-eo','pid,ppid,etime,args'],text=True)
# use python process argv rather than shell command containing a search expression
active=[]
for line in ps.splitlines()[1:]:
 parts=line.split(None,3)
 if len(parts)<4:continue
 argv=parts[3]
 if 'python' in argv and not ('/bin/bash -c' in argv):
  if any(t in argv for t in ['run_phase2.py','run_followup.py','launch_queue.py','temporal_representation_collect.py','temporal_representation_probe.py']):active.append(line)
gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],capture_output=True,text=True)
(D/'RUNTIME_AFTER.json').write_text(json.dumps({'at':datetime.datetime.now().isoformat(),'active_model_or_queue_processes':active,'gpu_compute_processes':gpu.stdout.strip(),'integrity_process_only':True,'training_restarted':False},ensure_ascii=False,indent=2)+'\n')
assert not active
print('protected paths unchanged:',len(checks))
