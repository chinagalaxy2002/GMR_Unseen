#!/usr/bin/env python3
"""
Parallel executor for all 15 benchmark settings across GPU 0 and GPU 1.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO / "experiments/agy_test/code"))

from run_all_5splits_benchmarks import run_single_setting

def worker(device_str: str, tasks: list[tuple[str, str]], out_file: Path):
    results = []
    print(f"Worker on {device_str} started with {len(tasks)} tasks.", flush=True)
    for sp, bb in tasks:
        print(f"[{device_str}] >>> Starting {sp} / {bb}...", flush=True)
        res = run_single_setting(sp, bb, device_str, seed=3407)
        results.append(res)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Worker on {device_str} finished! Saved {len(results)} results to {out_file}", flush=True)
    return results

def main():
    gpu0_tasks = [
        ("A1", "qd"),
        ("A1", "moment"),
        ("A1", "flash"),
        ("A2_alt", "qd"),
        ("A2_alt", "moment"),
        ("A2_alt", "flash"),
        ("A3", "qd"),
        ("A3", "moment"),
    ]
    gpu1_tasks = [
        ("A3", "flash"),
        ("C1", "qd"),
        ("C1", "moment"),
        ("C1", "flash"),
        ("C2_alt", "qd"),
        ("C2_alt", "moment"),
        ("C2_alt", "flash"),
    ]

    out0 = AGY_TEST / "report/BENCHMARK_GPU0.json"
    out1 = AGY_TEST / "report/BENCHMARK_GPU1.json"

    with ProcessPoolExecutor(max_workers=2) as executor:
        f0 = executor.submit(worker, "cuda:0", gpu0_tasks, out0)
        f1 = executor.submit(worker, "cuda:1", gpu1_tasks, out1)
        r0 = f0.result()
        r1 = f1.result()

    all_results = r0 + r1
    final_out = AGY_TEST / "report/FULL_15_BENCHMARK_RESULTS.json"
    final_out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n=======================================================")
    print(f"ALL 15 SETTINGS SUCCESSFULLY PROCESSED AND SAVED TO {final_out}!")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
