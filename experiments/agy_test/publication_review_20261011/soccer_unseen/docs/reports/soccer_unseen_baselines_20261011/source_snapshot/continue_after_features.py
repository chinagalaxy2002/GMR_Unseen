"""Let the running extractor finish, then apply the updated automatic training policy."""
import argparse
import datetime
import fcntl
import json
import subprocess
import time
from pathlib import Path
from common import ROOT, REPO, GMR, environment, save_json


def main(pid):
    save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage='armed',waiting_for_pipeline_pid=pid,
        policy='After extraction, exclude missing/invalid-feature qids from experiment snapshots and train all 15 settings.'))
    last_sample = 0
    process = Path('/proc')/str(pid)/'cmdline'
    while process.exists():
        try:
            if 'soccer_unseen_baselines_20261011/background_pipeline.py' not in process.read_bytes().decode():
                break
        except FileNotFoundError:
            break
        if time.time()-last_sample >= 60:
            result = subprocess.run(['nvidia-smi','--query-gpu=index,temperature.gpu,power.draw,power.limit,utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits'],capture_output=True,text=True)
            with (ROOT/'GPU_TELEMETRY.jsonl').open('a') as out:
                out.write(json.dumps(dict(time=datetime.datetime.now().isoformat(),gpu_rows=result.stdout.splitlines(),
                    fields=['index','temperature_C','power_W','power_limit_W','utilization_pct','memory_used_MiB','memory_total_MiB'],
                    returncode=result.returncode))+'\n')
            last_sample = time.time()
        time.sleep(10)
    state = json.loads((ROOT/'BACKGROUND_STATUS.json').read_text())
    if state['stage'] == 'complete':
        save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage='complete',handled_by_original_pipeline=True))
        return
    if state['stage'] != 'feature_extraction_finished_with_missing':
        save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage='pipeline_failure_requires_review',pipeline_state=state))
        return
    save_json(ROOT/'BACKGROUND_STATUS.json',dict(stage='training_and_evaluating',settings=15,
        updated=datetime.datetime.now().isoformat(),feature_policy='exclude missing/invalid features, recorded in FEATURE_EXCLUSIONS.json'))
    save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage='training_and_evaluating',settings=15))
    with (ROOT/'baseline_queue.log').open('a') as out:
        result = subprocess.run([GMR,str(ROOT/'run_baselines.py')],cwd=REPO,env=environment(),stdout=out,stderr=subprocess.STDOUT)
    stage = 'complete' if result.returncode == 0 else 'failed'
    save_json(ROOT/'AUTOTRAIN_STATUS.json',dict(stage=stage,returncode=result.returncode))
    save_json(ROOT/'BACKGROUND_STATUS.json',dict(stage=stage,updated=datetime.datetime.now().isoformat(),returncode=result.returncode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipeline_pid',type=int,required=True)
    args = parser.parse_args()
    with (ROOT/'autotrain_guard.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        main(args.pipeline_pid)
