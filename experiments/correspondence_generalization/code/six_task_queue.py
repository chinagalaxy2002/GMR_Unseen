"""Resume exactly six A1/QD tasks, two slots per GPU, without budget audits."""
import concurrent.futures
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE / 'runs/autonomous_queue_20260930_strict'
STATE = ROOT / 'queue_state.json'
LOCK = threading.RLock()
TASKS = [f'formal_A1_qd_{track}_{method}_s3407'
         for track in ('gmr', 'vtg') for method in ('baseline', 'regularized', 'adapter')]
state = json.loads(STATE.read_text())

def save():
    with LOCK:
        tmp = STATE.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(STATE)

def alive(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().split(') ', 1)[1][0] != 'Z'
    except FileNotFoundError:
        return False

def wait_resource(gpu):
    while True:
        free = int(subprocess.check_output(
            ['nvidia-smi', '-i', str(gpu), '--query-gpu=memory.free',
             '--format=csv,noheader,nounits'], text=True).strip())
        if free >= 4096:
            return
        time.sleep(15)

def env(gpu):
    result = os.environ.copy()
    result.update(CUDA_VISIBLE_DEVICES=str(gpu), PYTHONDONTWRITEBYTECODE='1',
                  CORRESPONDENCE_SKIP_BUDGET_AUDIT='1',
                  XDG_CACHE_HOME=str(HERE / 'cache/runtime'),
                  TORCH_HOME=str(HERE / 'cache/runtime/torch'),
                  TMPDIR=str(HERE / 'cache/runtime'))
    return result

def job(ident, gpu, action='train'):
    original = state['tasks'][ident]
    key = ident if action == 'train' else ident + '_evaluate'
    record = state['tasks'][key]
    # Adopt the already running in-scope worker; never launch a duplicate.
    if record['state'] == 'running' and alive(record.get('pid', 0)):
        pid = record['pid']
        command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
        assert 'queue_worker.py' in command and record['run'] in command
        while alive(pid):
            time.sleep(5)
    old_run = Path(record['run']) if record.get('run') else None
    result_path = old_run / ('result.json' if action == 'train' else 'test/report.json') if old_run else None
    if result_path and result_path.exists():
        result = json.loads(result_path.read_text())
        if action == 'evaluate' or result.get('state') == 'completed':
            with LOCK:
                record.update(state='completed')
                save()
            return
    attempts = record.setdefault('attempts', [])
    # Preserve any incomplete adopted attempt before retrying from scratch.
    if action == 'train' and old_run and old_run.exists() and not any(
            a.get('run') == str(old_run) for a in attempts):
        attempts.append({'run': str(old_run), 'returncode': 'adopted worker incomplete'})
    for attempt in range(len(attempts), 2):
        run = ROOT / 'jobs' / f'{ident}_attempt{attempt + 1}' if action == 'train' else Path(original['run'])
        if action == 'evaluate' and (run / 'test').exists():
            (run / 'test').rename(run / f'test_incomplete_{time.time_ns()}')
        wait_resource(gpu)
        cmd = [sys.executable, '-u', str(HERE / 'code/queue_worker.py'), str(run),
               '--backbone', 'qd', '--split', 'A1', '--track', original['track'],
               '--method', original['method'], '--seed', '3407', '--action', action]
        log = ROOT / f'{key}_six_tasks_attempt{attempt + 1}_console.log'
        with log.open('a') as output:
            proc = subprocess.Popen(cmd, cwd=HERE, env=env(gpu), stdout=output,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            with LOCK:
                record.update(state='running', gpu=gpu, pid=proc.pid, run=str(run),
                              budget_audit_enabled=False)
                save()
            ret = proc.wait()
        attempts.append({'run': str(run), 'returncode': ret})
        result_path = run / ('result.json' if action == 'train' else 'test/report.json')
        success = ret == 0 and result_path.exists()
        if action == 'train' and success:
            success = json.loads(result_path.read_text()).get('state') == 'completed'
        with LOCK:
            record.update(state='completed' if success else 'retrying', returncode=ret)
            save()
        if success:
            return
    with LOCK:
        record.update(state='failed', reason=f'{action} exhausted two attempts')
        save()

def lane(gpu, identifiers, action):
    for ident in identifiers:
        if action == 'evaluate' and state['tasks'][ident]['state'] != 'completed':
            with LOCK:
                state['tasks'][ident + '_evaluate'].update(state='skipped', reason='Training incomplete')
                save()
            continue
        job(ident, gpu, action)

def run_lanes(action):
    # Four fixed slots, two per GPU. Slot 0 adopts the active GPU 0 adapter.
    lanes = [(0, TASKS[:3]), (0, [TASKS[5]]), (1, [TASKS[3]]), (1, [TASKS[4]])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(lane, gpu, tasks, action) for gpu, tasks in lanes]
        for future in futures:
            future.result()

def main():
    with (ROOT / 'queue.lock').open('w') as fd:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state.update(pid=os.getpid(), state='formal_training', training_scope=TASKS,
                     scheduler='six_task_queue.py', concurrency_per_gpu=2,
                     budget_audit_enabled=False)
        save()
        try:
            run_lanes('train')
            state['state'] = 'formal_evaluation'
            save()
            run_lanes('evaluate')
            state['state'] = 'aggregation'
            save()
            ret = subprocess.call([sys.executable, str(HERE / 'code/aggregate_queue.py'), str(ROOT)],
                                  cwd=HERE, env=env(0))
            selected = [state['tasks'][k] for ident in TASKS for k in (ident, ident + '_evaluate')]
            state.update(state='completed' if ret == 0 and all(t['state'] == 'completed' for t in selected)
                         else 'completed_with_failures', aggregation_returncode=ret,
                         finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
            save()
        except BaseException:
            state.update(state='failed', error=traceback.format_exc())
            save()
            raise

if __name__ == '__main__':
    main()
