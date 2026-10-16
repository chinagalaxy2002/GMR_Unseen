"""Run four jobs with at most two training processes on each physical GPU."""
import argparse
import csv
import fcntl
import io
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from environment import read_json, write_json


def gpu_processes():
    gpu_rows = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader,nounits'], text=True
    )
    uuid_to_index = {row[1].strip(): int(row[0]) for row in csv.reader(io.StringIO(gpu_rows))}
    result = {index: set() for index in uuid_to_index.values()}
    try:
        app_rows = subprocess.check_output(
            ['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader,nounits'], text=True
        )
        for row in csv.reader(io.StringIO(app_rows)):
            if len(row) == 2 and row[0].strip() in uuid_to_index:
                result[uuid_to_index[row[0].strip()]].add(int(row[1]))
    except subprocess.CalledProcessError:
        pass
    return result


def alive(pid, run_id):
    try:
        command = (Path('/proc') / str(pid) / 'cmdline').read_bytes().replace(b'\0', b' ').decode()
        state = (Path('/proc') / str(pid) / 'stat').read_text().split(') ', 1)[1].split()[0]
        return state != 'Z' and 'train.py' in command and run_id in command
    except (FileNotFoundError, ProcessLookupError):
        return False


def summarize(jobs, state):
    rows = []
    markdown = [
        '# Task A enhancement: Train/Val status', '',
        'All methods load the same E0 checkpoint, freeze the localizer, and require an exact E0 localizer fingerprint.', '',
        '| Run | State | GPU | Epoch | Val AUROC | G-mIoU@1(0.4) | G-mIoU@1(0.5) | Native mAP | Fingerprint |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|',
    ]
    for job in jobs:
        name = job['run_id']
        run = ROOT / 'runs' / name
        status = read_json(run / 'STATUS.json') if (run / 'STATUS.json').exists() else {}
        selected = read_json(run / 'selected.json') if (run / 'selected.json').exists() else {}
        metrics = read_json(run / 'validation_metrics.json') if (run / 'validation_metrics.json').exists() else {}
        row = {'job': job, 'queue': state.get(name, {}), 'status': status, 'selected': selected, 'val_metrics': metrics}
        rows.append(row)
        markdown.append(
            f"| {name} | {state.get(name, {}).get('state', 'queued')} | {state.get(name, {}).get('gpu', '')} | "
            f"{status.get('epoch', selected.get('epoch', ''))} | {selected.get('val_AUROC', '')} | "
            f"{selected.get('val_G_mIoU_04', '')} | {selected.get('val_G_mIoU_05', '')} | "
            f"{selected.get('native_pre_nms_mAP', '')} | {'OK' if selected.get('localizer_fingerprint') else ''} |"
        )
    write_json(ROOT / 'RESULTS.json', {'updated': time.time(), 'test_evaluated': False, 'jobs': rows})
    (ROOT / 'RESULTS.md').write_text('\n'.join(markdown) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--poll-seconds', type=int, default=15)
    args = parser.parse_args()
    lock = (ROOT / 'scheduler.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    config = read_json(ROOT / 'configs/jobs.json')
    jobs = config['jobs']
    limit = int(config['max_tasks_per_gpu'])
    state = read_json(ROOT / 'QUEUE_STATE.json') if (ROOT / 'QUEUE_STATE.json').exists() else {}
    children = {}
    logs = {}
    for job in jobs:
        name = job['run_id']
        entry = state.setdefault(name, {'run_id': name, 'state': 'queued'})
        if (ROOT / 'runs' / name / 'COMPLETE.json').exists():
            entry['state'] = 'complete'
        elif entry.get('state') == 'running' and not alive(entry['pid'], name):
            entry.update(state='failed', error='process disappeared')
    write_json(ROOT / 'SCHEDULER_PID.json', {'pid': os.getpid(), 'limit_per_gpu': limit, 'started': time.time()})

    while True:
        for job in jobs:
            name = job['run_id']
            entry = state[name]
            if entry['state'] != 'running':
                continue
            process = children.get(name)
            done = process.poll() is not None if process else not alive(entry['pid'], name)
            if done:
                code = process.returncode if process else None
                if name in logs:
                    logs.pop(name).close()
                ok = (ROOT / 'runs' / name / 'COMPLETE.json').exists() and code in (0, None)
                entry.update(state='complete' if ok else 'failed', exit_code=code, finished=time.time())

        physical = gpu_processes()
        ours = {gpu: set() for gpu in physical}
        for entry in state.values():
            if entry['state'] == 'running':
                ours.setdefault(entry['gpu'], set()).add(entry['pid'])
        occupied = {gpu: set(pids) for gpu, pids in physical.items()}
        for gpu, pids in ours.items():
            occupied.setdefault(gpu, set()).update(pids)

        for job in jobs:
            name = job['run_id']
            if state[name]['state'] != 'queued':
                continue
            allowed = [gpu for gpu in sorted(occupied) if len(occupied[gpu]) < limit]
            if not allowed:
                break
            preferred = int(job.get('gpu', allowed[0]))
            gpu = preferred if preferred in allowed else min(allowed, key=lambda item: len(occupied[item]))
            command = [sys.executable, '-B', str(ROOT / 'code/train.py'), '--job', name, '--device', 'cuda']
            log = (ROOT / 'logs' / f'{name}.log').open('a')
            process = subprocess.Popen(
                command, cwd=ROOT, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu)),
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            )
            children[name] = process
            logs[name] = log
            state[name] = {
                'run_id': name, 'state': 'running', 'pid': process.pid, 'gpu': gpu,
                'started': time.time(), 'command': command,
            }
            occupied[gpu].add(process.pid)

        write_json(ROOT / 'QUEUE_STATE.json', state)
        write_json(ROOT / 'GPU_OCCUPANCY.json', {
            'updated': time.time(), 'max_tasks_per_gpu': limit,
            'pids': {str(gpu): sorted(pids) for gpu, pids in occupied.items()},
        })
        summarize(jobs, state)
        if all(entry['state'] in ('complete', 'failed') for entry in state.values()):
            write_json(ROOT / 'QUEUE_TERMINAL.json', {
                'all_complete': all(entry['state'] == 'complete' for entry in state.values()),
                'test_evaluated': False, 'updated': time.time(),
            })
            return
        time.sleep(args.poll_seconds)


if __name__ == '__main__':
    main()
