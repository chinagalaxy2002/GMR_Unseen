#!/usr/bin/env bash
# Five semantic splits in order; three models run concurrently within each split.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
run_base="${MULTISPLIT_RUN_ROOT:-$ROOT_DIR/results/semantic_existence/multi_split_v2}"
release_root="${MULTISPLIT_RELEASE_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2}"
feature_base="${MULTISPLIT_FEATURE_ROOT:-$ROOT_DIR/features/semantic_existence_v2}"
export VIDEO_ROOT="${VIDEO_ROOT:-/home/guoxiangyu/paper/新建文件夹/charades}"
export GMR_PYTHON="${GMR_PYTHON:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}"
export FLASH_PYTHON="${FLASH_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"
export SEMANTIC_SEED=3407
mkdir -p "$run_base"

if [[ "${1:-}" == "start" ]]; then
  if tmux has-session -t semantic_v2_training_queue 2>/dev/null; then
    echo "Queue already running: semantic_v2_training_queue" >&2
    exit 1
  fi
  printf -v quoted_log '%q' "$run_base/queue.log"
  tmux new-session -d -s semantic_v2_training_queue -c "$ROOT_DIR" \
    "bash scripts/queue_semantic_multisplit_training.sh run >> $quoted_log 2>&1"
  echo "Started tmux queue semantic_v2_training_queue; log: $run_base/queue.log"
  exit 0
fi
if [[ "${1:-}" != "run" ]]; then
  echo "Usage: bash scripts/queue_semantic_multisplit_training.sh start" >&2
  exit 2
fi

printf 'running %s\n' "$(date -Is)" > "$run_base/queue_status.txt"
for split_id in A1 A2_alt A3 C1 C2_alt; do
  export DATA_ROOT="$release_root/$split_id"
  export FEATURE_ROOT="$feature_base/$split_id"
  export RUN_ROOT="$run_base/$split_id"
  export SESSION_PREFIX="semantic_v2_${split_id}"
  python scripts/validate_release.py --release "$DATA_ROOT" > /dev/null
  if [[ ! -f "$FEATURE_ROOT/val_seen.jsonl" || ! -d "$FEATURE_ROOT/clip_text" ]]; then
    printf 'failed %s missing_features %s\n' "$split_id" "$(date -Is)" > "$run_base/queue_status.txt"
    exit 1
  fi
  for model in moment qd flash; do
    if [[ -e "$RUN_ROOT/$model/exit_code" ]]; then
      printf 'failed %s existing_result_%s %s\n' "$split_id" "$model" "$(date -Is)" > "$run_base/queue_status.txt"
      exit 1
    fi
  done
  printf 'training %s %s\n' "$split_id" "$(date -Is)" > "$run_base/queue_status.txt"
  echo "Starting $split_id: moment and qd on GPU 0, flash on GPU 1"
  bash scripts/run_semantic_existence_100ep_tmux.sh moment & p_moment=$!
  bash scripts/run_semantic_existence_100ep_tmux.sh qd & p_qd=$!
  bash scripts/run_semantic_existence_100ep_tmux.sh flash & p_flash=$!
  failed=0
  wait "$p_moment" || failed=1
  wait "$p_qd" || failed=1
  wait "$p_flash" || failed=1
  if [[ "$failed" -ne 0 ]]; then
    printf 'failed %s training %s\n' "$split_id" "$(date -Is)" > "$run_base/queue_status.txt"
    echo "Training failed in $split_id; inspect model console.log and exit_code" >&2
    exit 1
  fi
  printf 'complete %s %s\n' "$split_id" "$(date -Is)" > "$RUN_ROOT/group_status.txt"
  echo "Completed $split_id"
done
printf 'complete_all %s\n' "$(date -Is)" > "$run_base/queue_status.txt"
echo "All fifteen model trainings completed"
