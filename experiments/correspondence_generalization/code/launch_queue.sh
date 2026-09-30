#!/usr/bin/env bash
set -euo pipefail
work="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$work"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$work/cache/runtime/pycache"
export XDG_CACHE_HOME="$work/cache/runtime"
export TORCH_HOME="$work/cache/runtime/torch"
export TMPDIR="$work/cache/runtime"
mkdir -p "$work/runs/autonomous_queue_20260930_strict"
/home/guoxiangyu/miniconda3/envs/gmr/bin/python - <<'PY'
import json
from pathlib import Path
p=Path('runs/autonomous_queue_20260930_strict/INTEGRATION_CHECKS.json')
assert json.loads(p.read_text())['state']=='passed'
assert json.loads(Path('code/configs/execution_queue.json').read_text())['seeds']==[3407]
PY
exec /home/guoxiangyu/miniconda3/envs/gmr/bin/python -u code/six_task_queue.py >> "$work/runs/autonomous_queue_20260930_strict/queue_console.log" 2>&1
