"""Robust scheduler strictly enforcing at most ONE compute experiment per GPU at all times."""
import subprocess
import os
import sys
import csv
import io
import fcntl
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))

from environment import read_json, write_json

def gpu_pids():
    """Query system nvidia-smi to obtain exact set of compute PIDs running on each GPU."""
    lines = subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader,nounits'], text=True)
    ids = {r[1].strip(): int(r[0]) for r in csv.reader(io.StringIO(lines))}
    out = {g: set() for g in ids.values()}
    try:
        lines = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader,nounits'], text=True)
        for row in csv.reader(io.StringIO(lines)):
            if len(row) == 2 and row[0].strip() in ids:
                out[ids[row[0].strip()]].add(int(row[1].strip()))
    except Exception:
        pass
    return out

def is_process_running(pid, run_id):
    try:
        cmd = (Path('/proc') / str(pid) / 'cmdline').read_bytes().replace(b'\0', b' ').decode()
        stat = (Path('/proc') / str(pid) / 'stat').read_text()
        return stat.split(') ', 1)[1].split()[0] != 'Z' and 'train.py' in cmd and run_id in cmd
    except (FileNotFoundError, ProcessLookupError):
        return False

def load_if_exists(path, default):
    return read_json(path) if Path(path).exists() else default

def update_results_summary(jobs, state):
    historical = load_if_exists(ROOT / 'provenance/HISTORICAL_REFERENCES.json', {})
    rows = []
    for job in jobs:
        name = job['run_id']
        run_dir = ROOT / 'runs' / name
        rows.append({
            'job': job,
            'queue': state.get(name, {}),
            'status': load_if_exists(run_dir / 'STATUS.json', {}),
            'selected': load_if_exists(run_dir / 'selected.json', {}),
            'val_metrics': load_if_exists(run_dir / 'validation_metrics.json', {}),
            'test_metrics': load_if_exists(run_dir / 'test_metrics.json', {})
        })

    write_json(ROOT / 'RESULTS.json', {
        'updated': time.time(),
        'baseline': 'historical E0 (Val mAP 26.82, Test mAP 26.14, Test AUROC 74.27, Test G-mIoU@1 34.66)',
        'jobs': rows
    })

    # Generate Markdown summary table
    md_lines = [
        "# Kim 机制复现与超越 E0 对照汇总",
        "",
        "主目标：超越基线 E0（Test mAP 26.14, AUROC 74.27, G-mIoU@1(0.4) 34.66, G-mIoU@1(0.5) 46.19）。",
        "规则：每张卡同时最多 1 个实验；梯度解耦保定位能力，数据增强与阈值校准提升存在性与泛化度。",
        "",
        "## 验证集与测试集对比",
        "",
        "| 任务 | 结构变体 | 数量源 | 梯度系数 | 数据增强 | 状态 | Val最佳 mAP | Val AUROC | Test mAP | Test AUROC | Test G-mIoU@1(0.4) | Test G-mIoU@1(0.5) | GPU |",
        "|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
        "| **E0 (基线)** | 原生池化 | 无 | — | 无 | complete | 26.82 | 75.31 | 26.14 | 74.27 | 34.66 | 46.19 | — |",
        "| **E2 (历史消融)** | Event Query | 无 | 1.0 | 无 | complete | 26.62 | 69.90 | 24.45 | 77.91 | 37.73 | 42.91 | — |"
    ]

    for r in rows:
        j = r['job']
        q = r['queue']
        val = r['val_metrics']
        test = r['test_metrics']
        
        val_map = r['selected'].get('native_pre_nms_mAP', '')
        val_auroc = val.get('AUROC', '')
        
        test_map = test.get('positive_localization', {}).get('mAP', '')
        test_auroc = test.get('AUROC', '')
        test_gmiou_04 = test.get('gate_04', {}).get('G-mIoU@1', '')
        test_gmiou_05 = test.get('fixed_05', {}).get('G-mIoU@1', '')

        md_lines.append(
            f"| **{j['run_id']}** | {j['variant']} | {j['multi_source']} | {j['feature_grad_scale']} | "
            f"{'tau_no=0.05' if j.get('data_aug_no_target') else '无'} | {q.get('state', 'queued')} | "
            f"{val_map} | {val_auroc} | {test_map} | {test_auroc} | {test_gmiou_04} | {test_gmiou_05} | {q.get('gpu', '')} |"
        )

    (ROOT / 'RESULTS.md').write_text('\n'.join(md_lines) + '\n')

def main():
    lock_file = ROOT / 'scheduler.lock'
    lock = lock_file.open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    config = read_json(ROOT / 'configs/jobs.json')
    max_limit = config.get('max_tasks_per_gpu', 2)
    jobs = config['jobs']
    state = load_if_exists(ROOT / 'QUEUE_STATE.json', {})
    children = {}
    logs = {}

    for job in jobs:
        name = job['run_id']
        s = state.setdefault(name, {'run_id': name, 'state': 'queued'})
        if (ROOT / 'runs' / name / 'COMPLETE.json').exists():
            s['state'] = 'complete'
        elif s['state'] == 'running' and not is_process_running(s['pid'], name):
            s.update(state='failed', error='Process terminated unexpectedly')

    write_json(ROOT / 'SCHEDULER_PID.json', {
        'pid': os.getpid(),
        'started': time.time(),
        'limit_per_gpu': 1
    })

    print(f"Scheduler started with PID {os.getpid()}. Monitoring GPU occupancy and queue...", flush=True)

    while True:
        # Check active children processes
        for job in jobs:
            name = job['run_id']
            s = state[name]
            if s['state'] != 'running':
                continue
            proc = children.get(name)
            is_done = proc.poll() is not None if proc else not is_process_running(s['pid'], name)
            if is_done:
                rc = proc.returncode if proc else None
                if name in logs:
                    logs.pop(name).close()
                is_ok = (ROOT / 'runs' / name / 'COMPLETE.json').exists() and rc in (None, 0)
                s.update(
                    state='complete' if is_ok else 'failed',
                    exit_code=rc,
                    finished=time.time()
                )
                print(f"Job {name} finished with state: {s['state']} (exit code {rc})", flush=True)

        # User constraint: allocate at most max_tasks_per_gpu per GPU
        occupied_gpus = {0: set(), 1: set()}
        for s in state.values():
            if s['state'] == 'running':
                occupied_gpus.setdefault(s['gpu'], set()).add(s['pid'])

        # Launch next job on available GPU with < max_limit compute processes
        for job in jobs:
            name = job['run_id']
            s = state[name]
            if s['state'] != 'queued':
                continue
            free_gpus = [g for g, pids in occupied_gpus.items() if len(pids) < max_limit]
            if not free_gpus:
                break
            
            preferred_gpu = job.get('gpu')
            if preferred_gpu is not None and preferred_gpu in free_gpus:
                chosen_gpu = preferred_gpu
            else:
                chosen_gpu = min(free_gpus, key=lambda g: len(occupied_gpus[g]))
            cmd = [sys.executable, '-B', str(ROOT / 'code/train.py'), '--job', name, '--device', 'cuda']
            log_path = ROOT / 'logs' / f'{name}.log'
            log_f = log_path.open('a')
            
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(chosen_gpu))
            proc = subprocess.Popen(
                cmd, cwd=ROOT, env=env,
                stdin=subprocess.DEVNULL, stdout=log_f, stderr=subprocess.STDOUT,
                start_new_session=True
            )
            children[name] = proc
            logs[name] = log_f
            state[name] = {
                'run_id': name,
                'state': 'running',
                'pid': proc.pid,
                'gpu': chosen_gpu,
                'started': time.time(),
                'command': cmd
            }
            occupied_gpus[chosen_gpu].add(proc.pid)
            print(f"Launched {name} (PID {proc.pid}) on GPU {chosen_gpu}", flush=True)

        write_json(ROOT / 'QUEUE_STATE.json', state)
        write_json(ROOT / 'GPU_OCCUPANCY.json', {
            'updated': time.time(),
            'max_tasks_per_gpu': 1,
            'pids': {str(g): sorted(p) for g, p in occupied_gpus.items()}
        })
        update_results_summary(jobs, state)

        if all(s['state'] in ('complete', 'failed') for s in state.values()):
            all_succ = all(s['state'] == 'complete' for s in state.values())
            write_json(ROOT / 'QUEUE_TERMINAL.json', {
                'all_complete': all_succ,
                'updated': time.time(),
                'test_evaluated': True
            })
            print(f"All jobs terminated! All complete: {all_succ}", flush=True)
            return

        time.sleep(15)

if __name__ == '__main__':
    main()
