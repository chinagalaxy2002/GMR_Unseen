#!/usr/bin/env bash
# Import genuine video/parse reviews, enforce frozen gates, and package five v2 releases.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

V2_ROOT="${V2_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2}"
V1_ROOT="${V1_ROOT:-/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1}"
SOURCE_ROOT="${SOURCE_ROOT:-/home/guoxiangyu/paper/Openword}"
selection="$V2_ROOT/selection"
work="$V2_ROOT/work"
split_ids=(A1 A2_alt A3 C1 C2_alt)
if [[ -n "${BATCH_ATTESTATION:-}" ]]; then
  negative_review_args=(--batch-attestation "$BATCH_ATTESTATION")
  parser_qc_args=(--batch-attestation "$BATCH_ATTESTATION")
else
  : "${NEGATIVE_REVIEWS:?Set NEGATIVE_REVIEWS or BATCH_ATTESTATION}"
  : "${PARSER_QC:?Set PARSER_QC or BATCH_ATTESTATION}"
  negative_review_args=(--reviews "$NEGATIVE_REVIEWS")
  parser_qc_args=(--parser-qc "$PARSER_QC")
fi

python scripts/review_semantic_multisplit.py \
  --work-root "$work" --split-ids "${split_ids[@]}" \
  --shared-action "$selection/shared_action_seen_negative_candidates.jsonl" \
  --shared-composition "$selection/shared_composition_seen_negative_candidates.jsonl" \
  --prior-release "$V1_ROOT" \
  --template "$selection/negative_review_template.csv" \
  "${negative_review_args[@]}"

python scripts/audit_shared_seen_negatives.py --work-root "$work" \
  --split-ids A1 A2_alt A3 --reviewed \
  --allowed-qids-from "$selection/shared_action_seen_negative_candidates.jsonl" \
  --output "$selection/shared_action_seen_negative_reviewed.jsonl"
python scripts/audit_shared_seen_negatives.py --work-root "$work" \
  --split-ids C1 C2_alt --reviewed \
  --allowed-qids-from "$selection/shared_composition_seen_negative_candidates.jsonl" \
  --output "$selection/shared_composition_seen_negative_reviewed.jsonl"

python scripts/audit_multisplit_feasibility.py --work-root "$work" \
  --selection "$selection" --reviewed "${parser_qc_args[@]}"
python - "$selection/reviewed_feasibility.json" <<'PY'
import json
import sys
rows = json.load(open(sys.argv[1]))
failed = [row['id'] for row in rows if not row['passes_all_gates']]
if len(rows) != 5 or failed:
    raise SystemExit(f'Reviewed feasibility gate failed or incomplete: {failed}; audited={len(rows)}')
PY

python scripts/package_semantic_multisplit.py \
  --selection "$selection" --work-root "$work" --release-root "$V2_ROOT" \
  --shared-action "$selection/shared_action_seen_negative_reviewed.jsonl" \
  --shared-composition "$selection/shared_composition_seen_negative_reviewed.jsonl" \
  --source-train "$SOURCE_ROOT/data/raw/charades_sta/charades_pos_train.jsonl" \
  --source-test "$SOURCE_ROOT/data/raw/charades_sta/charades_pos_test.jsonl" \
  --video-archive "$SOURCE_ROOT/downloads/Charades_v1_480.zip"

for split_id in "${split_ids[@]}"; do
  python scripts/validate_release.py --release "$V2_ROOT/$split_id"
done
