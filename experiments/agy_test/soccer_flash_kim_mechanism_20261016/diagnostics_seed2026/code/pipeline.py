"""Seed-2026 E0 baseline followed by the published-path A3 branch."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import fcntl
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PYTHON = Path('/home/guoxiangyu/miniconda3/envs/gmr/bin/python')
SEEDS = (2026,)
MAX_PER_GPU = 2
GPUS = (1,)
STATE_PATH = ROOT / 'PIPELINE_STATE.json'


def write_json(path: Path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def alive(pid: int) -> bool:
    try:
        stat = (Path('/proc') / str(pid) / 'stat').read_text().split(') ', 1)[1].split()[0]
        return stat != 'Z'
    except (FileNotFoundError, ProcessLookupError, IndexError):
        return False


def paths(seed: int):
    baseline = ROOT / 'baseline/runs' / f'E0_s{seed}'
    control = ROOT / 'minneg/runs' / f'no_minneg_s{seed}'
    minneg = ROOT / 'minneg/runs' / f'minneg_s{seed}'
    return baseline, control, minneg


def jobs():
    result = []
    for index, seed in enumerate(SEEDS):
        preferred_gpu = GPUS[index // 2]
        baseline, control, minneg = paths(seed)
        result.extend([
            {
                'id': f'baseline_s{seed}', 'seed': seed, 'stage': 'baseline',
                'gpu': preferred_gpu, 'cwd': ROOT / 'baseline', 'done': baseline / 'COMPLETE.json',
                'deps': [],
                'command': [PYTHON, '-B', 'code/run.py', '--variant', 'E0', '--device', 'cuda',
                            '--seed', seed, '--epochs', 100, '--patience', 23, '--run-name', f'E0_s{seed}'],
            },
            {
                'id': f'no_minneg_train_s{seed}', 'seed': seed, 'stage': 'no_minneg_train',
                'gpu': preferred_gpu, 'cwd': ROOT / 'minneg', 'done': control / 'COMPLETE.json',
                'deps': [f'baseline_s{seed}'],
                'command': [PYTHON, '-B', 'code/train.py', '--job', 'A0_readout_no_hardneg_s2024',
                            '--device', 'cuda', '--seed', seed, '--epochs', 100, '--patience', 23,
                            '--run-name', f'no_minneg_s{seed}', '--init-checkpoint', baseline / 'best.ckpt',
                            '--reference-predictions', baseline / 'validation_predictions_pre_nms.jsonl'],
            },
            {
                'id': f'minneg_train_s{seed}', 'seed': seed, 'stage': 'minneg_train',
                'gpu': preferred_gpu, 'cwd': ROOT / 'minneg', 'done': minneg / 'COMPLETE.json',
                'deps': [f'baseline_s{seed}'],
                'command': [PYTHON, '-B', 'code/train.py', '--job', 'A3_similarity_hardneg_s2024',
                            '--device', 'cuda', '--seed', seed, '--epochs', 100, '--patience', 23,
                            '--run-name', f'minneg_s{seed}', '--init-checkpoint', baseline / 'best.ckpt',
                            '--reference-predictions', baseline / 'validation_predictions_pre_nms.jsonl'],
            },
            {
                'id': f'no_minneg_test_s{seed}', 'seed': seed, 'stage': 'no_minneg_test',
                'gpu': preferred_gpu, 'cwd': ROOT / 'minneg',
                'done': control / 'test_metrics.json', 'deps': [f'no_minneg_train_s{seed}'],
                'command': [PYTHON, '-B', 'code/eval_test.py', '--run', f'no_minneg_s{seed}',
                            '--device', 'cuda', '--reference-predictions', baseline / 'test_predictions_pre_nms.jsonl'],
            },
            {
                'id': f'minneg_test_s{seed}', 'seed': seed, 'stage': 'minneg_test',
                'gpu': preferred_gpu, 'cwd': ROOT / 'minneg',
                'done': minneg / 'test_metrics.json', 'deps': [f'minneg_train_s{seed}'],
                'command': [PYTHON, '-B', 'code/eval_test.py', '--run', f'minneg_s{seed}',
                            '--device', 'cuda', '--reference-predictions', baseline / 'test_predictions_pre_nms.jsonl'],
            },
        ])
    return result


def serializable_command(command):
    return [str(value) for value in command]


def main():
    (ROOT / 'logs').mkdir(exist_ok=True)
    lock = (ROOT / 'pipeline.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    specs = jobs()
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {
        'protocol': {
            'source_commit': '857b1fdf03a9afc5cb81731752268ea4fdd7ebf5',
            'seeds': list(SEEDS), 'epochs': 100, 'early_stop_patience': 23,
            'selection_metrics': {
                'baseline': 'Val native pre-NMS MR-full-mAP',
                'no_minneg_control': 'Val AUROC',
                'minneg': 'Val AUROC',
            },
            'max_tasks_per_gpu': MAX_PER_GPU,
            'pipeline': ['baseline', 'no_minneg_control', 'baseline_to_minneg_train',
                         'control_and_minneg_test', 'threshold_report'],
        },
        'jobs': {}, 'started': time.time(),
    }
    state['controller_pid'] = os.getpid()
    active_ids = {spec['id'] for spec in specs}
    state['jobs'] = {key: value for key, value in state.get('jobs', {}).items() if key in active_ids}
    state['protocol']['seeds'] = list(SEEDS)
    state['protocol']['selection_metrics'].pop('task_a_independent_control', None)
    state['protocol']['selection_metrics']['no_minneg_control'] = 'Val AUROC'
    state['protocol']['pipeline'] = ['baseline', 'no_minneg_control', 'baseline_to_minneg_train',
                                     'control_and_minneg_test', 'mechanism_comparison', 'threshold_report']
    for spec in specs:
        entry = state['jobs'].setdefault(spec['id'], {'status': 'queued'})
        if spec['done'].exists():
            entry['status'] = 'complete'
        elif entry.get('status') == 'running' and not alive(int(entry['pid'])):
            restarts = int(entry.get('restart_count', 0))
            if restarts < 1:
                entry.update(status='queued', restart_count=restarts + 1,
                             note='one automatic checkpoint-resume after worker interruption')
            else:
                entry.update(status='failed', error='process disappeared before completion marker', finished=time.time())

    children = {}
    streams = {}
    while True:
        for spec in specs:
            entry = state['jobs'][spec['id']]
            if entry.get('status') != 'running':
                continue
            process = children.get(spec['id'])
            if process is None and alive(int(entry['pid'])):
                continue
            return_code = process.poll() if process is not None else None
            if process is not None and return_code is None:
                continue
            if spec['id'] in streams:
                streams.pop(spec['id']).close()
            if spec['done'].exists() and return_code in (0, None):
                entry.update(status='complete', return_code=return_code, finished=time.time())
            else:
                entry.update(status='failed', return_code=return_code,
                             error='command failed or completion marker missing', finished=time.time())

        failed = {name for name, entry in state['jobs'].items()
                  if entry['status'] in ('failed', 'blocked')}
        for spec in specs:
            entry = state['jobs'][spec['id']]
            if entry['status'] == 'queued' and any(dep in failed for dep in spec['deps']):
                entry.update(status='blocked', error='upstream dependency failed', finished=time.time())

        occupied = {gpu: 0 for gpu in GPUS}
        for spec in specs:
            if state['jobs'][spec['id']]['status'] == 'running':
                occupied[int(state['jobs'][spec['id']]['gpu'])] += 1

        for spec in specs:
            entry = state['jobs'][spec['id']]
            if entry['status'] != 'queued':
                continue
            if not all(state['jobs'][dep]['status'] == 'complete' for dep in spec['deps']):
                continue
            allowed = [gpu for gpu in GPUS if occupied[gpu] < MAX_PER_GPU]
            if not allowed:
                break
            gpu = spec['gpu'] if spec['gpu'] in allowed else min(allowed, key=occupied.get)
            command = serializable_command(spec['command'])
            log_path = ROOT / 'logs' / f"{spec['id']}.log"
            stream = log_path.open('a')
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), PYTHONUNBUFFERED='1',
                       CUBLAS_WORKSPACE_CONFIG=':4096:8')
            process = subprocess.Popen(command, cwd=spec['cwd'], env=env, stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            children[spec['id']] = process
            streams[spec['id']] = stream
            entry.update(status='running', pid=process.pid, gpu=gpu, command=command,
                         cwd=str(spec['cwd']), log=str(log_path), started=time.time())
            occupied[gpu] += 1

        state['updated'] = time.time()
        state['gpu_slots'] = occupied
        write_json(STATE_PATH, state)

        terminal = {'complete', 'failed', 'blocked'}
        if all(entry['status'] in terminal for entry in state['jobs'].values()):
            if all(entry['status'] == 'complete' for entry in state['jobs'].values()):
                mechanism_log = (ROOT / 'logs/mechanism_comparison.log').open('a')
                mechanism_command = [str(PYTHON), '-B', str(ROOT / 'mechanism_comparison.py')]
                mechanism_result = subprocess.run(mechanism_command, cwd=ROOT, stdout=mechanism_log, stderr=subprocess.STDOUT)
                mechanism_log.close()
                state['mechanism_comparison'] = {
                    'status': 'complete' if mechanism_result.returncode == 0 else 'failed',
                    'return_code': mechanism_result.returncode,
                    'log': str(ROOT / 'logs/mechanism_comparison.log'),
                }
                report_log = (ROOT / 'logs/threshold_report.log').open('a')
                command = [str(PYTHON), '-B', str(ROOT / 'threshold_report.py')]
                result = subprocess.run(command, cwd=ROOT, stdout=report_log, stderr=subprocess.STDOUT)
                report_log.close()
                state['threshold_report'] = {
                    'status': 'complete' if result.returncode == 0 and mechanism_result.returncode == 0 else 'failed',
                    'return_code': result.returncode,
                    'log': str(ROOT / 'logs/threshold_report.log'),
                }
                handoff_log = (ROOT / 'logs/handoff.log').open('a')
                handoff_command = [str(PYTHON), '-B', str(ROOT / 'build_handoff.py')]
                handoff_result = subprocess.run(handoff_command, cwd=ROOT, stdout=handoff_log, stderr=subprocess.STDOUT)
                handoff_log.close()
                state['handoff'] = {
                    'status': 'complete' if handoff_result.returncode == 0 and state['threshold_report']['status'] == 'complete' else 'failed',
                    'return_code': handoff_result.returncode,
                    'path': str(ROOT / 'HANDOFF.md'),
                    'log': str(ROOT / 'logs/handoff.log'),
                }
                if state['handoff']['status'] != 'complete':
                    state['threshold_report']['status'] = 'failed'
            else:
                state['threshold_report'] = {'status': 'blocked', 'error': 'one or more training jobs failed'}
            state['finished'] = time.time()
            write_json(STATE_PATH, state)
            return 0 if state['threshold_report']['status'] == 'complete' else 1
        time.sleep(15)


if __name__ == '__main__':
    raise SystemExit(main())
