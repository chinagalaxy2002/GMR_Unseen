#!/usr/bin/env bash
set -euo pipefail
work="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$work"
export PYTHONDONTWRITEBYTECODE=1
export XDG_CACHE_HOME="$work/cache/runtime"
export TORCH_HOME="$work/cache/runtime/torch"
export TMPDIR="$work/cache/runtime"
export CUDA_VISIBLE_DEVICES=0,1
run="$work/runs/qd_throw_strict_diagnostic_20260930"
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -u code/run_development.py "$run" > "$work/runs/qd_throw_strict_diagnostic_console.log" 2>&1 &
training_pid=$!
while [[ ! -f "$run/status.json" ]]; do
  if ! kill -0 "$training_pid" 2>/dev/null; then wait "$training_pid"; exit 1; fi
  sleep 1
done
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -u code/watch_diagnostics.py "$run" > "$run/diagnostics_watcher_console.log" 2>&1 &
watcher_pid=$!
wait "$training_pid"
wait "$watcher_pid"
