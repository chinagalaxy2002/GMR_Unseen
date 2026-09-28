#!/usr/bin/env bash
# Launch one reviewed and packaged v2 split at a time with the v1 100-epoch protocol.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

split_id="${1:?Usage: bash scripts/run_semantic_multisplit_100ep.sh SPLIT_ID launch}"
action="${2:?Usage: bash scripts/run_semantic_multisplit_100ep.sh SPLIT_ID launch}"
if [[ "$action" != "launch" ]]; then
  echo "Only launch is supported" >&2
  exit 2
fi
case "$split_id" in
  A1|A2_alt|A3|C1|C2_alt) ;;
  *) echo "Unknown frozen split: $split_id" >&2; exit 2 ;;
esac

release_root="${MULTISPLIT_RELEASE_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2}"
export DATA_ROOT="$release_root/$split_id"
export FEATURE_ROOT="${MULTISPLIT_FEATURE_ROOT:-$ROOT_DIR/features/semantic_existence_v2}/$split_id"
export RUN_ROOT="${MULTISPLIT_RUN_ROOT:-$ROOT_DIR/results/semantic_existence/multi_split_v2}/$split_id"
export SESSION_PREFIX="semantic_v2_${split_id}"

python scripts/validate_release.py --release "$DATA_ROOT"
if [[ ! -f "$FEATURE_ROOT/val_seen.jsonl" || ! -d "$FEATURE_ROOT/clip_text" ]]; then
  echo "Missing prepared text features or seen validation view: $FEATURE_ROOT" >&2
  exit 1
fi
if [[ -d "$RUN_ROOT" ]] && find "$RUN_ROOT" -mindepth 1 -print -quit | rg -q .; then
  echo "Run directory already populated: $RUN_ROOT" >&2
  exit 1
fi
: "${VIDEO_ROOT:?Set VIDEO_ROOT to the Charades video-feature directory}"
bash scripts/run_semantic_existence_100ep_tmux.sh launch
