#!/usr/bin/env bash
# ==============================================================================
# Decomposed Directional Verifier (DDV) Reproduction Script
#
# Usage:
#   bash reproduce.sh              # Full multi-GPU training & evaluation (~3 mins)
#   bash reproduce.sh --mode eval  # Fast verification of existing checkpoints (~5s)
#   bash reproduce.sh --mode all   # Complete ground-zero pipeline from scratch
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Select Python binary
if command -v conda &> /dev/null && [ -f "/home/guoxiangyu/miniconda3/envs/univtg/bin/python" ]; then
    PYTHON_BIN="/home/guoxiangyu/miniconda3/envs/univtg/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="$(command -v python3)"
else
    PYTHON_BIN="python"
fi

echo "================================================================================"
echo "          DECOMPOSED DIRECTIONAL VERIFIER (DDV): REPRODUCTION SUITE             "
echo "================================================================================"
echo "Script Directory : ${SCRIPT_DIR}"
echo "Python Executable: ${PYTHON_BIN}"
echo "Arguments        : ${*:-<default: --mode train>}"
echo "================================================================================"
echo ""

"${PYTHON_BIN}" "${SCRIPT_DIR}/reproduce.py" "${@:-}"

echo ""
echo "================================================================================"
echo "                       REPRODUCTION RUN FINISHED                                "
echo "Artifacts generated in: ${SCRIPT_DIR}"
echo "  - Report : ${SCRIPT_DIR}/DDV_VERIFIER_REPORT.md"
echo "  - Summary: ${SCRIPT_DIR}/benchmark_summary.json"
echo "  - Models : ${SCRIPT_DIR}/runs/{split}/best_model.pt"
echo "================================================================================"
