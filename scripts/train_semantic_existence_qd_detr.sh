#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

TRAIN_PATH="${TRAIN_PATH:-$ROOT_DIR/data/release/semantic_existence_v1/train.jsonl}"
EVAL_PATH="${EVAL_PATH:-$ROOT_DIR/features/charades_semantic_existence/val_seen.jsonl}"
CLIP_FEAT_DIR="${CLIP_FEAT_DIR:?Set CLIP_FEAT_DIR to the video CLIP feature directory}"
SLOWFAST_FEAT_DIR="${SLOWFAST_FEAT_DIR:?Set SLOWFAST_FEAT_DIR to the video SlowFast feature directory}"
TEXT_FEAT_DIR="${TEXT_FEAT_DIR:-$ROOT_DIR/features/charades_semantic_existence/clip_text}"
RESULTS_DIR="${RESULTS_DIR:-results/semantic_existence/qd_detr_gmr}"
DEVICE="${DEVICE:-cuda:0}"
PYTHON_BIN="${PYTHON_BIN:-python}"

"${PYTHON_BIN}" training/qd_detr_gmr/train.py \
  --dataset charades_semantic_existence \
  --feature clip_slowfast \
  --train_path "${TRAIN_PATH}" \
  --eval_path "${EVAL_PATH}" \
  --t_feat_dir "${TEXT_FEAT_DIR}" \
  --v_feat_dirs "${CLIP_FEAT_DIR}" "${SLOWFAST_FEAT_DIR}" \
  --results_dir "${RESULTS_DIR}" \
  --device "${DEVICE}" \
  --bsz 16 \
  --eval_bsz 16 \
  --n_epoch 30 \
  --max_es_cnt 8 \
  --overwrite \
  "$@"
