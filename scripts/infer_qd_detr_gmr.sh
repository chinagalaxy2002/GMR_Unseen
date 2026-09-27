#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

MODEL_PATH=${MODEL_PATH:-results/qd_detr_gmr/best.ckpt}
SPLIT=${SPLIT:-test}
EVAL_PATH=${EVAL_PATH:-data/label/Standard/test.jsonl}
TEXT_FEAT_DIR=${TEXT_FEAT_DIR:-Soccergmr/clip_text}
CLIP_FEAT_DIR=${CLIP_FEAT_DIR:-Soccergmr/clip}
SLOWFAST_FEAT_DIR=${SLOWFAST_FEAT_DIR:-Soccergmr/slowfast}
RESULTS_DIR=${RESULTS_DIR:-results/qd_detr_gmr/${SPLIT}}
DEVICE=${DEVICE:-cuda}
PYTHON_BIN=${PYTHON_BIN:-/home/guoxiangyu/miniconda3/envs/gmr/bin/python}

"${PYTHON_BIN}" training/qd_detr_gmr/evaluate.py \
  --dataset soccer_gmr \
  --feature clip_slowfast \
  --model_path "${MODEL_PATH}" \
  --split "${SPLIT}" \
  --eval_path "${EVAL_PATH}" \
  --t_feat_dir "${TEXT_FEAT_DIR}" \
  --v_feat_dirs "${CLIP_FEAT_DIR}" "${SLOWFAST_FEAT_DIR}" \
  --results_dir "${RESULTS_DIR}" \
  --device "${DEVICE}" \
  "$@"
