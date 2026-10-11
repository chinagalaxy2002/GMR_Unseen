#!/usr/bin/env bash
# Seen-only baseline: at most 100 epochs, patience 26.
set -euo pipefail

ROOT_DIR="${V3_NATIVE_REPO:?}"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
SESSION_PREFIX="${SESSION_PREFIX:-semantic}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/seed${SEED}_100ep}"
DATA_ROOT="${DATA_ROOT:-$ROOT_DIR/data/release/semantic_existence_v1}"
FEATURE_ROOT="${FEATURE_ROOT:-$ROOT_DIR/features/charades_semantic_existence}"
VIDEO_ROOT="${VIDEO_ROOT:?Set VIDEO_ROOT to a directory containing vid_clip and vid_slowfast}"
GMR_PYTHON="${GMR_PYTHON:-python}"
FLASH_PYTHON="${FLASH_PYTHON:-python}"

if [[ "${1:-}" == "launch" ]]; then
  mkdir -p "$RUN_ROOT"
  for model in moment qd flash; do
    session="${SESSION_PREFIX}_${model}_seed${SEED}_100ep"
    if tmux has-session -t "$session" 2>/dev/null; then
      echo "Already running: $session"
      continue
    fi
    printf -v launch_cmd '%q ' env "SEMANTIC_SEED=$SEED" "RUN_ROOT=$RUN_ROOT" \
      "DATA_ROOT=$DATA_ROOT" "FEATURE_ROOT=$FEATURE_ROOT" "VIDEO_ROOT=$VIDEO_ROOT" \
      "SESSION_PREFIX=$SESSION_PREFIX" \
      "GMR_PYTHON=$GMR_PYTHON" "FLASH_PYTHON=$FLASH_PYTHON" \
      bash scripts/run_semantic_existence_100ep_tmux.sh "$model"
    tmux new-session -d -s "$session" -c "$ROOT_DIR" "$launch_cmd"
    echo "Started: $session"
  done
  exit 0
fi

model="${1:?Use launch, moment, qd, or flash}"
mkdir -p "$RUN_ROOT/$model"
printf 'seed=%s\nepochs=100\nmodel=%s\nstarted=%s\n' \
  "$SEED" "$model" "$(date -Is)" > "$RUN_ROOT/$model/run_metadata.txt"

set +e
case "$model" in
  moment)
    CUDA_VISIBLE_DEVICES="${TRAIN_GPU:?}" "$GMR_PYTHON" training/moment_detr_gmr/train.py \
      --dataset charades_semantic_existence \
      --train_path "$DATA_ROOT/train.jsonl" \
      --eval_path "$FEATURE_ROOT/val_seen.jsonl" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
      --results_dir "$RUN_ROOT/moment" \
      --device cuda --seed "$SEED" --n_epoch 100 --max_es_cnt 26 \
      --bsz 16 --eval_bsz 16 \
      > "$RUN_ROOT/moment/console.log" 2>&1
    ;;
  qd)
    CUDA_VISIBLE_DEVICES="${TRAIN_GPU:?}" "$GMR_PYTHON" training/qd_detr_gmr/train.py \
      --dataset charades_semantic_existence \
      --train_path "$DATA_ROOT/train.jsonl" \
      --eval_path "$FEATURE_ROOT/val_seen.jsonl" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dirs "$VIDEO_ROOT/vid_clip" "$VIDEO_ROOT/vid_slowfast" \
      --results_dir "$RUN_ROOT/qd" \
      --device cuda:0 --seed "$SEED" --n_epoch 100 --max_es_cnt 26 \
      --bsz 16 --eval_bsz 16 \
      > "$RUN_ROOT/qd/console.log" 2>&1
    ;;
  flash)
    CUDA_VISIBLE_DEVICES="${TRAIN_GPU:?}" "$FLASH_PYTHON" -m training.flash_vtg_gmr.train \
      configs/flash_vtg_gmr/model.py \
      --dset_name charadesSTA --ctx_mode video_tef \
      --train_path "$DATA_ROOT/train.jsonl" \
      --eval_path "$FEATURE_ROOT/val_seen.jsonl" --eval_split_name val \
      --v_feat_dirs "$VIDEO_ROOT/vid_slowfast" "$VIDEO_ROOT/vid_clip" \
      --t_feat_dir "$FEATURE_ROOT/clip_text" \
      --v_feat_dim 2816 --t_feat_dim 512 \
      --max_q_l 40 --max_v_l 200 --clip_length 1 --max_windows 5 \
      --lr 3e-5 --lr_drop 400 --wd 1e-4 \
      --n_epoch 100 --max_es_cnt 26 --bsz 8 --eval_bsz 1 \
      --eval_epoch 1 --num_workers 0 --device 0 \
      --results_root "$RUN_ROOT/flash" --exp_id "seen_only_seed${SEED}_100ep" \
      --seed "$SEED" --hidden_dim 256 --dim_feedforward 1024 \
      --enc_layers 3 --t2v_layers 6 --dummy_layers 2 --nheads 8 \
      --num_dummies 40 --total_prompts 10 --num_prompts 1 \
      --kernel_size 5 --num_conv_layers 1 --num_mlp_layers 5 --use_SRM \
      --input_dropout 0.5 --dropout 0.1 --span_loss_type l1 \
      --lw_reg 1 --lw_cls 5 --lw_sal 0 --lw_saliency 0 \
      --lw_wattn 1 --lw_ms_align 1 \
      --mr_only --eval_full_only --use_exist_head \
      --exist_pool mean --exist_loss_coef 1 --exist_gate_thd 0.5 \
      --nms_thd -1 \
      > "$RUN_ROOT/flash/console.log" 2>&1
    ;;
  *)
    echo "Unknown model: $model" >&2
    exit 2
    ;;
esac
status=$?
set -e
printf '%s\n' "$status" > "$RUN_ROOT/$model/exit_code"
printf 'finished=%s\nexit_code=%s\n' "$(date -Is)" "$status" >> "$RUN_ROOT/$model/run_metadata.txt"
exit "$status"
