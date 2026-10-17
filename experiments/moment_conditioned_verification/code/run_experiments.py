"""Queue runner for training and evaluating ideas across the 2 GPUs."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_pipeline(job_id, device, seed=2026, epochs=35, patience=12):
    run_name = f"{job_id}_s{seed}"
    log_file = ROOT / 'logs' / f"{run_name}.log"
    print(f"\n[LAUNCH] Starting {run_name} on {device} (logs -> {log_file})...")
    
    # 1. Train
    env = dict(os.environ, CUBLAS_WORKSPACE_CONFIG=':4096:8')
    train_cmd = [
        PYTHON, str(ROOT / 'code/train.py'),
        '--job', job_id,
        '--device', device,
        '--seed', str(seed),
        '--epochs', str(epochs),
        '--patience', str(patience),
        '--run-name', run_name
    ]
    with open(log_file, 'w') as f:
        res = subprocess.run(train_cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    if res.returncode != 0:
        print(f"[ERROR] Training failed for {run_name}! See {log_file}")
        return False
        
    print(f"[SUCCESS] Training completed for {run_name}!")
    
    # 2. Evaluate on Test
    test_cmd = [
        PYTHON, str(ROOT / 'code/eval_test.py'),
        '--run', run_name,
        '--device', device
    ]
    with open(log_file, 'a') as f:
        res = subprocess.run(test_cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    if res.returncode != 0:
        print(f"[ERROR] Test evaluation failed for {run_name}! See {log_file}")
        return False
        
    print(f"[EVAL COMPLETE] Test evaluation finished for {run_name}!")
    return True


def worker(queue, device):
    for job_id, seed, epochs, patience in queue:
        success = run_pipeline(job_id, device, seed, epochs, patience)
        if not success:
            print(f"[WARN] Job {job_id} encountered an error.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', default='0')
    parser.add_argument('--jobs', nargs='+', required=True)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--epochs', type=int, default=35)
    parser.add_argument('--patience', type=int, default=12)
    args = parser.parse_args()
    
    device = f"cuda:{args.gpu}"
    queue = [(job_id, args.seed, args.epochs, args.patience) for job_id in args.jobs]
    worker(queue, device)
