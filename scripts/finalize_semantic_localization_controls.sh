#!/usr/bin/env bash
# Score E0/E1 and QD localization-only controls after their training sessions exit.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/localization_only_seed${SEED}_100ep}"
GMR_ROOT="${GMR_ROOT:-$ROOT_DIR/results/semantic_existence/seed${SEED}_100ep}"
TEST_POS="$ROOT_DIR/features/charades_semantic_existence/test_positive.jsonl"

for model in moment qd flash; do
  code_file="$RUN_ROOT/$model/exit_code"
  [[ -f "$code_file" ]] || { echo "Still running: $model" >&2; exit 1; }
  [[ "$(cat "$code_file")" == 0 ]] || { echo "Failed: $model" >&2; exit 1; }
done

python scripts/analyze_localization_controls.py \
  --ground-truth "$TEST_POS" \
  --plain "$RUN_ROOT/moment/test/moment_detr_gmr_test_submission.jsonl" \
  --gmr "$GMR_ROOT/moment/test/moment_detr_gmr_test_submission.jsonl" \
  --output "$RUN_ROOT/moment/localization_comparison.json"
python scripts/analyze_localization_controls.py \
  --ground-truth "$TEST_POS" \
  --plain "$RUN_ROOT/qd/test/qd_detr_gmr_test_submission.jsonl" \
  --gmr "$GMR_ROOT/qd/test/qd_detr_gmr_test_submission.jsonl" \
  --output "$RUN_ROOT/qd/localization_comparison.json"
python scripts/analyze_localization_controls.py \
  --ground-truth "$TEST_POS" \
  --plain "$RUN_ROOT/flash/test/hl_test_submission.jsonl" \
  --gmr "$GMR_ROOT/flash/test/hl_test_submission.jsonl" \
  --output "$RUN_ROOT/flash/localization_comparison.json"
