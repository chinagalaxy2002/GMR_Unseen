#!/usr/bin/env bash
# Wait for all three controls and produce the comparison files automatically.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
SEED="${SEMANTIC_SEED:-3407}"
RUN_ROOT="${RUN_ROOT:-$ROOT_DIR/results/semantic_existence/localization_only_seed${SEED}_100ep}"
while :; do
  ready=1
  for model in moment qd flash; do
    if [[ ! -f "$RUN_ROOT/$model/exit_code" ]]; then ready=0; fi
  done
  [[ "$ready" -eq 1 ]] && break
  sleep 30
done
set +e
bash scripts/finalize_semantic_localization_controls.sh > "$RUN_ROOT/finalize_console.log" 2>&1
status=$?
set -e
printf '%s\n' "$status" > "$RUN_ROOT/finalize_exit_code"
exit "$status"
