#!/usr/bin/env bash
# Evaluate one completed v2 split using checkpoints and seen-validation thresholds.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
split="${1:?Usage: bash scripts/finalize_semantic_multisplit_group.sh SPLIT_ID}"
case "$split" in A1|A2_alt|A3|C1|C2_alt) ;; *) echo "Unknown split: $split" >&2; exit 2 ;; esac
release="${MULTISPLIT_RELEASE_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2}/$split"
features="${MULTISPLIT_FEATURE_ROOT:-$root/features/semantic_existence_v2}/$split"
run="${MULTISPLIT_RUN_ROOT:-$root/results/semantic_existence/multi_split_v2}/$split"
video="${VIDEO_ROOT:-/home/guoxiangyu/paper/新建文件夹/charades}"
gmr_python="${GMR_PYTHON:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}"
flash_python="${FLASH_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"

python scripts/validate_release.py --release "$release" >/dev/null
for model in moment qd flash; do
  [[ "$(cat "$run/$model/exit_code")" == 0 ]] || { echo "Training incomplete: $model" >&2; exit 1; }
done

for model in moment qd; do
  if [[ "$model" == moment ]]; then module=moment_detr_gmr; device=cuda; else module=qd_detr_gmr; device=cuda:0; fi
  mkdir -p "$run/$model/test"
  CUDA_VISIBLE_DEVICES=0 "$gmr_python" "training/$module/evaluate.py" \
    --dataset charades_semantic_existence --model_path "$run/$model/best.ckpt" \
    --split test --eval_path "$release/test.jsonl" \
    --t_feat_dir "$features/clip_text" \
    --v_feat_dirs "$video/vid_clip" "$video/vid_slowfast" \
    --results_dir "$run/$model/test" --device "$device" \
    > "$run/$model/test_console.log" 2>&1
done

flash_run="$(find "$run/flash" -mindepth 1 -maxdepth 1 -type d -name 'charadesSTA-*' | sort | tail -1)"
[[ -n "$flash_run" && -f "$flash_run/model_best.ckpt" ]] || { echo "Flash best checkpoint missing" >&2; exit 1; }
mkdir -p "$run/flash/test"
CUDA_VISIBLE_DEVICES=1 "$flash_python" -m training.flash_vtg_gmr.inference \
  configs/flash_vtg_gmr/model.py --resume "$flash_run/model_best.ckpt" \
  --eval_split_name test --eval_path "$release/test.jsonl" \
  --eval_results_dir "$run/flash/test" --device 0 --nms_thd -1 \
  > "$run/flash/test_console.log" 2>&1

for model in moment qd flash; do
  case "$model" in
    moment) val_pred="$run/moment/best_charades_semantic_existence_val_preds.jsonl";
            test_pred="$run/moment/test/moment_detr_gmr_test_submission.jsonl" ;;
    qd) val_pred="$run/qd/best_charades_semantic_existence_val_preds.jsonl";
        test_pred="$run/qd/test/qd_detr_gmr_test_submission.jsonl" ;;
    flash) val_pred="$flash_run/best_charadesSTA_val_preds.jsonl";
           test_pred="$run/flash/test/hl_test_submission.jsonl" ;;
  esac
  "$gmr_python" scripts/analyze_semantic_existence.py \
    --release "$release" --val-predictions "$val_pred" \
    --test-predictions "$test_pred" --output "$run/$model/diagnostics.json" \
    > "$run/$model/diagnostics_console.log" 2>&1
  "$gmr_python" eval/eval_main.py \
    --submission_path "$test_pred" --gt_path "$release/test.jsonl" \
    --save_path "$run/$model/official_test_metrics.json" \
    > "$run/$model/official_console.log" 2>&1
done
printf 'complete %s\n' "$(date -Is)" > "$run/evaluation_status.txt"
