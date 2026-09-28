#!/usr/bin/env bash
# E0/E1 and QD-DETR: localization-only controls with the same features and 100-epoch budget as seed 3407 GMR.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
DATA_ROOT="${DATA_ROOT:-$ROOT_DIR/data/release/semantic_existence_v1}"
FEATURE_ROOT="${FEATURE_ROOT:-$ROOT_DIR/features/charades_semantic_existence}"
VIDEO_ROOT="${VIDEO_ROOT:-/home/guoxiangyu/paper/新建文件夹/charades}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/localization_only_seed${SEED}_100ep}"
GMR_PYTHON="${GMR_PYTHON:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}"
FLASH_PYTHON="${FLASH_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"

prepare_views() {
  mkdir -p "$FEATURE_ROOT"
  "$GMR_PYTHON" - "$DATA_ROOT" "$FEATURE_ROOT" <<'PY'
import json
import sys
from pathlib import Path

release, output = map(Path, sys.argv[1:])
for split in ("train", "val", "test"):
    source = release / f"{split}.jsonl"
    dest = output / f"{split}_positive.jsonl"
    with source.open(encoding="utf-8") as src, dest.open("w", encoding="utf-8") as dst:
        for line in src:
            row = json.loads(line)
            allowed = ("S+", "U+") if split == "test" else ("S+",)
            if row["partition"] in allowed:
                dst.write(line)
    count = sum(1 for _ in dest.open())
    expected = {"train": 6851, "val": 694, "test": 2971}[split]
    if count != expected:
        raise ValueError(f"{dest}: expected {expected} rows, got {count}")
    print(f"{dest}: {count} rows")
PY
}

if [[ "${1:-}" == "launch" ]]; then
  prepare_views
  mkdir -p "$RUN_ROOT"
  for model in gpu0 flash; do
    session="semantic_${model}_loc_seed${SEED}_100ep"
    if tmux has-session -t "$session" 2>/dev/null; then
      echo "Already running: $session"
      continue
    fi
    if [[ "$model" != gpu0 && -e "$RUN_ROOT/$model/exit_code" ]]; then
      echo "Already finished: $RUN_ROOT/$model/exit_code"
      continue
    fi
    tmux new-session -d -s "$session" -c "$ROOT_DIR" \
      "SEMANTIC_SEED=$SEED DATA_ROOT='$DATA_ROOT' FEATURE_ROOT='$FEATURE_ROOT' VIDEO_ROOT='$VIDEO_ROOT' RUN_ROOT='$RUN_ROOT' GMR_PYTHON='$GMR_PYTHON' FLASH_PYTHON='$FLASH_PYTHON' bash scripts/run_semantic_localization_controls.sh $model"
    echo "Started: $session"
  done
  exit 0
fi

model="${1:?Use launch, moment, or flash}"
if [[ "$model" == gpu0 ]]; then
  if [[ ! -e "$RUN_ROOT/moment/exit_code" ]]; then
    bash "$0" moment
  fi
  if [[ ! -e "$RUN_ROOT/qd/exit_code" ]]; then
    bash "$0" qd
  fi
  exit 0
fi
mkdir -p "$RUN_ROOT/$model"
printf 'experiment=localization_only\nmodel=%s\nseed=%s\nepochs=100\nstarted=%s\n' \
  "$model" "$SEED" "$(date -Is)" > "$RUN_ROOT/$model/run_metadata.txt"
set +e
case "$model" in
  moment)
    CUDA_VISIBLE_DEVICES=0 "$GMR_PYTHON" training/moment_detr_gmr/train.py \
      --dataset charades_semantic_existence --no_exist_head \
      --train_path "$FEATURE_ROOT/train_positive.jsonl" \
      --eval_path "$FEATURE_ROOT/val_positive.jsonl" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
      --results_dir "$RUN_ROOT/moment" \
      --device cuda --seed "$SEED" --n_epoch 100 --max_es_cnt -1 \
      --bsz 16 --eval_bsz 16 > "$RUN_ROOT/moment/train_console.log" 2>&1
    status=$?
    if [[ "$status" -eq 0 ]]; then
      CUDA_VISIBLE_DEVICES=0 "$GMR_PYTHON" training/moment_detr_gmr/evaluate.py \
        --dataset charades_semantic_existence \
        --model_path "$RUN_ROOT/moment/best.ckpt" --split test \
        --eval_path "$FEATURE_ROOT/test_positive.jsonl" \
        --t_feat_dir "$FEATURE_ROOT/clip_text" \
        --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
        --results_dir "$RUN_ROOT/moment/test" --device cuda \
        > "$RUN_ROOT/moment/test_console.log" 2>&1
      status=$?
    fi
    ;;
  qd)
    CUDA_VISIBLE_DEVICES=0 "$GMR_PYTHON" training/qd_detr_gmr/train.py \
      --dataset charades_semantic_existence --no_exist_head \
      --train_path "$FEATURE_ROOT/train_positive.jsonl" \
      --eval_path "$FEATURE_ROOT/val_positive.jsonl" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
      --results_dir "$RUN_ROOT/qd" \
      --device cuda:0 --seed "$SEED" --n_epoch 100 --max_es_cnt -1 \
      --bsz 16 --eval_bsz 16 > "$RUN_ROOT/qd/train_console.log" 2>&1
    status=$?
    if [[ "$status" -eq 0 ]]; then
      CUDA_VISIBLE_DEVICES=0 "$GMR_PYTHON" training/qd_detr_gmr/evaluate.py \
        --dataset charades_semantic_existence \
        --model_path "$RUN_ROOT/qd/best.ckpt" --split test \
        --eval_path "$FEATURE_ROOT/test_positive.jsonl" \
        --t_feat_dir "$FEATURE_ROOT/clip_text" \
        --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
        --results_dir "$RUN_ROOT/qd/test" --device cuda:0 \
        > "$RUN_ROOT/qd/test_console.log" 2>&1
      status=$?
    fi
    ;;
  flash)
    CUDA_VISIBLE_DEVICES=1 "$FLASH_PYTHON" -m training.flash_vtg_gmr.train \
      configs/flash_vtg_gmr/model.py \
      --dset_name charadesSTA --ctx_mode video_tef \
      --train_path "$FEATURE_ROOT/train_positive.jsonl" \
      --eval_path "$FEATURE_ROOT/val_positive.jsonl" --eval_split_name val \
      --v_feat_dirs "$VIDEO_ROOT/vid_slowfast" "$VIDEO_ROOT/vid_clip" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dim 2816 --t_feat_dim 512 \
      --max_q_l 40 --max_v_l 200 --clip_length 1 --max_windows 5 \
      --lr 3e-5 --lr_drop 400 --wd 1e-4 \
      --n_epoch 100 --max_es_cnt -1 --bsz 8 --eval_bsz 1 \
      --eval_epoch 1 --num_workers 0 --device 0 \
      --results_root "$RUN_ROOT/flash" --exp_id "localization_only_seed${SEED}_100ep" \
      --seed "$SEED" --hidden_dim 256 --dim_feedforward 1024 \
      --enc_layers 3 --t2v_layers 6 --dummy_layers 2 --nheads 8 \
      --num_dummies 40 --total_prompts 10 --num_prompts 1 \
      --kernel_size 5 --num_conv_layers 1 --num_mlp_layers 5 --use_SRM \
      --input_dropout 0.5 --dropout 0.1 --span_loss_type l1 \
      --lw_reg 1 --lw_cls 5 --lw_sal 0 --lw_saliency 0 \
      --lw_wattn 1 --lw_ms_align 1 \
      --mr_only --eval_full_only --nms_thd -1 \
      > "$RUN_ROOT/flash/train_console.log" 2>&1
    status=$?
    if [[ "$status" -eq 0 ]]; then
      run_dir="$(find "$RUN_ROOT/flash" -mindepth 1 -maxdepth 1 -type d -name 'charadesSTA-*' | sort | tail -1)"
      CUDA_VISIBLE_DEVICES=1 "$FLASH_PYTHON" -m training.flash_vtg_gmr.inference \
        configs/flash_vtg_gmr/model.py --resume "$run_dir/model_best.ckpt" \
        --eval_split_name test --eval_path "$FEATURE_ROOT/test_positive.jsonl" \
        --eval_results_dir "$RUN_ROOT/flash/test" --device 0 --nms_thd -1 \
        > "$RUN_ROOT/flash/test_console.log" 2>&1
      status=$?
    fi
    ;;
  *) echo "Unknown model: $model" >&2; exit 2 ;;
esac
set -e
printf '%s\n' "$status" > "$RUN_ROOT/$model/exit_code"
printf 'finished=%s\nexit_code=%s\n' "$(date -Is)" "$status" >> "$RUN_ROOT/$model/run_metadata.txt"
exit "$status"
