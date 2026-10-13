#!/usr/bin/env python3
"""Adopt existing suite processes and run CG/clean_v3 before Soccer."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from decoder_suite import ROOT, choose_job, gpu_occupancy, live_report, read_json, save_json
from mechanism_suite import final_report


def eligible_tags(manifest, state):
    high = [j for j in manifest['jobs'] if j['dataset'] != 'soccer']
    high_pending = any(state['jobs'][j['tag']]['state'] in ('queued', 'running', 'launching', 'paused') for j in high)
    return {j['tag'] for j in manifest['jobs']
            if state['jobs'][j['tag']]['state'] in ('queued', 'paused')
            and (j['dataset'] != 'soccer' or not high_pending)}


def process_alive(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0] != 'Z'
    except FileNotFoundError:
        return False


def command(job, output, gpu, epochs):
    if job.get('runner') == 'publication_reproduction':
        return [sys.executable, '-u', str(ROOT/'run_publication_reproduction.py'),
                '--config', job['config'], '--gpu', str(gpu)]
    if job['backbone'] == 'flash':
        return ['/home/guoxiangyu/miniconda3/envs/univtg/bin/python', '-u',
                str(ROOT/'run_flash_monitor_experiment.py'), '--output', str(output/job['tag']),
                '--dataset', job['dataset'], '--split', job['split'], '--gpu', str(gpu),
                '--epochs', str(epochs), '--seed', '3407', '--workers', '2', '--gradient-every', '50']
    return [sys.executable, '-u', str(ROOT/'run_decoder_experiment.py'), '--output', str(output/job['tag']),
            '--dataset', job['dataset'], '--split', job['split'], '--backbone', job['backbone'],
            '--variant', job['variant'], '--gpu', str(gpu), '--epochs', str(epochs),
            '--initialization', 'fresh', '--model-kind', 'baseline', '--lr-factor', '1',
            '--seed', '3407', '--workers', '2', '--decoder-every', '50', '--gradient-every', '50']


def run(output):
    manifest = read_json(output/'SUITE.json')
    manifest['jobs'] = manifest['jobs'] + read_json(output/'EXTRA_JOBS.json', {}).get('jobs', [])
    state = read_json(output/'STATUS.json')
    for job in manifest['jobs']:
        state['jobs'].setdefault(job['tag'], dict(state='queued', job_kind=job.get('runner','baseline_diagnostic')))
    paths = {j['tag']:Path(j.get('output_dir', output/j['tag'])) for j in manifest['jobs']}
    policy = read_json(output/'SCHEDULING_POLICY.json')
    state.update(controller_pid=os.getpid(), state='running', scheduling_policy=policy)
    save_json(output/'STATUS.json', state)
    children = {}
    last_report = 0
    while True:
        for tag, entry in state['jobs'].items():
            if entry['state'] != 'running':
                continue
            process = children.get(tag)
            code = process.poll() if process else None
            if (process and code is not None) or (not process and not process_alive(entry['pid'])):
                result = read_json(paths[tag]/'STATUS.json', {})
                success = result.get('state') == 'complete' and (code is None or code == 0)
                entry.update(state='complete' if success else 'failed', finished=time.time())
                if code is not None:
                    entry['returncode'] = code
                else:
                    entry['exit_verification'] = 'adopted PID exited; runner STATUS determines outcome'
                save_json(output/'STATUS.json', state)
        eligible = eligible_tags(manifest, state)
        owned = {j.get('pid') for j in state['jobs'].values() if j['state'] in ('running', 'paused')}
        occupancy = gpu_occupancy()
        for gpu in manifest['gpus']:
            running = [dict(**j, gpu=state['jobs'][j['tag']]['gpu']) for j in manifest['jobs']
                       if state['jobs'][j['tag']]['state'] == 'running']
            def belongs_to_suite(pid):
                seen = set()
                while pid > 1 and pid not in seen:
                    if pid in owned:
                        return True
                    seen.add(pid)
                    try:
                        pid = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[1])
                    except FileNotFoundError:
                        return False
                return False
            external = sum(index == gpu and not belongs_to_suite(pid) for index, pid in occupancy)
            slots = policy['jobs_per_gpu'] - external - sum(j['gpu'] == gpu for j in running)
            while slots > 0:
                choices = [j for j in manifest['jobs'] if j['tag'] in eligible
                           and (state['jobs'][j['tag']]['state'] != 'paused' or state['jobs'][j['tag']]['gpu'] == gpu)]
                if not choices:
                    break
                priority = [j for j in choices if j.get('runner') == 'publication_reproduction']
                if priority:
                    choices = priority
                job = choices[choose_job(choices, running, gpu)]
                tag = job['tag']
                entry = state['jobs'][tag]
                if entry['state'] == 'paused':
                    assert process_alive(entry['pid']), f'Paused process disappeared: {tag}'
                    assert Path(f"/proc/{entry['pid']}/cmdline").read_bytes().decode().split('\0')[:-1] == entry['argv']
                    for pid in entry['stopped_pids']:
                        if process_alive(pid):
                            os.kill(pid, signal.SIGCONT)
                    entry.update(state='running', resumed_at=time.time())
                else:
                    if paths[tag].exists():
                        entry.update(state='failed', error='Fresh output directory already exists; preserved')
                        eligible.remove(tag)
                        continue
                    cmd = command(job, output, gpu, manifest['epochs'])
                    with (output/'logs'/f'{tag}.log').open('w') as stream:
                        process = subprocess.Popen(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                            env={**os.environ, 'OMP_NUM_THREADS':'2', 'MKL_NUM_THREADS':'2', 'OPENBLAS_NUM_THREADS':'2'})
                    children[tag] = process
                    entry.update(state='running', gpu=gpu, pid=process.pid, argv=cmd, launched_at=time.time())
                    owned.add(process.pid)
                save_json(output/'STATUS.json', state)
                running.append(dict(**job, gpu=gpu))
                eligible.remove(tag)
                slots -= 1
        if time.time() - last_report >= 30:
            live_report(output)
            save_json(output/'REPRODUCTION_STATUS.json', dict(jobs={j['tag']:dict(
                **state['jobs'][j['tag']], output_dir=str(paths[j['tag']]),
                run=read_json(paths[j['tag']]/'STATUS.json', {}))
                for j in manifest['jobs'] if j.get('runner') == 'publication_reproduction'}))
            last_report = time.time()
        if all(j['state'] in ('complete', 'failed', 'cancelled') for j in state['jobs'].values()):
            state.update(state='complete' if all(j['state'] in ('complete', 'cancelled') for j in state['jobs'].values()) else 'partial_failed', finished=time.time())
            save_json(output/'STATUS.json', state)
            live_report(output)
            final_report(output)
            return
        time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        run(args.output.resolve())
    except Exception as error:
        state = read_json(args.output/'STATUS.json', {})
        state.update(state='controller_failed', error=repr(error), updated=time.time())
        save_json(args.output/'STATUS.json', state)
        raise
