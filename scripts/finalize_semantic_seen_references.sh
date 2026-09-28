#!/usr/bin/env bash
# Evaluate the three semantic-seen reference checkpoints after scheduled training.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/semantic_seen_reference_seed${SEED}_100ep}"
RELEASE="$ROOT_DIR/data/release/semantic_existence_v1"
FEATURE_ROOT="$ROOT_DIR/features/charades_semantic_existence"
VIDEO_ROOT="${VIDEO_ROOT:-/home/guoxiangyu/paper/新建文件夹/charades}"
GMR_PYTHON="${GMR_PYTHON:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}"
FLASH_PYTHON="${FLASH_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"

if [[ "${1:-}" == wait ]]; then
  while :; do
    ready=1
    for model in moment qd flash; do
      [[ -f "$RUN_ROOT/$model/exit_code" ]] || ready=0
    done
    [[ "$ready" -eq 1 ]] && break
    sleep 30
  done
  set +e
  bash "$0" run > "$RUN_ROOT/finalize_console.log" 2>&1
  status=$?
  set -e
  printf '%s\n' "$status" > "$RUN_ROOT/finalize_exit_code"
  exit "$status"
fi
[[ "${1:-}" == run ]] || { echo "Use wait or run" >&2; exit 2; }
for model in moment qd flash; do
  [[ "$(cat "$RUN_ROOT/$model/exit_code")" == 0 ]] || { echo "Training failed: $model" >&2; exit 1; }
done

for model in moment qd; do
  if [[ "$model" == moment ]]; then
    module="moment_detr_gmr"
    device="cuda"
  else
    module="qd_detr_gmr"
    device="cuda:0"
  fi
  CUDA_VISIBLE_DEVICES=0 "$GMR_PYTHON" "training/$module/evaluate.py" \
    --dataset charades_semantic_existence --model_path "$RUN_ROOT/$model/best.ckpt" \
    --split test --eval_path "$RELEASE/test.jsonl" \
    --t_feat_dir "$FEATURE_ROOT/clip_text" \
    --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
    --results_dir "$RUN_ROOT/$model/test" --device "$device" \
    > "$RUN_ROOT/$model/test_console.log" 2>&1
done

flash_run="$(find "$RUN_ROOT/flash" -mindepth 1 -maxdepth 1 -type d -name 'charadesSTA-*' | sort | tail -1)"
CUDA_VISIBLE_DEVICES=1 "$FLASH_PYTHON" -m training.flash_vtg_gmr.inference \
  configs/flash_vtg_gmr/model.py --resume "$flash_run/model_best.ckpt" \
  --eval_split_name test --eval_path "$RELEASE/test.jsonl" \
  --eval_results_dir "$RUN_ROOT/flash/test" --device 0 --nms_thd -1 \
  > "$RUN_ROOT/flash/test_console.log" 2>&1

for model in moment qd flash; do
  if [[ "$model" == moment ]]; then
    val_pred="$RUN_ROOT/moment/best_charades_semantic_existence_val_preds.jsonl"
    test_pred="$RUN_ROOT/moment/test/moment_detr_gmr_test_submission.jsonl"
  elif [[ "$model" == qd ]]; then
    val_pred="$RUN_ROOT/qd/best_charades_semantic_existence_val_preds.jsonl"
    test_pred="$RUN_ROOT/qd/test/qd_detr_gmr_test_submission.jsonl"
  else
    val_pred="$flash_run/best_charadesSTA_val_preds.jsonl"
    test_pred="$RUN_ROOT/flash/test/hl_test_submission.jsonl"
  fi
  "$GMR_PYTHON" scripts/analyze_semantic_existence.py \
    --release "$RELEASE" --val-predictions "$val_pred" \
    --test-predictions "$test_pred" --output "$RUN_ROOT/$model/diagnostics.json" \
    > "$RUN_ROOT/$model/diagnostics_console.log" 2>&1
  "$GMR_PYTHON" eval/eval_main.py \
    --submission_path "$test_pred" --gt_path "$RELEASE/test.jsonl" \
    --save_path "$RUN_ROOT/$model/official_test_metrics.json" \
    > "$RUN_ROOT/$model/official_console.log" 2>&1
done

"$GMR_PYTHON" scripts/compare_semantic_seen_reference.py \
  --strict-root "$ROOT_DIR/results/semantic_existence/seed${SEED}_100ep" \
  --reference-root "$RUN_ROOT" \
  --release "$RELEASE" \
  --output "$RUN_ROOT/strict_vs_reference.json"
