#!/usr/bin/env python3
"""
Multi-GPU Parallel Runner for QSW QD-DETR Training across all 5 holdout splits.
Dispatches splits across available GPUs (cuda:0, cuda:1), monitors execution,
and aggregates cross-split benchmark metrics.
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
E2E_DIR = AGY_TEST / "e2e_training"
PYTHON_BIN = sys.executable

ALL_SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]

# Baseline QD-DETR metrics evaluated directly from the official pretrained checkpoints
# (results/semantic_existence/multi_split_v2/{split}/qd/best.ckpt) on each split's data views
BASELINE_QD = {
    "A1": {
        "Seen_AUROC": 0.8128, "Unseen_AUROC": 0.5075, "Seen_Unseen_Gap": 0.3053,
        "Matched_PairAcc": 0.6026, "U_pos_FRR": 15.91, "U_neg_RR": 90.03, "Gated_R1@0.5": 20.43
    },
    "A2_alt": {
        "Seen_AUROC": 0.7759, "Unseen_AUROC": 0.4174, "Seen_Unseen_Gap": 0.3585,
        "Matched_PairAcc": 0.3291, "U_pos_FRR": 27.50, "U_neg_RR": 85.83, "Gated_R1@0.5": 32.10
    },
    "A3": {
        "Seen_AUROC": 0.7721, "Unseen_AUROC": 0.4804, "Seen_Unseen_Gap": 0.2917,
        "Matched_PairAcc": 0.4806, "U_pos_FRR": 19.34, "U_neg_RR": 87.28, "Gated_R1@0.5": 32.80
    },
    "C1": {
        "Seen_AUROC": 0.7901, "Unseen_AUROC": 0.5697, "Seen_Unseen_Gap": 0.2204,
        "Matched_PairAcc": 0.6875, "U_pos_FRR": 20.83, "U_neg_RR": 86.11, "Gated_R1@0.5": 42.00
    },
    "C2_alt": {
        "Seen_AUROC": 0.6870, "Unseen_AUROC": 0.5445, "Seen_Unseen_Gap": 0.1425,
        "Matched_PairAcc": 0.4848, "U_pos_FRR": 27.03, "U_neg_RR": 84.86, "Gated_R1@0.5": 24.30
    },
}

def run_single_split(split: str, device: str, epochs: int, lr: float, train_mode: str, seed: int):
    log_dir = E2E_DIR / "runs" / split / "qd"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "train.log"

    cmd = [
        PYTHON_BIN, "-u", str(E2E_DIR / "train_qsw.py"),
        "--split", split,
        "--device", device,
        "--epochs", str(epochs),
        "--lr", str(lr),
        "--train_mode", train_mode,
        "--seed", str(seed),
    ]

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [LAUNCH] Split {split} on {device} (Epochs={epochs}, Mode={train_mode})...")
    with open(log_file, "w", encoding="utf-8") as f_out:
        p = subprocess.Popen(cmd, stdout=f_out, stderr=subprocess.STDOUT)
        ret = p.wait()

    if ret != 0:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [FAILED] Split {split} exited with code {ret}! Check {log_file}")
        return split, False, None

    result_file = log_dir / "results.json"
    if not result_file.exists():
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [ERROR] Split {split} finished but {result_file} not found!")
        return split, False, None

    data = json.loads(result_file.read_text(encoding="utf-8"))
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [SUCCESS] Split {split} completed! "
          f"Seen AUC: {data['Seen_AUROC']:.4f} | Unseen AUC: {data['Unseen_AUROC']:.4f} | "
          f"Gap: {data['Seen_Unseen_Gap']:.4f} | PairAcc: {data['Matched_PairAcc']:.4f}")
    return split, True, data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--splits", nargs="+", default=ALL_SPLITS)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--train_mode", default="adapter_and_decoder", choices=["adapter_only", "adapter_and_decoder", "full"])
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--gpus", nargs="+", default=["cuda:0", "cuda:1"])
    parser.add_argument("--max_parallel_per_gpu", type=int, default=2)
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 70)
    print("  QSW QD-DETR Multi-Split Parallel Training Runner")
    print(f"  Splits:     {args.splits}")
    print(f"  GPUs:       {args.gpus}")
    print(f"  Epochs:     {args.epochs}")
    print(f"  Mode:       {args.train_mode}")
    print(f"  LR:         {args.lr}")
    print(f"  Seed:       {args.seed}")
    print(f"  Max/GPU:    {args.max_parallel_per_gpu}")
    print("=" * 70)

    # Assign splits across GPUs
    # E.g. with 2 GPUs and 5 splits:
    # cuda:0 -> A1, A2_alt, A3
    # cuda:1 -> C1, C2_alt
    gpu_assignments = []
    for idx, s in enumerate(args.splits):
        gpu = args.gpus[idx % len(args.gpus)]
        gpu_assignments.append((s, gpu))

    total_workers = len(args.gpus) * args.max_parallel_per_gpu
    results = {}

    with ThreadPoolExecutor(max_workers=total_workers) as executor:
        futures = []
        for s, gpu in gpu_assignments:
            fut = executor.submit(run_single_split, s, gpu, args.epochs, args.lr, args.train_mode, args.seed)
            futures.append(fut)

        for fut in futures:
            split, ok, data = fut.result()
            if ok and data is not None:
                results[split] = data

    elapsed = time.time() - start_time
    print(f"\nAll tasks finished in {elapsed:.1f}s ({elapsed/60:.2f} min).\n")

    # Generate Summary Table
    print("=" * 95)
    print(f"{'Split':<8} | {'Seen AUC (B/Q)':<16} | {'Unseen AUC (B/Q)':<18} | {'Gap (B/Q)':<16} | {'PairAcc (B/Q)':<16} | {'Gated R1 (B/Q)'}")
    print("-" * 95)

    base_seen, qsw_seen = [], []
    base_u, qsw_u = [], []
    base_gap, qsw_gap = [], []
    base_pair, qsw_pair = [], []
    base_gated, qsw_gated = [], []

    for s in args.splits:
        if s not in results:
            print(f"{s:<8} | FAILED")
            continue
        q = results[s]
        b = BASELINE_QD.get(s, {})

        b_seen = b.get("Seen_AUROC", 0.0)
        q_seen = q.get("Seen_AUROC", 0.0)
        b_u = b.get("Unseen_AUROC", 0.0)
        q_u = q.get("Unseen_AUROC", 0.0)
        b_g = b.get("Seen_Unseen_Gap", 0.0)
        q_g = q.get("Seen_Unseen_Gap", 0.0)
        b_p = b.get("Matched_PairAcc", 0.0)
        q_p = q.get("Matched_PairAcc", 0.0)
        b_r = b.get("Gated_R1@0.5", 0.0)
        q_r = q.get("Gated_R1@0.5", 0.0)

        base_seen.append(b_seen)
        qsw_seen.append(q_seen)
        base_u.append(b_u)
        qsw_u.append(q_u)
        base_gap.append(b_g)
        qsw_gap.append(q_g)
        base_pair.append(b_p)
        qsw_pair.append(q_p)
        base_gated.append(b_r)
        qsw_gated.append(q_r)

        d_u = (q_u - b_u) * 100.0
        d_g = (q_g - b_g) * 100.0
        d_p = (q_p - b_p) * 100.0

        print(f"{s:<8} | {b_seen:.4f} / {q_seen:.4f} | {b_u:.4f} / {q_u:.4f} ({d_u:+.1f}%) | "
              f"{b_g:.4f} / {q_g:.4f} ({d_g:+.1f}%) | {b_p:.4f} / {q_p:.4f} ({d_p:+.1f}%) | "
              f"{b_r:.1f}% / {q_r:.1f}%")

    print("-" * 95)
    if qsw_u:
        mean_b_seen = sum(base_seen) / len(base_seen)
        mean_q_seen = sum(qsw_seen) / len(qsw_seen)
        mean_b_u = sum(base_u) / len(base_u)
        mean_q_u = sum(qsw_u) / len(qsw_u)
        mean_b_gap = sum(base_gap) / len(base_gap)
        mean_q_gap = sum(qsw_gap) / len(qsw_gap)
        mean_b_pair = sum(base_pair) / len(base_pair)
        mean_q_pair = sum(qsw_pair) / len(qsw_pair)
        mean_b_gated = sum(base_gated) / len(base_gated)
        mean_q_gated = sum(qsw_gated) / len(qsw_gated)

        d_mean_u = (mean_q_u - mean_b_u) * 100.0
        d_mean_g = (mean_q_gap - mean_b_gap) * 100.0
        d_mean_p = (mean_q_pair - mean_b_pair) * 100.0

        print(f"{'MEAN':<8} | {mean_b_seen:.4f} / {mean_q_seen:.4f} | {mean_b_u:.4f} / {mean_q_u:.4f} ({d_mean_u:+.1f}%) | "
              f"{mean_b_gap:.4f} / {mean_q_gap:.4f} ({d_mean_g:+.1f}%) | {mean_b_pair:.4f} / {mean_q_pair:.4f} ({d_mean_p:+.1f}%) | "
              f"{mean_b_gated:.1f}% / {mean_q_gated:.1f}%")
    print("=" * 95)

    # Save aggregated report
    agg_report = {
        "config": vars(args),
        "elapsed_seconds": elapsed,
        "results": results,
        "summary": {
            "mean_seen_auroc": mean_q_seen if qsw_u else 0.0,
            "mean_unseen_auroc": mean_q_u if qsw_u else 0.0,
            "mean_gap": mean_q_gap if qsw_u else 0.0,
            "mean_matched_pair_acc": mean_q_pair if qsw_u else 0.0,
            "mean_gated_r1": mean_q_gated if qsw_u else 0.0,
        },
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    agg_path = E2E_DIR / "runs" / f"aggregate_report_{args.train_mode}_{args.epochs}ep.json"
    agg_path.write_text(json.dumps(agg_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Aggregated report saved to {agg_path}")

if __name__ == "__main__":
    main()
