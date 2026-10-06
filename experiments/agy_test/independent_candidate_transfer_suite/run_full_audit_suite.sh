#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="/home/guoxiangyu/miniconda3/envs/univtg/bin/python"

echo "================================================================================"
echo "          INDEPENDENT CANDIDATE TRANSFER & ABLATION SUITE (AUDIT RUN)           "
echo "================================================================================"

echo ""
echo ">>> STEP 1: Re-extracting Target-Specific Features (continuous logit scale for Flash)..."
$PYTHON "$SCRIPT_DIR/scripts/01_extract_target_candidate_features.py"

echo ""
echo ">>> STEP 2: Running Corrected Ablation Suite (raw unsigned direction & checkpoint saving)..."
$PYTHON "$SCRIPT_DIR/scripts/02_ablation_and_a3_diagnosis.py"

echo ""
echo ">>> STEP 3: Running 3-Seed Multi-Regime Transfer Suite (saving weights & transfer_predictions.npz)..."
$PYTHON "$SCRIPT_DIR/scripts/03_run_multi_seed_transfer.py"

echo ""
echo ">>> STEP 4: Generating Suite Report..."
$PYTHON "$SCRIPT_DIR/scripts/05_generate_suite_report.py"

echo ""
echo ">>> STEP 5: Verifying runs/ Artifacts..."
PT_COUNT=$(find "$SCRIPT_DIR/runs" -name "*.pt" | wc -l)
NPZ_COUNT=$(find "$SCRIPT_DIR/runs" -name "*.npz" | wc -l)
echo "Verification: found $PT_COUNT checkpoint (.pt) files and $NPZ_COUNT prediction (.npz) files in runs/."

echo ""
echo ">>> ALL SUITE STEPS COMPLETED SUCCESSFULLY!"
