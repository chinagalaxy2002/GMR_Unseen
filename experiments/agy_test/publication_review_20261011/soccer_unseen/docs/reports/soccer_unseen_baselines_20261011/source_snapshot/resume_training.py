"""Restart the scheduler with six slots while native training subprocesses continue."""
import datetime
import subprocess
import sys
from common import ROOT, REPO, GMR, environment, save_json

save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage='resuming_six_training_slots',
    started=datetime.datetime.now().isoformat(),workers=6,workers_per_gpu=3,
    note='Existing native train processes are detected and awaited; completed jobs are reused.'))
with (ROOT/'baseline_queue.log').open('a') as out:
    result=subprocess.run([GMR,str(ROOT/'run_baselines.py')],cwd=REPO,env=environment(),stdout=out,stderr=subprocess.STDOUT)
stage='complete' if result.returncode==0 else 'failed'
save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage=stage,returncode=result.returncode,finished=datetime.datetime.now().isoformat()))
save_json(ROOT/'BACKGROUND_STATUS.json',dict(stage=stage,returncode=result.returncode,finished=datetime.datetime.now().isoformat()))
sys.exit(result.returncode)
