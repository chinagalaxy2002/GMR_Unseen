#!/usr/bin/env python3
"""Isolated decoder-monitor suite; waits for existing training before using GPUs."""
import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mechanism_suite import ROOT, choose_job, read_json, live_report as original_live_report, final_report
from full_monitor_report import report as full_report

def live_report(output):
    original_live_report(output)
    full_report(output)
sys.path.insert(0, str(ROOT / 'src'))
from mechanism_monitor import save_json
import monitor_qivr as diagnostics


def alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def prior_finished(folder):
    state = read_json(Path(folder)/'STATUS.json', {})
    return (state.get('state') in ('complete', 'partial_failed', 'controller_failed', 'cancelled') and
            not any(alive(job.get('pid')) for job in state.get('jobs', {}).values()
                    if job.get('state') in ('running', 'launching')))


def gpu_occupancy():
    result = subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True)
    mapping = {uuid.strip():int(index) for index,uuid in (line.split(',') for line in result.splitlines())}
    result = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'], text=True)
    return [(mapping[uuid.strip()], int(pid)) for uuid,pid in (line.split(',') for line in result.splitlines())
            if uuid.strip() in mapping]


def work(output):
    manifest = read_json(output/'SUITE.json')
    state = dict(state='waiting_for_existing_suite', controller_pid=os.getpid(), jobs={j['tag']:dict(state='queued') for j in manifest['jobs']})
    save_json(output/'STATUS.json', state)
    while not all(prior_finished(folder) for folder in manifest['wait_suites']):
        state['updated'] = time.time()
        save_json(output/'STATUS.json', state)
        time.sleep(30)
    pending, lock = list(manifest['jobs']), threading.Lock()
    state.update(state='running', started=time.time())
    save_json(output/'STATUS.json', state)

    def worker(gpu):
        while True:
            job = None
            with lock:
                if not pending:
                    return
                running = [dict(**next(j for j in manifest['jobs'] if j['tag'] == tag), gpu=s['gpu'])
                           for tag,s in state['jobs'].items() if s['state'] in ('running', 'launching')]
                own_pids = {s.get('pid') for s in state['jobs'].values() if s['state'] == 'running'}
                external = sum(index == gpu and pid not in own_pids for index,pid in gpu_occupancy())
                if external + sum(r['gpu'] == gpu for r in running) < manifest['jobs_per_gpu']:
                    job = pending.pop(choose_job(pending, running, gpu))
                    state['jobs'][job['tag']].update(state='launching', gpu=gpu)
            if job is None:
                time.sleep(20)
                continue
            if job['backbone']=='flash':
                cmd=['/home/guoxiangyu/miniconda3/envs/univtg/bin/python','-u',str(ROOT/'run_flash_monitor_experiment.py'),
                     '--output',str(output/job['tag']),'--dataset',job['dataset'],'--split',job['split'],
                     '--gpu',str(gpu),'--epochs',str(manifest['epochs']),'--seed','3407','--workers','2','--gradient-every','50']
            else:
                cmd = [sys.executable, '-u', str(ROOT/'run_decoder_experiment.py'), '--output', str(output/job['tag']),
                       '--dataset', job['dataset'], '--split', job['split'], '--backbone', job['backbone'],
                       '--variant', job['variant'], '--gpu', str(gpu), '--epochs', str(manifest['epochs']),
                       '--initialization', 'fresh', '--model-kind', 'baseline', '--lr-factor', '1', '--seed', '3407',
                       '--workers', '2', '--decoder-every', '50', '--gradient-every', '50']
            with (output/'logs'/f"{job['tag']}.log").open('w') as stream:
                process = subprocess.Popen(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                    env={**os.environ, 'OMP_NUM_THREADS':'2', 'MKL_NUM_THREADS':'2', 'OPENBLAS_NUM_THREADS':'2'})
                with lock:
                    state['jobs'][job['tag']].update(state='running', pid=process.pid, argv=cmd)
                    save_json(output/'STATUS.json', state)
                while True:
                    try:
                        code = process.wait(timeout=30)
                        break
                    except subprocess.TimeoutExpired:
                        with lock:
                            live_report(output)
            with lock:
                state['jobs'][job['tag']].update(state='complete' if code == 0 else 'failed', returncode=code)
                save_json(output/'STATUS.json', state)
                live_report(output)
    with ThreadPoolExecutor(max_workers=len(manifest['gpus'])*manifest['jobs_per_gpu']) as pool:
        futures = [pool.submit(worker, gpu) for gpu in manifest['gpus'] for _ in range(manifest['jobs_per_gpu'])]
        for future in futures:
            future.result()
    state.update(state='complete' if all(j['state'] == 'complete' for j in state['jobs'].values()) else 'partial_failed', finished=time.time())
    save_json(output/'STATUS.json', state)
    live_report(output)
    final_report(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('launch', 'work', 'status'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wait-suite', action='append', type=Path, default=[])
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--gpus', default='0,1')
    args = parser.parse_args()
    output = args.output.resolve()
    if args.mode == 'launch':
        if output.exists() or args.epochs < 1:
            parser.error('Choose a fresh output and positive epochs')
        for folder in args.wait_suite:
            if not (folder/'SUITE.json').exists():
                parser.error(f'Unknown suite: {folder}')
        gpus = [int(gpu) for gpu in args.gpus.split(',')]
        if not gpus or len(set(gpus)) != len(gpus):
            parser.error('GPU indices must be unique')
        jobs=[]
        # Native baselines precede their self-attention interventions.
        for variant in ('with_sa','no_sa'):
            for split_index in range(5):
                for dataset in ('soccer','clean_v3','charades_cg_v2'):
                    splits=diagnostics.registry.SPECS[dataset][2]
                    if split_index>=len(splits):continue
                    split=splits[split_index]
                    for bb in ('moment','qd','flash'):
                        if bb=='flash' and variant=='no_sa':continue
                        actual='native' if bb=='flash' else variant
                        jobs.append(dict(dataset=dataset,split=split,backbone=bb,variant=actual,tag=f'{dataset}_{split}_{bb}_{actual}'))
        output.mkdir(parents=True)
        (output/'logs').mkdir()
        import hashlib
        files = [Path(__file__).resolve(), ROOT/'run_decoder_experiment.py', ROOT/'run_flash_monitor_experiment.py', ROOT/'src/decoder_slot_monitor.py', ROOT/'src/auroc_mechanism_monitor.py', ROOT/'src/response_monitor.py', ROOT/'src/mechanism_monitor.py', ROOT/'mechanism_suite.py', ROOT/'monitor_qivr.py', ROOT/'full_monitor_report.py']
        import shutil
        snapshot=output/'SOURCE_SNAPSHOT';snapshot.mkdir()
        for file in files:shutil.copy2(file,snapshot/file.name)
        shutil.copytree(ROOT/'src/models',snapshot/'models',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT/'src/training',snapshot/'training',ignore=shutil.ignore_patterns('__pycache__'))
        save_json(output/'SUITE.json', dict(jobs=jobs, gpus=gpus, jobs_per_gpu=2, epochs=args.epochs,
            seed=3407, initialization='fresh', model_kind='baseline', lr_factor=1., gradient_every=50, decoder_every=50,
            wait_suites=[str(folder.resolve()) for folder in args.wait_suite],
            scope='33 native baselines (3 backbones x 11 splits), plus 22 DETR no-SA interventions; complete mechanism monitoring; Unseen only after freezing',
            code_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
        live_report(output)
        with (output/'controller.log').open('w') as stream:
            process = subprocess.Popen([sys.executable, '-u', str(Path(__file__).resolve()), 'work', '--output', str(output)],
                                       cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        save_json(output/'LAUNCH.json', dict(controller_pid=process.pid, launched=time.time(), jobs=len(jobs)))
        print(json.dumps(dict(controller_pid=process.pid, output=str(output), jobs=len(jobs))))
    elif args.mode == 'work':
        try:
            work(output)
        except Exception as error:
            state = read_json(output/'STATUS.json', {})
            state.update(state='controller_failed', error=repr(error), updated=time.time())
            save_json(output/'STATUS.json', state)
            raise
    else:
        print(json.dumps(read_json(output/'STATUS.json', {}), indent=2))


if __name__ == '__main__':
    main()
