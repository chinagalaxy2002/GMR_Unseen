#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
release_root="${MULTISPLIT_RELEASE_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2}"
feature_root="${MULTISPLIT_FEATURE_ROOT:-$ROOT_DIR/features/semantic_existence_v2}"
old_text="${OLD_TEXT_DIR:-/home/guoxiangyu/paper/新建文件夹/charades/txt_clip}"
clip_code="${CLIP_CODE_DIR:-/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video}"
clip_weights="${CLIP_WEIGHTS:-/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt}"
feature_python="${FEATURE_PYTHON:-/home/guoxiangyu/miniconda3/envs/univtg/bin/python}"
shared="$feature_root/shared_clip_text"
mkdir -p "$shared"
for file in "$ROOT_DIR"/features/charades_semantic_existence/clip_text/qid*.npz; do
  target="$shared/${file##*/}"
  if [[ ! -e "$target" ]]; then ln -s "$file" "$target"; fi
done
for split_id in A1 A2_alt A3 C1 C2_alt; do
  output="$feature_root/$split_id"
  mkdir -p "$output"
  if [[ ! -e "$output/clip_text" ]]; then ln -s "$shared" "$output/clip_text"; fi
  "$feature_python" scripts/prepare_charades_semantic_existence.py \
    --release "$release_root/$split_id" --old-text "$old_text" \
    --clip-code "$clip_code" --clip-weights "$clip_weights" \
    --output "$output" --device cuda:0
done
