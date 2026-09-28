#!/usr/bin/env bash
# Schedule three single-seed semantic-seen references for one common start time.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
TARGET_UTC="${TARGET_UTC:-2026-09-27T18:54:44Z}"
TARGET_EPOCH="$(date -u -d "$TARGET_UTC" +%s)"
RELEASE="$ROOT_DIR/data/release/semantic_existence_v1"
FEATURE_ROOT="$ROOT_DIR/features/charades_semantic_existence"
ORACLE_DATA_ROOT="$FEATURE_ROOT/semantic_seen_reference_data"
VIDEO_ROOT="${VIDEO_ROOT:-/home/guoxiangyu/paper/新建文件夹/charades}"
GMR_PYTHON="${GMR_PYTHON:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}"
FLASH_PYTHON="${FLASH_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/semantic_seen_reference_seed${SEED}_100ep}"

prepare() {
  mkdir -p "$ORACLE_DATA_ROOT" "$RUN_ROOT"
  "$GMR_PYTHON" - "$FEATURE_ROOT/train_semantic_seen_reference.jsonl" "$FEATURE_ROOT/clip_text" <<'PY'
import json
import sys
from pathlib import Path
path, text_dir = map(Path, sys.argv[1:])
rows = [json.loads(s) for s in path.open(encoding="utf-8")]
if len(rows) != 10996 or len({str(x["qid"]) for x in rows}) != 10996:
    raise ValueError("Expected 10,996 unique oracle-training rows")
if sum(bool(x["relevant_windows"]) for x in rows) != 9530:
    raise ValueError("Oracle positive count differs from protocol")
missing = [x["qid"] for x in rows if not (text_dir / f"qid{x['qid']}.npz").exists()]
if missing:
    raise ValueError(f"Missing {len(missing)} text features")
print("Oracle train verified: 10,996 unique rows, 9,530 positive, 1,466 negative")
PY
  ln -sfn "$FEATURE_ROOT/train_semantic_seen_reference.jsonl" "$ORACLE_DATA_ROOT/train.jsonl"
  printf 'experiment=semantic_seen_reference\nseed=%s\ntrain_rows=10996\nscheduled_start_utc=%s\nscheduled_start_local=%s\n' \
    "$SEED" "$TARGET_UTC" "$(TZ=Asia/Shanghai date -d "$TARGET_UTC" '+%Y-%m-%d %H:%M:%S %Z')" \
    > "$RUN_ROOT/schedule_metadata.txt"
}

case "${1:-}" in
  schedule)
    prepare
    session="semantic_oracle_schedule_seed${SEED}"
    if tmux has-session -t "$session" 2>/dev/null; then
      echo "Already scheduled: $session"
      exit 0
    fi
    printf -v launch_cmd '%q ' env "SEMANTIC_SEED=$SEED" "TARGET_UTC=$TARGET_UTC" \
      "RUN_ROOT=$RUN_ROOT" "VIDEO_ROOT=$VIDEO_ROOT" "GMR_PYTHON=$GMR_PYTHON" \
      "FLASH_PYTHON=$FLASH_PYTHON" bash scripts/schedule_semantic_seen_references.sh wait
    tmux new-session -d -s "$session" -c "$ROOT_DIR" "$launch_cmd"
    echo "Scheduled three parallel oracle-reference trainings at $(TZ=Asia/Shanghai date -d "$TARGET_UTC" '+%Y-%m-%d %H:%M:%S %Z')"
    ;;
  wait)
    while :; do
      now="$(date +%s)"
      remaining="$((TARGET_EPOCH - now))"
      [[ "$remaining" -le 0 ]] && break
      if [[ "$remaining" -gt 60 ]]; then sleep 60; else sleep "$remaining"; fi
    done
    exec bash "$0" start
    ;;
  start)
    prepare
    printf 'actual_start_local=%s\nstart_reason=localization_controls_completed_user_requested_proceed\n' \
      "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S %Z')" >> "$RUN_ROOT/schedule_metadata.txt"
    for model in moment qd flash; do
      session="semantic_oracle_${model}_seed${SEED}_100ep"
      if [[ -f "$RUN_ROOT/$model/exit_code" ]]; then
        echo "Already completed: $model"
        continue
      fi
      if tmux has-session -t "$session" 2>/dev/null; then
        echo "Already running: $model"
        continue
      fi
      printf -v launch_cmd '%q ' env "SEMANTIC_SEED=$SEED" "TARGET_UTC=$TARGET_UTC" \
        "RUN_ROOT=$RUN_ROOT" "VIDEO_ROOT=$VIDEO_ROOT" "GMR_PYTHON=$GMR_PYTHON" \
        "FLASH_PYTHON=$FLASH_PYTHON" bash scripts/schedule_semantic_seen_references.sh "$model"
      tmux new-session -d -s "$session" -c "$ROOT_DIR" "$launch_cmd"
      echo "Started: $model"
    done
    session="semantic_oracle_finalize_seed${SEED}"
    if ! tmux has-session -t "$session" 2>/dev/null; then
      printf -v launch_cmd '%q ' env "SEMANTIC_SEED=$SEED" "RUN_ROOT=$RUN_ROOT" \
        "VIDEO_ROOT=$VIDEO_ROOT" "GMR_PYTHON=$GMR_PYTHON" "FLASH_PYTHON=$FLASH_PYTHON" \
        bash scripts/finalize_semantic_seen_references.sh wait
      tmux new-session -d -s "$session" -c "$ROOT_DIR" "$launch_cmd"
    fi
    ;;
  moment|qd|flash)
    model="$1"
    export SEMANTIC_SEED="$SEED" RUN_ROOT DATA_ROOT="$ORACLE_DATA_ROOT" FEATURE_ROOT VIDEO_ROOT GMR_PYTHON FLASH_PYTHON
    exec bash scripts/run_semantic_existence_100ep_tmux.sh "$model"
    ;;
  *) echo "Use schedule, wait, start, moment, qd, or flash" >&2; exit 2 ;;
esac
